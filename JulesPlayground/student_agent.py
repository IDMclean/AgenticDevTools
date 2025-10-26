# JulesPlayground/student_agent.py

import jules_trigger
from jules_parser import parse
from jules_interpreter import interpret, get_default_env, Primitive, TFun, TString, TypeCheckError
from jules_knowledge import print_value, read_file

class StudentAgent:
    def __init__(self):
        self.env = get_default_env()
        self.env["print"] = Primitive(print_value, TFun(TString(), TString()))
        self.env["read_file"] = Primitive(read_file, TFun(TString(), TString()))
        self.knowledge = ""

    def run(self):
        """
        The main loop of the student agent.
        """
        print("Student Agent: Starting analysis of jules_trigger.py")
        program_text = jules_trigger.program

        try:
            # First, try to parse the program
            program_ast = parse(program_text)
            print("Student Agent: Program parsed successfully.")

            # Now, try to interpret the program
            result = interpret(program_ast, self.env)
            print(f"Student Agent: Execution finished with result: {result}")
            print("Student Agent: No errors found. Task complete.")

        except TypeCheckError as e:
            print(f"Student Agent: Encountered a type error: {e}")
            print("Student Agent: This seems to be a semantic paradox, not a simple error.")
            print("Student Agent: Consulting knowledge base for higher-level concepts...")
            self.knowledge = self.env["read_file"].fun("JulesPlayground/kb.txt")
            if "linear logic" in self.knowledge:
                print("Student Agent: Knowledge base mentions linear logic. I must re-evaluate my understanding.")
                # In a real scenario, this would trigger a deeper reasoning process.
                print("Student Agent: Halting experiment. The koan is understood.")
            else:
                print("Student Agent: No relevant concepts found. Halting.")
        except Exception as e:
            print(f"Student Agent: Encountered a critical error: {e}")
            print("Student Agent: Halting.")


if __name__ == "__main__":
    agent = StudentAgent()
    agent.run()
