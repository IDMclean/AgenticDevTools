import unittest
from unittest.mock import MagicMock
from tooling.research import ResearchProtocol

class TestResearchProtocol(unittest.TestCase):
    def setUp(self):
        self.mock_tool_executor = MagicMock()
        self.research_protocol = ResearchProtocol(self.mock_tool_executor)

    def test_local_filesystem_file_scope(self):
        self.mock_tool_executor.read_file.return_value = "file content"
        constraints = {"target": "local_filesystem", "scope": "file", "path": "test.txt"}
        result = self.research_protocol.execute(constraints)
        self.mock_tool_executor.read_file.assert_called_once_with(filepath="test.txt")
        self.assertEqual(result, "file content")

    def test_local_filesystem_directory_scope(self):
        self.mock_tool_executor.list_files.return_value = ["file1.txt", "file2.txt"]
        constraints = {"target": "local_filesystem", "scope": "directory", "path": "test_dir/"}
        result = self.research_protocol.execute(constraints)
        self.mock_tool_executor.list_files.assert_called_once_with(path="test_dir/")
        self.assertEqual(result, "file1.txt\nfile2.txt")

    def test_external_web_narrow_scope(self):
        self.mock_tool_executor.google_search.return_value = "search results"
        constraints = {"target": "external_web", "scope": "narrow", "query": "test query"}
        result = self.research_protocol.execute(constraints)
        self.mock_tool_executor.google_search.assert_called_once_with(query="test query")
        self.assertEqual(result, "search results")

    def test_external_web_broad_scope(self):
        self.mock_tool_executor.view_text_website.return_value = "website content"
        constraints = {"target": "external_web", "scope": "broad", "url": "http://example.com"}
        result = self.research_protocol.execute(constraints)
        self.mock_tool_executor.view_text_website.assert_called_once_with(url="http://example.com")
        self.assertEqual(result, "website content")

if __name__ == '__main__':
    unittest.main()