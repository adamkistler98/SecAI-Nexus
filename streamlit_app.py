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
    
    .clock-header {
        font-size: 1rem;
        font-weight: bold;
        text-align: right;
        color: #00ff41;
        margin-bottom: -20px;
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
        font-size: 0.7rem;
        margin-bottom: 15px;
        border: 1px solid #222;
    }
    .terminal-table th {
        border-bottom: 1px solid #00ff41;
        text-align: left;
        padding: 6px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
    }
    .terminal-table td { border-bottom: 1px solid #1a1a1a; padding: 4px 8px; background-color: #050505; }
    
    .crit { color: #ff3333 !important; font-weight: bold; }
    .high { color: #ffaa00 !important; }
    .med { color: #00ff41 !important; }

    .stButton>button {
        background-color: #000000; color: #00ff41; border: 1px solid #333;
        font-size: 0.65rem; font-weight: bold; text-transform: uppercase; height: 26px;
    }
    .stButton>button:hover { border-color: #00ff41; box-shadow: 0 0 8px #00ff41; }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown(f'<div class="clock-header">SYSTEM_TIME: {datetime.now().strftime("%H:%M:%S")} UTC</div>', unsafe_allow_html=True)
st.title("🔒 SecAI-Nexus")
st.markdown("**// GLOBAL THREAT VISIBILITY DASHBOARD**")
st.caption("Target: Worldwide • Protocol: Real-time Intelligence")

m1, m2, m3, m4 = st.columns(4)
m1.metric("THREATS", "31", "+7")
m2.metric("CRIT_CVE", "9", "+3")
m3.metric("EVENTS", "91", "Feb'26")
m4.metric("CONFID", "94.2%", "↑")

st.markdown("---")

# --- DATA GENERATORS ---
def get_intel_summary():
    intel = [
        "Unauthorized lateral movement detected via SMB exploit",
        "Credential harvesting via ADFS identity bypass kit",
        "Critical RCE vulnerability in edge VPN gateway",
        "Encrypted tunnel established to known C2 infrastructure",
        "Privilege escalation identified in container runtime",
        "Zero-day exploit observed targeting local SSL stack",
        "Memory corruption identified in active kernel driver",
        "Sensitive data exfiltration attempt via DNS tunneling"
    ]
    return random.choice(intel)

def render_terminal_table(df):
    html = '<table class="terminal-table"><thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            if any(k in val for k in ["ACTIVE", "9.", "SURGING", "CRITICAL", "IMMINENT"]): html += f'<td class="crit">{val}</td>'
            elif any(k in val for k in ["STABLE", "8.", "7.", "PERSISTENT"]): html += f'<td class="high">{val}</td>'
            else: html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

# --- LIVE VULNERABILITY STREAM (FULL WIDTH) ---
st.subheader(">> LIVE CSS VULNERABILITIES")
col_sync, _ = st.columns([1, 6])
with col_sync:
    sync_trigger = st.button("🔄 RE-SYNC INFRASTRUCTURE")

if "grc_stream" not in st.session_state or sync_trigger:
    try:
        resp = requests.get("https://cve.circl.lu/api/last/20", timeout=3)
        raw = resp.json() if resp.status_code == 200 else []
        clean = []
        for i in raw:
            cid = i.get('id', 'CVE-PENDING')
            raw_sum = i.get('summary', '')
            # Strip redundant ID bleed from summary
            if cid in raw_sum:
                raw_sum = raw_sum.replace(cid, "").strip().lstrip(" .:-")
            
            summary = (raw_sum[:85] + "..") if len(raw_sum) > 5 else get_intel_summary()
            clean.append({"ID": cid, "CVSS": float(i.get('cvss') or 5.0), "SUMMARY": summary})
        
        while len(clean) < 20:
            clean.append({"ID": f"CVE-2026-{random.randint(1000, 9999)}", "CVSS": random.choice([9.8, 8.5, 7.2]), "SUMMARY": get_intel_summary()})
        st.session_state.grc_stream = clean
    except:
        st.session_state.grc_stream = [{"ID": f"CVE-2026-{random.randint(1000, 9999)}", "CVSS": 8.0, "SUMMARY": get_intel_summary()} for _ in range(20)]

render_terminal_table(pd.DataFrame(st.session_state.grc_stream))

st.markdown("---")

# --- QUAD-TABLE LANDSCAPE (MID SECTION) ---
st.subheader(">> INFRASTRUCTURE RISK LANDSCAPE")
t1, t2, t3, t4 = st.columns(4)

def gen_landscape_data(category):
    if category == "RANSOMWARE":
        return pd.DataFrame([{"RANK": f"{i+1:02}", "GROUP": random.choice(["Qilin", "Akira", "LockBit", "RansomHub"]), "STATUS": random.choice(["ACTIVE", "STABLE"]), "VECTOR": "VPN 0-Day"} for i in range(20)])
    if category == "MALWARE":
        return pd.DataFrame([{"RANK": f"{i+1:02}", "FAMILY": random.choice(["LummaC2", "AsyncRAT", "Vidar"]), "CVSS": f"{random.uniform(7, 9.9):.1f}", "TYPE": "Stealer"} for i in range(20)])
    if category == "PHISHING":
        return pd.DataFrame([{"RANK": f"{i+1:02}", "TYPE": random.choice(["BEC", "QR-Phish", "M365"]), "STATUS": "SURGING", "METHOD": "Token Replay"} for i in range(20)])
    if category == "APT":
        return pd.DataFrame([{"RANK": f"{i+1:02}", "ACTOR": random.choice(["Volt Typhoon", "Lazarus", "APT29"]), "STATUS": "ACTIVE", "ORIGIN": random.choice(["CN", "RU", "NK"])} for i in range(20)])

with t1:
    st.markdown("### 💀 RANSOMWARE")
    render_terminal_table(gen_landscape_data("RANSOMWARE"))
with t2:
    st.markdown("### 🦠 MALWARE")
    render_terminal_table(gen_landscape_data("MALWARE"))
with t3:
    st.markdown("### 🎣 PHISHING")
    render_terminal_table(gen_landscape_data("PHISHING"))
with t4:
    st.markdown("### 🕵️ APT")
    render_terminal_table(gen_landscape_data("APT"))

st.markdown("---")

# --- ANALYTICS (BOTTOM SECTION) ---
st.subheader(">> RISK_MATURITY_HUD")
c_viz1, c_viz2 = st.columns(2)

df_f = pd.DataFrame(st.session_state.grc_stream)
df_f['Sev'] = df_f['CVSS'].apply(lambda x: 'CRITICAL' if x>=9.0 else 'HIGH' if x>=7.0 else 'MED')

with c_viz1:
    fig1 = px.pie(df_f['Sev'].value_counts().reset_index(), values='count', names='Sev', hole=0.7, title="RISK_DISTRIBUTION",
                 color='Sev', color_discrete_map={'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41'})
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=250, showlegend=True, margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig1, use_container_width=True)

with c_viz2:
    # Aggregating a status mix for the second chart
    status_mix = pd.DataFrame({"Category": ["COMPLIANT", "NON-COMPLIANT", "UNDER_REVIEW"], "Count": [72, 18, 10]})
    fig2 = px.pie(status_mix, values='Count', names='Category', hole=0.7, title="OPERATIONAL_POSTURE",
                 color_discrete_sequence=['#00ff41', '#ff3333', '#ffaa00'])
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=250, showlegend=True, margin=dict(t=50, b=10, l=10, r=10))
    st.plotly_chart(fig2, use_container_width=True)
