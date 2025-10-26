# JulesPlayground/lab.py

import logging
import sys
sys.path.append("JulesPlayground")
from student_agent import StudentAgent

def main():
    """
    This script is the lab orchestrator.
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("lab_results.log"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger("Lab")

    logger.info("--- Starting Experiment ---")

    # Create and run the student agent
    agent = StudentAgent()
    agent.run("jules_trigger")

    logger.info("--- Experiment Finished ---")

if __name__ == "__main__":
    main()
