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

# --- CUSTOM CSS (GRC Professional) ---
st.markdown("""
<style>
    .stApp { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stCaptionContainer"] { color: #00ff41 !important; font-family: 'Courier New', Courier, monospace !important; }
    
    /* GRC Status Banner */
    .grc-banner {
        background-color: #0a0a0a;
        border: 1px solid #222;
        padding: 10px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        border-top: 2px solid #00ff41;
    }

    div[data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #222;
        border-left: 3px solid #00ff41 !important;
        padding: 5px 10px;
    }
    
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        color: #cccccc;
        font-family: 'Courier New', monospace;
        font-size: 0.68rem;
        margin-bottom: 10px;
        border: 1px solid #222;
    }
    .terminal-table th {
        border-bottom: 1px solid #00ff41;
        text-align: left;
        padding: 6px 8px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
    }
    .terminal-table td { border-bottom: 1px solid #1a1a1a; padding: 3px 8px; background-color: #050505; }
    
    /* GRC Risk Level Coloring */
    .crit { color: #ff3333 !important; font-weight: bold; } /* Critical Risk */
    .high { color: #ffaa00 !important; }                /* High Exposure */
    .med { color: #00ff41 !important; }                 /* Managed/Baseline */

    .stButton>button {
        background-color: #000000; color: #00ff41; border: 1px solid #333;
        font-size: 0.65rem; font-weight: bold; text-transform: uppercase; height: 25px;
    }
    .stButton>button:hover { border-color: #00ff41; box-shadow: 0 0 8px #00ff41; }
</style>
""", unsafe_allow_html=True)

# --- GRC STATUS BANNER ---
st.markdown(f"""
<div class="grc-banner">
    <span>OPERATIONAL_STATUS: <b>RESILIENT</b></span>
    <span>COMPLIANCE_FRAMEWORK: <b>NIST_CSF_2.0</b></span>
    <span>TIME_STAMP: <b>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC</b></span>
</div>
""", unsafe_allow_html=True)

# --- PROFESSIONAL GRC DATASETS (20 ENTRIES) ---
def gen_ransom_data():
    groups = ["Qilin", "Akira", "LockBit", "Play", "BlackBasta", "Medusa", "BianLian", "Rhysida", "Phobos", "INC Ransom", "Storm-0506", "Cactus", "8Base", "ALPHV", "Hunters", "Fog", "Embargo", "RansomHub", "Dragonforce", "Estate"]
    # Professional GRC Status Terms
    grc_status = ["ACTIVE_THREAT", "PERSISTENT_RISK", "MITIGATED", "MONITORED"]
    return pd.DataFrame([{
        "RANK": f"{i+1:02}", 
        "GROUP": groups[i % len(groups)], 
        "GRC_RISK_POSTURE": random.choice(grc_status), 
        "PRIMARY_VECTOR": "Initial Access via Exploit" if i % 2 == 0 else "Credential Compromise"
    } for i in range(20)])

def gen_malware_data():
    families = ["LummaC2", "AsyncRAT", "XWorm", "RedLine", "AgentTesla", "Pikabot", "Vidar", "Remcos", "SnakeKey", "Gootloader", "Strela", "IcedID", "GuLoader", "Bumblebee", "Amadey", "QuasarRAT", "Warzone", "Sykipot", "Latrodectus", "Meduza"]
    return pd.DataFrame([{
        "RANK": f"{i+1:02}", 
        "FAMILY": families[i % len(families)], 
        "CVSS_SCORE": f"{random.uniform(7.0, 9.9):.1f}", 
        "EXPOSURE_TYPE": "Data Exfiltration" if i % 3 == 0 else "Remote Command & Control"
    } for i in range(20)])

def gen_phish_data():
    types = ["BEC", "QR-Phish", "M365_OAUTH", "SMISHING", "VISHING", "SEO_POISONING", "AiTM_PROXY"]
    readiness = ["IMMINENT_DETECTION", "EVADING_CONTROLS", "BASELINE_THREAT"]
    return pd.DataFrame([{
        "RANK": f"{i+1:02}", 
        "THREAT_CATEGORY": random.choice(types), 
        "CONTROL_STATUS": random.choice(readiness), 
        "MITIGATION_STRATEGY": "MFA_Hardening" if i % 2 == 0 else "User_Awareness_Training"
    } for i in range(20)])

