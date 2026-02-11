import streamlit as st
import subprocess
import os
import pandas as pd
import plotly.express as px
import sys
import requests

# Clean stealthy dark theme
st.markdown("""
<style>
    .main, .stApp {background-color: #0a0a0a !important; color: #00cc66 !important;}
    h1, h2, h3, h4 {color: #00cc66 !important; font-family: monospace;}
    .stMetric {background-color: #1a1a1a !important; border-left: 4px solid #00cc66 !important;}
    .stButton>button {background-color: #00cc66; color: #000000; font-weight: bold;}
    .stDataFrame, .stTable {background-color: #1a1a1a !important;}
    .stDataFrame td, .stDataFrame th, .stTable td, .stTable th {color: #00cc66 !important; background-color: #1a1a1a !important;}
    .stPlotlyChart {background-color: #0a0a0a !important;}
</style>
""", unsafe_allow_html=True)

# Imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src', 'python'))

from ai_analyzer import analyze_file
from grc_checker import perform_grc_check

# Session state
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
if "global_threats" not in st.session_state:
    st.session_state.global_threats = None
if "prev_critical" not in st.session_state:
    st.session_state.prev_critical = 0

st.set_page_config(page_title="SecAI-Nexus", layout="wide", page_icon="🔒")

# Sidebar
with st.sidebar:
    st.header("Controls")
    if st.button("Build C & Java Binaries"):
        with st.spinner("Compiling..."):
            try:
                result = subprocess.run(["make"], capture_output=True, text=True, timeout=45, cwd=project_root)
                if result.returncode == 0:
                    st.success("✅ Binaries ready")
                else:
                    st.error("Build failed")
            except Exception as e:
                st.error(f"Error: {e}")

    with st.expander("About"):
        st.write("Single-dashboard real-time threat visibility platform.")
        st.write("Live CVE feed + active ransomware, malware, phishing & APT tracking.")

st.title("🔒 SecAI-Nexus")
st.markdown("**GLOBAL THREAT VISIBILITY DASHBOARD**")
st.caption("Real-time intelligence • February 2026")

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Threats", "24", "+7")
col2.metric("Critical CVEs (24h)", "6", "+2")
col3.metric("Ransomware Claims", "91", "Jan-Feb 2026")
col4.metric("AI Detection", "93%", "↑")

# Live CVE Feed
st.subheader("🌍 Live CVE Feed (Worldwide)")
if st.button("🔄 Refresh Live CVE Data"):
    with st.spinner("Fetching latest CVEs..."):
        try:
            resp = requests.get("https://cve.circl.lu/api/last/20", timeout=15)
            resp.raise_for_status()
            cves = resp.json()
            st.session_state.global_threats = cves
            current_crit = sum(1 for c in cves if float(c.get('cvss', 0)) >= 9.0)
            delta = current_crit - st.session_state.prev_critical
            st.session_state.prev_critical = current_crit
            st.success("Live data updated")
        except Exception as e:
            st.error(f"API error: {e}")

# CVE Charts & Table (only show when data exists)
if st.session_state.global_threats:
    df = pd.DataFrame(st.session_state.global_threats)
    if 'cvss' in df.columns:
        df['cvss'] = pd.to_numeric(df['cvss'], errors='coerce').fillna(0)
    else:
        df['cvss'] = 0.0
    df['severity'] = df['cvss'].apply(lambda x: 'Critical' if x >= 9 else 'High' if x >= 7 else 'Medium' if x >= 4 else 'Low')
    
    col_left, col_right = st.columns(2)
    with col_left:
        fig_sev = px.bar(df['severity'].value_counts().reset_index(), x='index', y='severity',
                         title="CVE Severity Distribution", color='index',
                         color_discrete_map={'Critical':'#ff3333','High':'#ffaa00','Medium':'#ffdd00','Low':'#00cc66'},
                         height=280)
        fig_sev.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a", font_color="#00cc66")
        st.plotly_chart(fig_sev, use_container_width=True)
    
    with col_right:
        fig_pie = px.pie(df.head(15), names='severity', title="Severity Breakdown",
                         color_discrete_map={'Critical':'#ff3333','High':'#ffaa00','Medium':'#ffdd00','Low':'#00cc66'},
                         height=280)
        fig_pie.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a", font_color="#00cc66")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.subheader("Latest CVEs")
    st.dataframe(df[['id', 'cvss', 'summary']].head(10), use_container_width=True, height=300)
