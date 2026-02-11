import streamlit as st
import pd as pd
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

# --- CUSTOM CSS (Maximum Density) ---
st.markdown("""
<style>
    .stApp { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stCaptionContainer"] { color: #00ff41 !important; font-family: 'Courier New', Courier, monospace !important; }
    
    /* Metric HUD */
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
        font-size: 0.72rem;
        margin-bottom: 10px;
        border: 1px solid #222;
    }
    .terminal-table th {
        border-bottom: 1px solid #00ff41;
        text-align: left;
        padding: 4px 8px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
        font-size: 0.65rem;
    }
    .terminal-table td { border-bottom: 1px solid #1a1a1a; padding: 3px 8px; background-color: #050505; }
    
    .crit { color: #ff3333 !important; font-weight: bold; }
    .high { color: #ffaa00 !important; }
    .med { color: #00ff41 !important; }

    .stButton>button {
        background-color: #000000; color: #00ff41; border: 1px solid #333;
        font-size: 0.65rem; font-weight: bold; text-transform: uppercase; height: 25px;
    }
    .stButton>button:hover { border-color: #00ff41; box-shadow: 0 0 8px #00ff41; }
</style>
""", unsafe_allow_html=True)

# --- DATA RESTORATION ---
df_ransom = pd.DataFrame([
    {"RANK": "01", "GROUP": "Qilin", "STATUS": "ACTIVE", "VECTOR": "VPN 0-Day"},
    {"RANK": "02", "GROUP": "Akira", "STATUS": "ACTIVE", "VECTOR": "ESXi Esc"},
    {"RANK": "03", "GROUP": "LockBit", "STATUS": "STABLE", "VECTOR": "Supply Ch"},
    {"RANK": "04", "GROUP": "Play", "STATUS": "DORMANT", "VECTOR": "RDP Brute"}
])

df_malware = pd.DataFrame([
    {"RANK": "01", "FAMILY": "LummaC2", "CVSS": "9.8", "TYPE": "Stealer"},
    {"RANK": "02", "FAMILY": "AsyncRAT", "CVSS": "8.5", "TYPE": "RAT"},
    {"RANK": "03", "FAMILY": "XWorm", "CVSS": "7.9", "TYPE": "Loader"},
    {"RANK": "04", "FAMILY": "RedLine", "CVSS": "7.2", "TYPE": "Stealer"}
])

df_phish = pd.DataFrame([
    {"RANK": "01", "TYPE": "BEC", "STATUS": "ACTIVE", "METHOD": "AI Voice"},
    {"RANK": "02", "TYPE": "QR-Phish", "STATUS": "ACTIVE", "METHOD": "Quishing"},
    {"RANK": "03", "TYPE": "M365", "STATUS": "STABLE", "METHOD": "Token Rep"},
    {"RANK": "04", "TYPE": "OAuth", "STATUS": "ACTIVE", "METHOD": "App Perms"}
])

df_apt = pd.DataFrame([
    {"RANK": "01", "ACTOR": "Volt Typhoon", "STATUS": "ACTIVE", "ORIGIN": "CN"},
    {"RANK": "02", "ACTOR": "Lazarus", "STATUS": "ACTIVE", "ORIGIN": "NK"},
    {"RANK": "03", "ACTOR": "APT29", "STATUS": "STABLE", "ORIGIN": "RU"},
    {"RANK": "04", "ACTOR": "Sandworm", "STATUS": "ACTIVE", "ORIGIN": "RU"}
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
    mock_vulns = ["Kernel OF", "MFA Bypass", "Auth Leak", "RCE Gate", "Core SQLi", "Priv Esc"]
    return {"ID": f"CVE-26-{random.randint(100, 999)}", "CVSS": random.choice([9.8, 8.5, 7.2]), "SUMMARY": random.choice(mock_vulns)}

if "global_threats" not in st.session_state: st.session_state.global_threats = [get_fallback_data() for _ in range(15)]

# --- HEADER ---
st.title("🔒 SecAI-Nexus")
st.markdown("**// GLOBAL THREAT VISIBILITY DASHBOARD**")
st.caption("Target: Worldwide • Protocol: Real-time Intelligence")

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
            resp = requests.get("https://cve.circl.lu/api/last/15", timeout=3)
            raw_data = resp.json() if resp.status_code == 200 else []
            clean_data = [{"ID": item.get('id'), "CVSS": float(item.get('cvss')) if item.get('cvss') else 5.0, "SUMMARY": (item.get('summary')[:35] + "..") if item.get('summary') else "No Intel"} for item in raw_data if item.get('id')]
            while len(clean_data) < 15: clean_data.append(get_fallback_data())
            st.session_state.global_threats = clean_data
        except: pass
    
    render_terminal_table(pd.DataFrame(st.session_state.global_threats))

with col_side:
    st.subheader(">> ANALYTICS")
    
    # CVSS Distro
    df_f = pd.DataFrame(st.session_state.global_threats)
    df_f['Sev'] = df_f['CVSS'].apply(lambda x: 'CRITICAL' if x>=9.0 else 'HIGH' if x>=7.0 else 'MED')
    f_counts = df_f['Sev'].value_counts().reset_index()
    
    fig1 = px.pie(f_counts, values='count', names='Sev', hole=0.7, title="CVSS_DISTRO",
                 color='Sev', color_discrete_map={'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41'})
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=140, showlegend=False, margin=dict(t=25, b=0, l=0, r=0))
    fig1.update_traces(textinfo='percent+label', textfont_size=9)
    st.plotly_chart(fig1, use_container_width=True)

    # Status Mix
    status_data = pd.concat([df_ransom['STATUS'], df_phish['STATUS'], df_apt['STATUS']])
    s_counts = status_data.value_counts().reset_index()
    
    fig2 = px.pie(s_counts, values='count', names='STATUS', hole=0.7, title="THREAT_STATUS",
                 color='STATUS', color_discrete_map={'ACTIVE':'#ff3333', 'STABLE':'#ffaa00', 'DORMANT':'#00ff41'})
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=140, showlegend=False, margin=dict(t=25, b=0, l=0, r=0))
    fig2.update_traces(textinfo='percent+label', textfont_size=9)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- QUAD-TABLE LANDSCAPE ---
st.subheader(">> THREAT LANDSCAPE")
t1, t2, t3, t4 = st.columns(4)

with t1:
    st.markdown("### 💀 RANSOMWARE")
    render_terminal_table(df_ransom)

with t2:
    st.markdown("### 🦠 MALWARE")
    render_terminal_table(df_malware)

with t3:
    st.markdown("### 🎣 PHISHING")
    render_terminal_table(df_phish)

with t4:
    st.markdown("### 🕵️ APT")
    render_terminal_table(df_apt)
