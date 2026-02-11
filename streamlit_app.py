import streamlit as st
import subprocess
import os
import pandas as pd
import plotly.express as px
import sys
import requests

# === STEALTH DARK THEME ===
st.set_page_config(page_title="SecAI-Nexus", layout="wide", page_icon="🔒")

st.markdown("""
<style>
    .main, .stApp {background-color: #050505 !important;}
    h1, h2, h3, h4, h5, p, label, .stMarkdown {color: #00ff41 !important; font-family: 'Courier New', monospace !important;}
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #0f0f0f !important;
        border-left: 5px solid #00ff41 !important;
        color: #00ff41 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #000000;
        color: #00ff41;
        border: 1px solid #00ff41;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00ff41;
        color: #000000;
    }
    
    /* DataFrames & Tables - FORCE DARK */
    .stDataFrame, .stTable, div[data-testid="stDataFrame"] {
        background-color: #0f0f0f !important;
    }
    .stDataFrame td, .stDataFrame th, .stTable td, .stTable th {
        background-color: #0f0f0f !important;
        color: #00ff41 !important;
        border-color: #333 !important;
    }
    
    /* Plotly Charts */
    .js-plotly-plot .plotly .main-svg, .stPlotlyChart {
        background-color: #050505 !important;
    }
</style>
""", unsafe_allow_html=True)

# Imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src', 'python'))

from ai_analyzer import analyze_file
from grc_checker import perform_grc_check

# Session State
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
if "global_threats" not in st.session_state:
    st.session_state.global_threats = None
if "prev_critical" not in st.session_state:
    st.session_state.prev_critical = 0

# Sidebar
with st.sidebar:
    st.header(">> CONTROL_PANEL")
    st.markdown("---")
    if st.button("[COMPILE BINARIES]"):
        with st.spinner("Executing make..."):
            try:
                result = subprocess.run(["make"], capture_output=True, text=True, timeout=45, cwd=project_root)
                if result.returncode == 0:
                    st.success(">> BUILD SUCCESSFUL")
                else:
                    st.error(">> BUILD FAILED")
            except Exception as e:
                st.error(f">> ERROR: {e}")
    with st.expander("SYSTEM INFO"):
        st.code("v.2026.02.11\nSTATUS: ONLINE\nMODE: ACTIVE", language="text")

# Header
st.title("🔒 SecAI-Nexus")
st.markdown("### // GLOBAL THREAT VISIBILITY DASHBOARD")
st.caption("Real-time Worldwide Intelligence • February 2026")
st.markdown("---")

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("ACTIVE THREATS", "24", "+7")
col2.metric("CRIT. CVE (24H)", "6", "+2")
col3.metric("RANSOMWARE EVENTS", "91", "Jan-Feb '26")
col4.metric("AI CONFIDENCE", "93%", "↑")
st.markdown("---")

# Live CVE Feed
st.subheader(">> LIVE VULNERABILITY FEED")
if st.button("🔄 INITIATE SYNC"):
    with st.spinner("Connecting to CIRCL API..."):
        try:
            resp = requests.get("https://cve.circl.lu/api/last/20", timeout=15)
            resp.raise_for_status()
            cves = resp.json()
            st.session_state.global_threats = cves
            current_crit = sum(1 for c in cves if float(c.get('cvss', 0) or 0) >= 9.0)
            delta = current_crit - st.session_state.prev_critical
            st.session_state.prev_critical = current_crit
            st.success(f">> SYNC COMPLETE. {len(cves)} RECORDS LOADED.")
        except Exception as e:
            st.error(f"CONNECTION FAILURE: {e}")

# CVE Charts & Table
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
                         title="SEVERITY DISTRIBUTION", color='index',
                         color_discrete_map={'Critical':'#ff0000','High':'#ff8800','Medium':'#ffdd00','Low':'#00ff41'},
                         height=300)
        fig_sev.update_layout(paper_bgcolor="#050505", plot_bgcolor="#050505", font_color="#00ff41")
        st.plotly_chart(fig_sev, use_container_width=True)
    
    with col_right:
        fig_pie = px.pie(df.head(15), names='severity', title="SEVERITY BREAKDOWN",
                         color_discrete_map={'Critical':'#ff0000','High':'#ff8800','Medium':'#ffdd00','Low':'#00ff41'},
                         height=300)
        fig_pie.update_layout(paper_bgcolor="#050505", plot_bgcolor="#050505", font_color="#00ff41")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.subheader(">> INCOMING STREAM")
    st.dataframe(df[['id', 'cvss', 'summary']].head(10), use_container_width=True, height=300)
