import streamlit as st
import subprocess
import tempfile
import os
import pandas as pd
import plotly.express as px
import sys

# Make imports work
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'python'))

from ai_analyzer import analyze_file
from grc_checker import perform_grc_check

st.set_page_config(page_title="SecAI-Nexus", layout="wide", page_icon="🔒")
st.title("🔒 SecAI-Nexus v2.0")
st.markdown("**AI-Powered Cybersecurity Research & Analysis Platform**")

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

with st.sidebar:
    st.header("Tools")
    if st.button("Build C & Java Tools"):
        with st.spinner("Compiling..."):
            try:
                result = subprocess.run(["make"], capture_output=True, text=True)
                st.success("Build successful!")
                if result.stdout: st.code(result.stdout)
            except Exception as e:
                st.error(f"Build failed: {e}")
    st.info("Requires gcc and javac installed.")
    with st.expander("About this Project"):
        st.write("Portfolio project demonstrating Python, C, and Java in a cybersecurity context.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "AI Threat Analyzer", "C Scanner", "Java Forensics", "GRC & Simulations"])

# (The rest of the Streamlit code is the same as the previous message — copy the full tab content from the last response into this file.)

# For brevity here, paste the entire tab1–tab5 block from the previous version into this file.
# It includes session history, all tabs, export button, etc.
