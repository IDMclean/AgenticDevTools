import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import shutil
import json

# Add tooling directory to path to import other tools
import sys
sys.path.insert(0, ".")

from tooling.master_control import MasterControlGraph
from tooling.state import AgentState

class TestNewMasterControl(unittest.TestCase):

    def setUp(self):
        self.original_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)

        # Create a hermetic test environment
        os.makedirs("tooling", exist_ok=True)
        os.makedirs("knowledge_core", exist_ok=True)

        # Create a dummy FSM for the test
        fsm_data = {
            "initial_state": "START",
            "start_state": "IDLE",
            "accept_states": ["DONE", "IDLE", "EXECUTING"],
            "final_states": ["AWAITING_SUBMISSION", "ERROR"],
            "transitions": {
                "IDLE": {"write_op": "EXECUTING", "read_op": "EXECUTING"},
                "ORIENTING": {"orientation_succeeded": "PLANNING"},
                "PLANNING": {"plan_is_set": "EXECUTING"},
                "EXECUTING": {"step_succeeded": "EXECUTING", "all_steps_completed": "FINALIZING", "read_op": "EXECUTING"},
                "FINALIZING": {"finalization_succeeded": "AWAITING_SUBMISSION"}
            }
        }
        with open("tooling/fsm.json", "w") as f:
            json.dump(fsm_data, f)

        with open("tooling/fdc_fsm.json", "w") as f:
            json.dump(fsm_data, f)

        # Create a dummy plan for the test
        with open("plan.txt", "w") as f:
            f.write("1. create_file_with_block: test.txt\nThis is a test file.\n\n2. read_file: test.txt")

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_master_control_workflow(self):
        # Create a mock tool executor
        mock_tool_executor = MagicMock()
        mock_tool_executor.get_plan_path.return_value = "plan.txt"
        mock_tool_executor.read_file.return_value = "1. create_file_with_block: test.txt\nThis is a test file.\n\n2. read_file: test.txt"

        # Initialize the master control graph
        graph = MasterControlGraph(tool_executor=mock_tool_executor)
        agent_state = AgentState(task="Test task")

        # Run the workflow
        final_state = graph.run(agent_state)

        # Assert that the correct tools were called in the correct order
        self.assertEqual(mock_tool_executor.run_in_bash_session.call_count, 1)
        self.assertEqual(mock_tool_executor.create_file_with_block.call_count, 1)
        self.assertEqual(mock_tool_executor.read_file.call_count, 4)

        # Assert that the final state is correct
        self.assertEqual(graph.current_state, "AWAITING_SUBMISSION")

if __name__ == "__main__":
    unittest.main()