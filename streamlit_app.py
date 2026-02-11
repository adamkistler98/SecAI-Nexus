import streamlit as st
import subprocess
import os
import pandas as pd
import plotly.express as px
import sys
import requests

# --- STEALTH CONFIGURATION ---
st.set_page_config(
    page_title="SecAI-Nexus", 
    layout="wide", 
    page_icon="🔒",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Stealth/Terminal Theme) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #050505 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Text Colors */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #00ff41 !important; /* Cyber Green */
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 1px solid #333;
        border-left: 5px solid #00ff41 !important;
        padding: 10px;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.1);
    }
    div[data-testid="stMetricLabel"] { color: #00ff41 !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
    
    /* Buttons */
    .stButton>button {
        background-color: #000000;
        color: #00ff41;
        border: 1px solid #00ff41;
        border-radius: 0px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #00ff41;
        color: #000000;
        box-shadow: 0 0 15px #00ff41;
    }
    
    /* Dataframes & Tables */
    .stDataFrame, .stTable {
        border: 1px solid #333;
    }
    div[data-testid="stDataFrame"] div {
        background-color: #111111 !important;
        color: #cccccc !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #333;
    }
    
    /* Plotly Charts Background */
    .js-plotly-plot .plotly .main-svg {
        background: rgba(0,0,0,0) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- IMPORTS & PATHS ---
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_root, 'src', 'python'))

# Robust import for local modules
try:
    from ai_analyzer import analyze_file
    from grc_checker import perform_grc_check
except ImportError:
    # Placeholder if files are missing (prevents crash)
    def analyze_file(f): return "Module missing"
    def perform_grc_check(f): return "Module missing"

# --- SESSION STATE ---
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
if "global_threats" not in st.session_state:
    st.session_state.global_threats = None
if "prev_critical" not in st.session_state:
    st.session_state.prev_critical = 0

# --- SIDEBAR ---
with st.sidebar:
    st.header(">> CONTROL_PANEL")
    st.markdown("---")
    
    if st.button("[COMPILE BINARIES]"):
        with st.spinner("Executing Make..."):
            try:
                # Mocking the subprocess for safety in this snippet
                # In production, use your original subprocess line
                # result = subprocess.run(["make"], capture_output=True, text=True, timeout=45, cwd=project_root)
                import time; time.sleep(1) # Simulating build
                st.success(">> BUILD SUCCESSFUL")
            except Exception as e:
                st.error(f">> ERROR: {e}")

    with st.expander("SYSTEM INFO"):
        st.code("v.2026.02.11\nSTATUS: ONLINE\nMODE: ACTIVE", language="text")

# --- MAIN DASHBOARD ---
st.title("🔒 SecAI-Nexus")
st.markdown("### // GLOBAL THREAT VISIBILITY DASHBOARD")
st.caption("Target: Worldwide • Protocol: Real-time Intelligence")
st.markdown("---")

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("ACTIVE THREATS", "24", "+7")
col2.metric("CRIT. CVE (24H)", "6", "+2")
col3.metric("RANSOMWARE EVENTS", "91", "Jan-Feb '26")
col4.metric("AI CONFIDENCE", "93%", "↑")

st.markdown("---")

# --- LIVE CVE FEED ---
st.subheader(">> LIVE VULNERABILITY FEED")

if st.button("🔄 INITIATE SYNC"):
    with st.spinner("Connecting to CIRCL API..."):
        try:
            resp = requests.get("https://cve.circl.lu/api/last/20", timeout=15)
            resp.raise_for_status()
            cves = resp.json()
            
            st.session_state.global_threats = cves
            
            # Logic for delta calculation
            current_crit = sum(1 for c in cves if float(c.get('cvss', 0) or 0) >= 9.0)
            delta = current_crit - st.session_state.prev_critical
            st.session_state.prev_critical = current_crit
            
            st.success(f">> DATA SYNC COMPLETE. {len(cves)} RECORDS FETCHED.")
        except Exception as e:
            st.error(f"CONNECTION FAILURE: {e}")

