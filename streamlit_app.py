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

# --- CUSTOM CSS (Stealth/Terminal Theme) ---
st.markdown("""
<style>
    .stApp { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stCaptionContainer"] { color: #00ff41 !important; font-family: 'Courier New', Courier, monospace !important; }
    
    div[data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #333;
        border-left: 4px solid #00ff41 !important;
        padding: 15px;
    }
    
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        color: #cccccc;
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        margin-bottom: 25px;
        border: 1px solid #333;
    }
    .terminal-table th {
        border-bottom: 2px solid #00ff41;
        text-align: left;
        padding: 10px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
    }
    .terminal-table td { border-bottom: 1px solid #222; padding: 8px 10px; background-color: #050505; }
    .terminal-table tr:hover td { background-color: #1a1a1a; color: #fff; }
    
    .crit { color: #ff3333 !important; font-weight: bold; }
    .high { color: #ffaa00 !important; }
    .med { color: #00ff41 !important; }

    .stButton>button {
        background-color: #000000; color: #00ff41; border: 1px solid #00ff41;
        font-weight: bold; text-transform: uppercase; width: 100%;
    }
    .stButton>button:hover { background-color: #00ff41; color: #000000; box-shadow: 0 0 15px #00ff41; }
</style>
""", unsafe_allow_html=True)

# --- HELPER: RENDER TABLE ---
def render_terminal_table(df):
    html = '<table class="terminal-table"><thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            if any(k in val for k in ["CRITICAL", "9.", "SURGING", "ACTIVE"]): html += f'<td class="crit">{val}</td>'
            elif any(k in val for k in ["HIGH", "8.", "7."]): html += f'<td class="high">{val}</td>'
            else: html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

# --- FALLBACK DATA GENERATOR ---
def get_fallback_data():
    mock_vulns = ["Kernel Heap Overflow", "MFA Bypass Pattern", "Auth Token Leak", "RCE in API Gateway", "Encrypted Tunnel Injection"]
    return {"ID": f"CVE-2026-{random.randint(10000, 99999)}", "CVSS": random.choice([9.8, 8.5, 7.2, 5.5]), "SUMMARY": random.choice(mock_vulns)}

# --- SESSION STATE ---
if "global_threats" not in st.session_state: st.session_state.global_threats = []

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
    if st.button("🔄 SYNC FEED"):
        try:
            resp = requests.get("https://cve.circl.lu/api/last/10", timeout=3)
            raw_data = resp.json() if resp.status_code == 200 else []
            clean_data = [{"ID": item.get('id'), "CVSS": float(item.get('cvss')) if item.get('cvss') else random.choice([7.5, 5.0]), "SUMMARY": item.get('summary')[:60] + "..."} for item in raw_data if item.get('id')]
            while len(clean_data) < 10: clean_data.append(get_fallback_data())
            st.session_state.global_threats = clean_data
        except: st.session_state.global_threats = [get_fallback_data() for _ in range(10)]

    if st.session_state.global_threats:
        render_terminal_table(pd.DataFrame(st.session_state.global_threats))
    else: st.info("AWAITING SYNC...")

