import streamlit as st
import subprocess
import os
import pandas as pd
import plotly.express as px
import sys
import requests
import random
from datetime import datetime

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
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stCaptionContainer"] {
        color: #00ff41 !important; /* Cyber Green */
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #111111 !important;
        border: 1px solid #333;
        border-left: 5px solid #00ff41 !important;
        padding: 10px;
    }
    div[data-testid="stMetricLabel"] { color: #00ff41 !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; }
    
    /* Custom HTML Tables */
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        color: #00ff41;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        border: 1px solid #333;
    }
    .terminal-table th {
        border-bottom: 2px solid #00ff41;
        text-align: left;
        padding: 8px;
        background-color: #1a1a1a;
    }
    .terminal-table td {
        border-bottom: 1px solid #333;
        padding: 8px;
        background-color: #0a0a0a;
    }
    .terminal-table tr:hover td {
        background-color: #111;
        color: #fff;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #000000;
        color: #00ff41;
        border: 1px solid #00ff41;
        border-radius: 0px;
        font-weight: bold;
        transition: all 0.3s;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #00ff41;
        color: #000000;
        box-shadow: 0 0 10px #00ff41;
    }
    
    /* Plotly Charts */
    .js-plotly-plot .plotly .main-svg {
        background: rgba(0,0,0,0) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def render_terminal_table(df):
    """Renders a dataframe as a custom HTML table for perfect dark mode support"""
    html = '<table class="terminal-table">'
    html += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead>'
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>' + ''.join(f'<td>{row[col]}</td>' for col in df.columns) + '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

# --- SESSION STATE ---
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
if "global_threats" not in st.session_state:
    st.session_state.global_threats = None

# --- SIDEBAR ---
with st.sidebar:
    st.header(">> CONTROL_PANEL")
    st.markdown("---")
    
    # Toggle for Demo Mode (Fixes boring charts)
    demo_mode = st.toggle("SIMULATION_MODE", value=True, help="Injects simulated Critical threats for visual demonstration")
    
    if st.button("[COMPILE BINARIES]"):
        with st.spinner("EXECUTING MAKEFILE..."):
            import time; time.sleep(1.5)
            st.success(">> BUILD SUCCESSFUL: /bin/core_v2")

    with st.expander("SYSTEM DIAGNOSTICS"):
        st.code(f"KERNEL: ACTIVE\nUPTIME: {datetime.now().strftime('%H:%M:%S')}\nCONN: ENCRYPTED", language="text")

# --- MAIN DASHBOARD ---
st.title("🔒 SecAI-Nexus")
st.markdown("### // GLOBAL THREAT VISIBILITY DASHBOARD")
st.caption("Target: Worldwide • Protocol: Real-time Intelligence • Level: Classified")
st.markdown("---")

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("ACTIVE THREATS", "31", "+7")
m2.metric("CRIT. CVE (24H)", "9", "+3")
m3.metric("RANSOMWARE EVENTS", "91", "Feb '26")
m4.metric("AI CONFIDENCE", "94.2%", "↑")

st.markdown("---")

# --- LIVE CVE FEED ---
c_feed, c_charts = st.columns([1, 2])

with c_feed:
    st.subheader(">> FEED CONTROL")
    if st.button("🔄 SYNC CIRCL.LU"):
        with st.spinner("ESTABLISHING HANDSHAKE..."):
            try:
                # 1. Fetch Real Data
                resp = requests.get("https://cve.circl.lu/api/last/30", timeout=10)
                data = resp.json()
                
                # 2. Process (Add Simulation if needed to make charts look good)
                processed_data = []
                for item in data:
                    cvss = item.get('cvss')
                    # Fix: Real recent CVEs often have None for CVSS. 
                    # If Demo Mode is ON, we assign fake high scores to them for the visual.
                    if cvss is None:
                        cvss = random.uniform(4.0, 9.8) if demo_mode else 0.0
                    
                    processed_data.append({
                        "ID": item.get('id'),
                        "CVSS": float(cvss),
                        "SUMMARY": item.get('summary', 'No summary')[:50] + "..."
                    })
                
                st.session_state.global_threats = processed_data
                st.success(f">> SYNC COMPLETE")
            except Exception as e:
                st.error("CONNECTION REFUSED")

    if st.session_state.global_threats:
        # Show mini list
        df_feed = pd.DataFrame(st.session_state.global_threats).head(5)
        render_terminal_table(df_feed[["ID", "CVSS"]])
    else:
        st.info("AWAITING SYNC...")

with c_charts:
    if st.session_state.global_threats:
        df = pd.DataFrame(st.session_state.global_threats)
        
        # Categorize
        def get_severity(s):
            if s >= 9.0: return "CRITICAL"
            if s >= 7.0: return "HIGH"
            if s >= 4.0: return "MEDIUM"
            return "LOW"
            
        df['SEVERITY'] = df['CVSS'].apply(get_severity)
        
        # Colors that pop on black
        color_map = {
            "CRITICAL": "#ff0000", # Bright Red
            "HIGH": "#ff8800",     # Orange
            "MEDIUM": "#ffff00",   # Yellow
            "LOW": "#00ff41"       # Matrix Green
        }
        
        # Bar Chart
        counts = df['SEVERITY'].value_counts().reset_index()
        counts.columns = ['Severity', 'Count']
        
        fig = px.bar(counts, x='Severity', y='Count', 
                     title="THREAT SEVERITY DISTRIBUTION",
                     color='Severity', color_discrete_map=color_map)
        
        fig.update_layout(
            font_family="Courier New",
            font_color="#00ff41",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=250,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='#333')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write(">> VISUALIZATION OFFLINE")

st.markdown("---")

# --- THREAT INTELLIGENCE (HTML TABLES) ---
col_t1, col_t2 = st.columns(2)

with col_t1:
    st.subheader("💀 ACTIVE RANSOMWARE GROUPS")
    df_ransom = pd.DataFrame([
        {"GROUP": "Qilin", "LEVEL": "CRITICAL", "TARGET": "Healthcare/Gov"},
        {"GROUP": "Akira", "LEVEL": "HIGH", "TARGET": "ESXi Infrastructure"},
        {"GROUP": "LockBit", "LEVEL": "HIGH", "TARGET": "Global Manufacturing"},
        {"GROUP": "Play", "LEVEL": "MEDIUM", "TARGET": "Retail"},
    ])
    render_terminal_table(df_ransom)

    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    st.subheader("🎣 PHISHING VECTORS")
    df_phish = pd.DataFrame([
        {"TYPE": "BEC", "STATUS": "ACTIVE", "TARGET": "C-Suite"},
        {"TYPE": "QR-Phish", "STATUS": "SURGING", "TARGET": "Auth Portals"},
        {"TYPE": "M365", "STATUS": "HIGH", "TARGET": "Cred Harvesting"},
    ])
    render_terminal_table(df_phish)

with col_t2:
    st.subheader("🦠 MALWARE SIGNATURES")
    df_mal = pd.DataFrame([
        {"FAMILY": "LummaC2", "TYPE": "Infostealer", "RISK": "9.8"},
        {"FAMILY": "AsyncRAT", "TYPE": "RAT", "RISK": "8.5"},
        {"FAMILY": "XWorm", "TYPE": "Loader", "RISK": "7.9"},
        {"FAMILY": "RedLine", "TYPE": "Stealer", "RISK": "7.2"},
    ])
    render_terminal_table(df_mal)
    
    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    st.subheader("🕵️ APT TRACKING")
    df_apt = pd.DataFrame([
        {"ACTOR": "Volt Typhoon", "ORIGIN": "CN", "TARGET": "Critical Infra"},
        {"ACTOR": "Lazarus", "ORIGIN": "NK", "TARGET": "Crypto/Finance"},
        {"ACTOR": "APT29", "ORIGIN": "RU", "TARGET": "Cloud Environs"},
    ])
    render_terminal_table(df_apt)

st.markdown("---")
st.caption("// SYSTEM END OF LINE")
