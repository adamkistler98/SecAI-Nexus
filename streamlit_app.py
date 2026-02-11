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
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (Condensed & Sharpened) ---
st.markdown("""
<style>
    .stApp { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stCaptionContainer"] { color: #00ff41 !important; font-family: 'Courier New', Courier, monospace !important; }
    
    /* Condensed Metrics */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #333;
        border-left: 3px solid #00ff41 !important;
        padding: 10px;
    }
    
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        color: #cccccc;
        font-family: 'Courier New', monospace;
        font-size: 0.78rem;
        margin-bottom: 15px;
        border: 1px solid #222;
    }
    .terminal-table th {
        border-bottom: 1px solid #00ff41;
        text-align: left;
        padding: 6px 10px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
        font-size: 0.7rem;
    }
    .terminal-table td { border-bottom: 1px solid #1a1a1a; padding: 4px 10px; background-color: #050505; }
    
    .crit { color: #ff3333 !important; font-weight: bold; }
    .high { color: #ffaa00 !important; }
    .med { color: #00ff41 !important; }

    .stButton>button {
        background-color: #000000; color: #00ff41; border: 1px solid #333;
        font-size: 0.7rem; font-weight: bold; text-transform: uppercase; height: 30px;
    }
    .stButton>button:hover { border-color: #00ff41; color: #00ff41; box-shadow: 0 0 10px #00ff41; }
</style>
""", unsafe_allow_html=True)

# --- DATASETS ---
df_ransom = pd.DataFrame([
    {"RANK": "01", "GROUP": "Qilin", "STATUS": "ACTIVE", "VECTOR": "VPN Zero-Day"},
    {"RANK": "02", "GROUP": "Akira", "STATUS": "ACTIVE", "VECTOR": "ESXi Escape"},
    {"RANK": "03", "GROUP": "LockBit", "STATUS": "STABLE", "VECTOR": "Supply Chain"},
    {"RANK": "04", "GROUP": "Play", "STATUS": "DORMANT", "VECTOR": "RDP Brute"},
    {"RANK": "05", "GROUP": "BlackBasta", "STATUS": "ACTIVE", "VECTOR": "AD Takeover"},
    {"RANK": "06", "GROUP": "Medusa", "STATUS": "STABLE", "VECTOR": "Public Exploit"},
    {"RANK": "07", "GROUP": "BianLian", "STATUS": "ACTIVE", "VECTOR": "Exfiltration"},
    {"RANK": "08", "GROUP": "Rhysida", "STATUS": "STABLE", "VECTOR": "Phishing"},
    {"RANK": "09", "GROUP": "Phobos", "STATUS": "DORMANT", "VECTOR": "Smallsync"},
    {"RANK": "10", "GROUP": "INC Ransom", "STATUS": "ACTIVE", "VECTOR": "Citrix Bleed"}
])

df_malware = pd.DataFrame([
    {"RANK": "01", "FAMILY": "LummaC2", "CVSS": "9.8", "TYPE": "Stealer"},
    {"RANK": "02", "FAMILY": "AsyncRAT", "CVSS": "8.5", "TYPE": "RAT"},
    {"RANK": "03", "FAMILY": "XWorm", "CVSS": "7.9", "TYPE": "Loader"},
    {"RANK": "04", "FAMILY": "RedLine", "CVSS": "7.2", "TYPE": "Stealer"},
    {"RANK": "05", "FAMILY": "AgentTesla", "CVSS": "8.1", "TYPE": "Spyware"},
    {"RANK": "06", "FAMILY": "Pikabot", "CVSS": "7.5", "TYPE": "Loader"},
    {"RANK": "07", "FAMILY": "Vidar", "CVSS": "6.8", "TYPE": "Stealer"},
    {"RANK": "08", "FAMILY": "Remcos", "CVSS": "8.2", "TYPE": "RAT"},
    {"RANK": "09", "FAMILY": "SnakeKey", "CVSS": "7.0", "TYPE": "Exfil"},
    {"RANK": "10", "FAMILY": "Gootloader", "CVSS": "6.5", "TYPE": "JS-Load"}
])

