"""
A refactored, robust orchestrator for the agent's development lifecycle.

This module replaces the old `master_control.py` and its subprocess-based
logic with a more integrated, library-based approach. It introduces a
clear separation of concerns between validating plans and executing the
agent's lifecycle.

Key Components:
- **PlanValidator:** A class dedicated to parsing and validating plan files
  against the governing FSMs. It provides clear, exception-based error
  handling.
- **Orchestrator:** The main FSM that guides the agent through its
  workflow (Orienting, Planning, Executing, etc.), using a generator-based
  approach to receive inputs from a driving loop.
"""
import json
import os
import sys
import shutil
import datetime
from typing import Set, List, Dict, Optional, Callable

# Ensure tooling is on the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from plan_parser import parse_plan, Command
from state import AgentState, PlanContext
# Directly import logic from other tools instead of using subprocess
from knowledge_compiler import extract_lessons_from_postmortem

# --- Constants ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_ORCHESTRATOR_FSM_PATH = os.path.join(ROOT_DIR, "tooling", "fsm.json")
DEFAULT_FDC_FSM_PATH = os.path.join(ROOT_DIR, "tooling", "fdc_fsm.json")
PLAN_REGISTRY_PATH = os.path.join(ROOT_DIR, "knowledge_core", "plan_registry.json")
POSTMORTEM_TEMPLATE_PATH = os.path.join(ROOT_DIR, "postmortem.md")
MAX_RECURSION_DEPTH = 10

# --- Custom Exceptions for Clear Error Handling ---

class PlanValidationError(Exception):
    """Base exception for all plan validation errors."""
    def __init__(self, message, line_number=None):
        self.line_number = line_number
        full_message = f"L{line_number}: {message}" if line_number else message
        super().__init__(full_message)

class FSMError(PlanValidationError):
    """Errors related to the FSM definition itself."""
    pass

class InvalidTransitionError(PlanValidationError):
    """Raised when a plan attempts an illegal state transition."""
    pass

class UnknownCommandError(PlanValidationError):
    """Raised when a plan uses a command not defined in the action map."""
    pass

class RecursionDepthExceededError(PlanValidationError):
    """Raised when a plan nests 'call_plan' too deeply."""
    pass

class FileSystemValidationError(PlanValidationError):
    """Raised for semantic errors like using a file before it's created."""
    pass

class OrchestratorError(Exception):
    """Base exception for orchestrator-level errors."""
    pass


