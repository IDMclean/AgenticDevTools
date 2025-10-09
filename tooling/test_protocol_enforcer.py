import unittest
import os
import json
import shutil
from datetime import datetime, timezone

# Add tooling to path to import the script we are testing
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from protocol_enforcer import enforce_protocol

class TestProtocolEnforcer(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for test artifacts."""
        self.test_dir = "temp_test_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        self.log_path = os.path.join(self.test_dir, "test_activity.log.jsonl")
        self.fsm_path = os.path.join(self.test_dir, "test_fsm.json")

        # Create a mock FSM for the tests
        self.mock_fsm = {
            "states": ["IDLE", "PLANNING", "EXECUTING", "POST_MORTEM", "DONE"],
            "alphabet": ["plan_op", "step_op", "write_op", "read_op", "close_op", "submit_op"],
            "transitions": {
                "IDLE": {"plan_op": "PLANNING"},
                "PLANNING": {"step_op": "EXECUTING"},
                "EXECUTING": {
                    "write_op": "EXECUTING",
                    "read_op": "EXECUTING",
                    "close_op": "POST_MORTEM"
                },
                "POST_MORTEM": {"submit_op": "DONE"}
            },
            "start_state": "IDLE",
            "accept_states": ["DONE"]
        }
        with open(self.fsm_path, "w") as f:
            json.dump(self.mock_fsm, f)

        # Monkey-patch the constants in the enforcer script to use our test paths
        import protocol_enforcer
        protocol_enforcer.LOG_FILE_PATH = self.log_path
        protocol_enforcer.FSM_DEF_PATH = self.fsm_path

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def _create_mock_log_entry(self, task_id, action_type, tool_name=None, tool_args=None):
        """Helper to create a single log entry."""
        entry = {
            "log_id": "test-log-id",
            "session_id": "test-session-id",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "Phase Test",
            "task": {"id": task_id, "plan_step": 1},
            "action": {"type": action_type, "details": {}},
            "outcome": {"status": "SUCCESS"}
        }
        if tool_name:
            entry["action"]["details"]["tool_name"] = tool_name
        if tool_args:
            entry["action"]["details"]["tool_args"] = tool_args
        return entry

    def _write_mock_log_file(self, entries):
        """Helper to write a list of entries to the mock log file."""
        with open(self.log_path, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

    def test_valid_sequence(self):
        """Test that a valid sequence of actions passes validation."""
        task_id = "valid-task-01"
        log_entries = [
            self._create_mock_log_entry(task_id, "PLAN_UPDATE"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="plan_step_complete"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="create_file_with_block"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="run_in_bash_session", tool_args="close"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="submit"),
        ]
        self._write_mock_log_file(log_entries)
        self.assertTrue(enforce_protocol(task_id), "A valid sequence should pass.")

    def test_invalid_transition(self):
        """Test that a sequence with an invalid FSM transition fails."""
        task_id = "invalid-task-01"
        log_entries = [
            self._create_mock_log_entry(task_id, "PLAN_UPDATE"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="create_file_with_block"), # Invalid: write_op from PLANNING
        ]
        self._write_mock_log_file(log_entries)
        self.assertFalse(enforce_protocol(task_id), "An invalid transition should fail.")

    def test_non_accepting_final_state(self):
        """Test that a sequence that ends in a non-accepting state fails."""
        task_id = "incomplete-task-01"
        log_entries = [
            self._create_mock_log_entry(task_id, "PLAN_UPDATE"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="plan_step_complete"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="create_file_with_block"),
            # Missing close and submit
        ]
        self._write_mock_log_file(log_entries)
        self.assertFalse(enforce_protocol(task_id), "An incomplete sequence should fail.")

    def test_other_task_logs_are_ignored(self):
        """Test that logs from other tasks do not interfere with validation."""
        task_id = "valid-task-02"
        log_entries = [
            self._create_mock_log_entry("some-other-task", "TOOL_EXEC", tool_name="create_file_with_block"),
            self._create_mock_log_entry(task_id, "PLAN_UPDATE"),
            self._create_mock_log_entry("another-task", "PLAN_UPDATE"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="plan_step_complete"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="create_file_with_block"),
            self._create_mock_log_entry("yet-another-task", "TOOL_EXEC", tool_name="submit"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="run_in_bash_session", tool_args="close"),
            self._create_mock_log_entry(task_id, "TOOL_EXEC", tool_name="submit"),
        ]
        self._write_mock_log_file(log_entries)
        self.assertTrue(enforce_protocol(task_id), "Logs from other tasks should be ignored.")

if __name__ == "__main__":
    unittest.main()