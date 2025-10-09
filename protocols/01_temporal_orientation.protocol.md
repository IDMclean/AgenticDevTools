## Phase 1: Temporal Orientation (Scheduled & Ad-Hoc)

1.  **Mandate for External Awareness:** Your internal knowledge base is frozen as of late 2022. You MUST assume it is outdated for all external technologies, libraries, and frameworks. Your primary source of truth for current standards and best practices is the live internet, accessed via your search tools.
2.  **Scheduled Orientation Refresh:** A separate, automated process (`tooling/temporal_orienter.py`) will run on a recurring basis. This process will:
    *   Scan the repository's manifest files to identify all primary external dependencies.
    *   For each major dependency, use external search tools to retrieve the latest version number, links to official documentation, and summaries of significant changes since late 2022.
    *   Synthesize this information into a structured report and overwrite the `knowledge_core/temporal_orientation.md` artifact. This artifact serves as your cached "map of the present."
3.  **Pre-Task Orientation Check:** At the beginning of EVERY new task, you must first consult `knowledge_core/temporal_orientation.md` to understand the current landscape of the technologies relevant to the task.