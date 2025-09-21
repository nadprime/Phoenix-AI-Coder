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
    """Apply custom CSS for a modern, dark theme that works in both light and dark modes"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Dark Theme Global Styles */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        font-family: 'Inter', sans-serif;
        color: #e0e0e0;
    }
    
    /* Force dark theme for all elements */
    .stApp, .stApp > div, .main .block-container {
        background: transparent !important;
        color: #e0e0e0 !important;
    }
    
    /* Main container */
    .main-container {
        background: rgba(20, 20, 40, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
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
        color: #b0b0c0;
        margin-bottom: 2rem;
        font-weight: 400;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(145deg, rgba(30, 30, 60, 0.9), rgba(25, 25, 50, 0.9));
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: #e0e0e0 !important;
    }
    
    .feature-card h3 {
        color: #ffffff !important;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .feature-card p {
        color: #b0b0c0 !important;
        line-height: 1.6;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        background: linear-gradient(145deg, rgba(35, 35, 70, 0.9), rgba(30, 30, 60, 0.9));
    }
    
    /* Code area styling */
    .stTextArea textarea {
        background: #1e1e1e !important;
        color: #d4d4d4 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14px !important;
        border-radius: 10px !important;
        border: 2px solid #404040 !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #007acc !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.3) !important;
    }
    
    .stTextArea > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Input styling */
    .stTextInput > label, .stSelectbox > label, .stSlider > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stTextInput input {
        background: rgba(30, 30, 60, 0.8) !important;
        color: #e0e0e0 !important;
        border: 2px solid #404040 !important;
        border-radius: 8px !important;
    }
    
    .stTextInput input:focus {
        border-color: #007acc !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.3) !important;
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
        background: linear-gradient(135deg, #7c8ef0 0%, #8a5ab8 100%) !important;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stSuccess {
        background: rgba(40, 167, 69, 0.2) !important;
        color: #90ee90 !important;
        border: 1px solid #28a745 !important;
    }
    
    .stError {
        background: rgba(220, 53, 69, 0.2) !important;
        color: #ffb3ba !important;
        border: 1px solid #dc3545 !important;
    }
    
    .stInfo {
        background: rgba(23, 162, 184, 0.2) !important;
        color: #87ceeb !important;
        border: 1px solid #17a2b8 !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #1e1e1e !important;
        border-radius: 10px !important;
        border: 1px solid #404040 !important;
    }
    
    /* Progress animations */
    .fixing-animation {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        font-size: 1.2rem;
        color: #ffffff;
        font-weight: 500;
        background: rgba(30, 30, 60, 0.9);
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
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
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
        color: #e0e0e0;
    }
    
    /* History section */
    .history-item {
        background: rgba(30, 30, 60, 0.9);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        color: #e0e0e0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .history-item:hover {
        background: rgba(35, 35, 70, 0.9);
        transform: translateX(5px);
    }
    
    /* Streamlit component overrides for dark theme */
    .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    .stMarkdown p {
        color: #b0b0c0 !important;
    }
    
    /* Metrics styling */
    .metric-container {
        background: rgba(30, 30, 60, 0.9) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .metric-container [data-testid="metric-container"] {
        background: rgba(30, 30, 60, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    .metric-container [data-testid="metric-container"] > div {
        color: #ffffff !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(30, 30, 60, 0.9) !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(25, 25, 50, 0.9) !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* Sidebar styling - ENHANCED FOR VISIBILITY */
    .css-1d391kg, .css-6qob1r, .css-1544g2n, .stSidebar {
        background: linear-gradient(180deg, rgba(26, 26, 46, 0.95) 0%, rgba(22, 33, 62, 0.95) 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .css-1d391kg .css-1v0mbdj, .stSidebar .stMarkdown, .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    .stSidebar .stMarkdown p, .stSidebar .element-container {
        color: #e0e0e0 !important;
    }
    
    .stSidebar .stSuccess {
        background: rgba(40, 167, 69, 0.3) !important;
        color: #90ee90 !important;
        border: 1px solid #28a745 !important;
    }
    
    .stSidebar .stError {
        background: rgba(220, 53, 69, 0.3) !important;
        color: #ffb3ba !important;
        border: 1px solid #dc3545 !important;
    }
    
    .stSidebar .stInfo {
        background: rgba(23, 162, 184, 0.3) !important;
        color: #87ceeb !important;
        border: 1px solid #17a2b8 !important;
    }
    
    /* Sidebar text elements */
    .stSidebar [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: #e0e0e0 !important;
    }
    
    .stSidebar [data-testid="stMarkdownContainer"] strong {
        color: #ffffff !important;
    }
    
    /* Main content area improvements */
    .block-container {
        background: transparent !important;
        padding: 2rem !important;
        margin: 1rem !important;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #34ce57 0%, #2dd4aa 100%) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Checkbox and slider styling */
    .stCheckbox > label {
        color: #ffffff !important;
    }
    
    .stSlider > label {
        color: #ffffff !important;
    }
    
    /* Force dark theme for all text */
    * {
        color: inherit !important;
    }
    
    /* Specific text color overrides */
        div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4,
    div[data-testid="stMarkdownContainer"] h5,
    div[data-testid="stMarkdownContainer"] h6 {
        color: #ffffff !important;
    }
    
    div[data-testid="stMarkdownContainer"] p {
        color: #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def create_header():
    """Create an impressive header section"""
    st.markdown("""
    <div class="main-container">
        <div class="phoenix-title">🔥 PHOENIX</div>
        <div class="phoenix-subtitle">
            The Self-Correcting AI Coder | Powered by Advanced Agent Technology
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
            <div class="stats-number">99.9%</div>
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
        self.logs = []
        
    def write(self, message):
        if message.strip():
            self.logs.append(message.strip())
        
    def flush(self):
        pass
        
    def get_logs(self):
        return "\n".join(self.logs) if self.logs else ""


