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

# Session state
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

st.set_page_config(page_title="SecAI-Nexus", layout="wide", page_icon="🔒")

# Sidebar
with st.sidebar:
    st.header("Tools")
    if st.button("Build C & Java (make)"):
        with st.spinner("Compiling binaries..."):
            try:
                result = subprocess.run(["make"], capture_output=True, text=True, timeout=45, cwd=project_root)
                if result.returncode == 0:
                    st.success("✅ Build successful")
                else:
                    st.error("Build failed")
                    st.code(result.stderr)
            except Exception as e:
                st.error(f"Error: {e}")

    with st.expander("Project Highlights"):
        st.markdown("""
        **SecAI-Nexus** showcases production-grade cybersecurity tooling:
        - AI/ML threat classification
        - Low-level C scanning (EDR-style)
        - Java-based log forensics (SIEM-like)
        - GRC risk & compliance simulation
        Perfect for Security Researcher, Analyst, and GRC roles.
        """)

# Header
st.title("🔒 SecAI-Nexus v2.0")
st.markdown("**AI-Powered Cybersecurity Research & Analysis Platform**")
st.caption("Multi-language toolkit demonstrating threat detection, forensics, low-level analysis, and GRC")

tabs = st.tabs(["Dashboard", "AI Threat Analyzer", "C Scanner", "Java Forensics", "GRC & Simulations"])

