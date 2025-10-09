import os
import re
import argparse
import sys
import shutil

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid filename.
    Removes special characters and replaces spaces with underscores.
    """
    name = name.lower()
    name = re.sub(r'^\d+[a-z]?\.\s*', '', name)
    name = re.sub(r'[^a-z0-9\s_-]', '', name)
    name = re.sub(r'[\s-]+', '_', name)
    return name

def decompile_protocol(input_filepath, output_dir):
    """
    Decompiles a monolithic AGENTS.md file into smaller, numbered protocol files.
    The file is split based on H2 (##) and H3 (###) markdown headers.
    """
    if not os.path.exists(input_filepath):
        print(f"Error: Input file not found at '{input_filepath}'", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(output_dir):
        # Be specific to only remove the files this script creates.
        for f in os.listdir(output_dir):
            if f.endswith(".protocol.md"):
                os.remove(os.path.join(output_dir, f))
    else:
        os.makedirs(output_dir, exist_ok=True)

    with open(input_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Corrected Regex: Split on both '## ' and '### ' at the start of a line.
    sections = re.split(r'(?m)^(## |### )', content)

    intro_content = sections.pop(0).strip()
    if intro_content:
        # Corrected Filename: Use the proper extension.
        intro_filename = os.path.join(output_dir, "00_introduction.protocol.md")
        with open(intro_filename, 'w') as f:
            f.write(intro_content)
        print(f"Created {os.path.basename(intro_filename)}")

    file_counter = 1
    for i in range(0, len(sections), 2):
        header_marker = sections[i]
        section_body = sections[i+1]
        header_title = section_body.split('\n', 1)[0].strip()
        full_header = f"{header_marker}{header_title}"
        section_content = ""
        if '\n' in section_body:
            section_content = section_body.split('\n', 1)[1].strip()

        sanitized_title = sanitize_filename(header_title)
        filename = f"{file_counter:02d}_{sanitized_title}.protocol.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w') as f:
            f.write(f"{full_header}\n\n{section_content}".strip())

        print(f"Created {filename}")
        file_counter += 1

    print(f"\nDecompilation complete. {file_counter} file(s) created in '{output_dir}'.")

def main():
    parser = argparse.ArgumentParser(description="Decompile a monolithic AGENTS.md file.")
    parser.add_argument("input_file", default="AGENTS.md", nargs='?', help="Path to the AGENTS.md file.")
    parser.add_argument("-o", "--output-dir", default="protocols", help="Output directory for protocol files.")
    args = parser.parse_args()
    decompile_protocol(args.input_file, args.output_dir)

if __name__ == "__main__":
    main()