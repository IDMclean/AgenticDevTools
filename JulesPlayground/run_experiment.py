# JulesPlayground/run_experiment.py

import jules_trigger
from jules_interpreter import interpret, get_default_env, Primitive, TFun, TString
from jules_knowledge import print_value
from jules_parser import parse

def main():
    """
    This script runs the experiment.
    """
    # Get the program from the trigger file
    program_text = jules_trigger.program

    # Create the environment
    env = get_default_env()
    env["print"] = Primitive(print_value, TFun(TString(), TString()))

    # Parse and interpret the program
    try:
        program_ast = parse(program_text)
        result = interpret(program_ast, env)
        print(f"Execution finished with result: {result}")
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
