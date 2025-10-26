# JulesPlayground/jules_knowledge.py

def print_value(value):
    """Prints a value to the console."""
    print(value)

def read_file(filepath):
    """Reads a file and returns its contents."""
    with open(filepath, "r") as f:
        return f.read()

def write_file(filepath, content):
    """Writes content to a file."""
    with open(filepath, "w") as f:
        f.write(content)
