import streamlit as st
import subprocess
import tempfile
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import requests

# Ensure imports from src/python work
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src', 'python'))

from ai_analyzer import analyze_file
from grc_checker import perform_grc_check

# Session state for scan history and global threats
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
if "global_threats" not in st.session_state:
    st.session_state.global_threats = None
if "prev_critical_count" not in st.session_state:
    st.session_state.prev_critical_count = 0

st.set_page_config(page_title="SecAI-Nexus", layout="wide", page_icon="🔒")

# Sidebar (kept simple and useful)
with st.sidebar:
    st.header("Tools & Controls")
    
    if st.button("Build C & Java (make)"):
        with st.spinner("Compiling..."):
            try:
                result = subprocess.run(["make"], capture_output=True, text=True, timeout=45, cwd=project_root)
                if result.returncode == 0:
                    st.success("Build successful")
                else:
                    st.error("Build failed")
                    st.code(result.stderr)
            except Exception as e:
                st.error(f"Build error: {e}")

    st.info("Binaries are active in this deployment.")

    with st.expander("About this Project"):
        st.write("Portfolio project showing Python, C, and Java in cybersecurity.")
        st.write("Includes AI classification, low-level scanning, log forensics, GRC scoring, and live global CVE feed.")

# Main title
st.title("🔒 SecAI-Nexus v2.0")
st.markdown("**AI-Powered Cybersecurity Research & Analysis Platform**")

tabs = st.tabs(["Dashboard", "AI Threat Analyzer", "C Scanner", "Java Forensics", "GRC & Simulations"])

