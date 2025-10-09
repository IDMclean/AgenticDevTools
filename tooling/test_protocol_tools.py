import unittest
import os
import shutil
import sys
from io import StringIO

# This is a bit of a hack to make the test run from the root directory
# without having to install the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tooling.protocol_decompiler import decompile_protocol
from tooling.protocol_analyzer import analyze_protocol

class TestProtocolTools(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for test files."""
        self.test_dir = "temp_protocol_test_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        self.output_dir = os.path.join(self.test_dir, "decomposed")

    def tearDown(self):
        """Clean up the temporary directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_decompiler_splits_protocol_correctly(self):
        """
        Ensures the decompiler correctly splits an AGENTS.md file
        based on H2 and H3 headers.
        """
        sample_agents_md = """
# Protocol Title

This is the introduction.

---
## 1. First H2 Section

Content for the first section.

### 1a. First H3 Section

Content for the subsection.

## 2. Second H2 Section

Content for the second section.
"""
        input_filepath = os.path.join(self.test_dir, "AGENTS.md")
        with open(input_filepath, "w") as f:
            f.write(sample_agents_md)

        decompile_protocol(input_filepath, self.output_dir)

        # Check that the correct number of files were created
        decomposed_files = sorted(os.listdir(self.output_dir))
        self.assertEqual(len(decomposed_files), 4)

        # Check the filenames
        self.assertEqual(decomposed_files[0], "00_introduction.md")
        self.assertEqual(decomposed_files[1], "01_1_first_h2_section.md")
        self.assertEqual(decomposed_files[2], "02_1a_first_h3_section.md")
        self.assertEqual(decomposed_files[3], "03_2_second_h2_section.md")

        # Check the content of a generated file
        with open(os.path.join(self.output_dir, "01_1_first_h2_section.md"), "r") as f:
            content = f.read()
            self.assertIn("## 1. First H2 Section", content)
            self.assertIn("Content for the first section.", content)

    def test_analyzer_on_valid_protocol(self):
        """
        Ensures the analyzer correctly validates a well-formed AGENTS.md file.
        """
        # Create a dummy referenced file so the check passes
        dummy_tool_path = os.path.join(self.test_dir, "dummy_tool.py")
        os.makedirs(os.path.dirname(dummy_tool_path), exist_ok=True)
        with open(dummy_tool_path, "w") as f:
            f.write("# dummy tool")

        valid_protocol = f"""
## 1. The Core Problem
Some text.

## 2. The Solution
References `tooling/dummy_tool.py` which exists.

### STANDING ORDERS
Some orders.
"""
        input_filepath = os.path.join(self.test_dir, "VALID_AGENTS.md")
        with open(input_filepath, "w") as f:
            f.write(valid_protocol.replace("tooling/dummy_tool.py", dummy_tool_path))

        # Capture stdout to check the report
        captured_output = StringIO()
        sys.stdout = captured_output

        analyze_protocol(input_filepath)

        sys.stdout = sys.__stdout__  # Restore stdout
        output = captured_output.getvalue()

        self.assertIn("Structural Validation:\n  - Status: PASSED", output)
        self.assertIn("Valid references (file exists): 1", output)
        self.assertNotIn("Invalid references", output)

    def test_analyzer_on_invalid_protocol(self):
        """
        Ensures the analyzer correctly identifies flaws in a malformed AGENTS.md.
        """
        invalid_protocol = """
## 1. The Core Problem
This protocol is missing the solution section.

It also references a file that does not exist: `tooling/non_existent_tool.py`.

### STANDING ORDERS
These orders are here.
"""
        input_filepath = os.path.join(self.test_dir, "INVALID_AGENTS.md")
        with open(input_filepath, "w") as f:
            f.write(invalid_protocol)

        captured_output = StringIO()
        sys.stdout = captured_output

        analyze_protocol(input_filepath)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("Structural Validation:\n  - Status: FAILED", output)
        self.assertIn("Missing required header: ## 2. The Solution", output)
        self.assertIn("Invalid references (file NOT found):", output)
        self.assertIn("- tooling/non_existent_tool.py", output)

if __name__ == '__main__':
    unittest.main()