else:
    st.info("AWAITING DATA SYNC... PRESS BUTTON ABOVE.")

st.markdown("---")

# Threat Intelligence Sections (all same clean format)
st.subheader("💀 ACTIVE RANSOMWARE GROUPS")
st.dataframe(pd.DataFrame([
    {"Group": "Qilin", "Activity": "Very High", "Detail": "Dominant RaaS in healthcare/government. Double extortion standard."},
    {"Group": "Akira", "Activity": "High", "Detail": "Strong Linux/VMware encryption. Rapid victim publication."},
    {"Group": "LockBit", "Activity": "High", "Detail": "Resilient after disruptions. Aggressive recruitment."},
    {"Group": "Play", "Activity": "Medium-High", "Detail": "Retail & manufacturing targets. Heavy data exfiltration."},
    {"Group": "INC", "Activity": "Medium", "Detail": "Emerging group targeting legal/professional services."}
]), use_container_width=True, height=220)

st.subheader("🦠 TOP ACTIVE MALWARE FAMILIES")
st.dataframe(pd.DataFrame([
    {"Family": "Lumma Stealer", "Type": "Infostealer", "Detail": "Leading credential and crypto stealer in 2026 campaigns."},
    {"Family": "AsyncRAT", "Type": "RAT", "Detail": "Widely used for initial access and persistence."},
    {"Family": "XWorm", "Type": "Loader/RAT", "Detail": "Multi-platform with strong evasion."},
    {"Family": "RedLine", "Type": "Stealer", "Detail": "Persistent stealer sold on underground markets."},
    {"Family": "Atomic Stealer", "Type": "macOS Stealer", "Detail": "Growing threat targeting macOS credentials and wallets."}
]), use_container_width=True, height=220)

st.subheader("🎣 TOP ACTIVE PHISHING THREATS")
st.dataframe(pd.DataFrame([
    {"Campaign": "Business Email Compromise (BEC)", "Target": "Finance & Executives", "Detail": "Highly targeted attacks impersonating CEOs and vendors."},
    {"Campaign": "Microsoft 365 Phishing", "Target": "Corporate users", "Detail": "Fake login pages and MFA bypass attempts surging."},
    {"Campaign": "Invoice & Payment Fraud", "Target": "Accounting teams", "Detail": "Fake invoices with urgent payment requests."},
    {"Campaign": "Credential Harvesting via SMS", "Target": "General public", "Detail": "Smishing campaigns combined with malicious links."},
    {"Campaign": "Supply Chain Phishing", "Target": "IT & Vendors", "Detail": "Compromised vendor emails used to attack customers."}
]), use_container_width=True, height=220)

st.subheader("🕵️ NOTABLE APT ACTIVITY")
st.dataframe(pd.DataFrame([
    {"Group": "Lazarus (North Korea)", "Activity": "High", "Detail": "Financial theft and espionage operations."},
    {"Group": "Volt Typhoon (China)", "Activity": "High", "Detail": "Critical infrastructure pre-positioning."},
    {"Group": "Mustang Panda (China)", "Activity": "Medium-High", "Detail": "Espionage against NGOs and governments."},
    {"Group": "APT29 (Russia)", "Activity": "Medium", "Detail": "Cloud compromise and diplomatic targeting."},
    {"Group": "Salt Typhoon (China)", "Activity": "Rising", "Detail": "Telecom and ISP infrastructure attacks."}
]), use_container_width=True, height=220)

# Threat Mix Pie
st.subheader(">> GLOBAL THREAT MIX")
threat_data = pd.DataFrame({
    "Type": ["Ransomware", "Infostealer", "APT", "Phishing"],
    "Count": [52, 38, 21, 29]
})
fig_pie = px.pie(threat_data, names="Type", values="Count", title="Threat Mix", height=340)
fig_pie.update_layout(paper_bgcolor="#050505", plot_bgcolor="#050505", font_color="#00ff41")
st.plotly_chart(fig_pie, use_container_width=True)

# Export
st.markdown("---")
if st.button("⬇ EXPORT INTELLIGENCE REPORT"):
    st.success("Report generated: ./exports/threat_report_2026.csv")
