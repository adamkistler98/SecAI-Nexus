import streamlit as st
import subprocess
import tempfile
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import requests
from datetime import datetime

# Import custom modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src', 'python'))

from ai_analyzer import analyze_file
from grc_checker import perform_grc_check

# Session state
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
if "global_threats" not in st.session_state:
    st.session_state.global_threats = None
if "previous_critical_count" not in st.session_state:
    st.session_state.previous_critical_count = 0

st.set_page_config(page_title="SecAI-Nexus", layout="wide", page_icon="🔒")

# Sidebar
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

    st.info("Compiled binaries are active in this deployment.")

    with st.expander("About this Project"):
        st.write("Portfolio project demonstrating Python, C, and Java in a cybersecurity context.")
        st.write("AI threat classification, low-level scanning, log forensics, GRC risk scoring, and live global threat intel.")

# Main title
st.title("🔒 SecAI-Nexus v2.0")
st.markdown("**AI-Powered Cybersecurity Research & Analysis Platform**")

tabs = st.tabs(["Dashboard", "AI Threat Analyzer", "C Scanner", "Java Forensics", "GRC & Simulations"])

# ==================== DASHBOARD (with Global Threat Data) ====================
with tabs[0]:
    st.header("Threat Intelligence Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Threats (Simulated)", "18", "+5")
    col2.metric("AI Accuracy (Demo)", "92%", "stable")
    col3.metric("GRC Compliance", "89/100", "+4")
    
    # Global Threat Intelligence Section
    st.subheader("🌍 Global Threat Intelligence (Live CVE Feed)")
    st.caption("Data from public CIRCL CVE Search API • Refreshed on demand • Shows worldwide recent vulnerabilities")
    
    if st.button("🔄 Refresh Live Global Threats"):
        with st.spinner("Fetching latest CVEs from CIRCL..."):
            try:
                resp = requests.get("https://cve.circl.lu/api/last/20", timeout=15)
                resp.raise_for_status()
                data = resp.json()
                st.session_state.global_threats = data
                # Track change in critical/high count
                current_critical = sum(1 for cve in data if cve.get("cvss", 0) >= 9.0)
                st.session_state.previous_critical_count = current_critical
                st.success("✅ Updated with latest global threat data")
            except Exception as e:
                st.error(f"Failed to fetch live data: {e}")
    
    if st.session_state.global_threats:
        df = pd.DataFrame(st.session_state.global_threats)
        
        # Severity chart
        severity_counts = df['cvss'].apply(lambda x: 
            "Critical" if x >= 9.0 else 
            "High" if x >= 7.0 else 
            "Medium" if x >= 4.0 else "Low").value_counts()
        
        fig_sev = px.bar(x=severity_counts.index, y=severity_counts.values,
                         title="Recent CVEs by Severity (Global)",
                         labels={"x": "Severity", "y": "Count"},
                         color=severity_counts.index,
                         color_discrete_map={"Critical":"red", "High":"orange", "Medium":"yellow", "Low":"green"})
        st.plotly_chart(fig_sev, use_container_width=True)
        
        # Top vendors (simple parse from ID or description)
        st.subheader("Top Affected Vendors (Recent CVEs)")
        st.dataframe(df[['id', 'cvss', 'summary']].head(10), use_container_width=True)
        
        # Change indicator
        current_crit = sum(1 for cve in st.session_state.global_threats if cve.get("cvss", 0) >= 9.0)
        delta = current_crit - st.session_state.previous_critical_count
        st.metric("Critical/High Threats (Latest 20)", current_crit, delta=delta)
    else:
        st.info("Click 'Refresh Live Global Threats' to load real-time worldwide CVE data.")

    # Existing charts / history
    st.subheader("Threat Distribution (Simulated)")
    threat_data = pd.DataFrame({"Threat Type": ["Malware", "Phishing", "Ransomware", "APT"], "Count": [45, 32, 18, 12]})
    st.plotly_chart(px.pie(threat_data, values="Count", names="Threat Type"), use_container_width=True)

    if st.session_state.scan_history:
        st.subheader("Recent Scans")
        st.dataframe(pd.DataFrame(st.session_state.scan_history))

# The rest of the tabs (AI, C, Java, GRC) remain the same as the last stable version you had.
# Paste the previous working code for tabs[1] to tabs[4] here if needed, or keep your current ones.

# Global export (keep as before)
if st.button("Export Scan History"):
    if st.session_state.scan_history:
        df = pd.DataFrame(st.session_state.scan_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV Report", csv, "scan_history.csv", "text/csv")
    else:
        st.info("No scans yet.")
