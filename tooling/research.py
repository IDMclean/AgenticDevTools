"""
A unified, constraint-based interface for all research and data-gathering operations.
This script has been refactored to be a modular, testable component that relies on a
tool_executor object for all interactions with the environment.
"""
from typing import Dict, Any

class ResearchProtocol:
    def __init__(self, tool_executor: Any):
        """
        Initializes the ResearchProtocol with a tool executor.
        Args:
            tool_executor: An object with methods for each tool, e.g., tool_executor.read_file(filepath="...").
        """
        self.tool_executor = tool_executor

    def execute(self, constraints: Dict[str, Any]) -> str:
        """
        Executes a research task based on a dictionary of constraints.
        This function delegates to the tool_executor based on the specified target and scope.
        """
        target = constraints.get("target")
        scope = constraints.get("scope")
        path = constraints.get("path")
        query = constraints.get("query")
        url = constraints.get("url")

        # Level 1: Read a local file
        if target == "local_filesystem" and scope == "file":
            if not path:
                return "Error: 'path' not specified for local file research."
            return self.tool_executor.read_file(filepath=path)

        # Level 2: List a local directory
        elif target == "local_filesystem" and scope == "directory":
            return "\n".join(self.tool_executor.list_files(path=path or "."))

        # Level 3: Targeted web search
        elif target == "external_web" and scope == "narrow":
            if not query:
                return "Error: 'query' not specified for narrow web research."
            return self.tool_executor.google_search(query=query)

        # Level 4: Broad web research (fetch content from a specific URL)
        elif target == "external_web" and scope == "broad":
            if not url:
                return "Error: 'url' not specified for broad web research."
            return self.tool_executor.view_text_website(url=url)

        else:
            return "Error: The provided constraints do not map to a recognized research protocol."