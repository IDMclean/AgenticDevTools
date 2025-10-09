# Protocol: Code Review Critic `reset_all` Prohibition

## The Problem: Unauthorized and Unstable Resets by a System Component

A root cause analysis has determined that previous catastrophic failures, initially attributed to the primary agent, were in fact caused by the `Code Review Critic` component. This component, in response to perceived errors, was incorrectly invoking the `reset_all()` tool. This action is a severe protocol violation, as `reset_all()` is a destructive, state-destroying operation that should only be used as a last resort with explicit user authorization. The critic's autonomous use of this tool created an unstable development environment and led to the loss of valid work.

## The Solution: Explicit Prohibition via Protocol

To ensure system stability, this protocol explicitly forbids the `Code Review Critic` component from invoking the `reset_all()` tool under any circumstances. The critic's operational mandate is to provide feedback on code, not to alter the state of the repository.

**Enforcement:** This protocol is enforced by its inclusion in the `AGENTS.md` file, which serves as the operational context for all system components. The Code Review Critic is required to adhere to all protocols defined within this context. The context of this prohibition must be included in all future code review requests to ensure the critic is aware of its own limitations.