class PlanValidator:
    """
    Validates an agent's plan against a given Finite State Machine (FSM).
    """
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
        "call_plan": "call_plan_op",
        "fdc_close": "close_op",
    }

    def __init__(self, default_fsm_path: str = DEFAULT_FDC_FSM_PATH):
        self.default_fsm = self._load_fsm(default_fsm_path)
        self.plan_registry = self._load_plan_registry()

    def _load_fsm(self, fsm_path: str) -> Dict:
        try:
            with open(fsm_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FSMError(f"FSM file not found at '{fsm_path}'.")
        except json.JSONDecodeError:
            raise FSMError(f"Invalid JSON in FSM file '{fsm_path}'.")

    def _load_plan_registry(self) -> Dict:
        if not os.path.exists(PLAN_REGISTRY_PATH):
            return {}
        try:
            with open(PLAN_REGISTRY_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def validate(self, plan_content: str):
        commands = parse_plan(plan_content)
        simulated_fs = self._get_initial_filesystem_state()
        self._validate_recursive(commands, self.default_fsm, simulated_fs, 0)

    def _get_initial_filesystem_state(self) -> Set[str]:
        fs = set()
        for root, dirs, files in os.walk(ROOT_DIR):
            if ".git" in dirs:
                dirs.remove(".git")
            for name in files:
                fs.add(os.path.relpath(os.path.join(root, name), ROOT_DIR))
            for name in dirs:
                 fs.add(os.path.relpath(os.path.join(root, name), ROOT_DIR) + "/")
        return fs

    def _validate_recursive(self, commands: List[Command], fsm: Dict, fs: Set[str], depth: int):
        if depth > MAX_RECURSION_DEPTH:
            raise RecursionDepthExceededError(f"Maximum recursion depth ({MAX_RECURSION_DEPTH}) exceeded.")

        state = fsm.get("initial_state") or fsm.get("start_state")
        if not state:
            raise FSMError("FSM definition must have an 'initial_state' or 'start_state' key.")

        for i, command in enumerate(commands):
            line_num = i + 1
            action_type = self.ACTION_TYPE_MAP.get(command.tool_name)
            if not action_type:
                raise UnknownCommandError(f"Unknown command '{command.tool_name}'", line_num)

            next_state = None
            if isinstance(fsm.get("transitions"), list):
                for transition in fsm["transitions"]:
                    if transition.get("source") == state and transition.get("trigger") == action_type:
                        next_state = transition.get("dest")
                        break
            elif isinstance(fsm.get("transitions"), dict):
                transitions = fsm["transitions"].get(state, {})
                next_state = transitions.get(action_type)

            if not next_state:
                raise InvalidTransitionError(f"Action '{command.tool_name}' ({action_type}) is not allowed from state '{state}'.", line_num)

            if command.tool_name == "call_plan":
                self._validate_sub_plan(command, fs, depth)

            state = next_state

        if state not in fsm["accept_states"]:
            raise PlanValidationError(f"Plan ends in a non-terminal state '{state}'.")

    def _validate_sub_plan(self, command: Command, fs: Set[str], depth: int):
        plan_name_or_path = command.args_text.strip()
        sub_plan_path = self.plan_registry.get(plan_name_or_path, plan_name_or_path)

        if not os.path.isabs(sub_plan_path):
            sub_plan_path = os.path.join(ROOT_DIR, sub_plan_path)

        try:
            with open(sub_plan_path, "r") as f:
                sub_plan_content = f.read()
        except FileNotFoundError:
            raise FileSystemValidationError(f"'call_plan' failed: Sub-plan file not found at '{sub_plan_path}'")

        sub_commands = parse_plan(sub_plan_content)
        self._validate_recursive(sub_commands, self.default_fsm, fs.copy(), depth + 1)


class Orchestrator:
    """
    Manages the agent's lifecycle using a generator-based FSM.
    """

    def __init__(self, fsm_path: str = DEFAULT_ORCHESTRATOR_FSM_PATH):
        self.fsm = self._load_fsm(fsm_path)
        self.plan_validator = PlanValidator()
        self.current_state = self.fsm["initial_state"]
        self.state_handlers: Dict[str, Callable] = {
            "ORIENTING": self._do_orienting,
            "PLANNING": self._do_planning,
            "EXECUTING": self._do_executing,
            "AWAITING_ANALYSIS": self._do_awaiting_analysis,
            "SELF_CORRECTING": self._do_self_correcting,
        }

    def _load_fsm(self, fsm_path: str) -> Dict:
        try:
            with open(fsm_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise OrchestratorError(f"Failed to load orchestrator FSM at '{fsm_path}': {e}")

    def run(self, agent_state: AgentState):
        """
        Runs the main lifecycle FSM as a generator that can receive data.
        """
        if self.current_state == "START":
            self.current_state = "ORIENTING"

        while self.current_state not in self.fsm["final_states"]:
            try:
                handler = self.state_handlers.get(self.current_state)
                if not handler:
                    raise OrchestratorError(f"No handler for state: {self.current_state}")

                trigger_or_request = handler(agent_state)

                if trigger_or_request == "NEEDS_PLAN":
                    plan_content = yield "AWAITING_PLAN"
                    trigger = self._handle_planning_input(agent_state, plan_content)
                elif trigger_or_request == "NEEDS_POSTMORTEM":
                    postmortem_content = yield "AWAITING_POSTMORTEM"
                    trigger = self._handle_postmortem_input(agent_state, postmortem_content)
                else:
                    trigger = trigger_or_request
                    yield self.current_state

                self.current_state = self._get_next_state(trigger)

            except Exception as e:
                agent_state.error = str(e)
                self.current_state = "ERROR"
                break

        return self.current_state

    def _get_next_state(self, trigger: str) -> str:
        for transition in self.fsm["transitions"]:
            if transition.get("source") == self.current_state and transition.get("trigger") == trigger:
                return transition["dest"]
        raise OrchestratorError(f"No transition for state {self.current_state} with trigger {trigger}")

    def _do_orienting(self, agent_state: AgentState) -> str:
        agent_state.orientation_complete = True
        return "orientation_succeeded"

    def _do_planning(self, agent_state: AgentState) -> str:
        return "NEEDS_PLAN"

    def _handle_planning_input(self, agent_state: AgentState, plan_content: str) -> str:
        try:
            self.plan_validator.validate(plan_content)
            commands = parse_plan(plan_content)
            agent_state.plan_stack.append(PlanContext(plan_path="plan.txt", commands=commands))
            return "plan_valid"
        except PlanValidationError as e:
            agent_state.error = f"Plan validation failed: {e}"
            return "plan_invalid"

    def _do_executing(self, agent_state: AgentState) -> str:
        if not agent_state.plan_stack:
            return "execution_complete"

        current_context = agent_state.plan_stack[-1]

        # Check if we have finished all steps in the current plan
        if current_context.current_step >= len(current_context.commands):
            agent_state.plan_stack.pop()
            # If the stack is now empty, we are done with all plans
            if not agent_state.plan_stack:
                return "execution_complete"
            else:
                # We finished a sub-plan, continue with the parent
                return "step_executed"

        # In a real run, the agent loop would execute the tool.
        # Here, we just advance the step to simulate completion.
        current_context.current_step += 1

        return "step_executed"

    def _do_awaiting_analysis(self, agent_state: AgentState) -> str:
        safe_task_id = "".join(c for c in agent_state.task if c.isalnum() or c in ("-", "_"))
        draft_path = f"DRAFT-{safe_task_id}.md"
        agent_state.draft_postmortem_path = draft_path
        if not os.path.exists(POSTMORTEM_TEMPLATE_PATH):
             raise OrchestratorError(f"Template not found: {POSTMORTEM_TEMPLATE_PATH}")
        shutil.copyfile(POSTMORTEM_TEMPLATE_PATH, draft_path)
        return "NEEDS_POSTMORTEM"

    def _handle_postmortem_input(self, agent_state: AgentState, postmortem_content: str) -> str:
        draft_path = agent_state.draft_postmortem_path
        if not draft_path or not os.path.exists(draft_path):
            raise OrchestratorError(f"Draft post-mortem file '{draft_path}' not found.")

        with open(draft_path, "w") as f:
            f.write(postmortem_content)

        safe_task_id = "".join(c for c in agent_state.task if c.isalnum() or c in ("-", "_"))
        final_path = f"postmortems/{datetime.date.today()}-{safe_task_id}.md"
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        os.rename(draft_path, final_path)

        lessons = extract_lessons_from_postmortem(postmortem_content)

        agent_state.final_report = f"Post-mortem saved to {final_path}"
        return "post_mortem_complete"

    def _do_self_correcting(self, agent_state: AgentState) -> str:
        return "self_correction_complete"