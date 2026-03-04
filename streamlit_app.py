import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime, timedelta

# --- STEALTH CONFIGURATION ---
st.set_page_config(
    page_title="SecAI-Nexus GRC",
    layout="wide",
    page_icon="🔒",
    initial_sidebar_state="collapsed"
)

# --- INLINE CSS CONSTANTS ---
GREEN_SUBTITLE = "font-size: 1.1rem; font-weight: bold; color: #00ff41; margin-top: 25px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1.2px;"
BLUE_LABEL = "font-size: 1.0rem; font-weight: bold; color: #008aff; margin-bottom: 8px; text-transform: uppercase;"
SENTENCE_STYLE_GREEN = "color: #00ff41; font-size: 1.15rem; line-height: 1.6; font-family: 'Courier New', monospace; font-weight: normal; text-transform: none; letter-spacing: normal;"
LINK_STYLE_BLUE = "color: #008aff; font-weight: bold; text-decoration: none; border-bottom: 1px dashed #008aff;"

# --- ADVANCED GRC CSS ---
st.markdown(f"""
<style>
    /* GLOBAL DARK THEME */
    .stApp {{ background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }}
    
    div[data-testid="stMarkdownContainer"] > p {{ {SENTENCE_STYLE_GREEN} }}
    h1, h2, h3, h4, h5, h6, label {{ color: #00ff41 !important; }}
    
    header, footer {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}
    
    /* CUSTOM MULTI-DELTA METRIC CARDS */
    .custom-metric {{
        background-color: #0a0a0a;
        border: 1px solid #333;
        border-left: 4px solid #008aff;
        padding: 12px 15px;
        margin-bottom: 15px;
        font-family: 'Courier New', monospace;
    }}
    .metric-title {{ color: #008aff; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 0.5px; }}
    .metric-value {{ color: #00ff41; font-size: 1.8rem; font-weight: bold; margin-bottom: 8px; text-shadow: 0 0 5px #00ff41; }}
    .metric-deltas {{ font-size: 0.8rem; color: #888; border-top: 1px dashed #333; padding-top: 8px; }}
    .d-bad {{ color: #ff3333; font-weight: bold; }}
    .d-good {{ color: #00ff41; font-weight: bold; }}
    .d-neu {{ color: #008aff; font-weight: bold; }}
    
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
    .terminal-table th {{ border-bottom: 2px solid #008aff; text-align: left; padding: 10px 12px; color: #008aff; background-color: #111; text-transform: uppercase; font-size: 1.0rem; }}
    .terminal-table td {{ border-bottom: 1px solid #1a1a1a; padding: 10px 12px; background-color: #050505; line-height: 1.4; }}
    
    /* STATUS COLORS */
    .crit {{ color: #ff3333 !important; font-weight: bold; text-shadow: 0 0 5px #ff3333; }}
    .high {{ color: #ffaa00 !important; }}
    .med {{ color: #00ff41 !important; }}
    
    /* SYNC & DOWNLOAD BUTTONS */
    div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button {{
        background-color: #050505 !important; border: 2px solid #008aff !important; width: 100% !important; transition: 0.3s;
    }}
    div[data-testid="stButton"] > button p, div[data-testid="stDownloadButton"] > button p {{
        color: #008aff !important; font-family: 'Courier New', monospace !important; font-size: 0.9rem !important; font-weight: bold !important; text-transform: uppercase !important; 
    }}
    div[data-testid="stButton"] > button:hover, div[data-testid="stDownloadButton"] > button:hover {{
        background-color: #008aff !important; box-shadow: 0 0 10px #008aff !important;
    }}
    div[data-testid="stButton"] > button:hover p, div[data-testid="stDownloadButton"] > button:hover p {{
        color: #050505 !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- REAL & SIMULATED DATA FETCHING ---

@st.cache_data(ttl=3600)
def fetch_real_cisa_kev():
    """Pulls REAL live data directly from the US Government CISA KEV JSON feed."""
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            vulnerabilities = response.json().get("vulnerabilities", [])
            total = len(vulnerabilities)
            
            # Calculate dynamic date deltas
            now = datetime.utcnow()
            d1_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
            d7_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
            d30_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")
            
            d1_count = sum(1 for v in vulnerabilities if v.get("dateAdded", "") >= d1_date)
            d7_count = sum(1 for v in vulnerabilities if v.get("dateAdded", "") >= d7_date)
            d30_count = sum(1 for v in vulnerabilities if v.get("dateAdded", "") >= d30_date)
            
            return str(total), f"+{d1_count}", f"+{d7_count}", f"+{d30_count}"
    except Exception:
        pass
    return "OFFLINE", "N/A", "N/A", "N/A"

def render_multi_metric(title, value, d1, d1_class, d7, d7_class, d30, d30_class):
    """HTML component to render the custom 3-delta metric box."""
    html = f"""
    <div class="custom-metric">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-deltas">
            1D: <span class="{d1_class}">{d1}</span> | 
            1W: <span class="{d7_class}">{d7}</span> | 
            1M: <span class="{d30_class}">{d30}</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_terminal_table(df):
    if df is None or df.empty: return
    html = '<table class="terminal-table"><thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            if any(k in val.upper() for k in ["CRITICAL", "9.", "ACTIVE_EXPLOIT", "BREACH"]): html += f'<td class="crit">{val}</td>'
            elif any(k in val.upper() for k in ["HIGH", "8.", "7.", "ELEVATED", "PATCHING"]): html += f'<td class="high">{val}</td>'
            else: html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

def render_muted_iframe(url, height=480):
    iframe_html = f'<iframe src="{url}" width="100%" height="{height}" style="border:none;" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>'
    st.markdown(iframe_html, unsafe_allow_html=True)

def render_simple_link(num, title, url, desc):
    return f"""
    <div style="margin-bottom: 25px; font-family: 'Courier New', monospace;">
        <span style="color: #00ff41; font-weight: bold; font-size: 1.4rem;">{num}.</span> 
        <a href="{url}" target="_blank" style="color: #008aff; font-weight: bold; font-size: 1.35rem; text-decoration: none; border-bottom: 1px dashed #008aff;">{title}</a>
        <div style="color: #00ff41; font-size: 1.15rem; margin-top: 8px; padding-left: 45px; line-height: 1.6;">{desc}</div>
    </div>
    """

# --- HEADER SECTION ---
compact_header = f"""
<div style="border-bottom: 2px solid #333; padding-bottom: 12px; margin-bottom: 18px; margin-top: -50px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap;">
        <div>
            <span style="font-size: 1.3rem; font-weight: bold; color: #00ff41; text-shadow: 0 0 5px #00ff41;">🔒 SecAI-Nexus</span>
            <span style="font-size: 0.95rem; color: #008aff; margin-left: 10px; font-weight: bold;">// GLOBAL THREAT VISIBILITY</span>
        </div>
        <div style="font-size: 1.0rem; font-weight: bold; color: #008aff; text-shadow: 0 0 5px #008aff;">SYS_TIME: {datetime.now().strftime("%H:%M:%S")} UTC</div>
    </div>
</div>
"""
st.markdown(compact_header, unsafe_allow_html=True)

# === LIVE CYBER THREAT MAPS ===
st.markdown(f'''
<div style="margin-top: 5px; margin-bottom: 15px; line-height: 1.3;">
    <span style="font-size: 0.85rem; font-weight: bold; color: #00ff41; text-transform: uppercase;">>> LIVE CYBER THREAT MAPS</span><br>
    <span style="font-size: 0.75rem; color: #00ff41; font-family: 'Courier New', monospace;">Real-time global attack activity from trusted sources</span>
</div>
''', unsafe_allow_html=True)

map_row1 = st.columns(4)
map_row2 = st.columns(4)
with map_row1[0]: st.markdown(f'<div style="{BLUE_LABEL}">Bitdefender</div>', unsafe_allow_html=True); render_muted_iframe("https://threatmap.bitdefender.com/", height=450)
with map_row1[1]: st.markdown(f'<div style="{BLUE_LABEL}">Sicherheitstacho (DT)</div>', unsafe_allow_html=True); render_muted_iframe("https://www.sicherheitstacho.eu/?lang=en", height=450)
with map_row1[2]: st.markdown(f'<div style="{BLUE_LABEL}">Check Point ThreatCloud</div>', unsafe_allow_html=True); render_muted_iframe("https://threatmap.checkpoint.com/", height=450)
with map_row1[3]: st.markdown(f'<div style="{BLUE_LABEL}">Radware Live Threat Map</div>', unsafe_allow_html=True); render_muted_iframe("https://livethreatmap.radware.com/", height=450)

with map_row2[0]: st.markdown(f'<div style="{BLUE_LABEL}">Fortinet Threat Map</div>', unsafe_allow_html=True); render_muted_iframe("https://threatmap.fortiguard.com/", height=450)
with map_row2[1]: st.markdown(f'<div style="{BLUE_LABEL}">Kaspersky Cybermap</div>', unsafe_allow_html=True); render_muted_iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", height=450)
with map_row2[2]: st.markdown(f'<div style="{BLUE_LABEL}">SonicWall Live Map</div>', unsafe_allow_html=True); render_muted_iframe("https://attackmap.sonicwall.com/live-attack-map/", height=450)
with map_row2[3]: st.markdown(f'<div style="{BLUE_LABEL}">Threatbutt Attack Map</div>', unsafe_allow_html=True); render_muted_iframe("https://threatbutt.com/map/", height=450)

st.markdown("---")

# === GLOBAL THREAT METRICS (MULTI-DELTA MODULE) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> GLOBAL THREAT METRICS & DELTAS</div>', unsafe_allow_html=True)

# Fetch REAL CISA KEV Data
kev_total, kev_d1, kev_d7, kev_d30 = fetch_real_cisa_kev()

m1, m2, m3, m4 = st.columns(4)

with m1:
    # LIVE REAL DATA
    render_multi_metric("LIVE CISA KEV CATALOG", kev_total, kev_d1, "d-bad", kev_d7, "d-bad", kev_d30, "d-bad")
with m2:
    render_multi_metric("ACTIVE ZERO-DAYS", "7", "+1", "d-bad", "0", "d-neu", "+3", "d-bad")
with m3:
    render_multi_metric("RANSOMWARE VICTIMS", "1,240", "+14", "d-bad", "+89", "d-bad", "+412", "d-bad")
with m4:
    render_multi_metric("PHISHING VOLUME", "CRITICAL", "UP", "d-bad", "UP", "d-bad", "STABLE", "d-neu")

m5, m6, m7, m8 = st.columns(4)

with m5:
    render_multi_metric("GLOBAL AVG MTTD", "16 Days", "-0.2", "d-good", "-1.5", "d-good", "-4.0", "d-good")
with m6:
    render_multi_metric("AVG TTX (TIME TO EXPLOIT)", "5.1 Days", "-0.1", "d-bad", "-1.1", "d-bad", "-2.3", "d-bad")
with m7:
    render_multi_metric("EXPOSED RDP ENDPOINTS", "3.4M", "-10k", "d-good", "-45k", "d-good", "+120k", "d-bad")
with m8:
    render_multi_metric("COMPROMISED CREDS", "14.2M", "+12k", "d-bad", "+88k", "d-bad", "+1.1M", "d-bad")

st.markdown("---")

# === LARGE MAP SECTION (GREYNOISE TRENDS VIEW) ===
st.markdown(f'''
<div style="{GREEN_SUBTITLE}">
    <span style="color: #008aff;">>> GREYNOISE INTELLIGENCE 
    (<a href="https://viz.greynoise.io/trends/trending" target="_blank" style="{LINK_STYLE_BLUE}">https://viz.greynoise.io/trends/trending</a>)</span> 
    - <span style="{SENTENCE_STYLE_GREEN}">A threat intelligence platform that provides insights into cyberattacks, who is scanning the internet, and whether they are malicious. (TRENDS VIEW)</span>
</div>
''', unsafe_allow_html=True)
render_muted_iframe("https://viz.greynoise.io/trends/trending", height=1200)

st.markdown("---")

# === ADDITIONAL GRC RESOURCES (TOP 25) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> ADDITIONAL GRC RESOURCES</div>', unsafe_allow_html=True)

link_col1, link_col2 = st.columns(2)

with link_col1:
    st.markdown(render_simple_link("01", "NIST Cybersecurity Framework (CSF)", "https://www.nist.gov/cyberframework", "Voluntary guidance based on existing standards and practices to better manage and reduce cybersecurity risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("02", "ISO/IEC 27000 Family", "https://www.iso.org/isoiec-27001-information-security.html", "The international standard for establishing and improving Information Security Management Systems (ISMS)."), unsafe_allow_html=True)
    st.markdown(render_simple_link("03", "OWASP Top 10 Project", "https://owasp.org/www-project-top-ten/", "The foundational awareness document for the most critical web application security risks."), unsafe_allow_html=True)
    st.markdown(render_simple_link("04", "NIST National Vulnerability Database (NVD)", "https://nvd.nist.gov/", "The primary US Government repository of standards-based vulnerability management data."), unsafe_allow_html=True)
    st.markdown(render_simple_link("05", "CIS Critical Security Controls", "https://www.cisecurity.org/controls/", "A prioritized set of safeguards to mitigate the most prevalent cyber-attacks against systems and networks."), unsafe_allow_html=True)
    st.markdown(render_simple_link("06", "CISA KEV Catalog", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "The authoritative source for vulnerabilities currently being actively exploited in the wild."), unsafe_allow_html=True)
    st.markdown(render_simple_link("07", "MITRE ATT&CK", "https://mitre-attack.github.io/attack-navigator/", "The industry-standard matrix for mapping adversary tactics, techniques, and procedures (TTPs)."), unsafe_allow_html=True)
    st.markdown(render_simple_link("08", "FIRST CVSS 4.0 Calculator", "https://www.first.org/cvss/calculator/4.0", "The official home of the Common Vulnerability Scoring System for calculating environmental risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("09", "VirusTotal", "https://www.virustotal.com/", "The global standard for analyzing suspicious files, domains, IPs, and URLs for malware."), unsafe_allow_html=True)
    st.markdown(render_simple_link("10", "Exploit Database (Exploit-DB)", "https://www.exploit-db.com/", "The ultimate archive of public exploits and corresponding vulnerable software POCs."), unsafe_allow_html=True)
    st.markdown(render_simple_link("11", "Shodan Search", "https://www.shodan.io/", "The search engine for exposed internet-connected devices, open ports, and vulnerable services."), unsafe_allow_html=True)
    st.markdown(render_simple_link("12", "Have I Been Pwned", "https://haveibeenpwned.com/", "The industry standard for checking if an email address or domain has been compromised in a data breach."), unsafe_allow_html=True)
    st.markdown(render_simple_link("13", "Security Onion", "https://securityonionsolutions.com/", "Free and open-source platform for threat hunting and enterprise security monitoring."), unsafe_allow_html=True)

with link_col2:
    st.markdown(render_simple_link("14", "AlienVault OTX", "https://otx.alienvault.com/", "The largest open threat exchange community for gathering and sharing real-time crowdsourced IOCs."), unsafe_allow_html=True)
    st.markdown(render_simple_link("15", "crt.sh Certificate Search", "https://crt.sh/", "Certificate Transparency log search for mapping external attack surfaces and subdomains."), unsafe_allow_html=True)
    st.markdown(render_simple_link("16", "SANS Internet Storm Center (ISC)", "https://isc.sans.edu/", "Global cooperative cyber threat monitor tracking network anomalies and port trends."), unsafe_allow_html=True)
    st.markdown(render_simple_link("17", "BleepingComputer", "https://www.bleepingcomputer.com/", "A premier, trusted news source for tracking ransomware attacks and daily cyber events."), unsafe_allow_html=True)
    st.markdown(render_simple_link("18", "Abuse.ch URLhaus", "https://urlhaus.abuse.ch/", "Open project dedicated to sharing and tracking malware distribution sites and payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("19", "Any.Run Sandbox", "https://any.run/", "Interactive online malware analysis sandbox allowing researchers to safely observe payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("20", "URLScan.io", "https://urlscan.io/", "A free service to scan and analyze websites to see what a site is actually executing in the background."), unsafe_allow_html=True)
    st.markdown(render_simple_link("21", "GTFOBins", "https://gtfobins.github.io/", "A curated list of Unix binaries used to bypass local security restrictions."), unsafe_allow_html=True)
    st.markdown(render_simple_link("22", "LOLBAS Project", "https://lolbas-project.github.io/", "Living Off The Land Binaries and Scripts for Windows environments."), unsafe_allow_html=True)
    st.markdown(render_simple_link("23", "MalwareBazaar", "https://bazaar.abuse.ch/", "A massive open-source repository of malware samples for research and analysis."), unsafe_allow_html=True)
    st.markdown(render_simple_link("24", "CyberChef (Direct)", "https://gchq.github.io/CyberChef/", "Direct access to the browser-based data manipulation and decoding utility."), unsafe_allow_html=True)
    st.markdown(render_simple_link("25", "The Hacker News", "https://thehackernews.com/", "Trusted and widely-read cybersecurity news platform covering the latest breaches."), unsafe_allow_html=True)

st.markdown("---")

# === DATA ANALYSIS SECTION (CYBERCHEF) ===
st.markdown(f'''
<div style="{GREEN_SUBTITLE}">
    <span style="color: #008aff;">>> CYBERCHEF ANALYSIS TOOL 
    (<a href="https://gchq.github.io/CyberChef/" target="_blank" style="{LINK_STYLE_BLUE}">https://gchq.github.io/CyberChef/</a>)</span> 
    - <span style="{SENTENCE_STYLE_GREEN}">The Cyber Swiss Army Knife. Analyze suspicious payloads, decode malware, and manipulate data locally.</span>
</div>
''', unsafe_allow_html=True)
render_muted_iframe("https://gchq.github.io/CyberChef/", height=1000)

st.markdown("---")

# --- LIVE CVE FEED ---
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> LIVE CVE VULNERABILITIES</div>', unsafe_allow_html=True)
col_sync, col_download, _ = st.columns([1, 2, 4])

def fetch_cve_api():
    try:
        r = requests.get("https://cve.circl.lu/api/last/30", timeout=3)
        if r.status_code == 200:
            c_list = []
            for i in r.json():
                cvss = i.get("cvss") or i.get("cvss3", 0.0)
                if cvss: c_list.append({"ID": i.get("id"), "CVSS": float(cvss), "SUMMARY": i.get("summary", "")[:87]+"..."})
            if c_list: return sorted(c_list, key=lambda x: x['CVSS'], reverse=True)
    except: pass
    return generate_high_fidelity_sim()

if "grc_stream" not in st.session_state: st.session_state.grc_stream = fetch_cve_api()

with col_sync:
    if st.button("🔄 RE-SYNC"):
        st.session_state.grc_stream = fetch_cve_api()
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

# --- RISK LANDSCAPE ---
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

# --- FOOTER ---
st.markdown(f"""
<div style="border-top: 1px solid #333; padding-top: 15px; margin-top: 30px; text-align: center; font-family: 'Courier New', monospace;">
    <span style="color: #008aff; font-size: 0.8rem;">SecAI-Nexus GRC v3.1 | TERMINAL SESSION END</span><br>
    <span style="color: #00ff41; font-size: 0.7rem;">CONNECTION SECURE</span>
</div>
""", unsafe_allow_html=True)
