import streamlit as st
import subprocess
import tempfile
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import requests

# Stealthy dark theme - clean & readable
st.markdown("""
<style>
    .main {background-color: #0a0a0a; color: #00cc66;}
    .stApp {background-color: #0a0a0a;}
    h1, h2, h3, h4 {color: #00cc66; font-family: monospace;}
    .stMetric {background-color: #1a1a1a; border-left: 4px solid #00cc66;}
    .stButton>button {background-color: #00cc66; color: #000000;}
    .stDataFrame {background-color: #1a1a1a;}
    .css-1d391kg {background-color: #0a0a0a;}
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
        st.write("Single-dashboard threat visibility platform.")
        st.write("Real-time CVE + active ransomware, malware, APT, and phishing intel.")

st.title("🔒 SecAI-Nexus")
st.markdown("**GLOBAL THREAT VISIBILITY DASHBOARD**")
st.caption("Real-time intelligence • February 2026")

# Metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Threats", "24", "+7")
col2.metric("Critical CVEs (24h)", "6", "+2")
col3.metric("Ransomware Claims", "91", "Jan-Feb 2026")
col4.metric("AI Detection", "93%", "↑")

# Live CVE Feed
st.subheader("🌍 Live CVE Feed (Worldwide Recent Vulnerabilities)")
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

if st.session_state.global_threats:
    df = pd.DataFrame(st.session_state.global_threats)
    df['severity'] = df['cvss'].apply(lambda x: 'Critical' if x >= 9 else 'High' if x >= 7 else 'Medium' if x >= 4 else 'Low')
    
    col_left, col_right = st.columns(2)
    with col_left:
        fig_sev = px.bar(df['severity'].value_counts().reset_index(), x='index', y='severity',
                         title="CVE Severity Distribution", color='index',
                         color_discrete_map={'Critical':'#ff3333','High':'#ffaa00','Medium':'#ffdd00','Low':'#00cc66'},
                         height=320)
        st.plotly_chart(fig_sev, use_container_width=True)
    
    with col_right:
        fig_pie = px.pie(df.head(15), names='severity', title="Severity Breakdown",
                         color_discrete_map={'Critical':'#ff3333','High':'#ffaa00','Medium':'#ffdd00','Low':'#00cc66'},
                         height=320)
        fig_pie.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.subheader("Latest CVEs")
    st.dataframe(df[['id', 'cvss', 'summary']].head(10), use_container_width=True)

# Ransomware Section
st.subheader("Top 5 Active Ransomware Groups (Feb 2026)")
ransom_data = pd.DataFrame([
    {"Group": "Qilin", "Activity": "Very High", "Detail": "Dominant RaaS in healthcare and government. Double extortion is standard."},
    {"Group": "Akira", "Activity": "High", "Detail": "Strong Linux and VMware encryption. Rapid victim posting."},
    {"Group": "LockBit", "Activity": "High", "Detail": "Resilient after 2024 disruptions. Aggressive recruitment continues."},
    {"Group": "Play", "Activity": "Medium-High", "Detail": "Focus on retail and manufacturing with heavy data exfiltration."},
    {"Group": "INC", "Activity": "Medium", "Detail": "Emerging group targeting legal and professional services."}
])
st.dataframe(ransom_data, use_container_width=True, height=220)

# Malware Section
st.subheader("Top 5 Active Malware Families")
malware_data = pd.DataFrame([
    {"Family": "Lumma Stealer", "Type": "Infostealer", "Detail": "Leading credential and crypto stealer in 2026 campaigns."},
    {"Family": "AsyncRAT", "Type": "RAT", "Detail": "Widely used for initial access and long-term persistence."},
    {"Family": "XWorm", "Type": "Loader/RAT", "Detail": "Multi-platform with strong evasion capabilities."},
    {"Family": "RedLine", "Type": "Stealer", "Detail": "Persistent stealer still sold heavily on underground markets."},
    {"Family": "Atomic Stealer", "Type": "macOS Stealer", "Detail": "Growing threat targeting macOS credentials and wallets."}
])
st.dataframe(malware_data, use_container_width=True, height=220)

# Phishing Section
st.subheader("Top 5 Active Phishing Threats")
phishing_data = pd.DataFrame([
    {"Campaign": "Business Email Compromise (BEC)", "Target": "Finance & Executives", "Detail": "Highly targeted attacks impersonating CEOs and vendors."},
    {"Campaign": "Microsoft 365 Phishing", "Target": "Corporate users", "Detail": "Fake login pages and MFA bypass attempts surging in 2026."},
    {"Campaign": "Invoice & Payment Fraud", "Target": "Accounting teams", "Detail": "Fake invoices with urgent payment requests."},
    {"Campaign": "Credential Harvesting via SMS", "Target": "General public", "Detail": "Smishing campaigns combined with malicious links."},
    {"Campaign": "Supply Chain Phishing", "Target": "IT & Vendors", "Detail": "Compromised vendor emails used to attack customers."}
])
st.dataframe(phishing_data, use_container_width=True, height=220)

# APT Section
st.subheader("Top 5 Notable APT Groups")
apt_data = pd.DataFrame([
    {"Group": "Lazarus (North Korea)", "Activity": "High", "Detail": "Financial theft and espionage operations."},
    {"Group": "Volt Typhoon (China)", "Activity": "High", "Detail": "Critical infrastructure pre-positioning."},
    {"Group": "Mustang Panda (China)", "Activity": "Medium-High", "Detail": "Espionage against NGOs and governments."},
    {"Group": "APT29 (Russia)", "Activity": "Medium", "Detail": "Cloud compromise and diplomatic targeting."},
    {"Group": "Salt Typhoon (China)", "Activity": "Rising", "Detail": "Telecom and ISP infrastructure attacks."}
])
st.dataframe(apt_data, use_container_width=True, height=220)

# Threat Distribution Pie (improved)
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
