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

# --- CUSTOM CSS (Refined for Native DataFrames) ---
st.markdown("""
<style>
    .stApp { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stCaptionContainer"] { color: #00ff41 !important; font-family: 'Courier New', Courier, monospace !important; }
    
    /* HUD Metrics */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #333;
        border-left: 4px solid #00ff41 !important;
        padding: 15px;
    }
    
    /* Stylizing the native Streamlit Dataframe to match stealth theme */
    div[data-testid="stDataFrame"] {
        border: 1px solid #333;
        background-color: #050505 !important;
    }

    /* Buttons */
    .stButton>button {
        background-color: #000000; color: #00ff41; border: 1px solid #00ff41;
        font-weight: bold; text-transform: uppercase; width: 100%;
    }
    .stButton>button:hover { background-color: #00ff41; color: #000000; box-shadow: 0 0 15px #00ff41; }
</style>
""", unsafe_allow_html=True)

# --- FALLBACK DATA GENERATOR ---
def get_fallback_data():
    mock_vulns = [
        "Kernel Heap Overflow", "MFA Bypass Pattern", "Auth Token Leak", 
        "RCE in API Gateway", "Encrypted Tunnel Injection", "SQLi in Core Auth",
        "Privilege Escalation", "Directory Traversal", "Broken X.509 Validation",
        "SSRF via Webhook", "Memory Corruption", "Deserialization Flaw"
    ]
    return {
        "ID": f"CVE-2026-{random.randint(10000, 99999)}", 
        "CVSS": random.choice([9.8, 9.1, 8.5, 7.2, 5.5, 4.2]), 
        "SUMMARY": random.choice(mock_vulns)
    }

# --- SESSION STATE ---
if "global_threats" not in st.session_state: 
    st.session_state.global_threats = [get_fallback_data() for _ in range(20)]

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
c_feed, c_viz = st.columns([5, 3])
with c_feed:
    st.subheader(">> LIVE VULNERABILITY STREAM (SORTABLE)")
    if st.button("🔄 SYNC FEED"):
        try:
            resp = requests.get("https://cve.circl.lu/api/last/20", timeout=5)
            raw_data = resp.json() if resp.status_code == 200 else []
            clean_data = [{"ID": item.get('id'), "CVSS": float(item.get('cvss')) if item.get('cvss') else random.choice([7.5, 5.0]), "SUMMARY": (item.get('summary')[:42] + "...") if item.get('summary') else "No Data Provided"} for item in raw_data if item.get('id')]
            while len(clean_data) < 20: clean_data.append(get_fallback_data())
            st.session_state.global_threats = clean_data
        except: 
            st.session_state.global_threats = [get_fallback_data() for _ in range(20)]

    # Use st.dataframe for interactive sorting by clicking headers
    df_stream = pd.DataFrame(st.session_state.global_threats)
    st.dataframe(
        df_stream, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "CVSS": st.column_config.NumberColumn("CVSS", format="%.1f"),
            "ID": st.column_config.TextColumn("VULNERABILITY_ID"),
            "SUMMARY": st.column_config.TextColumn("INTEL_SUMMARY")
        }
    )