# ==================== DASHBOARD ====================
with tabs[0]:
    st.header("Threat Intelligence Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Threats (Simulated)", "18", "+5")
    col2.metric("AI Accuracy (Demo)", "92%", "stable")
    col3.metric("GRC Compliance", "89/100", "+4")
    
    # Global Live Threat Feed
    st.subheader("🌍 Live Global Threat Vectors (Recent CVEs)")
    st.caption("Fetched from public CIRCL CVE API – worldwide recent vulnerabilities")
    
    if st.button("🔄 Refresh Global Threat Data"):
        with st.spinner("Fetching latest CVEs..."):
            try:
                response = requests.get("https://cve.circl.lu/api/last/20", timeout=12)
                response.raise_for_status()
                cves = response.json()
                st.session_state.global_threats = cves
                
                # Simple change detection
                current_critical = sum(1 for cve in cves if float(cve.get('cvss', 0)) >= 9.0)
                delta = current_critical - st.session_state.prev_critical_count
                st.session_state.prev_critical_count = current_critical
                
                st.success("Data refreshed")
            except Exception as e:
                st.error(f"Could not fetch data: {e}")
    
    if st.session_state.global_threats:
        df = pd.DataFrame(st.session_state.global_threats)
        
        # Severity distribution chart
        df['severity'] = df['cvss'].apply(lambda x: 
            'Critical' if x >= 9.0 else 
            'High' if x >= 7.0 else 
            'Medium' if x >= 4.0 else 'Low')
        
        severity_counts = df['severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        
        fig_sev = px.bar(severity_counts, x='Severity', y='Count',
                         title="Recent CVEs by Severity (Global)",
                         color='Severity',
                         color_discrete_map={'Critical':'red', 'High':'orange', 'Medium':'yellow', 'Low':'green'})
        st.plotly_chart(fig_sev, use_container_width=True)
        
        # Table of recent CVEs
        st.subheader("Latest 20 CVEs")
        display_df = df[['id', 'cvss', 'summary']].rename(columns={'id': 'CVE ID', 'cvss': 'CVSS Score', 'summary': 'Description'})
        st.dataframe(display_df.head(20), use_container_width=True)
        
        # Change metric
        current_crit = sum(1 for cve in st.session_state.global_threats if float(cve.get('cvss', 0)) >= 9.0)
        st.metric("Critical CVEs in latest refresh", current_crit, delta=delta, delta_color="inverse")
    else:
        st.info("Click 'Refresh Global Threat Data' to load real-time CVE information.")
    
    # Simulated / local charts (kept as before)
    st.subheader("Local / Simulated Threat Distribution")
    threat_data = pd.DataFrame({
        "Threat Type": ["Malware", "Phishing", "Ransomware", "APT"],
        "Count": [45, 32, 18, 12]
    })
    fig_pie = px.pie(threat_data, values="Count", names="Threat Type")
    st.plotly_chart(fig_pie, use_container_width=True)

    if st.session_state.scan_history:
        st.subheader("Recent Scans")
        st.dataframe(pd.DataFrame(st.session_state.scan_history))

# ==================== AI THREAT ANALYZER ====================
with tabs[1]:
    st.header("AI Threat Analyzer")
    st.markdown("Upload a file or use sample for ML classification (entropy + keywords)")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded = st.file_uploader("Upload file", type=None)
    with col2:
        if st.button("Load Suspicious Sample"):
            try:
                with open("data/sample_suspicious_file.txt", "rb") as f:
                    content = f.read()
                    uploaded = type('FakeFile', (object,), {'name': 'suspicious.txt', 'read': lambda: content})()
            except FileNotFoundError:
                st.error("Sample file missing")
        if st.button("Load Benign Sample"):
            try:
                with open("data/sample_benign.txt", "rb") as f:
                    content = f.read()
                    uploaded = type('FakeFile', (object,), {'name': 'benign.txt', 'read': lambda: content})()
            except FileNotFoundError:
                st.error("Sample file missing")

    if uploaded is not None:
        try:
            content = uploaded.read() if hasattr(uploaded, 'read') else uploaded
            file_name = uploaded.name if hasattr(uploaded, 'name') else "manual"
            
            if st.button("Analyze"):
                with st.spinner("Analyzing..."):
                    result = analyze_file(content)
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result["threat_score"],
                    title={"text": "Threat Score"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "red" if result["threat_score"] > 60 else "green"},
                        "steps": [
                            {"range": [0, 40], "color": "lightgreen"},
                            {"range": [40, 70], "color": "yellow"},
                            {"range": [70, 100], "color": "red"}
                        ]
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
                
                col_a, col_b = st.columns(2)
                col_a.metric("Prediction", result["prediction"])
                col_b.metric("Confidence", f"{result['confidence']}%")
                
                st.subheader("Features")
                st.json(result["features"])
                
                if result["threat_score"] > 60:
                    st.error("HIGH THREAT DETECTED")
                else:
                    st.success("Likely benign")
                
                st.session_state.scan_history.append({
                    "Type": "AI", "File": file_name, "Score": result["threat_score"], "Result": result["prediction"]
                })
        except Exception as e:
            st.error(f"Error: {e}")

# ==================== C SCANNER ====================
with tabs[2]:
    st.header("C Low-Level Scanner")
    st.markdown("Fast file integrity & signature check")
    
    uploaded = st.file_uploader("Upload file", key="c_upload")
    if st.button("Load Suspicious Sample (C)"):
        try:
            with open("data/sample_suspicious_file.txt", "rb") as f:
                content = f.read()
                uploaded = type('FakeFile', (object,), {'name': 'suspicious.txt', 'getvalue': lambda: content})()
        except FileNotFoundError:
            st.error("Sample missing")
    
    if uploaded and st.button("Run Scan"):
        if not os.path.exists("bin/c_scanner"):
            st.error("C binary missing")
        else:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                if hasattr(uploaded, 'getvalue'):
                    tmp.write(uploaded.getvalue())
                else:
                    tmp.write(uploaded.read())
                tmp_path = tmp.name
            
            try:
                result = subprocess.run(["bin/c_scanner", tmp_path], capture_output=True, text=True, timeout=15)
                st.code(result.stdout)
                if "ALERT" in result.stdout:
                    st.error("Potential threat found")
                else:
                    st.success("Clean")
                st.session_state.scan_history.append({"Type": "C", "File": uploaded.name, "Result": "Completed"})
            except Exception as e:
                st.error(f"Scan error: {e}")
            finally:
                os.unlink(tmp_path)

# ==================== JAVA FORENSICS ====================
with tabs[3]:
    st.header("Java Log Forensics")
    st.markdown("Rule-based log analysis")
    
    uploaded = st.file_uploader("Upload log", type=["txt", "log"], key="java_upload")
    if st.button("Load Sample Log"):
        try:
            with open("data/sample_log.txt", "rb") as f:
                content = f.read()
                uploaded = type('FakeFile', (object,), {'name': 'sample_log.txt', 'getvalue': lambda: content})()
        except FileNotFoundError:
            st.error("Sample missing")
    
    if uploaded and st.button("Analyze"):
        if not os.path.exists("bin/LogAnalyzer.class"):
            st.error("Java class missing")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                if hasattr(uploaded, 'getvalue'):
                    tmp.write(uploaded.getvalue())
                else:
                    tmp.write(uploaded.read())
                tmp_path = tmp.name
            
            try:
                result = subprocess.run(["java", "-cp", "bin", "LogAnalyzer", tmp_path], capture_output=True, text=True, timeout=15)
                st.code(result.stdout)
                suspicious = result.stdout.lower().count("suspicious") + result.stdout.lower().count("high risk")
                st.metric("Suspicious Entries", suspicious)
                if suspicious > 3:
                    st.error("HIGH RISK")
                else:
                    st.success("Normal")
                st.session_state.scan_history.append({"Type": "Java", "File": uploaded.name, "Result": "Analyzed"})
            except Exception as e:
                st.error(f"Analysis error: {e}")
            finally:
                os.unlink(tmp_path)

# ==================== GRC ====================
with tabs[4]:
    st.header("GRC Risk Assessment")
    st.markdown("Risk scoring based on factors")
    
    unpatched = st.slider("Unpatched Systems", 0, 10, 3)
    weak_auth = st.slider("Weak Authentication", 0, 10, 4)
    exposure = st.slider("Data Exposure", 0, 10, 2)
    
    if st.button("Calculate"):
        factors = {"unpatched": unpatched, "auth": weak_auth, "exposure": exposure}
        result = perform_grc_check(factors)
        st.json(result)

# Export
if st.button("Export Scan History"):
    if st.session_state.scan_history:
        df = pd.DataFrame(st.session_state.scan_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "scan_history.csv", "text/csv")
    else:
        st.info("No scans yet.")
