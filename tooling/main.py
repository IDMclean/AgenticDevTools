"""
The main entrypoint for the refactored Jules agent system.

This script initializes and runs the new, robust, library-based orchestrator.
It replaces the old `master_control_cli.py` and demonstrates the improved
stability and maintainability of the new architecture.

This entrypoint is responsible for:
1.  Initializing the `AgentState` for a new task.
2.  Creating an instance of the `Orchestrator`.
3.  Running the main lifecycle loop, driving the orchestrator's generator
    by providing inputs when requested.
"""
import os
import sys

# Ensure tooling is on the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from orchestrator import Orchestrator, OrchestratorError
from state import AgentState

def main():
    """
    The main function to run the agent's lifecycle.
    """
    print("--- Initializing Refactored Agent System ---")

    task = "Demonstrate the refactored, stable development state."
    agent_state = AgentState(task=task)

    try:
        orchestrator = Orchestrator()
    except OrchestratorError as e:
        print(f"FATAL: Could not initialize Orchestrator: {e}")
        return

    # Run the lifecycle using the new generator-based FSM
    try:
        lifecycle = orchestrator.run(agent_state)
        current_request = next(lifecycle) # Start the generator

        while True:
            print(f"\n[Main Loop] Orchestrator is in state '{orchestrator.current_state}', requesting: {current_request}")

            if current_request == "AWAITING_PLAN":
                print("[Main Loop] Simulating agent creating a plan...")
                # This plan is now compliant with fdc_fsm.json
                sample_plan_content = """\
set_plan
This is a demonstration plan.

plan_step_complete
This moves us to the EXECUTING state.

read_file
README.md

plan_step_complete
We are still in EXECUTING state.

fdc_close
This moves us to the POST_MORTEM state.

submit
This moves us to the DONE state.
"""
                current_request = lifecycle.send(sample_plan_content)

            elif current_request == "AWAITING_POSTMORTEM":
                print("[Main Loop] Simulating agent providing post-mortem analysis...")
                sample_postmortem_content = """\
# Post-Mortem Analysis
## Outcome
The refactoring was successful.
## Lessons Learned
Lesson: Direct function calls are better than subprocesses.
Action: Refactor more components to use a library-based approach.
"""
                current_request = lifecycle.send(sample_postmortem_content)

            elif orchestrator.current_state in orchestrator.fsm["final_states"]:
                 print(f"[Main Loop] Orchestrator reached final state: {orchestrator.current_state}")
                 break
            else:
                # For simple states that don't need input, just advance
                current_request = next(lifecycle)

    except StopIteration as e:
        final_state = e.value
        print(f"\n[Main Loop] Lifecycle finished in state: {final_state}")
    except Exception as e:
        print(f"\n[Main Loop] An unexpected error occurred: {e}")
        agent_state.error = str(e)


    # Print the final report
    print("\n--- Final State ---")
    print(agent_state.to_json())
    print("--- System Run Complete ---")


if __name__ == "__main__":
    main()