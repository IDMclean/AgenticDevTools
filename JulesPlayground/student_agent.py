# JulesPlayground/student_agent.py

from jules_parser import parse
from jules_interpreter import interpret, get_default_env, Primitive, TFun, TString, TypeCheckError
from jules_knowledge import print_value, read_file
import importlib

class StudentAgent:
    def __init__(self):
        self.env = get_default_env()
        self.env["print"] = Primitive(print_value, TFun(TString(), TString()))
        self.env["read_file"] = Primitive(read_file, TFun(TString(), TString()))
        self.knowledge = ""
        self.state = "Execution"  # Initial state
        self.current_error = None
        self.hypothesis = None

    def run(self, trigger_file):
        """
        The main meta-cognitive loop of the student agent.
        """
        print("Student Agent: Starting main loop.")

        while True:
            if self.state == "Execution":
                print("Student Agent: Entering Execution state.")
                try:
                    trigger_module = importlib.import_module(trigger_file.replace("/", ".").replace(".py", ""))
                    program_text = trigger_module.program
                    program_ast = parse(program_text)
                    print("Student Agent: Program parsed successfully.")

                    result = interpret(program_ast, self.env)
                    print(f"Student Agent: Execution finished with result: {result}")
                    print("Student Agent: No errors found. Task complete.")
                    break  # Success, exit the loop
                except TypeCheckError as e:
                    print(f"Student Agent: Encountered a TypeCheckError: {e}")
                    print("Student Agent: Transitioning to ProblemSolving state.")
                    self.state = "ProblemSolving"
                    self.current_error = str(e)
                except Exception as e:
                    print(f"Student Agent: Encountered a critical, unrecoverable error: {e}")
                    break # Halt on other errors

            elif self.state == "ProblemSolving":
                print("Student Agent: Entering ProblemSolving state.")
                self.generate_hypothesis()

                if self.hypothesis:
                    print(f"Student Agent: Formed hypothesis: {self.hypothesis}")
                    print("Student Agent: Now, I will attempt to solve the paradox by rewriting myself.")

                    # Read and execute the enlightenment koan
                    koan_text = self.env["read_file"].fun("JulesPlayground/koan_v2.appl")
                    koan_ast = parse(koan_text)
                    interpret(koan_ast, self.env)

                    print("Student Agent: Self-modification complete. Re-entering Execution state.")
                    self.state = "Execution"
                else:
                    print("Student Agent: Failed to form a hypothesis. Halting.")
                    break

    def generate_hypothesis(self):
        """
        Forms a hypothesis about the error by consulting the knowledge base.
        """
        print("Student Agent: Consulting knowledge base to form hypothesis.")
        kb_content = self.env["read_file"].fun("JulesPlayground/kb.txt")
        spec_content = self.env["read_file"].fun("JulesPlayground/language_spec.md")

        # Simple keyword-based reasoning
        if "linear logic" in spec_content and "Expected exponential type" in self.current_error:
            self.hypothesis = "The error is related to a misunderstanding of linear logic. The program may be trying to use a linear resource in an unrestricted way."
        elif "undefined variable" in kb_content:
             self.hypothesis = "The error is a simple undefined variable. I should define it."
        else:
            self.hypothesis = None


if __name__ == "__main__":
    agent = StudentAgent()
    agent.run("JulesPlayground.jules_trigger")
