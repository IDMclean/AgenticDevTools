"""
Integration tests for the master control FSM and CFDC workflow.

This test suite has been redesigned to be single-threaded and deterministic,
eliminating the file-polling, multi-threaded architecture that was causing
timeouts and instability in the test environment.
"""
import unittest
import sys
import os
sys.path.insert(0, ".")
import datetime
import json
import subprocess
import tempfile
import shutil
from unittest.mock import patch

from tooling.master_control import MasterControlGraph
from tooling.state import AgentState, PlanContext
from tooling.plan_parser import parse_plan, Command
from unittest.mock import MagicMock

class TestMasterControlRedesigned(unittest.TestCase):
    """
    Validates the FSM workflow in a single-threaded, deterministic manner.
    """

    def setUp(self):
        self.original_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)

        # Create a hermetic test environment
        os.makedirs("knowledge_core", exist_ok=True)
        os.makedirs("postmortems", exist_ok=True)
        os.makedirs("tooling", exist_ok=True)
        os.makedirs("protocols", exist_ok=True)
        # Copy essential dependencies
        shutil.copyfile(os.path.join(self.original_cwd, "postmortem.md"), "postmortem.md")
        shutil.copyfile(os.path.join(self.original_cwd, "tooling", "fdc_cli.py"), "tooling/fdc_cli.py")
        shutil.copyfile(os.path.join(self.original_cwd, "tooling", "master_control.py"), "tooling/master_control.py")
        shutil.copyfile(os.path.join(self.original_cwd, "tooling", "fsm.json"), "tooling/fsm.json")

        # Create a dummy fsm.json
        fsm_data = {
            "initial_state": "START",
            "start_state": "IDLE",
            "accept_states": ["DONE", "IDLE", "EXECUTING"],
            "final_states": ["AWAITING_SUBMISSION", "ERROR"],
            "transitions": {
                "IDLE": {"write_op": "EXECUTING", "read_op": "EXECUTING", "user_comm": "IDLE"},
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


        self.fsm_path = "tooling/fsm.json"
        self.task_id = "test-redesigned-workflow"
        self.agent_state = AgentState(task=self.task_id)
        self.mock_tool_executor = MagicMock()
        self.graph = MasterControlGraph(tool_executor=self.mock_tool_executor, fsm_path=self.fsm_path)

        # Ensure a clean slate for tests that use tokens
        if os.path.exists("authorization.token"):
            os.remove("authorization.token")

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_do_orientation(self):
        trigger = self.graph.do_orientation(self.agent_state)
        self.assertEqual(trigger, "orientation_succeeded")

    def test_do_planning(self):
        with open("plan.txt", "w") as f:
            f.write("1. message_user: Test message")
        self.mock_tool_executor.get_plan_path.return_value = "plan.txt"
        self.mock_tool_executor.read_file.return_value = "1. message_user: Test message"
        trigger = self.graph.do_planning(self.agent_state)
        self.assertEqual(trigger, "plan_is_set")

    def test_do_execution(self):
        self.agent_state.plan_stack.append(
            PlanContext(plan_path="plan.txt", commands=[
                Command(tool_name="message_user", args_text="test"),
            ])
        )
        trigger = self.graph.do_execution(self.agent_state)
        self.assertEqual(trigger, "all_steps_completed")

    def test_do_finalizing(self):
        trigger = self.graph.do_finalizing(self.agent_state)
        self.assertEqual(trigger, "finalization_succeeded")


if __name__ == "__main__":
    unittest.main()