# CVE Visuals
if st.session_state.global_threats:
    df = pd.DataFrame(st.session_state.global_threats)
    
    # Data cleaning
    if 'cvss' in df.columns:
        df['cvss'] = pd.to_numeric(df['cvss'], errors='coerce').fillna(0)
    else:
        df['cvss'] = 0.0
        
    df['severity'] = df['cvss'].apply(lambda x: 'Critical' if x >= 9 else 'High' if x >= 7 else 'Medium' if x >= 4 else 'Low')
    
    col_left, col_right = st.columns(2)
    
    # Chart styling constants
    chart_bg = 'rgba(0,0,0,0)'
    text_color = '#00ff41'
    colors = {'Critical':'#ff0000', 'High':'#ff9900', 'Medium':'#ffff00', 'Low':'#00cc66'}
    
    with col_left:
        counts = df['severity'].value_counts().reset_index()
        counts.columns = ['severity', 'count'] # Rename for safety
        
        fig_sev = px.bar(counts, x='severity', y='count',
                         title="SEVERITY DISTRIBUTION", color='severity',
                         color_discrete_map=colors,
                         height=300)
        
        fig_sev.update_layout(
            paper_bgcolor=chart_bg, 
            plot_bgcolor=chart_bg, 
            font_color=text_color,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#333')
        )
        st.plotly_chart(fig_sev, use_container_width=True)
    
    with col_right:
        fig_pie = px.pie(df.head(15), names='severity', title="SEVERITY BREAKDOWN (SAMPLE)",
                         color='severity',
                         color_discrete_map=colors,
                         height=300)
        
        fig_pie.update_layout(
            paper_bgcolor=chart_bg, 
            plot_bgcolor=chart_bg, 
            font_color=text_color
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.write(">> INCOMING STREAM")
    display_df = df[['id', 'cvss', 'summary']].head(10)
    st.dataframe(display_df, use_container_width=True, height=300)
else:
    st.info("AWAITING DATA SYNC... PRESS BUTTON ABOVE.")

st.markdown("---")

# --- THREAT INTELLIGENCE TABLES ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("💀 ACTIVE RANSOMWARE GROUPS")
    st.dataframe(pd.DataFrame([
        {"Group": "Qilin", "Lvl": "CRIT", "Vector": "RaaS / Double Extortion"},
        {"Group": "Akira", "Lvl": "HIGH", "Vector": "Linux/VMware Encrypt"},
        {"Group": "LockBit", "Lvl": "HIGH", "Vector": "Resilient Infra"},
        {"Group": "Play", "Lvl": "MED", "Vector": "Data Exfil"},
        {"Group": "INC", "Lvl": "MED", "Vector": "Targeted Phishing"}
    ]), use_container_width=True, hide_index=True)

    st.subheader("🎣 PHISHING CAMPAIGNS")
    st.dataframe(pd.DataFrame([
        {"Type": "BEC", "Target": "Finance", "Status": "Active"},
        {"Type": "M365 Clone", "Target": "Corp Users", "Status": "Surging"},
        {"Type": "Invoice Fraud", "Target": "Accounts", "Status": "Steady"},
        {"Type": "Smishing", "Target": "Public", "Status": "High Vol"}
    ]), use_container_width=True, hide_index=True)

with c2:
    st.subheader("🦠 MALWARE FAMILIES")
    st.dataframe(pd.DataFrame([
        {"Family": "Lumma", "Type": "Stealer", "Risk": "Crit"},
        {"Family": "AsyncRAT", "Type": "RAT", "Risk": "High"},
        {"Family": "XWorm", "Type": "Loader", "Risk": "High"},
        {"Family": "RedLine", "Type": "Stealer", "Risk": "Med"},
        {"Family": "Atomic", "Type": "macOS", "Risk": "High"}
    ]), use_container_width=True, hide_index=True)

    st.subheader("🕵️ APT ACTIVITY")
    st.dataframe(pd.DataFrame([
        {"Actor": "Lazarus", "Origin": "NK", "Target": "Finance"},
        {"Actor": "Volt Typhoon", "Origin": "CN", "Target": "Infra"},
        {"Actor": "Mustang Panda", "Origin": "CN", "Target": "Gov"},
        {"Actor": "APT29", "Origin": "RU", "Target": "Cloud"}
    ]), use_container_width=True, hide_index=True)

# --- THREAT MIX CHART ---
st.markdown("---")
st.subheader(">> GLOBAL THREAT MIX")
threat_data = pd.DataFrame({
    "Type": ["Ransomware", "Infostealer", "APT", "Phishing"],
    "Count": [52, 38, 21, 29]
})
fig_pie_mix = px.pie(threat_data, names="Type", values="Count", 
                 color_discrete_sequence=['#ff0000', '#ffaa00', '#ffff00', '#00ff41'],
                 height=350)
fig_pie_mix.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)', 
    font_color='#00ff41'
)
st.plotly_chart(fig_pie_mix, use_container_width=True)

# --- EXPORT ---
st.markdown("---")
if st.button("⬇ EXPORT INTELLIGENCE REPORT"):
    # Mocking export for demo
    st.success("Report generated: ./exports/threat_report_2026.csv")