# ==================== DASHBOARD ====================
with tabs[0]:
    st.header("Threat Intelligence Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Threats (Simulated)", "18", "+5")
    col2.metric("AI Detection Accuracy", "92%", "stable")
    col3.metric("GRC Compliance Score", "89/100", "+4")
    
    st.subheader("Threat Landscape")
    threat_data = pd.DataFrame({
        "Threat Type": ["Malware", "Phishing", "Ransomware", "APT", "Other"],
        "Count": [45, 32, 18, 12, 8]
    })
    fig_pie = px.pie(threat_data, values="Count", names="Threat Type", title="Threat Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=7).strftime("%Y-%m-%d")
    trend_data = pd.DataFrame({"Date": dates, "Threat Score": [45, 52, 48, 61, 55, 72, 68]})
    st.plotly_chart(px.line(trend_data, x="Date", y="Threat Score", title="Threat Score Trend (Simulated)"), use_container_width=True)
    
    if st.session_state.scan_history:
        st.subheader("Recent Activity")
        st.dataframe(pd.DataFrame(st.session_state.scan_history))

# ==================== AI THREAT ANALYZER ====================
with tabs[1]:
    st.header("AI Threat Analyzer")
    st.markdown("**Static malware analysis using Random Forest + engineered features** (entropy, size, suspicious keywords)")
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        uploaded_file = st.file_uploader("Upload file for analysis", type=None, key="ai_uploader")
    with col_b:
        sample_choice = st.radio("Or use sample:", ["None", "Suspicious", "Benign"])

    content = None
    file_name = "uploaded_file"

    if uploaded_file is not None:
        content = uploaded_file.read()
        file_name = uploaded_file.name
    elif sample_choice == "Suspicious":
        try:
            with open("data/sample_suspicious_file.txt", "rb") as f:
                content = f.read()
            file_name = "sample_suspicious_file.txt"
        except FileNotFoundError:
            st.error("Sample file not found in data/ folder")
    elif sample_choice == "Benign":
        try:
            with open("data/sample_benign.txt", "rb") as f:
                content = f.read()
            file_name = "sample_benign.txt"
        except FileNotFoundError:
            st.error("Sample file not found in data/ folder")

    if content is not None and st.button("Analyze File", key="ai_analyze"):
        with st.spinner("Running ML classification..."):
            result = analyze_file(content)
        
        # Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=result["threat_score"],
            title={"text": "Threat Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkred" if result["threat_score"] > 60 else "forestgreen"},
                "steps": [
                    {"range": [0, 40], "color": "lightgreen"},
                    {"range": [40, 70], "color": "yellow"},
                    {"range": [70, 100], "color": "red"}
                ]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        col1, col2 = st.columns(2)
        col1.metric("Prediction", result["prediction"])
        col2.metric("Confidence", f"{result['confidence']}%")
        
        st.subheader("Extracted Features")
        st.dataframe(pd.DataFrame([result["features"]]), use_container_width=True)
        
        if result["threat_score"] > 60:
            st.error("🚨 HIGH THREAT DETECTED — Recommend immediate quarantine and deeper analysis")
        else:
            st.success("✅ File appears benign")
        
        st.session_state.scan_history.append({
            "Type": "AI",
            "File": file_name,
            "Score": result["threat_score"],
            "Result": result["prediction"]
        })

# ==================== C SCANNER ====================
with tabs[2]:
    st.header("C Low-Level Scanner")
    st.markdown("**Performance-critical file integrity & signature scanner**")
    
    uploaded_file = st.file_uploader("Upload file for low-level scan", key="c_uploader")
    sample_c = st.button("Load Suspicious Sample (C)")

    if sample_c:
        try:
            with open("data/sample_suspicious_file.txt", "rb") as f:
                content = f.read()
            uploaded_file = type('FakeFile', (), {'name': 'sample_suspicious.txt', 'getvalue': lambda: content})()
        except FileNotFoundError:
            st.error("Sample file missing")

    if uploaded_file is not None and st.button("Run C Scanner"):
        if not os.path.exists("bin/c_scanner"):
            st.error("C binary not found")
        else:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                if hasattr(uploaded_file, 'getvalue'):
                    tmp.write(uploaded_file.getvalue())
                else:
                    tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            with st.spinner("Scanning..."):
                proc = subprocess.run(["bin/c_scanner", tmp_path], capture_output=True, text=True, timeout=15)
            
            st.subheader("C Scanner Report")
            st.code(proc.stdout)
            if "ALERT" in proc.stdout.upper() or "threat" in proc.stdout.lower():
                st.error("🚨 Potential threat indicators found")
            else:
                st.success("✅ Clean")
            
            st.session_state.scan_history.append({
                "Type": "C",
                "File": uploaded_file.name,
                "Result": "Completed"
            })
            os.unlink(tmp_path)

# ==================== JAVA FORENSICS ====================
with tabs[3]:
    st.header("Java Log Forensics")
    st.markdown("**Rule-based IOC detection in logs** (SIEM-style)")
    
    uploaded_file = st.file_uploader("Upload log file", type=["txt", "log"], key="java_uploader")
    sample_log_btn = st.button("Load Sample Log")

    if sample_log_btn:
        try:
            with open("data/sample_log.txt", "rb") as f:
                content = f.read()
            uploaded_file = type('FakeFile', (), {'name': 'sample_log.txt', 'getvalue': lambda: content})()
        except FileNotFoundError:
            st.error("Sample log missing")

    if uploaded_file is not None and st.button("Analyze Log"):
        if not os.path.exists("bin/LogAnalyzer.class"):
            st.error("Java class not found")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                if hasattr(uploaded_file, 'getvalue'):
                    tmp.write(uploaded_file.getvalue())
                else:
                    tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            with st.spinner("Parsing log..."):
                proc = subprocess.run(["java", "-cp", "bin", "LogAnalyzer", tmp_path], capture_output=True, text=True, timeout=15)
            
            st.subheader("Java Forensics Report")
            st.code(proc.stdout)
            
            suspicious = proc.stdout.lower().count("suspicious") + proc.stdout.lower().count("high risk") + proc.stdout.lower().count("alert")
            st.metric("Suspicious Entries", suspicious)
            
            if suspicious > 3:
                st.error("HIGH RISK — Potential incident detected")
            else:
                st.success("Log appears normal")
            
            st.session_state.scan_history.append({
                "Type": "Java",
                "File": uploaded_file.name,
                "Result": "Analyzed"
            })
            os.unlink(tmp_path)

# ==================== GRC & SIMULATIONS ====================
with tabs[4]:
    st.header("GRC Risk Assessment & Simulations")
    st.markdown("**Interactive risk scoring and compliance simulation**")
    
    col1, col2 = st.columns(2)
    with col1:
        unpatched = st.slider("Unpatched Systems", 0, 10, 3)
        weak_auth = st.slider("Weak Authentication", 0, 10, 4)
    with col2:
        data_exposure = st.slider("Data Exposure Risk", 0, 10, 2)
        third_party = st.slider("Third-Party Risk", 0, 10, 5)
    
    if st.button("Calculate Risk & Generate Report"):
        risk_factors = {
            "unpatched": unpatched,
            "auth": weak_auth,
            "exposure": data_exposure,
            "third_party": third_party
        }
        result = perform_grc_check(risk_factors)
        
        st.subheader("Risk Assessment Result")
        st.json(result)
        
        risk_matrix = pd.DataFrame({
            "Category": ["Unpatched", "Auth", "Exposure", "3rd Party"],
            "Score": [unpatched*10, weak_auth*10, data_exposure*10, third_party*10]
        })
        fig = px.bar(risk_matrix, x="Category", y="Score", color="Score",
                     title="Risk Factor Heatmap", color_continuous_scale="RdYlGn_r")
        st.plotly_chart(fig, use_container_width=True)

# Global export
if st.button("Export Full Scan History"):
    if st.session_state.scan_history:
        df = pd.DataFrame(st.session_state.scan_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV Report", csv, "SecAI-Nexus_Scan_Report.csv", "text/csv")
    else:
        st.info("No scans recorded yet.")