else:
    st.info("Click 'Refresh Live CVE Data' to load current worldwide vulnerabilities.")

# Ransomware
st.subheader("Top 5 Active Ransomware Groups (Feb 2026)")
st.dataframe(pd.DataFrame([
    {"Group": "Qilin", "Activity": "Very High", "Detail": "Dominant RaaS in healthcare/government. Double extortion standard."},
    {"Group": "Akira", "Activity": "High", "Detail": "Strong Linux/VMware encryption. Rapid victim publication."},
    {"Group": "LockBit", "Activity": "High", "Detail": "Resilient after disruptions. Aggressive recruitment."},
    {"Group": "Play", "Activity": "Medium-High", "Detail": "Retail & manufacturing targets. Heavy data exfiltration."},
    {"Group": "INC", "Activity": "Medium", "Detail": "Emerging group targeting legal/professional services."}
]), use_container_width=True, height=220)

# Malware
st.subheader("Top 5 Active Malware Families")
st.dataframe(pd.DataFrame([
    {"Family": "Lumma Stealer", "Type": "Infostealer", "Detail": "Leading credential and crypto stealer in 2026 campaigns."},
    {"Family": "AsyncRAT", "Type": "RAT", "Detail": "Widely used for initial access and persistence."},
    {"Family": "XWorm", "Type": "Loader/RAT", "Detail": "Multi-platform with strong evasion."},
    {"Family": "RedLine", "Type": "Stealer", "Detail": "Persistent stealer sold on underground markets."},
    {"Family": "Atomic Stealer", "Type": "macOS Stealer", "Detail": "Growing threat targeting macOS credentials and wallets."}
]), use_container_width=True, height=220)

# Phishing
st.subheader("Top 5 Active Phishing Threats")
st.dataframe(pd.DataFrame([
    {"Campaign": "Business Email Compromise (BEC)", "Target": "Finance & Executives", "Detail": "Highly targeted attacks impersonating CEOs and vendors."},
    {"Campaign": "Microsoft 365 Phishing", "Target": "Corporate users", "Detail": "Fake login pages and MFA bypass attempts surging."},
    {"Campaign": "Invoice & Payment Fraud", "Target": "Accounting teams", "Detail": "Fake invoices with urgent payment requests."},
    {"Campaign": "Credential Harvesting via SMS", "Target": "General public", "Detail": "Smishing campaigns combined with malicious links."},
    {"Campaign": "Supply Chain Phishing", "Target": "IT & Vendors", "Detail": "Compromised vendor emails used to attack customers."}
]), use_container_width=True, height=220)

# APT
st.subheader("Top 5 Notable APT Groups")
st.dataframe(pd.DataFrame([
    {"Group": "Lazarus (North Korea)", "Activity": "High", "Detail": "Financial theft and espionage operations."},
    {"Group": "Volt Typhoon (China)", "Activity": "High", "Detail": "Critical infrastructure pre-positioning."},
    {"Group": "Mustang Panda (China)", "Activity": "Medium-High", "Detail": "Espionage against NGOs and governments."},
    {"Group": "APT29 (Russia)", "Activity": "Medium", "Detail": "Cloud compromise and diplomatic targeting."},
    {"Group": "Salt Typhoon (China)", "Activity": "Rising", "Detail": "Telecom and ISP infrastructure attacks."}
]), use_container_width=True, height=220)

# Threat Distribution Pie
st.subheader("Current Threat Distribution")
threat_data = pd.DataFrame({
    "Type": ["Ransomware", "Infostealer", "APT", "Phishing"],
    "Count": [52, 38, 21, 29]
})
fig_pie = px.pie(threat_data, names="Type", values="Count", title="Threat Mix", height=340)
fig_pie.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a", font_color="#00cc66")
st.plotly_chart(fig_pie, use_container_width=True)

# Scan History
if st.session_state.scan_history:
    st.subheader("Scan History")
    st.dataframe(pd.DataFrame(st.session_state.scan_history), use_container_width=True)

# Export
if st.button("Export Full Threat Report"):
    if st.session_state.scan_history:
        df = pd.DataFrame(st.session_state.scan_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "threat_report.csv", "text/csv")
    else:
        st.info("No scans recorded yet.")
