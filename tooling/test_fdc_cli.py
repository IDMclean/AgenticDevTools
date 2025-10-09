import unittest
import os
import json
import shutil
import sys
from io import StringIO
from unittest.mock import patch

# This is a bit of a hack to make the test run from the root directory
# without having to install the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tooling.fdc_cli import start_task, close_task, lint_plan

class TestFdcCli(unittest.TestCase):

    def setUp(self):
        """Set up temporary directories and files for testing."""
        self.test_dir = "temp_test_dir_cli"
        self.logs_dir = os.path.join(self.test_dir, "logs")
        self.postmortems_dir = os.path.join(self.test_dir, "postmortems")
        self.tooling_dir = os.path.join(self.test_dir, "tooling")
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.postmortems_dir, exist_ok=True)
        os.makedirs(self.tooling_dir, exist_ok=True)

        self.fsm_path = os.path.join(self.tooling_dir, "fdc_fsm.json")
        self.plan_path = os.path.join(self.test_dir, "plan.txt")
        self.postmortem_template_path = os.path.join(self.test_dir, "postmortem.md")

        with open(self.postmortem_template_path, "w") as f:
            f.write("# Post-mortem Template")

        # Use a complete and correct FSM definition for the test
        self.fsm_def = {
            "states": ["IDLE", "ORIENTING", "PLANNING", "EXECUTING", "REVIEW", "DONE"],
            "alphabet": ["start_op", "plan_op", "step_op", "submit_op", "read_op", "write_op", "delete_op", "move_op", "tool_exec", "close_op", "loop_op"],
            "transitions": {
                "IDLE": {"start_op": "ORIENTING"},
                "ORIENTING": {"plan_op": "PLANNING"},
                "PLANNING": {"step_op": "EXECUTING", "read_op": "PLANNING", "tool_exec": "PLANNING"},
                "EXECUTING": {
                    "step_op": "EXECUTING", "read_op": "EXECUTING", "write_op": "EXECUTING",
                    "delete_op": "EXECUTING", "move_op": "EXECUTING", "tool_exec": "EXECUTING",
                    "loop_op": "EXECUTING", "close_op": "REVIEW"
                },
                "REVIEW": {"submit_op": "DONE"}
            },
            "start_state": "IDLE",
            "accept_states": ["DONE"]
        }
        with open(self.fsm_path, "w") as f:
            json.dump(self.fsm_def, f)

        self.held_stdout = sys.stdout
        self.held_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        """Clean up temporary directories and files."""
        shutil.rmtree(self.test_dir)
        sys.stdout = self.held_stdout
        sys.stderr = self.held_stderr

    @patch('tooling.fdc_cli.LOG_FILE_PATH', new_callable=lambda: "temp_test_dir_cli/logs/activity.log.jsonl")
    def test_start_task(self, mock_log_path):
        start_task("test-task-1")
        self.assertTrue(os.path.exists(mock_log_path))
        with open(mock_log_path, "r") as f:
            log_entry = json.loads(f.readline())
            self.assertEqual(log_entry["task_id"], "test-task-1")
            self.assertEqual(log_entry["action"]["type"], "TASK_START")

    @patch('tooling.fdc_cli.POSTMORTEMS_DIR', new_callable=lambda: "temp_test_dir_cli/postmortems")
    @patch('tooling.fdc_cli.POSTMORTEM_TEMPLATE_PATH', new_callable=lambda: "temp_test_dir_cli/postmortem.md")
    @patch('tooling.fdc_cli.LOG_FILE_PATH', new_callable=lambda: "temp_test_dir_cli/logs/activity.log.jsonl")
    def test_close_task(self, mock_log_path, mock_template_path, mock_postmortems_dir):
        close_task("test-task-2")
        self.assertTrue(any(f.endswith("-test-task-2.md") for f in os.listdir(mock_postmortems_dir)))
        with open(mock_log_path, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            log1 = json.loads(lines[0])
            log2 = json.loads(lines[1])
            self.assertEqual(log1["action"]["type"], "POST_MORTEM")
            self.assertEqual(log2["action"]["type"], "TASK_END")

    @patch('tooling.fdc_cli.FSM_DEF_PATH', new_callable=lambda: "temp_test_dir_cli/tooling/fdc_fsm.json")
    @patch('os.walk')
    def test_lint_plan_valid(self, mock_os_walk, mock_fsm_path):
        mock_os_walk.return_value = [("./", [], ["existing_file.txt"])]
        plan_content = """
set_plan
plan_step_complete
read_file existing_file.txt
create_file_with_block new_file.txt
run_in_bash_session echo "test"
run_in_bash_session python3 tooling/fdc_cli.py close --task-id my-task
"""
        with open(self.plan_path, "w") as f:
            f.write(plan_content)

        lint_plan(self.plan_path)
        output = sys.stdout.getvalue()
        self.assertIn("Linting complete. Plan is valid and well-formed.", output)

    @patch('tooling.fdc_cli.FSM_DEF_PATH', new_callable=lambda: "temp_test_dir_cli/tooling/fdc_fsm.json")
    @patch('os.walk')
    def test_lint_plan_invalid_fsm_transition(self, mock_os_walk, mock_fsm_path):
        mock_os_walk.return_value = [("./", [], [])]
        plan_content = """
read_file some_file.txt
run_in_bash_session python3 tooling/fdc_cli.py close --task-id my-task
"""
        with open(self.plan_path, "w") as f:
            f.write(plan_content)

        with self.assertRaises(SystemExit):
            lint_plan(self.plan_path)
        output = sys.stderr.getvalue()
        self.assertIn("Invalid FSM transition", output)

    @patch('tooling.fdc_cli.FSM_DEF_PATH', new_callable=lambda: "temp_test_dir_cli/tooling/fdc_fsm.json")
    @patch('os.walk')
    def test_lint_plan_semantic_error(self, mock_os_walk, mock_fsm_path):
        mock_os_walk.return_value = [("./", [], [])]
        plan_content = """
set_plan
plan_step_complete
read_file non_existent_file.txt
run_in_bash_session python3 tooling/fdc_cli.py close --task-id my-task
"""
        with open(self.plan_path, "w") as f:
            f.write(plan_content)

        with self.assertRaises(SystemExit):
            lint_plan(self.plan_path)
        output = sys.stderr.getvalue()
        self.assertIn("Cannot access 'non_existent_file.txt' because it does not exist", output)

    @patch('tooling.fdc_cli.FSM_DEF_PATH', new_callable=lambda: "temp_test_dir_cli/tooling/fdc_fsm.json")
    @patch('os.walk')
    def test_lint_plan_missing_close_command(self, mock_os_walk, mock_fsm_path):
        mock_os_walk.return_value = [("./", [], [])]
        plan_content = """
set_plan
plan_step_complete
"""
        with open(self.plan_path, "w") as f:
            f.write(plan_content)

        with self.assertRaises(SystemExit):
            lint_plan(self.plan_path)
        output = sys.stderr.getvalue()
        self.assertIn("The plan must end with the 'close' command", output)

if __name__ == '__main__':
    unittest.main()