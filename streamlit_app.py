import streamlit as st
import pandas as pd
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
    /* GLOBAL DARK THEME */
    .stApp { background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #00ff41 !important; }
    
    /* REMOVE WHITE ELEMENTS */
    header, footer { visibility: hidden; }
    .stDeployButton { display: none; }
    
    /* SYSTEM HEADER */
    .clock-header {
        font-size: 1rem;
        font-weight: bold;
        text-align: right;
        color: #00ff41;
        margin-bottom: -20px;
        text-shadow: 0 0 5px #00ff41;
    }
    
    /* METRICS BOXES */
    div[data-testid="stMetric"] {
        background-color: #0a0a0a !important;
        border: 1px solid #333;
        border-left: 3px solid #00ff41 !important;
        padding: 5px 10px;
    }
    div[data-testid="stMetricValue"] { color: #00ff41 !important; font-size: 1.2rem !important; }
    div[data-testid="stMetricLabel"] { color: #888 !important; }
    
    /* TERMINAL TABLE STYLING */
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        color: #cccccc;
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        margin-bottom: 15px;
        border: 1px solid #222;
        background-color: #050505;
    }
    .terminal-table th {
        border-bottom: 1px solid #00ff41;
        text-align: left;
        padding: 8px 10px;
        color: #00ff41;
        background-color: #111;
        text-transform: uppercase;
    }
    .terminal-table td { 
        border-bottom: 1px solid #1a1a1a; 
        padding: 8px 10px; 
        background-color: #050505; 
    }
    
    /* STATUS COLORS */
    .crit { color: #ff3333 !important; font-weight: bold; text-shadow: 0 0 5px #ff3333; }
    .high { color: #ffaa00 !important; }
    .med { color: #00ff41 !important; }
    
    /* BUTTON STYLING */
    .stButton>button {
        background-color: #000000; color: #00ff41; border: 1px solid #333;
        font-size: 0.75rem; font-weight: bold; text-transform: uppercase; 
        width: 100%;
    }
    .stButton>button:hover { 
        border-color: #00ff41; 
        box-shadow: 0 0 8px #00ff41; 
        color: #fff;
    }
    
    /* DOWNLOAD BUTTON */
    div[data-testid="stDownloadButton"]>button {
        background-color: #111 !important;
        color: #00ff41 !important;
        border: 1px solid #00ff41 !important;
        font-family: 'Courier New', monospace !important;
        text-transform: uppercase;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA GENERATORS ---

def render_terminal_table(df):
    if df is None or df.empty:
        st.info("No data available yet. Click RE-SYNC.")
        return
    html = '<table class="terminal-table"><thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            if any(k in val.upper() for k in ["CRITICAL", "9.", "ACTIVE_EXPLOIT", "BREACH"]):
                html += f'<td class="crit">{val}</td>'
            elif any(k in val.upper() for k in ["HIGH", "8.", "7.", "ELEVATED"]):
                html += f'<td class="high">{val}</td>'
            else:
                html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown(f'<div class="clock-header">SYSTEM_TIME: {datetime.now().strftime("%H:%M:%S")} UTC // SECURE_UPLINK_ESTABLISHED</div>', unsafe_allow_html=True)
st.title("🔒 SecAI-Nexus")
st.markdown("**// GLOBAL THREAT VISIBILITY DASHBOARD**")
st.caption("Target: Worldwide • Protocol: Real-time Intelligence • Encryption: AES-256")
st.markdown("---")

# === LIVE CYBER THREAT MAPS (SMALL GRID) ===
st.subheader(">> LIVE CYBER THREAT MAPS (SECTOR A)")
st.caption("Real-time global attack activity from trusted sources")
map_row1 = st.columns(4)
map_row2 = st.columns(4)

with map_row1[0]:
    st.markdown("**Bitdefender**")
    st.components.v1.iframe("https://threatmap.bitdefender.com/", height=480, scrolling=True)
with map_row1[1]:
    st.markdown("**Sicherheitstacho (DT)**")
    st.components.v1.iframe("https://www.sicherheitstacho.eu/?lang=en", height=480, scrolling=True)
with map_row1[2]:
    # REPLACED: Barracuda -> NETSCOUT Cyber Threat Horizon (High-end 3D Map)
    st.markdown("**NETSCOUT Threat Horizon**")
    st.components.v1.iframe("https://horizon.netscout.com/?kiosk=true", height=480, scrolling=True)
with map_row1[3]:
    st.markdown("**Radware Live Threat Map**")
    st.components.v1.iframe("https://livethreatmap.radware.com/", height=480, scrolling=True)

with map_row2[0]:
    st.markdown("**Fortinet Threat Map**")
    st.components.v1.iframe("https://threatmap.fortiguard.com/", height=480, scrolling=True)
with map_row2[1]:
    st.markdown("**Kaspersky Cybermap**")
    st.components.v1.iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", height=480, scrolling=True)
with map_row2[2]:
    st.markdown("**SonicWall Live Map**")
    st.components.v1.iframe("https://attackmap.sonicwall.com/live-attack-map/", height=480, scrolling=True)
with map_row2[3]:
    st.markdown("**Threatbutt Attack Map**")
    st.components.v1.iframe("https://threatbutt.com/map/", height=480, scrolling=True)

st.markdown("---")

# === LARGE MAP SECTION (GREYNOISE - NO HEADER) ===
# Header removed as requested. Directly placing the large sensor map.
st.components.v1.iframe("https://viz.greynoise.io/", height=800, scrolling=True)

st.markdown("---")

# --- LIVE CVE VULNERABILITIES ---
st.subheader(">> LIVE CVE VULNERABILITIES")
col_sync, col_download, _ = st.columns([1, 2, 4])

# Realistic CVE Simulator
def generate_realistic_cves():
    vendors = ["Apache", "Microsoft", "Cisco", "Oracle", "VMware", "Adobe", "Linux Kernel", "Kubernetes"]
    types = ["Remote Code Execution", "Privilege Escalation", "SQL Injection", "Buffer Overflow", "XSS"]
    cves = []
    for _ in range(20):
        year = random.choice([2025, 2026])
        num = random.randint(1000, 99999)
        score = round(random.uniform(5.0, 10.0), 1)
        vendor = random.choice(vendors)
        vuln_type = random.choice(types)
        cves.append({
            "ID": f"CVE-{year}-{num}",
            "CVSS": score,
            "SUMMARY": f"{vuln_type} in {vendor} Core causing denial of service or data leak."
        })
    return sorted(cves, key=lambda x: x['CVSS'], reverse=True)

if "grc_stream" not in st.session_state:
    st.session_state.grc_stream = generate_realistic_cves()

with col_sync:
    if st.button("🔄 RE-SYNC/REFRESH"):
        st.session_state.grc_stream = generate_realistic_cves()
        st.rerun()

with col_download:
    # CSV GENERATOR
    csv_data = pd.DataFrame(st.session_state.grc_stream).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇ DOWNLOAD VULNERABILITY REPORT (.CSV)",
        data=csv_data,
        file_name=f"vuln_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("CRITICAL VULNERABILITIES (Top 10)")
    df1 = pd.DataFrame(st.session_state.grc_stream[:10])
    render_terminal_table(df1[['ID', 'CVSS', 'SUMMARY']])
with col_right:
    st.subheader("ELEVATED VULNERABILITIES (Next 10)")
    df2 = pd.DataFrame(st.session_state.grc_stream[10:20])
    render_terminal_table(df2[['ID', 'CVSS', 'SUMMARY']])

st.markdown("---")

# --- INFRASTRUCTURE RISK LANDSCAPE ---
st.subheader(">> INFRASTRUCTURE RISK LANDSCAPE")
t1, t2, t3, t4 = st.columns(4)

def gen_landscape_data(category):
    risks = ["CRITICAL", "HIGH", "MEDIUM"]
    statuses = ["ACTIVE_EXPLOIT", "PATCHING", "MONITORING", "CONTAINED"]
    data = []
    for i in range(10): 
        risk = random.choice(risks)
        status = "ACTIVE_EXPLOIT" if risk == "CRITICAL" else random.choice(statuses)
        
        if category == "RANSOMWARE":
            groups = ["BlackCat", "LockBit 3.0", "Akira", "Clop", "Royal"]
            sectors = ["Healthcare", "Finance", "Mfg", "Retail"]
            data.append({"GROUP": random.choice(groups), "SECTOR": random.choice(sectors), "RISK": risk, "STATUS": status})
        elif category == "MALWARE":
            families = ["Emotet", "Cobalt Strike", "Qakbot", "AgentTesla"]
            vectors = ["Email", "Drive-by", "USB", "RDP"]
            data.append({"FAMILY": random.choice(families), "VECTOR": random.choice(vectors), "RISK": risk, "STATUS": status})
        elif category == "PHISHING":
            types = ["Spear Phishing", "Whaling", "Clone Phishing", "Smishing"]
            targets = ["Execs", "HR Dept", "IT Admins", "Sales"]
            data.append({"TYPE": random.choice(types), "TARGET": random.choice(targets), "RISK": risk, "STATUS": status})
        elif category == "APT":
            actors = ["APT29 (RU)", "APT41 (CN)", "Lazarus (NK)", "Charming Kitten (IR)"]
            methods = ["Supply Chain", "Zero-Day", "Social Eng.", "Valid Accts"]
            data.append({"ACTOR": random.choice(actors), "METHOD": random.choice(methods), "RISK": risk, "STATUS": status})

    return pd.DataFrame(data)

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
    st.markdown("### 🕵️ APT GROUPS")
    render_terminal_table(gen_landscape_data("APT"))

# DASHBOARD ENDS HERE
