import unittest
from unittest.mock import MagicMock
from tooling.research import execute_research_protocol


class TestResearchExecutor(unittest.TestCase):
    """
    Tests for the research executor tool, providing a mock dictionary of
    native tools to test the dependency injection pattern.
    """

    def setUp(self):
        """Set up a dictionary of mock native tools for each test."""
        self.mock_read_file = MagicMock(return_value="file content")
        self.mock_list_files = MagicMock(return_value=["file1.txt", "file2.txt"])
        self.mock_google_search = MagicMock(return_value="search results")
        self.mock_view_text_website = MagicMock(return_value="website content")

        self.native_tools = {
            "read_file": self.mock_read_file,
            "list_files": self.mock_list_files,
            "google_search": self.mock_google_search,
            "view_text_website": self.mock_view_text_website,
        }

    def test_local_filesystem_file_scope(self):
        """Verify it calls read_file for local file scope."""
        constraints = {
            "target": "local_filesystem",
            "scope": "file",
            "path": "test.txt",
        }
        result = execute_research_protocol(constraints, self.native_tools)

        self.mock_read_file.assert_called_once_with(filepath="test.txt")
        self.assertEqual(result, "file content")
        # Ensure other mocks were not called
        self.mock_list_files.assert_not_called()
        self.mock_google_search.assert_not_called()
        self.mock_view_text_website.assert_not_called()

    def test_local_filesystem_directory_scope(self):
        """Verify it calls list_files for local directory scope."""
        constraints = {
            "target": "local_filesystem",
            "scope": "directory",
            "path": "test_dir/",
        }
        result = execute_research_protocol(constraints, self.native_tools)

        self.mock_list_files.assert_called_once_with(path="test_dir/")
        self.assertEqual(result, "file1.txt\nfile2.txt")

    def test_external_web_narrow_scope(self):
        """Verify it calls google_search for external narrow scope."""
        constraints = {
            "target": "external_web",
            "scope": "narrow",
            "query": "test query",
        }
        result = execute_research_protocol(constraints, self.native_tools)

        self.mock_google_search.assert_called_once_with(query="test query")
        self.assertEqual(result, "search results")

    def test_external_web_broad_scope(self):
        """Verify it calls view_text_website for external broad scope."""
        self.mock_view_text_website.return_value = "website content"
        constraints = {
            "target": "external_web",
            "scope": "broad",
            "url": "http://example.com",
        }
        result = execute_research_protocol(constraints, self.native_tools)

        self.mock_view_text_website.assert_called_once_with(url="http://example.com")
        self.assertEqual(result, "website content")

    def test_external_repository_scope(self):
        """Verify it calls view_text_website for external repository scope."""
        self.mock_view_text_website.return_value = "repo file content"
        constraints = {
            "target": "external_repository",
            "url": "http://example.com/file.py",
        }
        result = execute_research_protocol(constraints, self.native_tools)

        self.mock_view_text_website.assert_called_once_with(
            url="http://example.com/file.py"
        )
        self.assertEqual(result, "repo file content")

    def test_invalid_target(self):
        """Verify it returns an error for an invalid target."""
        constraints = {"target": "invalid_target"}
        result = execute_research_protocol(constraints, self.native_tools)
        self.assertEqual(
            result,
            "Error: The provided constraints do not map to a recognized research protocol.",
        )

    def test_missing_parameters(self):
        """Verify it returns an error if required parameters are missing."""
        constraints = {"target": "local_filesystem", "scope": "file"}  # Missing 'path'
        result = execute_research_protocol(constraints, self.native_tools)
        self.assertEqual(result, "Error: 'path' not specified for local file research.")

    def test_missing_tool_in_registry(self):
        """Verify it returns an error if a required tool is not in the native_tools dict."""
        constraints = {
            "target": "local_filesystem",
            "scope": "file",
            "path": "test.txt",
        }
        # Execute with an incomplete tool registry
        result = execute_research_protocol(
            constraints, {"list_files": self.mock_list_files}
        )
        self.assertEqual(
            result, "Error: The required tool 'read_file' was not provided."
        )


if __name__ == "__main__":
    unittest.main()
