#!/usr/bin/env python
import sys
import os
import warnings
import contextlib
from pathlib import Path
from datetime import datetime

os.environ["PYTHONWARNINGS"] = "ignore"  # Suppress all warnings

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

# Suppress all warnings before any imports
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore")

# Import with stderr suppression for the persistent Pydantic warning
with suppress_stderr():
    from phoenix.crew import Phoenix

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince.*")
warnings.filterwarnings("ignore", message=".*No path_separator found.*")
warnings.filterwarnings("ignore", message=".*model_fields.*")
warnings.filterwarnings("ignore", message=".*Using extra keyword arguments.*")
warnings.filterwarnings("ignore", message=".*Extra keys.*")
warnings.filterwarnings("ignore")  # Suppress all remaining warnings

def run():
    """
    Run the crew.
    """
    query = input("Enter your query: ")
    inputs = {
        "query": query,
    }
    
    try:
        result = Phoenix().crew().kickoff(inputs=inputs)
        print(f"Result: {result}")
    except Exception as e:
        print(f"An error occurred while running the crew: {e}")
        return None

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "query": "How to center a div in CSS?",
    }
    try:
        Phoenix().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        print(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Phoenix().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        print(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Phoenix().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)
    except Exception as e:
        print(f"An error occurred while testing the crew: {e}")

# Add main execution logic
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "train" and len(sys.argv) >= 4:
            train()
        elif command == "replay" and len(sys.argv) >= 3:
            replay()
        elif command == "test" and len(sys.argv) >= 4:
            test()
        else:
            print("Usage:")
            print("  python main.py train <n_iterations> <filename>")
            print("  python main.py replay <task_id>")
            print("  python main.py test <n_iterations> <eval_llm>")
            print("  python main.py (for interactive run)")
    else:
        run()
