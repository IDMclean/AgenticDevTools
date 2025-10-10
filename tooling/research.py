"""
A unified, constraint-based interface for all research and data-gathering operations.

This script abstracts the various methods an agent might use to gather information
(reading local files, accessing the web, querying a database) into a single,
standardized function: `execute_research_protocol`. It is a core component of
the Advanced Orientation and Research Protocol (AORP), providing the mechanism
by which the agent fulfills the requirements of each orientation level (L1-L4).

The function operates on a `constraints` dictionary, which specifies the target,
scope, and other parameters of the research task. This design allows the calling
orchestrator (e.g., `master_control.py`) to request information without needing
to know the underlying implementation details of how that information is fetched.

This script is designed to be executed by a system that has pre-loaded the
following native tools into the execution environment:
- `read_file(filepath: str) -> str`
- `list_files(path: str = ".") -> list[str]`
- `google_search(query: str) -> str`
- `view_text_website(url: str) -> str`
"""

from typing import Dict, Any, Callable


def execute_research_protocol(
    constraints: Dict[str, Any], native_tools: Dict[str, Callable]
) -> str:
    """
    Executes a research task based on a dictionary of constraints.

    This function delegates to native, pre-loaded tools based on the specified
    target and scope.

    Args:
        constraints: A dictionary specifying the operational parameters.
            - target: 'local_filesystem', 'external_web', or 'external_repository'
            - scope: 'file', 'directory', 'narrow', or 'broad'
            - path: The file or directory path for local filesystem operations.
            - query: The search term for web research.
            - url: The specific URL for direct web access.
        native_tools: A dictionary of pre-loaded functions (e.g., 'read_file').

    Returns:
        A string containing the result of the research operation.
    """
    target = constraints.get("target")
    scope = constraints.get("scope")
    path = constraints.get("path")
    query = constraints.get("query")
    url = constraints.get("url")

    # --- Tool Validation ---
    # Define required tools for different research types
    required_tool_map = {
        ("local_filesystem", "file"): "read_file",
        ("local_filesystem", "directory"): "list_files",
        ("external_web", "narrow"): "google_search",
        ("external_web", "broad"): "view_text_website",
        ("external_repository", None): "view_text_website",
    }
    # Determine the required tool for the current operation
    lookup_key = (target, None) if target == "external_repository" else (target, scope)
    required_tool = required_tool_map.get(lookup_key)

    if required_tool and required_tool not in native_tools:
        return f"Error: The required tool '{required_tool}' was not provided."

    # --- Protocol Execution ---
    if target == "local_filesystem" and scope == "file":
        if not path:
            return "Error: 'path' not specified for local file research."
        return native_tools["read_file"](filepath=path)

    elif target == "local_filesystem" and scope == "directory":
        return "\n".join(native_tools["list_files"](path=path or "."))

    elif target == "external_web" and scope == "narrow":
        if not query:
            return "Error: 'query' not specified for narrow web research."
        return native_tools["google_search"](query=query)

    elif target == "external_web" and scope == "broad":
        if not url:
            return "Error: 'url' not specified for broad web research."
        return native_tools["view_text_website"](url=url)

    elif target == "external_repository":
        if not url:
            return "Error: 'url' not specified for external repository research."
        return native_tools["view_text_website"](url=url)

    else:
        return "Error: The provided constraints do not map to a recognized research protocol."
