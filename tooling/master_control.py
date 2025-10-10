"""
A refactored, active master orchestrator for the agent's lifecycle.
This script is the heart of the agent's operational loop, actively executing
the agent's plan and calling the agent's tools directly.
"""
import json
import sys
import os
import subprocess
from typing import Any

# Add tooling directory to path to import other tools
sys.path.insert(0, "./tooling")
from state import AgentState, PlanContext
from research import ResearchProtocol
from fdc_cli import FDC_CLI
from plan_parser import parse_plan, Command

class MasterControlGraph:
    """
    An active FSM that enforces the agent's protocol and executes the plan.
    """

    def __init__(self, tool_executor: Any, fsm_path: str = "tooling/fsm.json"):
        self.tool_executor = tool_executor
        with open(fsm_path, "r") as f:
            self.fsm = json.load(f)
        self.current_state = self.fsm["initial_state"]
        self.research_protocol = ResearchProtocol(tool_executor)
        self.fdc_cli = FDC_CLI(tool_executor)

    def get_trigger(self, source_state: str, dest_state: str) -> str:
        transitions = self.fsm["transitions"].get(source_state, {})
        for trigger, destination in transitions.items():
            if destination == dest_state:
                return trigger
        raise ValueError(f"No trigger found for transition from {source_state} to {dest_state}")

    def do_orientation(self, agent_state: AgentState) -> str:
        print("[MasterControl] State: ORIENTING")
        # L1: Self-Awareness
        l1_constraints = {"target": "local_filesystem", "scope": "file", "path": "knowledge_core/agent_meta.json"}
        self.research_protocol.execute(l1_constraints)
        # L2: Repo Sync
        l2_constraints = {"target": "local_filesystem", "scope": "directory", "path": "knowledge_core/"}
        self.research_protocol.execute(l2_constraints)
        # L3: Environmental Probe
        self.tool_executor.run_in_bash_session("python3 tooling/environmental_probe.py")
        agent_state.orientation_complete = True
        return self.get_trigger("ORIENTING", "PLANNING")

    def do_planning(self, agent_state: AgentState) -> str:
        print("[MasterControl] State: PLANNING")
        plan_path = self.tool_executor.get_plan_path()
        self.fdc_cli.validate_plan(plan_path)
        plan_content = self.tool_executor.read_file(plan_path)
        commands = parse_plan(plan_content)
        agent_state.plan_stack.append(PlanContext(plan_path=plan_path, commands=commands))
        return "plan_is_set"

    def do_execution(self, agent_state: AgentState) -> str:
        print("[MasterControl] State: EXECUTING")
        if not agent_state.plan_stack:
            return self.get_trigger("EXECUTING", "FINALIZING")

        current_context = agent_state.plan_stack[-1]
        commands = current_context.commands

        if current_context.current_step >= len(commands):
            agent_state.plan_stack.pop()
            return self.do_execution(agent_state)

        command = commands[current_context.current_step]

        # Directly execute the command using the tool executor
        tool_name = command.tool_name
        args_text = command.args_text

        if hasattr(self.tool_executor, tool_name):
            getattr(self.tool_executor, tool_name)(args_text)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

        current_context.current_step += 1
        if current_context.current_step >= len(commands):
            return self.get_trigger("EXECUTING", "FINALIZING")
        else:
            return self.get_trigger("EXECUTING", "EXECUTING")

    def do_finalizing(self, agent_state: AgentState) -> str:
        print("[MasterControl] State: FINALIZING")
        # For simplicity in this refactoring, we'll just signal completion.
        # A more robust implementation would handle post-mortem analysis here.
        return self.get_trigger("FINALIZING", "AWAITING_SUBMISSION")

    def run(self, initial_agent_state: AgentState):
        agent_state = initial_agent_state
        while self.current_state not in self.fsm["final_states"]:
            if self.current_state == "START":
                self.current_state = "ORIENTING"
                continue

            if self.current_state == "ORIENTING":
                trigger = self.do_orientation(agent_state)
            elif self.current_state == "PLANNING":
                trigger = self.do_planning(agent_state)
            elif self.current_state == "EXECUTING":
                trigger = self.do_execution(agent_state)
            elif self.current_state == "FINALIZING":
                trigger = self.do_finalizing(agent_state)
            else:
                agent_state.error = f"Unknown state: {self.current_state}"
                self.current_state = "ERROR"
                break

            transitions = self.fsm["transitions"].get(self.current_state, {})
            if trigger in transitions:
                self.current_state = transitions[trigger]
            else:
                agent_state.error = f"No transition found for state {self.current_state} with trigger {trigger}"
                self.current_state = "ERROR"

        return agent_state