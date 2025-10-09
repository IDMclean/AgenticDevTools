import argparse
import datetime
import json
import os
import shutil
import sys
import uuid

# --- Configuration ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POSTMORTEM_TEMPLATE_PATH = os.path.join(ROOT_DIR, "postmortem.md")
POSTMORTEMS_DIR = os.path.join(ROOT_DIR, "postmortems")
LOG_FILE_PATH = os.path.join(ROOT_DIR, "logs", "activity.log.jsonl")
FSM_DEF_PATH = os.path.join(ROOT_DIR, "tooling", "fdc_fsm.json")

ACTION_TYPE_MAP = {
    "set_plan": "plan_op",
    "plan_step_complete": "step_op",
    "submit": "submit_op",
    "create_file_with_block": "write_op",
    "overwrite_file_with_block": "write_op",
    "replace_with_git_merge_diff": "write_op",
    "read_file": "read_op",
    "list_files": "read_op",
    "grep": "read_op",
    "delete_file": "delete_op",
    "rename_file": "move_op",
    "run_in_bash_session": "tool_exec",
    "for_each_file": "loop_op",
}

# --- Logging Helpers ---


def _log_event(log_entry):
    """Appends a new log entry to the activity log."""
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    with open(LOG_FILE_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def _create_log_entry(task_id, action_type, details):
    """Creates a structured log entry dictionary."""
    return {
        "log_id": str(uuid.uuid4()),
        "session_id": os.getenv("JULES_SESSION_ID", "unknown"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "task_id": task_id,
        "action": {"type": action_type, "details": details},
        "status": "SUCCESS",
    }


# --- CLI Subcommands ---


def start_task(task_id):
    """Initiates a new FDC task."""
    if not task_id:
        print("Error: --task-id is required.", file=sys.stderr)
        sys.exit(1)

    _log_event(
        _create_log_entry(
            task_id,
            "TASK_START",
            {"summary": f"Development phase for FDC task '{task_id}' formally started."},
        )
    )
    print(f"Logged TASK_START event for task: {task_id}")
    print("Orientation complete. Ready to proceed with planning.")


def close_task(task_id):
    """Closes an FDC task and generates a post-mortem."""
    if not task_id:
        print("Error: --task-id is required.", file=sys.stderr)
        sys.exit(1)

    safe_task_id = "".join(c for c in task_id if c.isalnum() or c in ("-", "_"))
    new_path = os.path.join(
        POSTMORTEMS_DIR, f"{datetime.date.today()}-{safe_task_id}.md"
    )
    os.makedirs(POSTMORTEMS_DIR, exist_ok=True)

    try:
        shutil.copyfile(POSTMORTEM_TEMPLATE_PATH, new_path)
        print(f"Successfully created new post-mortem file: {new_path}")
    except FileNotFoundError:
        print(f"Warning: Post-mortem template not found at '{POSTMORTEM_TEMPLATE_PATH}'. Creating an empty file.", file=sys.stderr)
        open(new_path, 'a').close()
    except Exception as e:
        print(f"Error creating post-mortem file: {e}", file=sys.stderr)
        sys.exit(1)

    _log_event(
        _create_log_entry(
            task_id,
            "POST_MORTEM",
            {"summary": f"Post-mortem initiated for '{task_id}'."},
        )
    )
    _log_event(
        _create_log_entry(
            task_id,
            "TASK_END",
            {"summary": f"Development phase for FDC task '{task_id}' formally closed."},
        )
    )
    print(f"Logged POST_MORTEM and TASK_END events for task: {task_id}")


def lint_plan(plan_filepath):
    """Validates and analyzes a plan file."""
    try:
        with open(FSM_DEF_PATH, "r") as f:
            fsm = json.load(f)
        with open(plan_filepath, "r") as f:
            lines_with_indent = f.readlines()
        lines = [(i, line.rstrip("\n")) for i, line in enumerate(lines_with_indent) if line.strip()]
    except FileNotFoundError as e:
        print(f"Error: Could not find file {e.filename}", file=sys.stderr)
        sys.exit(1)

    # --- 1. Closure Mandate Validation ---
    last_line = lines[-1][1].strip() if lines else ""
    if not ("run_in_bash_session" in last_line and "fdc_cli.py" in last_line and "close" in last_line):
        print("\nValidation failed. The plan must end with the 'close' command.", file=sys.stderr)
        sys.exit(1)

    # --- 2. FSM and Semantic Validation ---
    simulated_fs = set()
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        for name in files:
            simulated_fs.add(os.path.join(root, name).replace("./", ""))

    initial_state = "ORIENTING"
    final_state, _, _ = _validate_plan_recursive(lines, 0, 0, initial_state, simulated_fs, {}, fsm)

    valid_lint_end_states = fsm.get("accept_states", []) + ["REVIEW"]
    if final_state not in valid_lint_end_states:
        print(f"\nValidation failed. Plan ends in non-accepted state: '{final_state}'", file=sys.stderr)
        sys.exit(1)

    # --- 3. Complexity Analysis ---
    complexity = _analyze_complexity(lines_with_indent)
    print(f"\nPlan Analysis Results:")
    print(f"  - Complexity: {complexity}")

    print("\nLinting complete. Plan is valid and well-formed.")


def _validate_plan_recursive(lines, start_index, indent_level, state, fs, placeholders, fsm):
    """Recursively validates a block of a plan."""
    i = start_index
    while i < len(lines):
        line_num, line_content = lines[i]
        current_indent = len(line_content) - len(line_content.lstrip(" "))

        if current_indent < indent_level:
            return state, fs, i
        if current_indent > indent_level:
            print(f"Error on line {line_num+1}: Unexpected indentation.", file=sys.stderr)
            sys.exit(1)

        line_content = line_content.strip()
        command, *args = line_content.split()

        if command == "for_each_file":
            loop_depth = len(placeholders) + 1
            placeholder_key = f"{{file{loop_depth}}}"
            dummy_file = f"dummy_file_for_loop_{loop_depth}"

            loop_body_start = i + 1
            j = loop_body_start
            while j < len(lines) and (len(lines[j][1]) - len(lines[j][1].lstrip(" "))) > indent_level:
                j += 1

            loop_fs = fs.copy()
            loop_fs.add(dummy_file)
            new_placeholders = placeholders.copy()
            new_placeholders[placeholder_key] = dummy_file

            state, loop_fs, _ = _validate_plan_recursive(
                lines, loop_body_start, indent_level + 2, state, loop_fs, new_placeholders, fsm
            )
            fs.update(loop_fs)
            i = j
        else:
            state, fs = _validate_action(line_num, line_content, state, fsm, fs, placeholders)
            i += 1

    return state, fs, i


def _validate_action(line_num, line_content, state, fsm, fs, placeholders):
    """Validates a single, non-loop action."""
    for key, val in placeholders.items():
        line_content = line_content.replace(key, val)

    command, *args = line_content.split()
    action_type = ACTION_TYPE_MAP.get(command)

    if command == "run_in_bash_session" and "close" in args and any("fdc_cli.py" in arg for arg in args):
        action_type = "close_op"

    if not action_type:
        print(f"Error on line {line_num+1}: Unknown command '{command}'.", file=sys.stderr)
        sys.exit(1)

    transitions = fsm["transitions"].get(state)
    if action_type not in (transitions or {}):
        print(f"Error on line {line_num+1}: Invalid FSM transition. Cannot perform '{action_type}' from state '{state}'.", file=sys.stderr)
        sys.exit(1)

    if command == "create_file_with_block" and args and args[0] in fs:
        print(f"Error on line {line_num+1}: Semantic error. Cannot create '{args[0]}' because it already exists.", file=sys.stderr)
        sys.exit(1)
    if command in ["read_file", "delete_file", "replace_with_git_merge_diff"] and args and args[0] not in fs:
        print(f"Error on line {line_num+1}: Semantic error. Cannot access '{args[0]}' because it does not exist.", file=sys.stderr)
        sys.exit(1)

    if command == "create_file_with_block" and args:
        fs.add(args[0])
    if command == "delete_file" and args and args[0] in fs:
        fs.remove(args[0])

    next_state = transitions[action_type]
    return next_state, fs


def _analyze_complexity(plan_lines_with_indent):
    """Determines the complexity class of a plan."""
    loop_indents = []
    for line in plan_lines_with_indent:
        if line.strip().startswith("for_each_file"):
            indent = len(line) - len(line.lstrip(" "))
            loop_indents.append(indent)

    if not loop_indents:
        return "Constant (O(1))"
    elif max(loop_indents) > min(loop_indents):
        return "Exponential (EXPTIME-Class)"
    else:
        return "Polynomial (P-Class)"


def main():
    parser = argparse.ArgumentParser(description="A tool to manage the Finite Development Cycle (FDC).")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands", required=True)

    start_parser = subparsers.add_parser("start", help="Starts a new task, initiating the FDC.")
    start_parser.add_argument("--task-id", required=True, help="The unique identifier for the task.")

    lint_parser = subparsers.add_parser("lint", help="Validates and analyzes a plan file.")
    lint_parser.add_argument("plan_file", help="The path to the plan file to lint.")

    close_parser = subparsers.add_parser("close", help="Closes a task, initiating the post-mortem process.")
    close_parser.add_argument("--task-id", required=True, help="The unique identifier for the task.")

    args = parser.parse_args()
    if args.command == "start":
        start_task(args.task_id)
    elif args.command == "lint":
        lint_plan(args.plan_file)
    elif args.command == "close":
        close_task(args.task_id)


if __name__ == "__main__":
    main()