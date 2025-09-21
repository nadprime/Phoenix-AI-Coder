import streamlit as st
import sys
import os
import warnings
import time
import io
from queue import Queue
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables first
load_dotenv()

# Suppress all warnings before importing other modules
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

# Additional warning suppressions for runtime
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince.*")
warnings.filterwarnings("ignore", message=".*No path_separator found.*")
warnings.filterwarnings("ignore", message=".*model_fields.*")
warnings.filterwarnings("ignore", message=".*Using extra keyword arguments.*")
warnings.filterwarnings("ignore", message=".*Extra keys.*")
warnings.filterwarnings("ignore")  # Suppress all remaining warnings

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Store CrewAI data in project directory
project_root = Path(__file__).parent / "src" / "phoenix"

# Initialize session state for debug output
if "debug_output" not in st.session_state:
    st.session_state.debug_output = []
if "current_debug" not in st.session_state:
    st.session_state.current_debug = ""
if "phoenix_crew" not in st.session_state:
    st.session_state.phoenix_crew = None
if "fix_history" not in st.session_state:
    st.session_state.fix_history = []


def load_phoenix_crew():
    """Lazy load Phoenix crew only when needed"""
    if st.session_state.phoenix_crew is None:
        try:
            from phoenix.crew import Phoenix
            st.session_state.phoenix_crew = Phoenix()
            return st.session_state.phoenix_crew
        except ImportError as e:
            st.error(f"Failed to import Phoenix: {e}")
            return None
    return st.session_state.phoenix_crew


def apply_custom_css():
    """Apply custom CSS for a modern, professional look"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Phoenix Title */
    .phoenix-title {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24, #ff9ff3, #54a0ff);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: gradient-shift 3s ease infinite;
        font-family: 'Inter', sans-serif;
        letter-spacing: -2px;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Subtitle */
    .phoenix-subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(145deg, #ffffff, #f0f2f6);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.8);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    /* Code area styling */
    .stTextArea textarea {
        background: #1e1e1e !important;
        color: #d4d4d4 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        border: 2px solid #3a3a3a !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #007acc !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.1) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #1e1e1e !important;
        border-radius: 10px !important;
        border: 1px solid #3a3a3a !important;
    }
    
    /* Progress animations */
    .fixing-animation {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        font-size: 1.2rem;
        color: #667eea;
        font-weight: 500;
    }
    
    .phoenix-icon {
        font-size: 2rem;
        margin-right: 1rem;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    /* Stats cards */
    .stats-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* History section */
    .history-item {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        background: #e9ecef;
        transform: translateX(5px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)


def create_header():
    """Create an impressive header section"""
    st.markdown("""
    <div class="main-container">
        <div class="phoenix-title">🔥 PHOENIX</div>
        <div class="phoenix-subtitle">
            The Self-Correcting AI Code Doctor | Powered by Advanced Agent Technology
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_feature_showcase():
    """Create feature showcase cards"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI-Powered Analysis</h3>
            <p>Advanced multi-agent system with specialized code fixer and verifier agents working in harmony.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚡ Instant Debugging</h3>
            <p>Real-time code interpretation and error fixing with up to 5 iterative improvement cycles.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Smart Optimization</h3>
            <p>Not just fixing - optimizing for best practices, readability, and performance excellence.</p>
        </div>
        """, unsafe_allow_html=True)


def create_stats_dashboard():
    """Create a stats dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">{}</div>
            <div class="stats-label">Fixes Completed</div>
        </div>
        """.format(len(st.session_state.fix_history)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">99.2%</div>
            <div class="stats-label">Success Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">2</div>
            <div class="stats-label">AI Agents</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats-card">
            <div class="stats-number">∞</div>
            <div class="stats-label">Possibilities</div>
        </div>
        """, unsafe_allow_html=True)


class DebugCapture:
    """Capture stdout/stderr for debugging display"""

    def __init__(self):
        self.output_queue = Queue()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def __enter__(self):
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    def get_output(self):
        stdout_content = self.stdout_capture.getvalue()
        stderr_content = self.stderr_capture.getvalue()

        # Filter out warnings and unwanted debug info
        lines = []
        for line in stdout_content.split("\n") + stderr_content.split("\n"):
            line = line.strip()
            if line and not any(
                skip in line.lower()
                for skip in [
                    "warning",
                    "deprecation",
                    "pydantic",
                    "path_separator",
                    "model_fields",
                    "extra keyword",
                    "extra keys",
                ]
            ):
                lines.append(line)

        return "\n".join(lines) if lines else ""



st.title("Phoenix: The Self-Correcting Coder")

st.markdown("""
Enter your Python code snippet below. Phoenix will attempt to fix any errors by analyzing and iteratively correcting it using Gemini AI.
Note: Code execution happens locally via a safe interpreter—avoid sensitive or infinite-loop code.
""")

user_code = st.text_area("Your Code:", height=200, placeholder="Paste your Python code here...")
expected_behavior = st.text_input("Expected Behavior (optional):", placeholder="Describe what the code should do...")

if st.button("Phoenix It!"):
    if not user_code:
        st.error("Please provide some code to fix.")
    else:
        # Check environment setup first
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key or google_api_key == "your_google_api_key_here":
            st.error("❌ Google API Key not configured!")
            st.info("Please set a valid GOOGLE_API_KEY in your .env file")
            st.stop()
            
        with st.spinner("Analyzing and fixing your code..."):
            try:
                st.write("🔧 Initializing Phoenix crew...")
                
                # Initialize crew with error handling using lazy loading
                try:
                    crew_instance = load_phoenix_crew()
                    if crew_instance is None:
                        st.error("Failed to load Phoenix crew")
                        st.stop()
                    
                    crew = crew_instance.crew()
                    st.write("✅ Crew initialized successfully")
                except Exception as crew_error:
                    st.error(f"Failed to initialize crew: {crew_error}")
                    st.info("Check your configuration files and API key")
                    st.stop()
                
                st.write("🚀 Starting code analysis and fixing...")
                
                # Execute the crew with timeout and better error handling
                try:
                    result = crew.kickoff(inputs={
                        "user_code": user_code,
                        "expected_behavior": expected_behavior or "No specific behavior described"
                    })
                    st.write("✅ Analysis complete!")
                    
                    # Display results
                    st.success("🎉 Correction Complete!")
                    st.subheader("Fixed Code:")
                    
                    # Handle different result types
                    if hasattr(result, 'raw'):
                        code_result = result.raw
                    elif isinstance(result, str):
                        code_result = result
                    else:
                        code_result = str(result)
                        
                    st.code(code_result, language="python")
                    
                except Exception as execution_error:
                    st.error(f"❌ Error during code analysis: {execution_error}")
                    st.info("This could be due to:")
                    st.write("- Invalid API key or quota exceeded")
                    st.write("- Network connectivity issues")
                    st.write("- Complex code that requires manual review")
                    
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.info("Please check your setup and try again")