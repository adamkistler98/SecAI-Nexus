import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import random
from datetime import datetime

# --- STEALTH CONFIGURATION ---
st.set_page_config(
    page_title="SecAI-Nexus GRC", 
    layout="wide", 
    page_icon="🔒",
    initial_sidebar_state="collapsed"
)

# --- ADVANCED GRC CSS ---
st.markdown("""
<style>
    .stApp { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #00ff41 !important; }
    
    /* GRC Risk Banner */
    .grc-banner {
        background-color: #0a0a0a;
        border: 1px solid #222;
        padding: 12px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        border-top: 2px solid #00ff41;
        box-shadow: 0 4px 10px rgba(0, 255, 65, 0.1);
    }

    /* Professional Metric HUD */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #222;
        border-left: 3px solid #00ff41 !important;
    }
    
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        color: #cccccc;
        font-family: 'Courier New', monospace;
        font-size: 0.68rem;
        margin-bottom: 15px;
        border: 1px solid #222;
    }
    .terminal-table th {
        border-bottom: 1px solid #00ff41;
        text-align: left;
        padding: 8px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
    }
    .terminal-table td { border-bottom: 1px solid #1a1a1a; padding: 4px 8px; background-color: #050505; }
    
    /* Risk Matrix Coloring */
    .crit { color: #ff3333 !important; font-weight: bold; background-color: rgba(255, 51, 51, 0.1); }
    .high { color: #ffaa00 !important; }
    .med { color: #00ff41 !important; }
    .mapping { color: #0088ff !important; font-style: italic; } /* Regulatory Mapping Color */

    .stButton>button {
        background-color: #000000; color: #00ff41; border: 1px solid #333;
        font-size: 0.65rem; font-weight: bold; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# --- GRC SYSTEM STATUS ---
st.markdown(f"""
<div class="grc-banner">
    <span>FRAMEWORK_ALIGNMENT: <b>ISO 27001:2022 / SOC2 TYPE II</b></span>
    <span>RESIDUAL_RISK_SCORE: <b style="color:#ffaa00;">HIGH (6.8)</b></span>
    <span>AUDIT_READINESS: <b style="color:#00ff41;">OPTIMIZED</b></span>
    <span>CLOCK: <b>{datetime.now().strftime("%H:%M:%S")} UTC</b></span>
</div>
""", unsafe_allow_html=True)

# --- GRC-CENTRIC DATASETS (20 ENTRIES) ---
def gen_grc_ransom():
    groups = ["Qilin", "Akira", "LockBit", "Play", "BlackBasta", "Medusa", "BianLian", "Rhysida", "Phobos", "INC Ransom"]
    controls = ["A.8.2 (Privilege Management)", "A.5.15 (Access Control)", "A.8.16 (Monitoring)", "A.8.24 (Info Deletion)"]
    return pd.DataFrame([{
        "ACTOR": groups[i % len(groups)], 
        "GRC_POSTURE": random.choice(["UNMITIGATED", "PARTIAL_CONTROL", "MONITORED"]), 
        "REG_MAPPING": random.choice(controls),
        "INHERENT_RISK": random.choice(["CRITICAL", "HIGH"])
    } for i in range(20)])

def gen_grc_malware():
    families = ["LummaC2", "AsyncRAT", "XWorm", "RedLine", "AgentTesla", "Pikabot", "Vidar", "Remcos"]
    return pd.DataFrame([{
        "FAMILY": families[i % len(families)], 
        "CVSS": f"{random.uniform(7.5, 9.9):.1f}", 
        "CONTROL_ID": f"CC{random.randint(1,9)}.{random.randint(1,3)}",
        "IMPACT": "Confidentiality Loss"
    } for i in range(20)])

def gen_grc_phish():
    strategies = ["Awareness (A.7.2)", "Endpoint Prot (A.8.7)", "Network Sec (A.8.20)", "Secure Auth (A.5.17)"]
    return pd.DataFrame([{
        "THREAT": random.choice(["BEC", "QR-Phish", "AiTM"]), 
        "EXPOSURE": random.choice(["IMMINENT", "MITIGATED"]), 
        "GRC_STRATEGY": random.choice(strategies),
        "RESIDUAL_RISK": random.choice(["HIGH", "MED"])
    } for i in range(20)])

def gen_grc_apt():
    return pd.DataFrame([{
        "ACTOR": random.choice(["Volt Typhoon", "Lazarus", "APT29"]), 
        "INTENT": "Exfiltration", 
        "COMPLIANCE_GAP": "Log Retention Flaw",
        "AUDIT_PRIORITY": "LEVEL_1"
    } for i in range(20)])

# --- HELPERS ---
def render_grc_table(df):
    html = '<table class="terminal-table"><thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            if any(k in val for k in ["CRITICAL", "9.", "UNMITIGATED", "IMMINENT", "LEVEL_1"]): html += f'<td class="crit">{val}</td>'
            elif any(k in val for k in ["HIGH", "8.", "PARTIAL", "EXPOSURE"]): html += f'<td class="high">{val}</td>'
            elif "A." in val or "CC" in val: html += f'<td class="mapping">{val}</td>' # Highlight compliance tags
            else: html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

# --- TOP LEVEL METRICS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("NON-COMPLIANCE_ALERTS", "14", "+2")
m2.metric("FAILED_CONTROLS", "3", "DEGRADED")
m3.metric("MEAN_TIME_TO_REMEDY", "4.2 Days", "-10%")
m4.metric("DATA_PRIVACY_SCORE", "91%", "STABLE")

st.markdown("---")

# --- MAIN HUD ---
col_stream, col_grc_side = st.columns([65, 35])

with col_stream:
    st.subheader(">> GRC_AUDIT_LOG: REAL-TIME VULNERABILITY EXPOSURE")
    if st.button("🔄 RE-VALIDATE CONTROLS"):
        resp = requests.get("https://cve.circl.lu/api/last/20", timeout=3)
        raw = resp.json() if resp.status_code == 200 else []
        clean = [{"ID": i.get('id'), "CVSS": float(i.get('cvss') or 5.0), "GRC_IMPACT": i.get('summary')[:45]+".."} for i in raw if i.get('id')]
        while len(clean) < 20: clean.append({"ID": "CVE-2026-PEND", "CVSS": 0.0, "GRC_IMPACT": "Pending Control Validation"})
        st.session_state.grc_stream = clean
    
    if "grc_stream" not in st.session_state: st.session_state.grc_stream = [{"ID": "HANDSHAKE", "CVSS": 0.0, "GRC_IMPACT": "Establishing Integrity..."} for _ in range(20)]
    render_grc_table(pd.DataFrame(st.session_state.grc_stream))

with col_grc_side:
    st.subheader(">> COMPLIANCE_ANALYTICS")
    
    # Chart 1: Control Health (Stacked)
    df_h = pd.DataFrame(st.session_state.grc_stream)
    df_h['Risk'] = df_h['CVSS'].apply(lambda x: 'CRITICAL' if x>=9 else 'HIGH' if x>=7 else 'MED')
    fig1 = px.pie(df_h['Risk'].value_counts().reset_index(), values='count', names='Risk', hole=0.75, title="RESIDUAL_RISK_MIX",
                 color='Risk', color_discrete_map={'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41'})
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=240, showlegend=False, margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Control Remediation Progress
    rem_data = pd.DataFrame({"Status": ["Remediated", "In-Progress", "Overdue"], "Count": [65, 25, 10]})
    fig2 = px.bar(rem_data, x="Status", y="Count", title="CONTROL_REMEDIATION_KPI", color="Status",
                 color_discrete_map={"Remediated": "#00ff41", "In-Progress": "#ffaa00", "Overdue": "#ff3333"})
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=240, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- QUAD GRC LANDSCAPE ---
st.subheader(">> REGULATORY THREAT MAPPING (ISO/SOC2 ALIGNMENT)")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("### 💀 RANSOMWARE_RISK")
    render_grc_table(gen_grc_ransom())

with c2:
    st.markdown("### 🦠 EXPOSURE_MALWARE")
    render_grc_table(gen_grc_malware())

with c3:
    st.markdown("### 🎣 PHISHING_CONTROLS")
    render_grc_table(gen_grc_phish())

with c4:
    st.markdown("### 🕵️ AUDIT_PRIORITY_APT")
    render_grc_table(gen_grc_apt())
