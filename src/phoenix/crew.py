import os
import warnings
from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import CodeInterpreterTool
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="alembic")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="chromadb")
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince20.*")
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince211.*")
warnings.filterwarnings("ignore", message=".*Using extra keyword arguments.*")
warnings.filterwarnings("ignore", message=".*Extra keys.*")
warnings.filterwarnings("ignore")  # Catch all remaining warnings

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
    raise ValueError("Please set a valid GOOGLE_API_KEY environment variable in your .env file.")

try:
    # Use CrewAI's LLM with Google API
    llm = LLM(
        model="gemini/gemini-1.5-flash",
        api_key=GOOGLE_API_KEY
    )
except Exception as e:
    raise ValueError(f"Failed to initialize LLM: {e}")

class Phoenix():
    """Phoenix crew for code fixing and verification"""

    def __init__(self):
        print("Initializing Phoenix crew...")
        self._fixer_agent = None
        self._verifier_agent = None
        self._fix_task = None
        self._verify_task = None

    def fixer_agent(self) -> Agent:
        if self._fixer_agent is None:
            self._fixer_agent = Agent(
                role="Code Fixer",
                goal="Analyze the provided code, identify errors, and propose corrected versions iteratively until it runs without errors.",
                backstory="You are an expert debugger specializing in Python code. You use logical reasoning to fix syntax, logic, and runtime errors. You always test your fixes. You provide responses in plain text format without markdown or special formatting.",
                llm=llm,
                tools=[CodeInterpreterTool()],
                verbose=True,
                allow_delegation=False
            )
        return self._fixer_agent

    def verifier_agent(self) -> Agent:
        if self._verifier_agent is None:
            self._verifier_agent = Agent(
                role="Code Verifier",
                goal="Review the fixed code for best practices, efficiency, and confirm it meets the user's intent.",
                backstory="You are a senior code reviewer ensuring the code is clean, efficient, and functional. You provide responses in plain text format without markdown or special formatting.",
                llm=llm,
                verbose=True,
                allow_delegation=False
            )
        return self._verifier_agent

    def fix_task(self) -> Task:
        if self._fix_task is None:
            self._fix_task = Task(
                description="""You are a Python code fixing expert. 

                {context}
                
                Your approach:
                1. First, run the provided code using the code interpreter tool to identify any errors
                2. If errors are found, analyze them carefully and create a fixed version
                3. Test the fixed code to ensure it runs without errors
                4. If needed, iterate until the code works properly
                5. Provide the final working code with explanations of what was fixed
                
                Always use the code interpreter tool to test your solutions.
                
                IMPORTANT: Provide your response in PLAIN TEXT format only. Do NOT use markdown formatting, code blocks with backticks, or any special formatting. Just provide the clean Python code and explanations in simple text.""",
                expected_output="Working Python code in plain text format without markdown, along with explanations of any fixes made.",
                agent=self.fixer_agent()
            )
        return self._fix_task

    def verify_task(self) -> Task:
        if self._verify_task is None:
            self._verify_task = Task(
                description="""Review and improve the fixed code from the previous task. Ensure it meets high quality standards.
                
                Your tasks:
                1. Review the fixed code from the previous agent
                2. Check if the code follows Python best practices
                3. Verify the code is readable and well-structured
                4. Suggest any optimizations for performance or clarity
                5. Provide a final, polished version of the code with explanations
                
                Only make necessary improvements - don't over-engineer simple solutions.
                Always provide the final working Python code.
                
                IMPORTANT: Provide your response in PLAIN TEXT format only. Do NOT use markdown formatting, code blocks with backticks, or any special formatting. Just provide the clean Python code and explanations in simple text.""",
                expected_output="Final, verified Python code in plain text format without markdown, with a summary of quality improvements made.",
                agent=self.verifier_agent()
            )
        return self._verify_task

    def crew(self) -> Crew:
        """Creates the Phoenix crew"""
        print("Creating Phoenix crew...")
        try:
            # Create agents and tasks
            agents = [self.fixer_agent(), self.verifier_agent()]
            tasks = [self.fix_task(), self.verify_task()]
            
            print(f"Agents created: {len(agents)}")
            print(f"Tasks created: {len(tasks)}")
            
            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            print("✅ Crew created successfully")
            return crew
            
        except Exception as e:
            print(f"❌ Error while creating crew: {e}")
            import traceback
            traceback.print_exc()
            raise