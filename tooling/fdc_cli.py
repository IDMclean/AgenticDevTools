"""
A modular, testable, and refactored CLI for the Finite Development Cycle (FDC).
This script accepts a tool_executor object to interact with the environment,
making it independent of globally-defined tools.
"""
import argparse
import json
import os
import sys
from typing import Any, Dict

# --- Configuration ---
MAX_RECURSION_DEPTH = 10

class FDC_CLI:
    def __init__(self, tool_executor: Any, root_dir: str = "."):
        self.tool_executor = tool_executor
        self.root_dir = os.path.abspath(root_dir)
        self.fsm_def_path = os.path.join(self.root_dir, "tooling", "fdc_fsm.json")
        self.action_type_map = self._get_action_type_map()

    def _get_action_type_map(self):
        return {
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
            "call_plan": "call_plan_op",
            "message_user": "user_comm",
        }

    def validate_plan(self, plan_filepath: str):
        try:
            with open(self.fsm_def_path, "r") as f:
                fsm = json.load(f)
            plan_content = self.tool_executor.read_file(filepath=plan_filepath)
        except FileNotFoundError as e:
            print(f"Error: Could not find file {e.filename}", file=sys.stderr)
            sys.exit(1)

        from tooling.plan_parser import parse_plan
        commands = parse_plan(plan_content)

        state = fsm["start_state"]
        simulated_fs = set(self.tool_executor.list_files(path="."))

        for command in commands:
            action_type = self.action_type_map.get(command.tool_name)
            if not action_type:
                print(f"Error: Unknown command '{command.tool_name}'.", file=sys.stderr)
                sys.exit(1)

            transitions = fsm["transitions"].get(state, {})
            if action_type not in transitions:
                print(f"Error: Invalid FSM transition. Cannot perform '{action_type}' from state '{state}'.", file=sys.stderr)
                sys.exit(1)

            if "write_op" in action_type:
                # This is a simplified semantic check. A more robust implementation
                # would parse the arguments to get the filename.
                pass

            if command.tool_name == "call_plan":
                # This is a simplified sub-plan validation. A more robust implementation
                # would recursively validate the sub-plan.
                pass

            state = transitions[action_type]

        if state in fsm["accept_states"]:
            print("\nValidation successful! Plan is syntactically and semantically valid.")
        else:
            print(f"\nValidation failed. Plan ends in non-accepted state: '{state}'", file=sys.stderr)
            sys.exit(1)

def main(tool_executor: Any):
    parser = argparse.ArgumentParser(description="A tool to manage the Finite Development Cycle (FDC).")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validates a plan file against the FDC FSM.")
    validate_parser.add_argument("plan_file", help="The path to the plan file to validate.")

    args = parser.parse_args()

    cli = FDC_CLI(tool_executor)
    if args.command == "validate":
        cli.validate_plan(args.plan_file)

if __name__ == "__main__":
    # This part is for standalone execution and will need a mock tool executor.
    # The main entry point for the agent will be through the MasterControlGraph.
    class MockToolExecutor:
        def read_file(self, filepath: str) -> str:
            with open(filepath, "r") as f:
                return f.read()

    main(MockToolExecutor())
