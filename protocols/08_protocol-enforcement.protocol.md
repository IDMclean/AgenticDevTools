# Protocol: Non-Discretionary Enforcement

## The Problem: Discretionary Adherence

The agent's previous operational model relied on its own discretion to follow the established protocols. This is not a robust system, as it depends on the agent's current interpretation and can lead to deviations from the standard, verifiable workflow. An unenforced protocol is merely a suggestion.

## The Solution: Programmatic Validation

To solve this, we introduce a mandatory, non-discretionary enforcement mechanism. This mechanism is a script, `tooling/protocol_enforcer.py`, that acts as an impartial auditor of the agent's actions.

### How It Works

1.  **Logging as Ground Truth:** Every action the agent takes is recorded in the `logs/activity.log.jsonl` file. This log serves as the immutable, ground-truth record of what actually happened during a task.
2.  **FSM Validation:** The `protocol_enforcer.py` script reads this log for a given task ID. It reconstructs the sequence of actions and validates this sequence against the formal Finite State Machine (FSM) defined in `tooling/fdc_fsm.json`.
3.  **Mandatory Pre-Submission Check:** The agent is now required, as part of its core pre-submission checklist, to execute this script.

**If the sequence of actions violates the FSM, the script will fail (exit with a non-zero status code), and the agent will be programmatically blocked from submitting its work.**

This creates a closed-loop system where protocol adherence is no longer optional. It is a mandatory prerequisite for task completion, ensuring that all work produced is done in a structured, verifiable, and predictable manner.