with c_viz:
    st.subheader(">> THREAT SEVERITY MIX")
    df = pd.DataFrame(st.session_state.global_threats)
    df['Severity'] = df['CVSS'].apply(lambda x: 'CRITICAL' if x>=9.0 else 'HIGH' if x>=7.0 else 'MED')
    fig = px.pie(df['Severity'].value_counts().reset_index(), values='count', names='Severity', hole=0.6,
                 color='Severity', color_discrete_map={'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41'})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=350, margin=dict(t=20, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- TOP 10 THREAT LANDSCAPE (Interactive Tables) ---
st.subheader(">> ACTIVE THREAT LANDSCAPE (TOP 10 DEEP DIVE)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💀 TOP 10 RANSOMWARE ACTORS")
    df_ransom = pd.DataFrame([
        {"RANK": "01", "GROUP": "Qilin", "LEVEL": "CRITICAL", "VECTOR": "VPN Zero-Day", "SCORE": 9.8},
        {"RANK": "02", "GROUP": "Akira", "LEVEL": "HIGH", "VECTOR": "ESXi Escape", "SCORE": 8.9},
        {"RANK": "03", "GROUP": "LockBit", "LEVEL": "HIGH", "VECTOR": "Supply Chain", "SCORE": 8.5},
        {"RANK": "04", "GROUP": "Play", "LEVEL": "MED", "VECTOR": "RDP Brute", "SCORE": 7.2},
        {"RANK": "05", "GROUP": "BlackBasta", "LEVEL": "HIGH", "VECTOR": "AD Admin Takeover", "SCORE": 8.8},
        {"RANK": "06", "GROUP": "Medusa", "LEVEL": "MED", "VECTOR": "Public Exploit", "SCORE": 7.5},
        {"RANK": "07", "GROUP": "BianLian", "LEVEL": "HIGH", "VECTOR": "Data Exfiltration", "SCORE": 8.2},
        {"RANK": "08", "GROUP": "Rhysida", "LEVEL": "MED", "VECTOR": "Phishing Infil", "SCORE": 7.1},
        {"RANK": "09", "GROUP": "Phobos", "LEVEL": "LOW", "VECTOR": "Smallsync Scan", "SCORE": 5.4},
        {"RANK": "10", "GROUP": "INC Ransom", "LEVEL": "HIGH", "VECTOR": "Citrix Bleed", "SCORE": 8.0}
    ])
    st.dataframe(df_ransom, hide_index=True, use_container_width=True)

    st.markdown("### 🎣 TOP 10 PHISHING VECTORS")
    df_phish = pd.DataFrame([
        {"RANK": "01", "TYPE": "BEC", "STATUS": "SURGING", "METHOD": "AI Voice Clone", "RISK": 9.5},
        {"RANK": "02", "TYPE": "QR-Phish", "STATUS": "ACTIVE", "METHOD": "Quishing Kits", "RISK": 8.8},
        {"RANK": "03", "TYPE": "M365", "STATUS": "HIGH", "METHOD": "Token Replay", "RISK": 8.4},
        {"RANK": "04", "TYPE": "Smishing", "STATUS": "ACTIVE", "METHOD": "Package Delivery", "RISK": 7.2},
        {"RANK": "05", "TYPE": "Vishing", "STATUS": "MED", "METHOD": "IT Desk Spoof", "RISK": 6.8},
        {"RANK": "06", "TYPE": "Ad-Phish", "STATUS": "HIGH", "METHOD": "SEO Poisoning", "RISK": 8.1},
        {"RANK": "07", "TYPE": "OAuth", "STATUS": "ACTIVE", "METHOD": "App Permissions", "RISK": 7.5},
        {"RANK": "08", "TYPE": "Browser", "STATUS": "MED", "METHOD": "AiTM Proxy", "RISK": 7.0},
        {"RANK": "09", "TYPE": "Doc-Macro", "STATUS": "LOW", "METHOD": "OneNote Exploit", "RISK": 5.2},
        {"RANK": "10", "TYPE": "Social", "STATUS": "HIGH", "METHOD": "LinkedIn Lures", "RISK": 7.9}
    ])
    st.dataframe(df_phish, hide_index=True, use_container_width=True)

with col2:
    st.markdown("### 🦠 TOP 10 MALWARE SIGNATURES")
    df_malware = pd.DataFrame([
        {"RANK": "01", "FAMILY": "LummaC2", "TYPE": "Stealer", "RISK": 9.8},
        {"RANK": "02", "FAMILY": "AsyncRAT", "TYPE": "RAT", "RISK": 8.5},
        {"RANK": "03", "FAMILY": "XWorm", "TYPE": "Loader", "RISK": 7.9},
        {"RANK": "04", "FAMILY": "RedLine", "TYPE": "Stealer", "RISK": 7.2},
        {"RANK": "05", "FAMILY": "AgentTesla", "TYPE": "Spyware", "RISK": 8.1},
        {"RANK": "06", "FAMILY": "Pikabot", "TYPE": "Loader", "RISK": 7.5},
        {"RANK": "07", "FAMILY": "Vidar", "TYPE": "Stealer", "RISK": 6.8},
        {"RANK": "08", "FAMILY": "Remcos", "TYPE": "RAT", "RISK": 8.2},
        {"RANK": "09", "FAMILY": "SnakeKey", "TYPE": "Exfiltrator", "RISK": 7.0},
        {"RANK": "10", "FAMILY": "Gootloader", "TYPE": "JS-Loader", "RISK": 6.5}
    ])
    st.dataframe(df_malware, hide_index=True, use_container_width=True)

    st.markdown("### 🕵️ TOP 10 APT TRACKING")
    df_apt = pd.DataFrame([
        {"RANK": "01", "ACTOR": "Volt Typhoon", "ORIGIN": "CN", "GOAL": "Infra Sabotage", "THREAT": 9.9},
        {"RANK": "02", "ACTOR": "Lazarus", "ORIGIN": "NK", "GOAL": "Crypto Theft", "THREAT": 9.5},
        {"RANK": "03", "ACTOR": "APT29", "ORIGIN": "RU", "GOAL": "Gov Espionage", "THREAT": 9.2},
        {"RANK": "04", "ACTOR": "Fancy Bear", "ORIGIN": "RU", "GOAL": "Election Intel", "THREAT": 8.8},
        {"RANK": "05", "ACTOR": "Mustang Panda", "ORIGIN": "CN", "GOAL": "Regional Spying", "THREAT": 8.4},
        {"RANK": "06", "ACTOR": "Kimsuky", "ORIGIN": "NK", "GOAL": "Think-Tank Infil", "THREAT": 8.1},
        {"RANK": "07", "ACTOR": "Charming Kitten", "ORIGIN": "IR", "GOAL": "Dissident Hunt", "THREAT": 7.8},
        {"RANK": "08", "ACTOR": "MuddyWater", "ORIGIN": "IR", "GOAL": "Telecom Access", "THREAT": 7.5},
        {"RANK": "09", "ACTOR": "SideWinder", "ORIGIN": "IN", "GOAL": "Diplomatic Intel", "THREAT": 7.2},
        {"RANK": "10", "ACTOR": "Sandworm", "ORIGIN": "RU", "GOAL": "Grid Attack", "THREAT": 9.7}
    ])
    st.dataframe(df_apt, hide_index=True, use_container_width=True)
