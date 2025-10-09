# Structured Activity Log Schema v2.0

This document defines the JSON schema for entries in `logs/activity.log.jsonl`. Each line in the log file is a complete JSON object that must conform to this schema. The goal of this schema is to provide a rich, structured dataset for post-mortem analysis, automated learning, and agent introspection.

## Core Principles

-   **Machine-Readable:** The log is designed primarily for automated analysis.
-   **Introspective:** The schema captures not just the *action* taken, but the agent's *reasoning* behind it.
-   **Traceable:** Every action is linked to a specific task and a step in the agent's plan.

## Schema Definition

```json
{
  "type": "object",
  "properties": {
    "timestamp_iso8601": {
      "type": "string",
      "format": "date-time",
      "description": "An unambiguous ISO 8601 timestamp for when the event occurred."
    },
    "agent_id": {
      "type": "string",
      "description": "A unique identifier for the specific Jules instance or session performing the task."
    },
    "task_id": {
      "type": "string",
      "description": "A unique identifier for the overall task assigned by the user."
    },
    "plan_step_id": {
      "type": "integer",
      "description": "The specific step number from the agent's generated plan that this action corresponds to."
    },
    "action_type": {
      "type": "string",
      "enum": [
        "FILE_READ",
        "FILE_WRITE",
        "TOOL_EXEC",
        "INTERNAL_RAG_QUERY",
        "EXTERNAL_RAG_QUERY",
        "PLAN_GENERATION",
        "CRITICAL_REVIEW",
        "POST_MORTEM_ANALYSIS"
      ],
      "description": "A standardized enum representing the type of action taken."
    },
    "action_params": {
      "type": "object",
      "description": "A JSON object containing the parameters for the action (e.g., file path, search query)."
    },
    "llm_reasoning": {
      "type": "string",
      "description": "The LLM's brief, self-generated rationale for taking this specific action at this point in the plan."
    },
    "critic_feedback": {
      "type": "string",
      "description": "If the action was preceded by a critical review, this field contains the output from the critic model."
    },
    "status": {
      "type": "string",
      "enum": ["SUCCESS", "FAILURE", "RETRY"],
      "description": "The outcome of the action."
    },
    "output_summary": {
        "type": "string",
        "description": "A brief, machine-generated summary of the action's result (e.g., hash of file contents, exit code of a tool, summary of search results)."
    }
  },
  "required": [
    "timestamp_iso8601",
    "agent_id",
    "task_id",
    "plan_step_id",
    "action_type",
    "action_params",
    "status"
    ]
}
```

## Action Parameter Examples (`action_params`)

-   **FILE_READ**: `{"file_path": "/path/to/file.js"}`
-   **FILE_WRITE**: `{"file_path": "/path/to/file.md", "content_hash": "sha256_hash_of_content"}`
-   **TOOL_EXEC**: `{"command": "ctags -R .", "working_directory": "/app"}`
-   **INTERNAL_RAG_QUERY**: `{"artifact": "symbols.json", "query": "find_function: 'getUser'"}`
-   **EXTERNAL_RAG_QUERY**: `{"query": "React 'use' hook documentation"}`
-   **PLAN_GENERATION**: `{"plan": "1. Step one...\n2. Step two..."}`
-   **CRITICAL_REVIEW**: `{"plan_step_id": 3, "critique": "The justification for this step is weak. It relies on an outdated blog post."}`

## Example Entry

```json
{
  "timestamp_iso8601": "2025-10-09T10:00:00Z",
  "agent_id": "jules-session-b7cde",
  "task_id": "update-auth-flow-01",
  "plan_step_id": 4,
  "action_type": "EXTERNAL_RAG_QUERY",
  "action_params": {
    "query": "react router v6 protected routes best practices"
  },
  "llm_reasoning": "The current implementation seems to be using an older pattern. I need to verify the current best practice for protected routes in React Router v6 before attempting a refactor.",
  "critic_feedback": null,
  "status": "SUCCESS",
  "output_summary": "Retrieved 3 links from official documentation and 2 high-ranking blog posts detailing the use of <Outlet> and a wrapper component."
}
```