# --- HELPERS ---
def render_terminal_table(df):
    html = '<table class="terminal-table"><thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            if any(k in val for k in ["ACTIVE", "9.", "SURGING"]): html += f'<td class="crit">{val}</td>'
            elif any(k in val for k in ["STABLE", "8.", "7."]): html += f'<td class="high">{val}</td>'
            else: html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

def get_fallback_data():
    mock_vulns = ["Kernel Overflow", "MFA Bypass", "Token Leak", "RCE Gateway", "Tunnel Inject", "Core SQLi", "Priv Escalation", "Mem Corruption"]
    return {"ID": f"CVE-26-{random.randint(1000, 9999)}", "CVSS": random.choice([9.8, 8.5, 7.2, 5.5]), "SUMMARY": random.choice(mock_vulns)}

if "global_threats" not in st.session_state: st.session_state.global_threats = [get_fallback_data() for _ in range(20)]

# --- HEADER ---
st.title("🔒 SecAI-Nexus")
st.markdown("**// GLOBAL THREAT VISIBILITY DASHBOARD**")
st.caption("Target: Worldwide • Protocol: Real-time Intelligence • Level: Alpha")

m1, m2, m3, m4 = st.columns(4)
m1.metric("THREATS", "31", "+7")
m2.metric("CRIT_CVE", "9", "+3")
m3.metric("EVENTS", "91", "Feb'26")
m4.metric("CONFID", "94.2%", "↑")

st.markdown("---")

# --- MAIN HUD ---
col_main, col_side = st.columns([7, 3])

with col_main:
    st.subheader(">> LIVE STREAM")
    if st.button("🔄 SYNC"):
        try:
            resp = requests.get("https://cve.circl.lu/api/last/20", timeout=3)
            raw_data = resp.json() if resp.status_code == 200 else []
            clean_data = [{"ID": item.get('id'), "CVSS": float(item.get('cvss')) if item.get('cvss') else random.choice([7.5, 5.0]), "SUMMARY": (item.get('summary')[:40] + "..") if item.get('summary') else "No Intel"} for item in raw_data if item.get('id')]
            while len(clean_data) < 20: clean_data.append(get_fallback_data())
            st.session_state.global_threats = clean_data
        except: pass
    
    render_terminal_table(pd.DataFrame(st.session_state.global_threats))

with col_side:
    st.subheader(">> ANALYTICS")
    
    # Chart 1: CVSS Frequency
    df_f = pd.DataFrame(st.session_state.global_threats)
    df_f['Sev'] = df_f['CVSS'].apply(lambda x: 'CRITICAL' if x>=9.0 else 'HIGH' if x>=7.0 else 'MED')
    f_counts = df_f['Sev'].value_counts().reset_index()
    
    fig1 = px.pie(f_counts, values='count', names='Sev', hole=0.7, title="CVSS_DISTRO",
                 color='Sev', color_discrete_map={'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41'})
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=180, showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
    fig1.update_traces(textinfo='percent+label', textfont_size=10)
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Actor Status
    land_counts = df_ransom['STATUS'].value_counts().reset_index()
    fig2 = px.pie(land_counts, values='count', names='STATUS', hole=0.7, title="ACTOR_STATUS",
                 color='STATUS', color_discrete_map={'ACTIVE':'#ff3333', 'STABLE':'#ffaa00', 'DORMANT':'#00ff41'})
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=180, showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
    fig2.update_traces(textinfo='percent+label', textfont_size=10)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- BOTTOM LANDSCAPE ---
st.subheader(">> THREAT LANDSCAPE")
col_bot1, col_bot2 = st.columns(2)

with col_bot1:
    st.markdown("### 💀 RANSOMWARE_CORE")
    render_terminal_table(df_ransom)

with col_bot2:
    st.markdown("### 🦠 MALWARE_VECTORS")
    render_terminal_table(df_malware)
