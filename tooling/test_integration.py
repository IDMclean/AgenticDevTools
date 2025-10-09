import unittest
import os
import sys
import json
import shutil
import threading
import time
import datetime
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tooling.master_control import MasterControlGraph
from tooling.state import AgentState

class TestFullSystemIntegration(unittest.TestCase):
    """
    Tests the full, end-to-end, synchronized integration of the hierarchical FSM.
    """

    def setUp(self):
        self.task_id = "test-full-integration"
        safe_task_id = "".join(c for c in self.task_id if c.isalnum() or c in ("-", "_"))

        self.test_dir = "temp_full_integration_test"
        os.makedirs(self.test_dir, exist_ok=True)

        self.tooling_dir = os.path.join(self.test_dir, "tooling")
        self.postmortems_dir = os.path.join(self.test_dir, "postmortems")
        os.makedirs(self.tooling_dir, exist_ok=True)
        os.makedirs(self.postmortems_dir, exist_ok=True)

        self.plan_file = os.path.join(self.test_dir, "plan.txt")
        self.step_complete_file = os.path.join(self.test_dir, "step_complete.txt")
        self.analysis_complete_file = os.path.join(self.test_dir, "analysis_complete.txt")
        self.draft_postmortem_file = os.path.join(self.test_dir, f"DRAFT-{self.task_id}.md")
        self.final_postmortem_file = os.path.join(self.postmortems_dir, f"{datetime.date.today()}-{safe_task_id}.md")
        self.postmortem_template = os.path.join(self.test_dir, "postmortem.md")
        self.master_fsm_path = os.path.join(self.tooling_dir, "fsm.json")
        self.toolchain_fsm_path = os.path.join(self.tooling_dir, "fdc_fsm.json")
        self.test_output_file = os.path.join(self.test_dir, "test_output.txt")

        with open(self.postmortem_template, "w") as f:
            f.write("# Post-mortem Template")

        # A complete FSM for the orchestrator
        master_fsm = {
            "initial_state": "START", "final_states": ["AWAITING_SUBMISSION", "ERROR"],
            "transitions": [
                {"source": "START", "dest": "ORIENTING", "trigger": "begin_task"},
                {"source": "ORIENTING", "dest": "PLANNING", "trigger": "orientation_succeeded"},
                {"source": "PLANNING", "dest": "EXECUTING", "trigger": "plan_is_set"},
                {"source": "PLANNING", "dest": "ERROR", "trigger": "planning_failed"},
                {"source": "EXECUTING", "dest": "EXECUTING", "trigger": "step_succeeded"},
                {"source": "EXECUTING", "dest": "AWAITING_ANALYSIS", "trigger": "all_steps_completed"},
                {"source": "AWAITING_ANALYSIS", "dest": "POST_MORTEM", "trigger": "analysis_complete"},
                {"source": "POST_MORTEM", "dest": "AWAITING_SUBMISSION", "trigger": "post_mortem_complete"}
            ]
        }
        with open(self.master_fsm_path, "w") as f:
            json.dump(master_fsm, f)

        # A complete FSM for the toolchain linter
        toolchain_fsm = {
            "states": ["IDLE", "ORIENTING", "PLANNING", "EXECUTING", "REVIEW", "DONE"],
            "transitions": {
                "ORIENTING": {"plan_op": "PLANNING"},
                "PLANNING": {"step_op": "EXECUTING"},
                "EXECUTING": {"write_op": "EXECUTING", "tool_exec": "EXECUTING", "close_op": "REVIEW"}
            },
            "start_state": "IDLE", "accept_states": ["DONE"]
        }
        with open(self.toolchain_fsm_path, "w") as f:
            json.dump(toolchain_fsm, f)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('tooling.master_control.subprocess.run')
    @patch('tooling.master_control.execute_research_protocol', return_value="Mocked Research Data")
    def test_full_synchronized_workflow(self, mock_research, mock_subprocess_run):
        mock_subprocess_run.return_value = Mock(returncode=0)

        with patch('tooling.master_control.FSM_PATH', self.master_fsm_path), \
             patch('tooling.master_control.PLAN_FILE', self.plan_file), \
             patch('tooling.master_control.STEP_COMPLETE_FILE', self.step_complete_file), \
             patch('tooling.master_control.ANALYSIS_COMPLETE_FILE', self.analysis_complete_file), \
             patch('tooling.master_control.POSTMORTEM_TEMPLATE', self.postmortem_template), \
             patch('tooling.master_control.POSTMORTEMS_DIR', self.postmortems_dir):

            valid_plan = (
                f'set_plan "A valid plan."\n'
                f'create_file_with_block {self.test_output_file} "content"\n'
                f'run_in_bash_session python3 tooling/fdc_cli.py close --task-id {self.task_id}'
            )
            plan_steps = [step for step in valid_plan.split('\n') if step.strip()]
            final_state_container = {}

            def run_fsm():
                initial_state = AgentState(task=self.task_id)
                graph = MasterControlGraph(fsm_path=self.master_fsm_path)
                final_state = graph.run(initial_state)
                final_state_container["final_state"] = final_state

            fsm_thread = threading.Thread(target=run_fsm)
            fsm_thread.start()

            # Wait for orchestrator to be ready for the plan
            time.sleep(1)
            with open(self.plan_file, "w") as f:
                f.write(valid_plan)

            # Wait for the plan to be consumed
            while os.path.exists(self.plan_file):
                time.sleep(0.1)

            # Synchronously signal completion for each step
            for i in range(len(plan_steps)):
                with open(self.step_complete_file, "w") as f:
                    f.write(f"Done step {i+1}")
                # Wait for the orchestrator to consume the signal file before proceeding
                while os.path.exists(self.step_complete_file):
                    time.sleep(0.1)

            # Signal analysis completion
            with open(self.analysis_complete_file, "w") as f:
                f.write("Analysis done.")

            fsm_thread.join(timeout=15)
            self.assertFalse(fsm_thread.is_alive(), "FSM thread timed out.")

            final_state = final_state_container.get("final_state")
            self.assertIsNotNone(final_state)
            self.assertIsNone(final_state.error, f"FSM ended in an error state: {final_state.error}")
            self.assertTrue(os.path.exists(self.final_postmortem_file))
            # The test_output_file is not created because the actual plan execution is mocked.
            # The key assertion is that the FSM completes its flow.

if __name__ == "__main__":
    unittest.main()