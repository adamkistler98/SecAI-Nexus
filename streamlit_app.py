This is a significant upgrade. I have:

1. **Added "Deep Dive" Details:** I expanded the threat tables to include specific attack vectors (e.g., "VPN Zero-day," "MFA Bypass") to give it that "Intel Analyst" feel.
2. **Fixed the "Squashed" Text:** I rewrote the CSS for the tables to force proper padding and spacing, so "ID" and "CVSS" won't smash together anymore.
3. **Cleaner Layout:** I separated the "Live Feed" and "Threat Intel" into distinct, visually separated zones with clear headers.

Here is the polished **SecAI-Nexus v2.0** code:

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import random
from datetime import datetime

# --- STEALTH CONFIGURATION ---
st.set_page_config(
    page_title="SecAI-Nexus", 
    layout="wide", 
    page_icon="🔒",
    initial_sidebar_state="collapsed" # Collapsed by default for cleaner look
)

# --- CUSTOM CSS (Stealth/Terminal Theme) ---
st.markdown("""
<style>
    /* Main Background - Deep Void Black */
    .stApp {
        background-color: #050505 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Text Colors - Cyber Green */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stCaptionContainer"] {
        color: #00ff41 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    
    /* Metric Cards - HUD Style */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #333;
        border-left: 4px solid #00ff41 !important;
        padding: 15px;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.05);
    }
    div[data-testid="stMetricLabel"] { color: #00ff41 !important; font-size: 0.9rem !important; }
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-weight: bold !important; }
    div[data-testid="stMetricDelta"] { color: #cccccc !important; }
    
    /* Terminal Tables - The Fix for "Squashed" Text */
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        color: #cccccc;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    .terminal-table th {
        border-bottom: 2px solid #00ff41;
        text-align: left;
        padding: 12px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .terminal-table td {
        border-bottom: 1px solid #222;
        padding: 10px 12px;
        background-color: #050505;
    }
    .terminal-table tr:hover td {
        background-color: #1a1a1a;
        color: #fff;
        cursor: crosshair;
    }
    
    /* Critical Severity Highlight */
    .crit { color: #ff3333 !important; font-weight: bold; }
    .high { color: #ffaa00 !important; }
    
    /* Buttons */
    .stButton>button {
        background-color: #000000;
        color: #00ff41;
        border: 1px solid #00ff41;
        font-weight: bold;
        text-transform: uppercase;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00ff41;
        color: #000000;
        box-shadow: 0 0 15px #00ff41;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER: RENDER TABLE ---
def render_terminal_table(df):
    """Renders a specific HTML table with class 'terminal-table'"""
    html = '<table class="terminal-table">'
    html += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead>'
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            # Auto-color severity
            if val in ["CRITICAL", "9.8", "9.5"]:
                html += f'<td class="crit">{val}</td>'
            elif val in ["HIGH", "8.5", "7.9"]:
                html += f'<td class="high">{val}</td>'
            else:
                html += f'<td>{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

# --- SESSION STATE ---
if "global_threats" not in st.session_state:
    st.session_state.global_threats = []

# --- HEADER & METRICS ---
st.title("🔒 SecAI-Nexus")
st.markdown("**// GLOBAL THREAT VISIBILITY DASHBOARD**")
st.caption("Target: Worldwide • Protocol: Real-time Intelligence • Level: Classified")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
m1.metric("ACTIVE THREATS", "31", "+7")
m2.metric("CRIT. CVE (24H)", "9", "+3")
m3.metric("RANSOMWARE EVENTS", "91", "Feb '26")
m4.metric("AI CONFIDENCE", "94.2%", "↑")

st.markdown("---")

# --- LIVE FEED & CHARTS ---
c_feed, c_viz = st.columns([4, 3])

with c_feed:
    st.subheader(">> LIVE VULNERABILITY STREAM")
    col_btn, col_txt = st.columns([1, 3])
    with col_btn:
        if st.button("🔄 SYNC FEED"):
            with st.spinner("ESTABLISHING HANDSHAKE..."):
                try:
                    # Fetch real data
                    resp = requests.get("https://cve.circl.lu/api/last/10", timeout=5)
                    raw_data = resp.json()
                    
                    # Process for display
                    clean_data = []
                    for item in raw_data:
                        # Simulation logic for demo purposes (since real recent CVEs often lack scores)
                        sim_score = random.choice([9.8, 8.5, 7.2, 5.5, 4.0])
                        
                        clean_data.append({
                            "ID": item.get('id'),
                            "CVSS": item.get('cvss') if item.get('cvss') else sim_score,
                            "SUMMARY": (item.get('summary', 'No Data')[:75] + "...")
                        })
                    st.session_state.global_threats = clean_data
                except:
                    st.error("CONNECTION FAILED")

    if st.session_state.global_threats:
        df_live = pd.DataFrame(st.session_state.global_threats)
        render_terminal_table(df_live)
    else:
        st.info("AWAITING SYNC... PRESS BUTTON TO CONNECT.")

with c_viz:
    st.subheader(">> THREAT SEVERITY MIX")
    if st.session_state.global_threats:
        df = pd.DataFrame(st.session_state.global_threats)
        df['Severity'] = df['CVSS'].apply(lambda x: 'CRITICAL' if float(x)>=9 else 'HIGH' if float(x)>=7 else 'MED')
        
        counts = df['Severity'].value_counts().reset_index()
        counts.columns = ['Severity', 'Count']
        
        fig = px.pie(counts, values='Count', names='Severity', hole=0.6,
                     color='Severity',
                     color_discrete_map={'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41'})
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#00ff41',
            showlegend=True,
            margin=dict(t=0, b=0, l=0, r=0),
            height=250
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("[NO DATA VISUALIZED]")

st.markdown("---")

# --- DETAILED THREAT INTEL ---
st.subheader(">> ACTIVE THREAT LANDSCAPE (FEB 2026)")

col_row1_a, col_row1_b = st.columns(2)

with col_row1_a:
    st.markdown("### 💀 RANSOMWARE ACTORS")
    df_ransom = pd.DataFrame([
        {"GROUP": "Qilin", "LEVEL": "CRITICAL", "TARGET": "Healthcare", "VECTOR": "VPN Zero-Day"},
        {"GROUP": "Akira", "LEVEL": "HIGH", "TARGET": "ESXi Servers", "VECTOR": "Hypervisor Escape"},
        {"GROUP": "LockBit", "LEVEL": "HIGH", "TARGET": "Manufacturing", "VECTOR": "Supply Chain"},
        {"GROUP": "Play", "LEVEL": "MEDIUM", "TARGET": "Retail/POS", "VECTOR": "Phishing"}
    ])
    render_terminal_table(df_ransom)

with col_row1_b:
    st.markdown("### 🦠 MALWARE SIGNATURES")
    df_malware = pd.DataFrame([
        {"FAMILY": "LummaC2", "TYPE": "Infostealer", "RISK": "9.8", "BEHAVIOR": "Cookie/Session Theft"},
        {"FAMILY": "AsyncRAT", "TYPE": "RAT", "RISK": "8.5", "BEHAVIOR": "Keylogging/C2"},
        {"FAMILY": "XWorm", "TYPE": "Loader", "RISK": "7.9", "BEHAVIOR": "USB Propagation"},
        {"FAMILY": "RedLine", "TYPE": "Stealer", "RISK": "7.2", "BEHAVIOR": "Browser Dump"}
    ])
    render_terminal_table(df_malware)

col_row2_a, col_row2_b = st.columns(2)

with col_row2_a:
    st.markdown("### 🎣 PHISHING VECTORS")
    df_phish = pd.DataFrame([
        {"TYPE": "BEC", "STATUS": "ACTIVE", "TARGET": "C-Suite", "METHOD": "Deepfake Audio"},
        {"TYPE": "QR-Phish", "STATUS": "SURGING", "TARGET": "Employees", "METHOD": "Malicious 2FA"},
        {"TYPE": "M365", "STATUS": "HIGH", "TARGET": "Cloud", "METHOD": "Token Replay"}
    ])
    render_terminal_table(df_phish)

with col_row2_b:
    st.markdown("### 🕵️ APT TRACKING")
    df_apt = pd.DataFrame([
        {"ACTOR": "Volt Typhoon", "ORIGIN": "CN", "TARGET": "Infra", "GOAL": "Pre-positioning"},
        {"ACTOR": "Lazarus", "ORIGIN": "NK", "TARGET": "DeFi", "GOAL": "Fund Theft"},
        {"ACTOR": "APT29", "ORIGIN": "RU", "TARGET": "Gov/Cloud", "GOAL": "Espionage"}
    ])
    render_terminal_table(df_apt)

```
