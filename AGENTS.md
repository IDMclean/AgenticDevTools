# Jules Agent Protocol: The Hierarchical Development Cycle

**Version:** 4.0.0

---
## 1. The Core Problem: Ensuring Formally Verifiable Execution

To tackle complex tasks reliably, an agent's workflow must be formally structured and guaranteed to terminate—it must be **decidable**. This is achieved through a hierarchical system composed of a high-level **Orchestrator** that manages the agent's overall state and a low-level **FDC Toolchain** that governs the validity of the agent's plans. This structure prevents the system from entering paradoxical, non-terminating loops.

---
## 2. The Solution: A Two-Layered FSM System

### Layer 1: The Orchestrator (`master_control.py` & `fsm.json`)

The Orchestrator is the master Finite State Machine (FSM) that guides the agent through its entire lifecycle, from orientation to submission. It is not directly controlled by the agent's plan but rather directs the agent's state based on the successful completion of each phase.

**Key States (defined in `tooling/fsm.json`):**
*   `ORIENTING`: The initial state where the agent gathers context.
*   `PLANNING`: The state where the Orchestrator waits for the agent to produce a `plan.txt`.
*   `EXECUTING`: The state where the Orchestrator oversees the step-by-step execution of the validated plan.
*   `POST_MORTEM`: The state for finalizing the task and recording learnings.
*   `AWAITING_SUBMISSION`: The final state before the code is submitted.

**The Orchestrator's Critical Role in Planning:**
During the `PLANNING` state, the Orchestrator's most important job is to validate the agent-generated `plan.txt`. It does this by calling the FDC Toolchain's `lint` command. **A plan that fails this check will halt the entire process, preventing the agent from entering an invalid state.**
### Layer 2: The FDC Toolchain (`fdc_cli.py` & `fdc_fsm.json`)

The FDC Toolchain is a set of utilities that the agent uses to structure its work and that the Orchestrator uses for validation. The toolchain is governed by its own FSM (`tooling/fdc_fsm.json`), which defines the legal sequence of commands *within a plan*.

#### **FDC Commands for Agent Use:**

**`start` - Task Initiation**
*   **Usage:** The first command the agent MUST issue upon receiving a task.
*   **Command:** `run_in_bash_session python3 tooling/fdc_cli.py start --task-id "your-task-id"`
*   **Function:** Logs the `TASK_START` event, formally beginning the development cycle.

**`lint` - Pre-Flight Plan Validation**
*   **Usage:** A command the agent can use to self-correct its own plan before finalizing it. The Orchestrator will *always* run this command on `plan.txt` as a mandatory check.
*   **Command:** `run_in_bash_session python3 tooling/fdc_cli.py lint <plan_file.txt>`
*   **Function:** Performs a comprehensive check against the low-level FSM:
    1.  **Closure Mandate:** Ensures the plan's final action is a call to the `close` command.
    2.  **FSM Validation:** Validates the sequence of agent tools against `tooling/fdc_fsm.json`.
    3.  **Semantic Validation:** Checks for errors like using a file before creating it.

**`close` - Task Closure**
*   **Usage:** The **last command** in any valid plan.
*   **Command:** `run_in_bash_session python3 tooling/fdc_cli.py close --task-id "your-task-id"`
*   **Function:** Logs `TASK_END`, generates a post-mortem template, and signals to the Orchestrator that plan execution is complete.
---
### STANDING ORDERS

1.  **Orchestrator is Sovereign:** The agent's lifecycle is governed by `master_control.py`. The agent's primary job is to provide a valid `plan.txt` when the Orchestrator enters the `PLANNING` state.
2.  **Toolchain is Law:** All plans must be valid according to the `fdc_cli.py lint` command. A valid plan is one that passes the Closure Mandate and is a valid string in the language defined by `fdc_fsm.json`.
3.  **Hierarchy is Structure:** The Orchestrator (`master_control.py`) validates the agent's plan using the FDC Toolchain (`fdc_cli.py`). This separation ensures a robust, verifiable, and decidable development process, preventing the system from executing paradoxical or non-terminating plans.