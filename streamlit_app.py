import streamlit as st
import subprocess
import tempfile
import os
import pandas as pd
import plotly.express as px
import sys
import traceback

# Make sure we can import from src/python even if cwd is not root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src', 'python'))

try:
    from ai_analyzer import analyze_file
    from grc_checker import perform_grc_check
    from utils import extract_features  # just to test import chain
except ImportError as e:
    st.error(f"Failed to import custom modules: {e}")
    st.error("Check folder structure: src/python/ai_analyzer.py etc. must exist")
    st.stop()

# Debug banner at the very top
st.markdown("**DEBUG MODE ACTIVE - This helps diagnose deployment issues**")

# Show basic environment info
st.write("Python version:", sys.version)
st.write("Current working directory:", os.getcwd())
st.write("bin/ folder exists?", os.path.isdir("bin"))
st.write("C binary exists?", os.path.exists("bin/c_scanner"))
st.write("Java class exists?", os.path.exists("bin/LogAnalyzer.class"))

# Session state for scan history
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

# Sidebar with build debug
with st.sidebar:
    st.header("Tools & Debug")
    
    if st.button("Try to Build C & Java (make)"):
        with st.spinner("Running make..."):
            try:
                result = subprocess.run(
                    ["make"],
                    capture_output=True,
                    text=True,
                    timeout=45,
                    cwd=project_root
                )
                st.code("STDOUT:\n" + result.stdout)
                st.code("STDERR:\n" + result.stderr)
                if result.returncode == 0:
                    st.success("make completed with return code 0")
                else:
                    st.error(f"make failed with return code {result.returncode}")
            except Exception as build_err:
                st.error(f"Could not run make: {build_err}")
                st.error(traceback.format_exc())

    st.info(
        "For full functionality on Streamlit Cloud:\n"
        "- packages.txt must contain: build-essential and openjdk-17-jdk\n"
        "- make must succeed during or after build\n"
        "After pushing changes, reboot the app at https://share.streamlit.io"
    )

    with st.expander("About this Project"):
        st.write("Portfolio project demonstrating Python, C, and Java in a cybersecurity context.")
        st.write("AI threat classification, low-level file scanning, log forensics, GRC risk scoring.")

# Main title
st.title("SecAI-Nexus v2.0")
st.markdown("**AI-Powered Cybersecurity Research & Analysis Platform**")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "AI Threat Analyzer",
    "C Scanner",
    "Java Forensics",
    "GRC & Simulations"
])

with tab1:
    st.header("Threat Intelligence Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Simulated Active Threats", "18", "↑5")
    col2.metric("AI Accuracy (Demo)", "92%", "-")
    col3.metric("GRC Compliance", "89/100", "↑4")
    
    if st.button("Simulate New Threat Feed"):
        st.success("New IOCs ingested: 3 malware hashes, 2 suspicious domains")
    
    if st.session_state.scan_history:
        history_df = pd.DataFrame(st.session_state.scan_history)
        st.subheader("Recent Scans")
        st.dataframe(history_df)

with tab2:
    st.header("AI Threat Analyzer")
    uploaded = st.file_uploader("Upload file for ML analysis", type=None)
    if uploaded:
        try:
            content = uploaded.read()
            with st.spinner("Analyzing with RandomForest model..."):
                result = analyze_file(content)
            st.json(result)
            if result["threat_score"] > 60:
                st.error("HIGH THREAT")
            else:
                st.success("Benign")
            st.session_state.scan_history.append({
                "Type": "AI",
                "File": uploaded.name,
                "Score": result["threat_score"],
                "Result": result["prediction"]
            })
        except Exception as e:
            st.error(f"AI analysis failed: {e}")
            st.exception(e)

with tab3:
    st.header("C Low-Level Scanner")
    st.info("Requires bin/c_scanner to exist (built via make)")
    
    uploaded = st.file_uploader("Upload for low-level scan", type=None, key="c_upload")
    if uploaded and st.button("Run C Scanner"):
        if not os.path.exists("bin/c_scanner"):
            st.error("C binary not found. Compilation likely failed on cloud.")
            st.info("Check build logs or run 'make' locally / in Docker.")
        else:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            
            try:
                with st.spinner("Scanning..."):
                    result = subprocess.run(
                        ["bin/c_scanner", tmp_path],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    st.code(result.stdout)
                    if result.stderr:
                        st.code("Errors:\n" + result.stderr)
                st.session_state.scan_history.append({
                    "Type": "C",
                    "File": uploaded.name,
                    "Result": "Completed"
                })
            except Exception as e:
                st.error(f"C scanner failed: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

with tab4:
    st.header("Java Log Forensics")
    st.info("Requires bin/LogAnalyzer.class to exist (built via make)")
    
    uploaded = st.file_uploader("Upload log", type=["txt", "log"], key="java_upload")
    if uploaded and st.button("Analyze Log"):
        if not os.path.exists("bin/LogAnalyzer.class"):
            st.error("Java class not found. Compilation likely failed on cloud.")
            st.info("Check build logs or run 'make' locally / in Docker.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            
            try:
                with st.spinner("Parsing log..."):
                    result = subprocess.run(
                        ["java", "-cp", "bin", "LogAnalyzer", tmp_path],
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    st.code(result.stdout)
                    if result.stderr:
                        st.code("Errors:\n" + result.stderr)
                st.session_state.scan_history.append({
                    "Type": "Java",
                    "File": uploaded.name,
                    "Result": "Analyzed"
                })
            except Exception as e:
                st.error(f"Java analyzer failed: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

with tab5:
    st.header("GRC Risk Assessment")
    risk_factors = {
        "unpatched": st.slider("Unpatched Systems (0-10)", 0, 10, 3),
        "auth": st.slider("Weak Authentication", 0, 10, 4),
        "exposure": st.slider("Data Exposure", 0, 10, 2)
    }
    if st.button("Calculate Risk Score"):
        try:
            result = perform_grc_check(risk_factors)
            st.json(result)
        except Exception as e:
            st.error(f"GRC calculation failed: {e}")

# Export history
if st.button("Export Scan History"):
    if st.session_state.scan_history:
        df = pd.DataFrame(st.session_state.scan_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV Report",
            data=csv,
            file_name="scan_report.csv",
            mime="text/csv"
        )
    else:
        st.info("No scans recorded yet.")