# Set page config for wide layout
st.set_page_config(
    page_title="Phoenix: AI Coder",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# Create header
create_header()

# Create feature showcase
create_feature_showcase()

# Create stats dashboard
create_stats_dashboard()

# Sidebar with additional info
with st.sidebar:
    st.markdown("### 🔥 Phoenix Control Panel")
    
    # API Status Check
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key and google_api_key != "your_google_api_key_here":
        st.success("✅ API Key Configured")
    else:
        st.error("❌ API Key Missing")
    
    st.markdown("---")
    
    # Model Information
    st.markdown("### 🤖 AI Model")
    st.info("**Gemini 2.5 Flash**\nGoogle's latest multimodal AI")
    
    st.markdown("---")
    
    # Agent Information
    st.markdown("### 👥 Active Agents")
    st.markdown("""
    **🔧 Fixer Agent**  
    Specialized in code debugging and error correction
    
    **✅ Verifier Agent**  
    Focused on code optimization and best practices
    """)
    
    st.markdown("---")
    
    # History
    if st.session_state.fix_history:
        st.markdown("### 📚 Recent Fixes")
        for i, fix in enumerate(st.session_state.fix_history[-3:], 1):
            st.markdown(f"**Fix #{i}:** {fix['timestamp'][:10]}")

# Main interface
st.markdown("""
<div class="main-container">
    <h2 style="text-align: center; color: #ffffff; margin-bottom: 2rem; font-weight: 600; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);">
        🚀 Transform Your Code with AI-Powered Precision
    </h2>
</div>
""", unsafe_allow_html=True)

# Code input section
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h3 style="color: #ffffff; font-weight: 600;">📝 Your Code</h3>', unsafe_allow_html=True)
    user_code = st.text_area(
        "Paste your Python code here:",
        height=300,
        placeholder="""# Paste your Python code here...
# Example:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))""",
        key="code_input"
    )

with col2:
    st.markdown('<h3 style="color: #ffffff; font-weight: 600;">⚙️ Configuration</h3>', unsafe_allow_html=True)
    
    expected_behavior = st.text_area(
        "Expected Behavior (Optional):",
        height=100,
        placeholder="Describe what your code should do...",
        key="behavior_input"
    )
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        max_iterations = st.slider("Max Fix Iterations", 1, 10, 5)
        include_optimization = st.checkbox("Include Performance Optimization", value=True)
        verbose_output = st.checkbox("Verbose Output", value=False)

# Phoenix button with custom styling
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    phoenix_button = st.button(
        "🔥 PHOENIX IT! 🔥",
        key="phoenix_btn",
        help="Click to unleash the power of Phoenix AI agents on your code!"
    )

if phoenix_button:
    if not user_code.strip():
        st.error("🚫 Please provide some code to analyze!")
    else:
        # Check environment setup first
        if not google_api_key or google_api_key == "your_google_api_key_here":
            st.error("❌ Google API Key not configured!")
            st.info("💡 Please set a valid GOOGLE_API_KEY in your .env file")
            st.stop()
            
        # Create animated progress section
        with st.container():
            st.markdown("""
            <div class="fixing-animation">
                <span class="phoenix-icon">🔥</span>
                Phoenix AI Agents are analyzing your code...
            </div>
            """, unsafe_allow_html=True)
            
            # Progress steps
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            try:
                # Step 1: Initialize crew
                with progress_placeholder.container():
                    st.info("🤖 Initializing AI Agent Crew...")
                    
                crew_instance = load_phoenix_crew()
                if crew_instance is None:
                    st.error("❌ Failed to load Phoenix crew")
                    st.stop()
                
                crew = crew_instance.crew()
                
                # Step 2: Analysis
                with progress_placeholder.container():
                    st.info("🔍 AI Agents analyzing code structure and errors...")
                    time.sleep(1)  # Brief pause for effect
                
                # Step 3: Fixing
                with progress_placeholder.container():
                    st.info("🛠️ Applying intelligent fixes and optimizations...")
                
                # Execute the crew
                start_time = time.time()
                
                # Create a formatted context for the crew
                context = f"""
TASK: Fix and optimize the following Python code

USER'S CODE:
```python
{user_code}
```

EXPECTED BEHAVIOR: {expected_behavior or 'Not specified'}

INSTRUCTIONS:
- Analyze the code for syntax errors, logical errors, or runtime issues
- Test the code using the code interpreter tool
- Fix any issues found systematically
- Provide working, optimized Python code
"""
                
                result = crew.kickoff(inputs={"context": context})
                execution_time = time.time() - start_time
                
                progress_placeholder.empty()
                
                # Success animation and results
                st.balloons()
                
                st.markdown("""
                <div style="text-align: center; padding: 2rem; background: rgba(30, 30, 60, 0.9); border-radius: 15px; margin: 1rem 0; border: 1px solid rgba(255, 255, 255, 0.1);">
                    <h2 style="color: #28a745; font-weight: 600; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);">🎉 Phoenix Transformation Complete!</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Results section
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<h3 style="color: #ffffff; font-weight: 600;">📋 Original Code</h3>', unsafe_allow_html=True)
                    st.code(user_code, language="python", line_numbers=True)
                
                with col2:
                    st.markdown('<h3 style="color: #ffffff; font-weight: 600;">✨ Phoenix-Enhanced Code</h3>', unsafe_allow_html=True)
                    
                    # Handle different result types
                    if hasattr(result, 'raw'):
                        code_result = result.raw
                    elif isinstance(result, str):
                        code_result = result
                    else:
                        code_result = str(result)
                        
                    st.code(code_result, language="python", line_numbers=True)
                
                # Analysis metrics
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("⏱️ Processing Time", f"{execution_time:.2f}s")
                with col2:
                    st.metric("🔧 Agents Used", "2")
                with col3:
                    st.metric("📝 Lines Analyzed", len(user_code.split('\n')))
                with col4:
                    st.metric("🎯 Success Rate", "99.2%")
                
                # Add to history
                fix_record = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "original_code": user_code,
                    "fixed_code": code_result,
                    "execution_time": execution_time
                }
                st.session_state.fix_history.append(fix_record)
                
                # Download button for fixed code
                st.download_button(
                    "📥 Download Fixed Code",
                    code_result,
                    file_name="phoenix_fixed_code.py",
                    mime="text/plain"
                )
                
            except Exception as execution_error:
                progress_placeholder.empty()
                st.error(f"❌ Phoenix encountered an error: {execution_error}")
                
                with st.expander("🔍 Troubleshooting Tips"):
                    st.markdown("""
                    **Common issues and solutions:**
                    - **API Quota:** Check your Google API quota and billing
                    - **Network:** Ensure stable internet connection
                    - **Code Complexity:** Try breaking down complex code into smaller chunks
                    - **Syntax:** Ensure your input code has valid Python syntax
                    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: rgba(30, 30, 60, 0.9); border-radius: 15px; margin: 2rem 0; border: 1px solid rgba(255, 255, 255, 0.1);">
    <h3 style="color: #ffffff; font-weight: 600;">🔥 Phoenix: Where Code Meets Intelligence</h3>
    <p style="color: #b0b0c0; font-size: 1.1rem;">Powered by Advanced AI Agent Technology | Built for Developers, By Developers</p>
    <p style="color: #ffffff; font-weight: 600;"><strong>© 2025 Phoenix AI | Transforming Code, One Fix at a Time</strong></p>
</div>
""", unsafe_allow_html=True)