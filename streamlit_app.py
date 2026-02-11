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

# --- CUSTOM CSS (Optimized HUD) ---
st.markdown("""
<style>
    .stApp { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div[data-testid="stCaptionContainer"] { color: #00ff41 !important; font-family: 'Courier New', Courier, monospace !important; }
    
    /* Live Clock Header */
    .clock-header {
        font-size: 1.2rem;
        font-weight: bold;
        text-align: right;
        color: #00ff41;
        padding-bottom: 10px;
        letter-spacing: 2px;
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
        padding: 4px 8px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
    }
    .terminal-table td { border-bottom: 1px solid #1a1a1a; padding: 2px 8px; background-color: #050505; }
    
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

# --- LIVE CLOCK INJECTOR ---
st.markdown(f'<div class="clock-header">SYSTEM_TIME: {datetime.now().strftime("%H:%M:%S")} UTC</div>', unsafe_allow_html=True)

# --- EXTENDED DATASETS (20 ENTRIES EACH) ---
def gen_ransom_data():
    groups = ["Qilin", "Akira", "LockBit", "Play", "BlackBasta", "Medusa", "BianLian", "Rhysida", "Phobos", "INC Ransom", "Storm-0506", "Cactus", "8Base", "ALPHV", "Hunters", "Fog", "Embargo", "RansomHub", "Dragonforce", "Estate"]
    vectors = ["VPN 0-Day", "ESXi Esc", "Supply Ch", "RDP Brute", "AD Takeover", "Public Exp", "Exfiltration", "Phishing", "Credential Stuff", "Citrix Bleed", "Zyxel Vuln", "Fortinet Exp", "ScreenConnect", "Ivanti Bypass", "Atera RMM", "Palo Alto Exp"]
    return pd.DataFrame([{"RANK": f"{i+1:02}", "GROUP": groups[i % len(groups)], "STATUS": random.choice(["ACTIVE", "ACTIVE", "STABLE", "DORMANT"]), "VECTOR": random.choice(vectors)} for i in range(20)])

def gen_malware_data():
    families = ["LummaC2", "AsyncRAT", "XWorm", "RedLine", "AgentTesla", "Pikabot", "Vidar", "Remcos", "SnakeKey", "Gootloader", "Strela", "IcedID", "GuLoader", "Bumblebee", "Amadey", "QuasarRAT", "Warzone", "Sykipot", "Latrodectus", "Meduza"]
    types = ["Stealer", "RAT", "Loader", "Spyware", "JS-Load", "Botnet"]
    return pd.DataFrame([{"RANK": f"{i+1:02}", "FAMILY": families[i % len(families)], "CVSS": f"{random.uniform(6.0, 9.9):.1f}", "TYPE": random.choice(types)} for i in range(20)])

def gen_phish_data():
    types = ["BEC", "QR-Phish", "M365", "OAuth", "Smishing", "Vishing", "SEO Poison", "AiTM Proxy", "Doc-Macro", "Social Lure", "Invoice Fraud", "HelpDesk Spoof"]
    return pd.DataFrame([{"RANK": f"{i+1:02}", "TYPE": random.choice(types), "STATUS": random.choice(["ACTIVE", "SURGING", "STABLE"]), "METHOD": random.choice(["AI Voice", "Quishing", "Token Rep", "MFA Bypass", "Deepfake"])} for i in range(20)])

def gen_apt_data():
    actors = ["Volt Typhoon", "Lazarus", "APT29", "Sandworm", "Mustang Panda", "Fancy Bear", "Kimsuky", "Charming Kitten", "MuddyWater", "SideWinder", "APT41", "OceanLotus", "Turla", "Cozy Bear", "Evil Corp", "Scattered Spider"]
    return pd.DataFrame([{"RANK": f"{i+1:02}", "ACTOR": actors[i % len(actors)], "STATUS": random.choice(["ACTIVE", "STABLE"]), "ORIGIN": random.choice(["CN", "RU", "NK", "IR", "BR", "VN"])} for i in range(20)])

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
            if any(k in val for k in ["ACTIVE", "9.", "SURGING"]): html += f'<td class="crit">{val}</td>'
            elif any(k in val for k in ["STABLE", "8.", "7."]): html += f'<td class="high">{val}</td>'
            else: html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

# Initialize Session State with updated column name
if "global_threats" not in st.session_state: 
    st.session_state.global_threats = [{"ID": f"CVE-26-{random.randint(100, 999)}", "CVSS": random.choice([9.8, 8.5, 7.2]), "LIVE CSS VULNERABILITIES": "System Handshake Active"} for _ in range(20)]

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
            resp = requests.get("https://cve.circl.lu/api/last/20", timeout=3)
            raw_data = resp.json() if resp.status_code == 200 else []
            # Renaming SUMMARY field to LIVE CSS VULNERABILITIES in clean_data
            clean_data = [{"ID": item.get('id'), "CVSS": float(item.get('cvss')) if item.get('cvss') else 5.0, "LIVE CSS VULNERABILITIES": (item.get('summary')[:35] + "..") if item.get('summary') else "No Intel"} for item in raw_data if item.get('id')]
            while len(clean_data) < 20: clean_data.append({"ID": f"CVE-26-{random.randint(100, 999)}", "CVSS": 8.0, "LIVE CSS VULNERABILITIES": "Inbound Threat Pattern"})
            st.session_state.global_threats = clean_data
        except: pass
    
    render_terminal_table(pd.DataFrame(st.session_state.global_threats))

with col_side:
    st.subheader(">> ANALYTICS")
    
    # CVSS Distro
    df_f = pd.DataFrame(st.session_state.global_threats)
    df_f['Sev'] = df_f['CVSS'].apply(lambda x: 'CRITICAL' if float(x)>=9.0 else 'HIGH' if float(x)>=7.0 else 'MED')
    f_counts = df_f['Sev'].value_counts().reset_index()
    
    fig1 = px.pie(f_counts, values='count', names='Sev', hole=0.7, title="CVSS_DISTRO",
                 color='Sev', color_discrete_map={'CRITICAL':'#ff3333', 'HIGH':'#ffaa00', 'MED':'#00ff41'})
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=210, showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
    fig1.update_traces(textinfo='percent+label', textfont_size=10)
    st.plotly_chart(fig1, use_container_width=True)

    # Threat Status Mix
    all_status = pd.concat([df_ransom['STATUS'], df_phish['STATUS'], df_apt['STATUS']])
    s_counts = all_status.value_counts().reset_index()
    
    fig2 = px.pie(s_counts, values='count', names='STATUS', hole=0.7, title="THREAT_STATUS",
                 color='STATUS', color_discrete_map={'ACTIVE':'#ff3333', 'SURGING':'#ff3333', 'STABLE':'#ffaa00', 'DORMANT':'#00ff41'})
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#00ff41', height=210, showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
    fig2.update_traces(textinfo='percent+label', textfont_size=10)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- QUAD-TABLE LANDSCAPE (20 ROWS EACH) ---
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
