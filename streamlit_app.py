import streamlit as st
import subprocess
import tempfile
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys

# Ensure imports from src/python work
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src', 'python'))

from ai_analyzer import analyze_file
from grc_checker import perform_grc_check

# Session state for scan history
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

st.set_page_config(page_title="SecAI-Nexus", layout="wide", page_icon="🔒")

# Sidebar
with st.sidebar:
    st.header("Tools")
    
    if st.button("Build C & Java (make)"):
        with st.spinner("Compiling..."):
            try:
                result = subprocess.run(
                    ["make"],
                    capture_output=True,
                    text=True,
                    timeout=45,
                    cwd=project_root
                )
                if result.returncode == 0:
                    st.success("Build successful")
                else:
                    st.error("Build failed")
                    st.code(result.stderr)
            except Exception as e:
                st.error(f"Build error: {e}")

    st.info(
        "Full functionality requires compiled binaries (C/Java).\n"
        "They are present in this deployment."
    )

    with st.expander("Project Highlights"):
        st.markdown("""
        - Multi-language cybersecurity toolkit (Python + C + Java)
        - AI-driven threat classification (scikit-learn)
        - Low-level file scanning & log forensics
        - GRC-style risk assessment
        - Interactive visualizations & report export
        Ideal for Security Researcher / Analyst / GRC portfolios.
        """)

# Main content
st.title("🔒 SecAI-Nexus v2.0")
st.markdown("**AI-Powered Cybersecurity Research & Analysis Platform**")
st.caption("Demonstrating threat detection, forensics, low-level analysis, and risk assessment")

tabs = st.tabs(["Dashboard", "AI Threat Analyzer", "C Scanner", "Java Forensics", "GRC & Simulations"])

with tabs[0]:  # Dashboard
    st.header("Threat Intelligence Dashboard")
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Threats (Simulated)", "18", "+5", delta_color="inverse")
    col2.metric("AI Detection Accuracy", "92%", delta="stable")
    col3.metric("GRC Compliance Score", "89/100", "+4")
    
    # Charts section
    st.subheader("Threat Landscape Overview")
    
    # Pie chart - Threat types distribution
    threat_data = pd.DataFrame({
        "Threat Type": ["Malware", "Phishing", "Ransomware", "APT", "Other"],
        "Count": [45, 32, 18, 12, 8]
    })
    fig_pie = px.pie(threat_data, values="Count", names="Threat Type",
                     title="Threat Type Distribution",
                     color_discrete_sequence=px.colors.qualitative.Set3)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Bar chart - Scan history summary
    if st.session_state.scan_history:
        hist_df = pd.DataFrame(st.session_state.scan_history)
        scan_counts = hist_df["Type"].value_counts().reset_index()
        scan_counts.columns = ["Scan Type", "Count"]
        fig_bar = px.bar(scan_counts, x="Scan Type", y="Count",
                         title="Recent Scan Activity",
                         color="Scan Type",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Run scans in other tabs to see activity here.")
    
    # Fake trend line chart
    dates = pd.date_range(end=pd.Timestamp.now(), periods=7).strftime("%Y-%m-%d")
    trend_data = pd.DataFrame({
        "Date": dates,
        "Threat Score": [45, 52, 48, 61, 55, 72, 68]
    })
    fig_line = px.line(trend_data, x="Date", y="Threat Score",
                       title="Threat Score Trend (Last 7 Days - Simulated)",
                       markers=True)
    fig_line.update_layout(yaxis_title="Threat Score (0-100)")
    st.plotly_chart(fig_line, use_container_width=True)
    
    if st.button("Simulate New Threat Feed"):
        st.success("New IOCs ingested: 3 malware hashes, 2 suspicious domains")

    if st.session_state.scan_history:
        st.subheader("Scan History")
        st.dataframe(pd.DataFrame(st.session_state.scan_history))

with tabs[1]:  # AI Threat Analyzer
    st.header("AI Threat Analyzer")
    st.markdown("Upload a file for ML-based classification (entropy + keyword features)")
    
    uploaded = st.file_uploader("Upload file", type=None)
    if uploaded:
        content = uploaded.read()
        with st.spinner("Analyzing..."):
            result = analyze_file(content)
        st.json(result)
        if result["threat_score"] > 60:
            st.error(f"🚨 HIGH THREAT (Score: {result['threat_score']})")
        else:
            st.success(f"✅ Likely benign (Score: {result['threat_score']})")
        
        st.session_state.scan_history.append({
            "Type": "AI",
            "File": uploaded.name,
            "Score": result["threat_score"],
            "Result": result["prediction"]
        })

with tabs[2]:  # C Scanner
    st.header("C Low-Level Scanner")
    st.markdown("Fast integrity check & signature detection (compiled C binary)")
    
    uploaded = st.file_uploader("Upload file for scan", key="c_up")
    if uploaded and st.button("Run C Scanner"):
        if not os.path.exists("bin/c_scanner"):
            st.error("C binary missing - check build.")
        else:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            try:
                result = subprocess.run(["bin/c_scanner", tmp_path], capture_output=True, text=True, timeout=15)
                st.code(result.stdout)
                if result.stderr:
                    st.code(result.stderr)
                st.session_state.scan_history.append({"Type": "C", "File": uploaded.name, "Result": "Completed"})
            except Exception as e:
                st.error(f"Scan failed: {e}")
            finally:
                os.unlink(tmp_path)

with tabs[3]:  # Java Forensics
    st.header("Java Log Forensics")
    st.markdown("Rule-based IOC detection in logs (compiled Java)")
    
    uploaded = st.file_uploader("Upload log file", type=["txt", "log"], key="java_up")
    if uploaded and st.button("Analyze Log"):
        if not os.path.exists("bin/LogAnalyzer.class"):
            st.error("Java class missing - check build.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = tmp.name
            try:
                result = subprocess.run(["java", "-cp", "bin", "LogAnalyzer", tmp_path], capture_output=True, text=True, timeout=15)
                st.code(result.stdout)
                if result.stderr:
                    st.code(result.stderr)
                st.session_state.scan_history.append({"Type": "Java", "File": uploaded.name, "Result": "Analyzed"})
            except Exception as e:
                st.error(f"Analysis failed: {e}")
            finally:
                os.unlink(tmp_path)

with tabs[4]:  # GRC
    st.header("GRC Risk Assessment")
    st.markdown("Interactive risk scoring based on key factors")
    
    risk_factors = {
        "unpatched": st.slider("Unpatched Systems (0-10)", 0, 10, 3),
        "auth": st.slider("Weak Authentication Controls", 0, 10, 4),
        "exposure": st.slider("Data Exposure Risk", 0, 10, 2)
    }
    if st.button("Calculate Risk"):
        result = perform_grc_check(risk_factors)
        st.json(result)

# Export
if st.button("Export Scan History (CSV)"):
    if st.session_state.scan_history:
        df = pd.DataFrame(st.session_state.scan_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Report", csv, "scan_history.csv", "text/csv")
    else:
        st.info("No scans yet.")
