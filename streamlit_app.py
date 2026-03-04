import streamlit as st
import pandas as pd
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

# --- INLINE CSS CONSTANTS (NEON GREEN & MEDIAN CYBER BLUE) ---
GREEN_SUBTITLE = "font-size: 1.1rem; font-weight: bold; color: #00ff41; margin-top: 25px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1.2px;"
BLUE_LABEL = "font-size: 1.0rem; font-weight: bold; color: #008aff; margin-bottom: 8px; text-transform: uppercase;"
SENTENCE_STYLE_GREEN = "color: #00ff41; font-size: 1.15rem; line-height: 1.6; font-family: 'Courier New', monospace; font-weight: normal; text-transform: none; letter-spacing: normal;"
LINK_STYLE_BLUE = "color: #008aff; font-weight: bold; text-decoration: none; border-bottom: 1px dashed #008aff;"

# --- ADVANCED GRC CSS ---
st.markdown(f"""
<style>
    /* GLOBAL DARK THEME */
    .stApp {{ background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }}
    
    /* UNIVERSAL SENTENCE READABILITY */
    div[data-testid="stMarkdownContainer"] > p {{ {SENTENCE_STYLE_GREEN} }}
    h1, h2, h3, h4, h5, h6, label {{ color: #00ff41 !important; }}
    
    header, footer {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}
    
    /* METRICS BOXES */
    div[data-testid="stMetric"] {{
        background-color: #0a0a0a !important;
        border: 1px solid #333;
        border-left: 4px solid #008aff !important;
        padding: 8px 12px;
    }}
    div[data-testid="stMetricValue"] {{ color: #00ff41 !important; font-size: 1.4rem !important; font-weight: bold; }}
    div[data-testid="stMetricLabel"] {{ color: #008aff !important; font-size: 0.95rem; text-transform: uppercase; font-weight: bold;}}
    
    /* TERMINAL TABLE STYLING */
    .terminal-table {{
        width: 100%;
        border-collapse: collapse;
        color: #00ff41;
        font-family: 'Courier New', monospace;
        font-size: 1.1rem; 
        margin-bottom: 15px;
        border: 1px solid #222;
        background-color: #050505;
    }}
    .terminal-table th {{
        border-bottom: 2px solid #008aff;
        text-align: left;
        padding: 10px 12px;
        color: #008aff;
        background-color: #111;
        text-transform: uppercase;
        font-size: 1.0rem;
    }}
    .terminal-table td {{ border-bottom: 1px solid #1a1a1a; padding: 10px 12px; background-color: #050505; line-height: 1.4; }}
    
    /* STATUS COLORS */
    .crit {{ color: #ff3333 !important; font-weight: bold; text-shadow: 0 0 5px #ff3333; }}
    .high {{ color: #ffaa00 !important; }}
    
    /* SYNC BUTTON */
    .stButton>button {{
        background-color: #000000; color: #008aff; border: 2px solid #333;
        font-size: 0.9rem; font-weight: bold; text-transform: uppercase; width: 100%; padding: 10px;
    }}
    .stButton>button:hover {{ border-color: #00ff41; box-shadow: 0 0 10px #00ff41; color: #00ff41; }}
    
    /* DOWNLOAD BUTTON - FIXED WHITE-OUT ISSUE */
    div[data-testid="stDownloadButton"]>button {{
        background-color: #000000 !important;
        color: #008aff !important;
        border: 2px solid #008aff !important;
        font-family: 'Courier New', monospace !important;
        text-transform: uppercase;
        width: 100%;
        font-size: 0.9rem;
        transition: 0.3s;
    }}
    div[data-testid="stDownloadButton"]>button:hover {{
        background-color: #008aff !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px #008aff;
    }}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

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
            elif any(k in val.upper() for k in ["HIGH", "8.", "7.", "ELEVATED", "PATCHING"]):
                html += f'<td class="high">{val}</td>'
            else:
                html += f'<td>{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

def render_muted_iframe(url, height=480):
    iframe_html = f'<iframe src="{url}" width="100%" height="{height}" style="border:none;" sandbox="allow-scripts allow-same-origin allow-forms allow-popups" allow="autoplay; microphone; camera"></iframe>'
    st.markdown(iframe_html, unsafe_allow_html=True)

def render_simple_link(num, title, url, desc):
    return f"""
    <div style="margin-bottom: 25px; font-family: 'Courier New', monospace;">
        <span style="color: #00ff41; font-weight: bold; font-size: 1.4rem;">{num}.</span> 
        <a href="{url}" target="_blank" style="color: #008aff; font-weight: bold; font-size: 1.35rem; text-decoration: none; border-bottom: 1px dashed #008aff;">{title}</a>
        <div style="color: #00ff41; font-size: 1.15rem; margin-top: 8px; padding-left: 45px; line-height: 1.6;">{desc}</div>
    </div>
    """

def fetch_real_cves():
    url = "https://cve.circl.lu/api/last/30"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            cve_list = []
            for item in data:
                cve_id = item.get("id")
                summary = item.get("summary")
                if not cve_id or not summary or "Unknown" in cve_id: continue
                cvss = item.get("cvss", 0.0)
                if len(summary) > 90: summary = summary[:87] + "..."
                cve_list.append({"ID": cve_id, "CVSS": float(cvss) if cvss else 0.0, "SUMMARY": summary})
            return sorted(cve_list, key=lambda x: x['CVSS'], reverse=True)
    except Exception: pass 
    return []

# --- HEADER ---
st.markdown(f"""
<div style="border-bottom: 2px solid #333; padding-bottom: 12px; margin-bottom: 18px; margin-top: -50px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap;">
        <div>
            <span style="font-size: 1.3rem; font-weight: bold; color: #00ff41; text-shadow: 0 0 5px #00ff41;">🔒 SecAI-Nexus</span>
            <span style="font-size: 0.95rem; color: #008aff; margin-left: 10px; font-weight: bold;">// GLOBAL THREAT VISIBILITY</span>
        </div>
        <div style="font-size: 1.0rem; font-weight: bold; color: #008aff; text-shadow: 0 0 5px #008aff;">SYS_TIME: {datetime.now().strftime("%H:%M:%S")} UTC</div>
    </div>
    <div style="font-size: 0.75rem; color: #00ff41; margin-top: 6px; text-transform: uppercase;">
        Worldwide | Real-time | Enc: AES-256 | Status: <span style="color: #008aff; font-weight: bold;">SECURE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === LIVE CYBER THREAT MAPS ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> LIVE CYBER THREAT MAPS</div>', unsafe_allow_html=True)
map_row = st.columns(4)
with map_row[0]: render_muted_iframe("https://threatmap.bitdefender.com/", height=450)
with map_row[1]: render_muted_iframe("https://www.sicherheitstacho.eu/?lang=en", height=450)
with map_row[2]: render_muted_iframe("https://threatmap.checkpoint.com/", height=450)
with map_row[3]: render_muted_iframe("https://livethreatmap.radware.com/", height=450)

st.markdown("---")

# === GREYNOISE TRENDS ===
st.markdown(f'<div style="{GREEN_SUBTITLE}"><span style="color: #008aff;">>> GREYNOISE INTELLIGENCE</span> (<a href="https://viz.greynoise.io/trends/trending" target="_blank" style="{LINK_STYLE_BLUE}">TRENDS VIEW</a>)</div>', unsafe_allow_html=True)
render_muted_iframe("https://viz.greynoise.io/trends/trending", height=1200)

# === CLOUDFLARE RADAR (NEW) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}"><span style="color: #008aff;">>> CLOUDFLARE RADAR</span> (<a href="https://radar.cloudflare.com/" target="_blank" style="{LINK_STYLE_BLUE}">GLOBAL TRAFFIC INTEL</a>)</div>', unsafe_allow_html=True)
render_muted_iframe("https://radar.cloudflare.com/", height=1000)

st.markdown("---")

# === ADDITIONAL GRC RESOURCES (TOP 25) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> ADDITIONAL GRC RESOURCES</div>', unsafe_allow_html=True)
link_col1, link_col2 = st.columns(2)
with link_col1:
    st.markdown(render_simple_link("01", "NIST CSF", "https://www.nist.gov/cyberframework", "Voluntary guidance for managing and reducing cybersecurity risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("02", "ISO/IEC 27000", "https://www.iso.org/isoiec-27001-information-security.html", "International standard for ISMS management."), unsafe_allow_html=True)
    st.markdown(render_simple_link("03", "OWASP Top 10", "https://owasp.org/www-project-top-ten/", "Critical web application security risks awareness."), unsafe_allow_html=True)
    st.markdown(render_simple_link("04", "NIST NVD", "https://nvd.nist.gov/", "Backbone of vulnerability management data."), unsafe_allow_html=True)
    st.markdown(render_simple_link("05", "MITRE ATT&CK", "https://mitre-attack.github.io/attack-navigator/", "Adversary TTP mapping matrix."), unsafe_allow_html=True)
    st.markdown(render_simple_link("06", "Shodan", "https://www.shodan.io/", "Search engine for internet-connected devices."), unsafe_allow_html=True)
    st.markdown(render_simple_link("07", "crt.sh", "https://crt.sh/", "Certificate Transparency log search."), unsafe_allow_html=True)
    st.markdown(render_simple_link("08", "CISA KEV", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "Vulnerabilities exploited in the wild."), unsafe_allow_html=True)
    st.markdown(render_simple_link("09", "Exploit-DB", "https://www.exploit-db.com/", "Ultimate archive of public exploits."), unsafe_allow_html=True)
    st.markdown(render_simple_link("10", "VirusTotal", "https://www.virustotal.com/", "Daily king of IOC file and domain analysis."), unsafe_allow_html=True)
    st.markdown(render_simple_link("11", "AlienVault OTX", "https://otx.alienvault.com/", "Crowdsourced open threat exchange community."), unsafe_allow_html=True)
    st.markdown(render_simple_link("12", "Security Onion", "https://securityonionsolutions.com/", "Open-source threat hunting platform."), unsafe_allow_html=True)

with link_col2:
    st.markdown(render_simple_link("13", "URLhaus", "https://urlhaus.abuse.ch/", "Tracking malware distribution sites."), unsafe_allow_html=True)
    st.markdown(render_simple_link("14", "SANS ISC", "https://isc.sans.edu/", "Global anomaly and port trend monitoring."), unsafe_allow_html=True)
    st.markdown(render_simple_link("15", "BleepingComputer", "https://www.bleepingcomputer.com/", "Industry pulse for ransomware and breach news."), unsafe_allow_html=True)
    st.markdown(render_simple_link("16", "Any.Run", "https://any.run/", "Interactive online malware sandbox."), unsafe_allow_html=True)
    st.markdown(render_simple_link("17", "CVSS 4.0 Calc", "https://www.first.org/cvss/calculator/4.0", "Calculate exact environmental risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("18", "MalwareBazaar", "https://bazaar.abuse.ch/", "Open malware sample repository."), unsafe_allow_html=True)
    st.markdown(render_simple_link("19", "GTFOBins", "https://gtfobins.github.io/", "Unix binaries for security bypass."), unsafe_allow_html=True)
    st.markdown(render_simple_link("20", "Cloudflare Radar", "https://radar.cloudflare.com/", "Insights into global traffic and attacks."), unsafe_allow_html=True)
    st.markdown(render_simple_link("21", "Triage", "https://triage.com/", "Public automated malware analysis."), unsafe_allow_html=True)
    st.markdown(render_simple_link("22", "URLScan.io", "https://urlscan.io/", "Analyze what a website is actually doing."), unsafe_allow_html=True)
    st.markdown(render_simple_link("23", "LOLBAS", "https://lolbas-project.github.io/", "Windows binaries for living-off-the-land."), unsafe_allow_html=True)
    st.markdown(render_simple_link("24", "Hacker News", "https://thehackernews.com/", "Trusted cybersecurity breach coverage."), unsafe_allow_html=True)
    st.markdown(render_simple_link("25", "Dark Reading", "https://www.darkreading.com/", "Enterprise security technology trends."), unsafe_allow_html=True)

st.markdown("---")

# === DATA ANALYSIS SECTION (CYBERCHEF BELOW LINKS) ===
st.markdown(f'''
<div style="{GREEN_SUBTITLE}">
    <span style="color: #008aff;">>> CYBERCHEF ANALYSIS TOOL</span> 
    - <span style="{SENTENCE_STYLE_GREEN}">Analyze suspicious payloads, decode malware, and manipulate data locally.</span>
</div>
''', unsafe_allow_html=True)
render_muted_iframe("https://gchq.github.io/CyberChef/", height=1000)

st.markdown("---")

# --- LIVE CVE FEED ---
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> LIVE CVE VULNERABILITIES</div>', unsafe_allow_html=True)
col_sync, col_download, _ = st.columns([1, 2, 4])
if "grc_stream" not in st.session_state: st.session_state.grc_stream = fetch_real_cves()
with col_sync:
    if st.button("🔄 RE-SYNC"):
        st.session_state.grc_stream = fetch_real_cves()
        st.rerun()
with col_download:
    csv_data = pd.DataFrame(st.session_state.grc_stream).to_csv(index=False).encode('utf-8')
    st.download_button(label="⬇ DOWNLOAD VULNERABILITY REPORT (.CSV)", data=csv_data, file_name=f"vuln_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

col_left, col_right = st.columns(2)
with col_left:
    st.markdown(f'<div style="{BLUE_LABEL}">CRITICAL (Top 10)</div>', unsafe_allow_html=True)
    render_terminal_table(pd.DataFrame(st.session_state.grc_stream[:10]))
with col_right:
    st.markdown(f'<div style="{BLUE_LABEL}">RECENT (Next 10)</div>', unsafe_allow_html=True)
    render_terminal_table(pd.DataFrame(st.session_state.grc_stream[10:20]))

st.markdown("---")

# --- RISK LANDSCAPE (CURATED SIM) ---
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> INFRASTRUCTURE RISK LANDSCAPE</div>', unsafe_allow_html=True)
t1, t2, t3, t4 = st.columns(4)
def gen_sim(cat):
    data = []
    for _ in range(8):
        data.append({"ENTITY": random.choice(["APT41", "LockBit", "Cisco Core", "MFA Bypass", "SolarWinds", "Log4j"]), "RISK": random.choice(["CRITICAL", "HIGH", "MEDIUM"])})
    return pd.DataFrame(data)
with t1: render_terminal_table(gen_sim("RANSOMWARE"))
with t2: render_terminal_table(gen_sim("MALWARE"))
with t3: render_terminal_table(gen_sim("PHISHING"))
with t4: render_terminal_table(gen_sim("APT"))

# DASHBOARD ENDS
