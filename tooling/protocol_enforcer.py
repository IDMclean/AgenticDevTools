"""
Validates the sequence of actions for a given task against the FDC FSM.

This script reads the activity log, filters for a specific task ID, and
replays the actions against the FSM definition to ensure protocol adherence.
It is intended to be used as a pre-submission check to programmatically
enforce the development protocol.
"""
import argparse
import json
import os
import sys

# --- Configuration ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_FILE_PATH = os.path.join(ROOT_DIR, "logs", "activity.log.jsonl")
FSM_DEF_PATH = os.path.join(ROOT_DIR, "tooling", "fdc_fsm.json")

# This map is critical for translating logged tool calls into FSM alphabet symbols.
# It is intentionally duplicated from fdc_cli.py to keep this enforcer as a
# standalone validation tool.
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
}

def get_fsm_action_for_log(log_entry):
    """
    Determines the FSM action type from a log entry.

    Args:
        log_entry (dict): A single log entry from the activity log.

    Returns:
        str or None: The corresponding FSM action type (e.g., 'plan_op') or None.
    """
    action = log_entry.get("action", {})
    action_type = action.get("type")
    action_details = action.get("details", {})

    # The log contains TOOL_EXEC actions, where the tool name is in the details.
    # We need to map this tool name back to an FSM operation.
    if action_type == "TOOL_EXEC":
        tool_name = action_details.get("tool_name")
        if not tool_name:
            return None

        # Handle the special case where 'close' is an argument to a bash command
        if tool_name == "run_in_bash_session" and "close" in action_details.get("tool_args", ""):
            return "close_op"

        # General case: Map the tool name directly to its FSM operation type
        return ACTION_TYPE_MAP.get(tool_name)

    # The 'PLAN_UPDATE' action type corresponds to the 'plan_op' in the FSM.
    if action_type == "PLAN_UPDATE":
        return "plan_op"

    # Other action types from the schema like FILE_READ or FILE_WRITE are not
    # directly used by the FSM validator, which relies on the more specific
    # tool names logged under TOOL_EXEC. We can ignore them.

    # Other log types like TASK_START, TASK_END are not direct FSM transitions
    # initiated by the agent's plan, so we ignore them for validation.
    return None

def enforce_protocol(task_id):
    """
    Validates the action sequence for a task against the FDC FSM.

    Args:
        task_id (str): The task ID to validate.

    Returns:
        bool: True if the protocol was followed, False otherwise.
    """
    try:
        with open(FSM_DEF_PATH, "r") as f:
            fsm = json.load(f)
        with open(LOG_FILE_PATH, "r") as f:
            log_lines = f.readlines()
    except FileNotFoundError as e:
        print(f"Error: Could not find required file: {e.filename}", file=sys.stderr)
        return False

    task_actions = []
    for line in log_lines:
        try:
            log_entry = json.loads(line)
            if log_entry.get("task", {}).get("id") == task_id:
                fsm_action = get_fsm_action_for_log(log_entry)
                if fsm_action:
                    task_actions.append((fsm_action, log_entry.get('timestamp')))
        except json.JSONDecodeError:
            print(f"Warning: Could not parse log line: {line.strip()}", file=sys.stderr)
            continue

    # Sort actions by timestamp to ensure correct order
    task_actions.sort(key=lambda x: x[1])

    current_state = fsm["start_state"]
    print(f"--- Validating action sequence for task '{task_id}' ---")
    print(f"Initial state: {current_state}")

    for i, (action, timestamp) in enumerate(task_actions):
        transitions = fsm["transitions"].get(current_state)
        if not transitions or action not in transitions:
            print(f"\nProtocol Violation Detected!")
            print(f"  Task ID: {task_id}")
            print(f"  Invalid Action: '{action}' from state '{current_state}'")
            print(f"  Violation occurred at step {i+1} (Timestamp: {timestamp})")
            print(f"  Allowed actions from '{current_state}': {list(transitions.keys()) if transitions else 'None'}")
            return False

        next_state = transitions[action]
        print(f"  Step {i+1}: Action '{action}' -> OK. Transition from {current_state} to {next_state}")
        current_state = next_state

    if current_state not in fsm["accept_states"]:
        print(f"\nProtocol Violation Detected!")
        print(f"  Task ID: {task_id}")
        print(f"  Final State '{current_state}' is not an accepted state.")
        print(f"  Accepted final states are: {fsm['accept_states']}")
        return False

    print(f"\n--- Protocol Adherence Verified for task '{task_id}' ---")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="A tool to enforce FDC protocol adherence by validating task logs."
    )
    parser.add_argument(
        "--task-id", required=True, help="The unique identifier for the task to validate."
    )
    args = parser.parse_args()

    if enforce_protocol(args.task_id):
        print("Validation successful.")
        sys.exit(0)
    else:
        print("Validation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()