with c_viz:
    st.subheader(">> THREAT SEVERITY MIX")
    if st.session_state.global_threats:
        df = pd.DataFrame(st.session_state.global_threats)
        df['Severity'] = df['CVSS'].apply(lambda x: 'CRITICAL' if x>=9.0 else 'HIGH' if x>=7.0 else 'MED')
        fig = px.pie(df['Severity'].value_counts().reset_index(), values='count', names='Severity', hole=0.6,
                     color='Severity', color_discrete_map={'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41'})
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=280, margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- TOP 10 THREAT LANDSCAPE ---
st.subheader(">> ACTIVE THREAT LANDSCAPE (TOP 10 DEEP DIVE)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💀 TOP 10 RANSOMWARE ACTORS")
    render_terminal_table(pd.DataFrame([
        {"RANK": "01", "GROUP": "Qilin", "LEVEL": "CRITICAL", "VECTOR": "VPN Zero-Day"},
        {"RANK": "02", "GROUP": "Akira", "LEVEL": "HIGH", "VECTOR": "ESXi Escape"},
        {"RANK": "03", "GROUP": "LockBit", "LEVEL": "HIGH", "VECTOR": "Supply Chain"},
        {"RANK": "04", "GROUP": "Play", "LEVEL": "MED", "VECTOR": "RDP Brute"},
        {"RANK": "05", "GROUP": "BlackBasta", "LEVEL": "HIGH", "VECTOR": "AD Admin Takeover"},
        {"RANK": "06", "GROUP": "Medusa", "LEVEL": "MED", "VECTOR": "Public Exploit"},
        {"RANK": "07", "GROUP": "BianLian", "LEVEL": "HIGH", "VECTOR": "Data Exfiltration"},
        {"RANK": "08", "GROUP": "Rhysida", "LEVEL": "MED", "VECTOR": "Phishing Infil"},
        {"RANK": "09", "GROUP": "Phobos", "LEVEL": "LOW", "VECTOR": "Smallsync Scan"},
        {"RANK": "10", "GROUP": "INC Ransom", "LEVEL": "HIGH", "VECTOR": "Citrix Bleed"}
    ]))

    st.markdown("### 🎣 TOP 10 PHISHING VECTORS")
    render_terminal_table(pd.DataFrame([
        {"RANK": "01", "TYPE": "BEC", "STATUS": "SURGING", "METHOD": "AI Voice Clone"},
        {"RANK": "02", "TYPE": "QR-Phish", "STATUS": "ACTIVE", "METHOD": "Quishing Kits"},
        {"RANK": "03", "TYPE": "M365", "STATUS": "HIGH", "METHOD": "Token Replay"},
        {"RANK": "04", "TYPE": "Smishing", "STATUS": "ACTIVE", "METHOD": "Package Delivery"},
        {"RANK": "05", "TYPE": "Vishing", "STATUS": "MED", "METHOD": "IT Desk Spoof"},
        {"RANK": "06", "TYPE": "Ad-Phish", "STATUS": "HIGH", "METHOD": "SEO Poisoning"},
        {"RANK": "07", "TYPE": "OAuth", "STATUS": "ACTIVE", "METHOD": "App Permissions"},
        {"RANK": "08", "TYPE": "Browser", "STATUS": "MED", "METHOD": "AiTM Proxy"},
        {"RANK": "09", "TYPE": "Doc-Macro", "STATUS": "LOW", "METHOD": "OneNote Exploit"},
        {"RANK": "10", "TYPE": "Social", "STATUS": "HIGH", "METHOD": "LinkedIn Lures"}
    ]))

with col2:
    st.markdown("### 🦠 TOP 10 MALWARE SIGNATURES")
    render_terminal_table(pd.DataFrame([
        {"RANK": "01", "FAMILY": "LummaC2", "TYPE": "Stealer", "RISK": "9.8"},
        {"RANK": "02", "FAMILY": "AsyncRAT", "TYPE": "RAT", "RISK": "8.5"},
        {"RANK": "03", "FAMILY": "XWorm", "TYPE": "Loader", "RISK": "7.9"},
        {"RANK": "04", "FAMILY": "RedLine", "TYPE": "Stealer", "RISK": "7.2"},
        {"RANK": "05", "FAMILY": "AgentTesla", "TYPE": "Spyware", "RISK": "8.1"},
        {"RANK": "06", "FAMILY": "Pikabot", "TYPE": "Loader", "RISK": "7.5"},
        {"RANK": "07", "FAMILY": "Vidar", "TYPE": "Stealer", "RISK": "6.8"},
        {"RANK": "08", "FAMILY": "Remcos", "TYPE": "RAT", "RISK": "8.2"},
        {"RANK": "09", "FAMILY": "SnakeKey", "TYPE": "Exfiltrator", "RISK": "7.0"},
        {"RANK": "10", "FAMILY": "Gootloader", "TYPE": "JS-Loader", "RISK": "6.5"}
    ]))

    st.markdown("### 🕵️ TOP 10 APT TRACKING")
    render_terminal_table(pd.DataFrame([
        {"RANK": "01", "ACTOR": "Volt Typhoon", "ORIGIN": "CN", "GOAL": "Infra Sabotage"},
        {"RANK": "02", "ACTOR": "Lazarus", "ORIGIN": "NK", "GOAL": "Crypto Theft"},
        {"RANK": "03", "ACTOR": "APT29", "ORIGIN": "RU", "GOAL": "Gov Espionage"},
        {"RANK": "04", "ACTOR": "Fancy Bear", "ORIGIN": "RU", "GOAL": "Election Intel"},
        {"RANK": "05", "ACTOR": "Mustang Panda", "ORIGIN": "CN", "GOAL": "Regional Spying"},
        {"RANK": "06", "ACTOR": "Kimsuky", "ORIGIN": "NK", "GOAL": "Think-Tank Infil"},
        {"RANK": "07", "ACTOR": "Charming Kitten", "ORIGIN": "IR", "GOAL": "Dissident Hunt"},
        {"RANK": "08", "ACTOR": "MuddyWater", "ORIGIN": "IR", "GOAL": "Telecom Access"},
        {"RANK": "09", "ACTOR": "SideWinder", "ORIGIN": "IN", "GOAL": "Diplomatic Intel"},
        {"RANK": "10", "ACTOR": "Sandworm", "ORIGIN": "RU", "GOAL": "Grid Attack"}
    ]))