def gen_apt_data():
    actors = ["Volt Typhoon", "Lazarus", "APT29", "Sandworm", "Mustang Panda", "Fancy Bear", "Kimsuky", "Charming Kitten"]
    intent = ["SABOTAGE", "ESPIONAGE", "FINANCIAL_THEFT", "INFRASTRUCTURE_PRE-POSITIONING"]
    return pd.DataFrame([{
        "RANK": f"{i+1:02}", 
        "ACTOR_INTENT": random.choice(intent), 
        "GRC_OPERATIONAL_IMPACT": "HIGH", 
        "ACTOR_ORIGIN": random.choice(["CN", "RU", "NK", "IR"])
    } for i in range(20)])

df_ransom = gen_ransom_data()
df_malware = gen_malware_data()
df_phish = gen_phish_data()
df_apt = gen_apt_data()

# --- HELPERS ---
def render_terminal_table(df):
    html = '<table class="terminal-table"><thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            if any(k in val for k in ["ACTIVE", "9.", "IMMINENT", "SABOTAGE", "HIGH"]): html += f'<td class="crit">{val}</td>'
            elif any(k in val for k in ["PERSISTENT", "8.", "EVADING", "ESPIONAGE"]): html += f'<td class="high">{val}</td>'
            else: html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

if "global_threats" not in st.session_state: 
    st.session_state.global_threats = [{"ID": f"CVE-2026-{random.randint(1000, 9999)}", "CVSS": 9.8, "SUMMARY": "CRITICAL RISK IDENTIFIED"} for _ in range(20)]

# --- HEADER METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("THREAT_EXPOSURE", "31", "+7")
m2.metric("CRITICAL_VULNS", "9", "+3")
m3.metric("SECURITY_INCIDENTS", "91", "Feb'26")
m4.metric("CONTROL_EFFICACY", "94.2%", "↑")

st.markdown("---")

# --- MAIN HUD ---
col_main, col_side = st.columns([7, 3])

with col_main:
    st.subheader(">> REAL-TIME TELEMETRY (GRC_AUDIT_LOG)")
    if st.button("🔄 RE-SCAN INFRASTRUCTURE"):
        try:
            resp = requests.get("https://cve.circl.lu/api/last/20", timeout=3)
            raw_data = resp.json() if resp.status_code == 200 else []
            clean_data = [{"ID": item.get('id'), "CVSS": float(item.get('cvss')) if item.get('cvss') else 5.0, "SUMMARY": (item.get('summary')[:35] + "..") if item.get('summary') else "Intel Pending"} for item in raw_data if item.get('id')]
            while len(clean_data) < 20: clean_data.append({"ID": "THREAT_PENDING", "CVSS": 0.0, "SUMMARY": "Awaiting Telemetry..."})
            st.session_state.global_threats = clean_data
        except: pass
    
    render_terminal_table(pd.DataFrame(st.session_state.global_threats))

with col_side:
    st.subheader(">> RISK_MATURITY_HUD")
    
    # Pie Charts with Scale-Up
    chart_colors = {'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41', 'BASELINE':'#00ff41'}
    
    df_f = pd.DataFrame(st.session_state.global_threats)
    df_f['Sev'] = df_f['CVSS'].apply(lambda x: 'CRITICAL' if float(x)>=9.0 else 'HIGH' if float(x)>=7.0 else 'MED')
    
    fig1 = px.pie(df_f['Sev'].value_counts().reset_index(), values='count', names='Sev', hole=0.7, title="RISK_DISTRIBUTION",
                 color='Sev', color_discrete_map=chart_colors)
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=230, showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
    fig1.update_traces(textinfo='percent+label', textfont_size=10)
    st.plotly_chart(fig1, use_container_width=True)

    # Operational Posture Mix
    all_status = pd.concat([df_ransom['GRC_RISK_POSTURE'], df_phish['CONTROL_STATUS']])
    s_counts = all_status.value_counts().reset_index()
    
    fig2 = px.pie(s_counts, values='count', names='index', hole=0.7, title="OPERATIONAL_POSTURE",
                 color_discrete_sequence=['#ff3333', '#ffaa00', '#00ff41'])
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=230, showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
    fig2.update_traces(textinfo='percent+label', textfont_size=10)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- GRC THREAT LANDSCAPE (QUAD) ---
st.subheader(">> INFRASTRUCTURE RISK LANDSCAPE")
t1, t2, t3, t4 = st.columns(4)

with t1:
    st.markdown("### 💀 RANSOMWARE_RISK")
    render_terminal_table(df_ransom)

with t2:
    st.markdown("### 🦠 MALWARE_EXPOSURE")
    render_terminal_table(df_malware)

with t3:
    st.markdown("### 🎣 PHISHING_VECTORS")
    render_terminal_table(df_phish)

with t4:
    st.markdown("### 🕵️ APT_INTEL")
    render_terminal_table(df_apt)
