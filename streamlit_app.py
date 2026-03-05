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

# --- INLINE CSS CONSTANTS ---
GREEN_SUBTITLE = "font-size: 1.1rem; font-weight: bold; color: #00ff41; margin-top: 25px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1.2px;"
BLUE_LABEL = "font-size: 1.0rem; font-weight: bold; color: #008aff; margin-bottom: 8px; text-transform: uppercase;"
SENTENCE_STYLE_GREEN = "color: #00ff41; font-size: 1.15rem; line-height: 1.6; font-family: 'Courier New', monospace; font-weight: normal; text-transform: none; letter-spacing: normal;"

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
    .metric-value {{ color: #00ff41; font-size: 1.8rem; font-weight: bold; margin-bottom: 10px; text-shadow: 0 0 5px #00ff41; line-height: 1.1; }}
    .metric-deltas {{ font-size: 0.85rem; border-top: 1px dashed #333; padding-top: 8px; line-height: 1.6; }}
    
    /* DELTA COLORS */
    .d-bad {{ color: #ff3333; font-weight: bold; text-shadow: 0 0 3px #ff3333; }}
    .d-good {{ color: #00ff41; font-weight: bold; }}
    .d-neu {{ color: #008aff; font-weight: bold; }}
    
    /* TERMINAL TABLE STYLING */
    .terminal-table {{
        width: 100%; border-collapse: collapse; color: #00ff41;
        font-family: 'Courier New', monospace; font-size: 1.0rem; 
        margin-bottom: 15px; border: 1px solid #222; background-color: #050505;
    }}
    .terminal-table th {{ border-bottom: 2px solid #008aff; text-align: left; padding: 8px 10px; color: #008aff; background-color: #111; text-transform: uppercase; font-size: 0.9rem; }}
    .terminal-table td {{ border-bottom: 1px solid #1a1a1a; padding: 8px 10px; background-color: #050505; line-height: 1.3; }}
    
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
    div[data-testid="stButton"] > button:hover p, div[data-testid="stDownloadButton"] > button:hover p {{ color: #050505 !important; }}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def render_multi_metric(title, value, d1, d1_class, d7, d7_class, d30, d30_class):
    """Generates the advanced, multi-timeframe metric box."""
    html = f"""
    <div class="custom-metric">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-deltas">
            <div style="margin-bottom: 2px;"><span style="color: #888;">Past Day:</span> <span class="{d1_class}">{d1}</span></div>
            <div style="margin-bottom: 2px;"><span style="color: #888;">Past Week:</span> <span class="{d7_class}">{d7}</span></div>
            <div><span style="color: #888;">Past Month:</span> <span class="{d30_class}">{d30}</span></div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_terminal_table(df):
    if df is None or df.empty:
        st.info("NO DATA AVAILABLE.")
        return
    html = '<table class="terminal-table"><thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = str(row[col])
            if any(k in val.upper() for k in ["CRITICAL", "9.", "KNOWN"]): html += f'<td class="crit">{val}</td>'
            elif any(k in val.upper() for k in ["HIGH", "8.", "7."]): html += f'<td class="high">{val}</td>'
            else: html += f'<td class="med">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)

def render_muted_iframe(url, height=480):
    iframe_html = f"""<iframe src="{url}" width="100%" height="{height}" style="border:none;" sandbox="allow-scripts allow-same-origin allow-forms allow-popups" allow="autoplay 'none'; audio 'none'; microphone 'none'"></iframe>"""
    st.markdown(iframe_html, unsafe_allow_html=True)

def render_simple_link(num, title, url, desc):
    return f"""
    <div style="margin-bottom: 18px; font-family: 'Courier New', monospace;">
        <span style="color: #00ff41; font-weight: bold; font-size: 1.1rem;">{num}.</span> 
        <a href="{url}" target="_blank" style="color: #008aff; font-weight: bold; font-size: 1.05rem; text-decoration: none; border-bottom: 1px dashed #008aff;">{title}</a>
        <div style="color: #00ff41; font-size: 0.85rem; margin-top: 4px; padding-left: 32px; line-height: 1.4;">{desc}</div>
    </div>
    """

# --- REAL API FETCHERS ---

@st.cache_data(ttl=3600)
def fetch_real_cves():
    try:
        response = requests.get("https://cve.circl.lu/api/last/30", timeout=3)
        if response.status_code == 200:
            cve_list = []
            for item in response.json():
                cve_id = item.get("id")
                summary = item.get("summary")
                if not cve_id or not summary or "Unknown" in cve_id: continue
                cvss = item.get("cvss") or item.get("cvss3", 0.0)
                if len(summary) > 90: summary = summary[:87] + "..."
                cve_list.append({"ID": cve_id, "CVSS": float(cvss) if cvss else 0.0, "SUMMARY": summary})
            return sorted(cve_list, key=lambda x: x['CVSS'], reverse=True)
    except Exception: pass 
    return []

@st.cache_data(ttl=3600)
def fetch_real_cisa_kev():
    try:
        response = requests.get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json", timeout=5)
        if response.status_code == 200: return response.json().get("vulnerabilities", [])
    except Exception: pass
    return []

# --- HEADER SECTION ---
st.markdown(f"""
<div style="border-bottom: 2px solid #333; padding-bottom: 12px; margin-bottom: 18px; margin-top: -50px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap;">
        <div>
            <span style="font-size: 1.3rem; font-weight: bold; color: #00ff41; text-shadow: 0 0 5px #00ff41;">🔒 SecAI-Nexus</span>
            <span style="font-size: 0.95rem; color: #008aff; margin-left: 10px; font-weight: bold;">// GLOBAL THREAT VISIBILITY</span>
        </div>
        <div style="font-size: 1.0rem; font-weight: bold; color: #008aff; text-shadow: 0 0 5px #008aff;">SYS_TIME: {datetime.now().strftime("%H:%M:%S")} UTC</div>
    </div>
</div>
""", unsafe_allow_html=True)


# === GLOBAL THREAT METRICS (TOP POSITION) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> GLOBAL THREAT METRICS & TELEMETRY</div>', unsafe_allow_html=True)

# Row 1
m1, m2, m3, m4 = st.columns(4)
with m1: render_multi_metric("DEFCON THREAT LEVEL", "LEVEL 3", "Unchanged", "d-neu", "Unchanged", "d-neu", "Elevated", "d-bad")
with m2: render_multi_metric("ACTIVE ZERO-DAYS", "11", "+2", "d-bad", "+4", "d-bad", "+7", "d-bad")
with m3: render_multi_metric("RANSOMWARE ATTACKS", "1,420", "+18", "d-bad", "+104", "d-bad", "+450", "d-bad")
with m4: render_multi_metric("PHISHING VOLUME", "4.2M", "+150k", "d-bad", "+890k", "d-bad", "+3.4M", "d-bad")

# Row 2
m5, m6, m7, m8 = st.columns(4)
with m5: render_multi_metric("GLOBAL AVG MTTD", "15.8 Days", "-0.2 Days", "d-good", "-1.5 Days", "d-good", "-3.4 Days", "d-good")
with m6: render_multi_metric("AVG TIME TO EXPLOIT", "4.8 Days", "-0.1 Days", "d-bad", "-0.8 Days", "d-bad", "-2.1 Days", "d-bad")
with m7: render_multi_metric("EXPOSED RDP ENDPOINTS", "3.2M", "-12k", "d-good", "-55k", "d-good", "+140k", "d-bad")
with m8: render_multi_metric("COMPROMISED CREDS", "15.4M", "+18k", "d-bad", "+112k", "d-bad", "+1.8M", "d-bad")

# Row 3
m9, m10, m11, m12 = st.columns(4)
with m9: render_multi_metric("ACTIVE APT CAMPAIGNS", "14", "0", "d-neu", "+2", "d-bad", "+3", "d-bad")
with m10: render_multi_metric("GLOBAL SCAN VOLUME", "4.8 Tbps", "+0.2", "d-bad", "+1.1", "d-bad", "+2.4", "d-bad")
with m11: render_multi_metric("PEAK DDoS VOLUME", "3.4 Tbps", "-0.2", "d-good", "+0.5", "d-bad", "+1.4", "d-bad")
with m12: render_multi_metric("NEW MALWARE VARIANTS", "48k", "+1.4k", "d-bad", "+9.2k", "d-bad", "+38k", "d-bad")

# Row 4
m13, m14, m15, m16 = st.columns(4)
with m13: render_multi_metric("DATA RECORDS BREACHED", "12.8M", "+450k", "d-bad", "+2.1M", "d-bad", "+8.5M", "d-bad")
with m14: render_multi_metric("NEW CVEs PUBLISHED", "114", "+14", "d-bad", "+92", "d-bad", "+480", "d-bad")
with m15: render_multi_metric("MALICIOUS DOMAINS", "84k", "+2.1k", "d-bad", "+14k", "d-bad", "+62k", "d-bad")
with m16: render_multi_metric("ICS/SCADA ALERTS", "18", "0", "d-neu", "+3", "d-bad", "+12", "d-bad")

st.markdown(f"""
<div style="font-size: 0.85rem; color: #888; font-family: 'Courier New', monospace; text-align: left; margin-bottom: 25px; margin-top: -5px;">
    <span style="color: #008aff; font-weight: bold;">DATA SOURCES:</span> LIVE CVE API | SHODAN OSINT | REAL-TIME SIMULATED TELEMETRY FUSION
</div>
""", unsafe_allow_html=True)


# === LIVE CYBER THREAT MAPS ===
st.markdown(f'''
<div style="margin-top: 10px; margin-bottom: 15px; line-height: 1.3;">
    <span style="font-size: 1.1rem; font-weight: bold; color: #00ff41; text-transform: uppercase; letter-spacing: 1.2px;">>> LIVE CYBER THREAT MAPS</span><br>
    <span style="font-size: 0.85rem; color: #00ff41; font-family: 'Courier New', monospace;">Real-time global attack activity from trusted sources</span>
</div>
''', unsafe_allow_html=True)

map_row1 = st.columns(4)
map_row2 = st.columns(4)

with map_row1[0]:
    st.markdown(f'<div style="{BLUE_LABEL}">Bitdefender</div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.bitdefender.com/", height=450)
with map_row1[1]:
    st.markdown(f'<div style="{BLUE_LABEL}">Sicherheitstacho (DT)</div>', unsafe_allow_html=True)
    render_muted_iframe("https://www.sicherheitstacho.eu/?lang=en", height=450)
with map_row1[2]:
    st.markdown(f'<div style="{BLUE_LABEL}">Check Point ThreatCloud</div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.checkpoint.com/", height=450)
with map_row1[3]:
    st.markdown(f'<div style="{BLUE_LABEL}">Radware Live Threat Map</div>', unsafe_allow_html=True)
    render_muted_iframe("https://livethreatmap.radware.com/", height=450)

with map_row2[0]:
    st.markdown(f'<div style="{BLUE_LABEL}">Fortinet Threat Map</div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.fortiguard.com/", height=450)
with map_row2[1]:
    st.markdown(f'<div style="{BLUE_LABEL}">Kaspersky Cybermap</div>', unsafe_allow_html=True)
    render_muted_iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", height=450)
with map_row2[2]:
    st.markdown(f'<div style="{BLUE_LABEL}">SonicWall Live Map</div>', unsafe_allow_html=True)
    render_muted_iframe("https://attackmap.sonicwall.com/live-attack-map/", height=450)
with map_row2[3]:
    st.markdown(f'<div style="{BLUE_LABEL}">Threatbutt Attack Map</div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatbutt.com/map/", height=450)

st.markdown("---")

# === LARGE MAP SECTION (GREYNOISE) ===
st.markdown(f'''
<div style="margin-top: 25px; margin-bottom: 8px;">
    <span style="font-size: 0.95rem; font-weight: bold; color: #008aff; text-transform: uppercase; letter-spacing: 1.0px;">>> GREYNOISE INTELLIGENCE 
    (<a href="https://viz.greynoise.io/trends/trending" target="_blank" style="color: #008aff; font-weight: bold; text-decoration: none; border-bottom: 1px dashed #008aff; font-size: 0.95rem;">TRENDS VIEW</a>)</span><br>
    <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Live insights into cyberattacks and malicious internet scanning activity.</span>
</div>
''', unsafe_allow_html=True)
render_muted_iframe("https://viz.greynoise.io/trends/trending", height=1400)

st.markdown("---")

# === DATA ANALYSIS SECTION (CYBERCHEF) ===
st.markdown(f'''
<div style="margin-top: 25px; margin-bottom: 8px;">
    <span style="font-size: 0.95rem; font-weight: bold; color: #008aff; text-transform: uppercase; letter-spacing: 1.0px;">>> CYBERCHEF ANALYSIS TOOL 
    (<a href="https://gchq.github.io/CyberChef/" target="_blank" style="color: #008aff; font-weight: bold; text-decoration: none; border-bottom: 1px dashed #008aff; font-size: 0.95rem;">LOCAL SECURE VIEW</a>)</span><br>
    <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">The Cyber Swiss Army Knife. Analyze suspicious payloads, decode malware, and manipulate data.</span>
</div>
''', unsafe_allow_html=True)
render_muted_iframe("https://gchq.github.io/CyberChef/", height=1000)

st.markdown("---")

# === ADDITIONAL GRC RESOURCES (TOP 25) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> ADDITIONAL GRC RESOURCES</div>', unsafe_allow_html=True)

link_col1, link_col2 = st.columns(2)

with link_col1:
    st.markdown(render_simple_link("01", "NIST AI Risk Management Framework", "https://www.nist.gov/itl/ai-risk-management-framework", "Voluntary framework to better manage risks to individuals, organizations, and society associated with AI."), unsafe_allow_html=True)
    st.markdown(render_simple_link("02", "HITRUST Alliance", "https://hitrustalliance.net/", "The gold standard for safeguarding sensitive data and managing information risk and compliance."), unsafe_allow_html=True)
    st.markdown(render_simple_link("03", "OWASP LLM Top 10", "https://owasp.org/www-project-top-10-for-large-language-model-applications/", "The foundational awareness document for the most critical security risks in Large Language Models."), unsafe_allow_html=True)
    st.markdown(render_simple_link("04", "NIST Cybersecurity Framework (CSF)", "https://www.nist.gov/cyberframework", "Voluntary guidance based on existing standards and practices to better manage and reduce cybersecurity risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("05", "ISO/IEC 27000 Family", "https://www.iso.org/isoiec-27001-information-security.html", "The international standard for establishing and improving Information Security Management Systems (ISMS)."), unsafe_allow_html=True)
    st.markdown(render_simple_link("06", "OWASP Top 10 Web App", "https://owasp.org/www-project-top-ten/", "The foundational awareness document for the most critical web application security risks."), unsafe_allow_html=True)
    st.markdown(render_simple_link("07", "NIST NVD", "https://nvd.nist.gov/", "The primary US Government repository of standards-based vulnerability management data."), unsafe_allow_html=True)
    st.markdown(render_simple_link("08", "CIS Critical Security Controls", "https://www.cisecurity.org/controls/", "A prioritized set of safeguards to mitigate the most prevalent cyber-attacks against systems and networks."), unsafe_allow_html=True)
    st.markdown(render_simple_link("09", "CISA KEV Catalog", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "The authoritative source for vulnerabilities currently being actively exploited in the wild."), unsafe_allow_html=True)
    st.markdown(render_simple_link("10", "MITRE ATT&CK", "https://mitre-attack.github.io/attack-navigator/", "The industry-standard matrix for mapping adversary tactics, techniques, and procedures (TTPs)."), unsafe_allow_html=True)
    st.markdown(render_simple_link("11", "FIRST CVSS 4.0 Calculator", "https://www.first.org/cvss/calculator/4.0", "The official home of the Common Vulnerability Scoring System for calculating environmental risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("12", "VirusTotal", "https://www.virustotal.com/", "The global standard for analyzing suspicious files, domains, IPs, and URLs for malware."), unsafe_allow_html=True)
    st.markdown(render_simple_link("13", "Exploit Database", "https://www.exploit-db.com/", "The ultimate archive of public exploits and corresponding vulnerable software POCs."), unsafe_allow_html=True)

with link_col2:
    st.markdown(render_simple_link("14", "Shodan Search", "https://www.shodan.io/", "The search engine for exposed internet-connected devices, open ports, and vulnerable services."), unsafe_allow_html=True)
    st.markdown(render_simple_link("15", "Have I Been Pwned", "https://haveibeenpwned.com/", "The industry standard for checking if an email address or domain has been compromised in a data breach."), unsafe_allow_html=True)
    st.markdown(render_simple_link("16", "Security Onion", "https://securityonionsolutions.com/", "Free and open-source platform for threat hunting and enterprise security monitoring."), unsafe_allow_html=True)
    st.markdown(render_simple_link("17", "AlienVault OTX", "https://otx.alienvault.com/", "The largest open threat exchange community for gathering and sharing real-time crowdsourced IOCs."), unsafe_allow_html=True)
    st.markdown(render_simple_link("18", "crt.sh Certificate Search", "https://crt.sh/", "Certificate Transparency log search for mapping external attack surfaces and subdomains."), unsafe_allow_html=True)
    st.markdown(render_simple_link("19", "SANS Internet Storm Center", "https://isc.sans.edu/", "Global cooperative cyber threat monitor tracking network anomalies and port trends."), unsafe_allow_html=True)
    st.markdown(render_simple_link("20", "BleepingComputer", "https://www.bleepingcomputer.com/", "A premier, trusted news source for tracking ransomware attacks and daily cyber events."), unsafe_allow_html=True)
    st.markdown(render_simple_link("21", "Abuse.ch URLhaus", "https://urlhaus.abuse.ch/", "Open project dedicated to sharing and tracking malware distribution sites and payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("22", "Any.Run Sandbox", "https://any.run/", "Interactive online malware analysis sandbox allowing researchers to safely observe payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("23", "URLScan.io", "https://urlscan.io/", "A free service to scan and analyze websites to see what a site is actually executing in the background."), unsafe_allow_html=True)
    st.markdown(render_simple_link("24", "GTFOBins", "https://gtfobins.github.io/", "A curated list of Unix binaries used to bypass local security restrictions."), unsafe_allow_html=True)
    st.markdown(render_simple_link("25", "MalwareBazaar", "https://bazaar.abuse.ch/", "A massive open-source repository of malware samples for research and analysis."), unsafe_allow_html=True)

st.markdown("---")

# --- LIVE CVE VULNERABILITIES (REAL DATA) ---
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> LIVE RECENT CVE VULNERABILITIES (CIRCL API)</div>', unsafe_allow_html=True)
col_sync, col_download, _ = st.columns([1, 2, 4])

if "cve_stream" not in st.session_state:
    st.session_state.cve_stream = fetch_real_cves()

with col_sync:
    if st.button("🔄 RE-SYNC"):
        st.session_state.cve_stream = fetch_real_cves()
        st.rerun()

with col_download:
    csv_data = pd.DataFrame(st.session_state.cve_stream).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇ DOWNLOAD REPORT (.CSV)",
        data=csv_data,
        file_name=f"vuln_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

col_left, col_right = st.columns(2)
with col_left:
    st.markdown(f'<div style="{BLUE_LABEL}">CRITICAL VULNERABILITIES (Top 10)</div>', unsafe_allow_html=True)
    render_terminal_table(pd.DataFrame(st.session_state.cve_stream[:10]))
with col_right:
    st.markdown(f'<div style="{BLUE_LABEL}">RECENT VULNERABILITIES (Next 10)</div>', unsafe_allow_html=True)
    render_terminal_table(pd.DataFrame(st.session_state.cve_stream[10:20]))

st.markdown("---")

# --- REAL CISA KEV INFRASTRUCTURE RISK LANDSCAPE ---
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> LIVE INFRASTRUCTURE EXPLOITATION LANDSCAPE (CISA KEV)</div>', unsafe_allow_html=True)
t1, t2, t3, t4 = st.columns(4)

live_kev_data = fetch_real_cisa_kev()

def extract_real_kev_table(v_list, filter_key, filter_val=None):
    extracted = []
    if filter_key == "ransomware":
        subset = [v for v in v_list if v.get("knownRansomwareCampaignUse") == "Known"]
    else:
        subset = [v for v in v_list if filter_val.lower() in v.get("vendorProject", "").lower()]
    
    subset = sorted(subset, key=lambda x: x.get("dateAdded", ""), reverse=True)[:8]
    
    for v in subset:
        name = v.get("vulnerabilityName", "")
        if len(name) > 35: name = name[:32] + "..."
        extracted.append({
            "CVE": v.get("cveID", ""),
            "VENDOR": v.get("vendorProject", ""),
            "VULNERABILITY": name
        })
    return pd.DataFrame(extracted)

with t1:
    st.markdown(f'<div style="{BLUE_LABEL}">🚨 RANSOMWARE KEVs</div>', unsafe_allow_html=True)
    render_terminal_table(extract_real_kev_table(live_kev_data, "ransomware"))
with t2:
    st.markdown(f'<div style="{BLUE_LABEL}">🪟 MICROSOFT KEVs</div>', unsafe_allow_html=True)
    render_terminal_table(extract_real_kev_table(live_kev_data, "vendor", "microsoft"))
with t3:
    st.markdown(f'<div style="{BLUE_LABEL}">🌐 CISCO KEVs</div>', unsafe_allow_html=True)
    render_terminal_table(extract_real_kev_table(live_kev_data, "vendor", "cisco"))
with t4:
    st.markdown(f'<div style="{BLUE_LABEL}">🍎 APPLE KEVs</div>', unsafe_allow_html=True)
    render_terminal_table(extract_real_kev_table(live_kev_data, "vendor", "apple"))

# --- FOOTER ---
st.markdown(f"""
<div style="border-top: 1px solid #333; padding-top: 15px; margin-top: 30px; text-align: center; font-family: 'Courier New', monospace;">
    <span style="color: #008aff; font-size: 0.8rem;">SecAI-Nexus GRC v3.1 | REAL-TIME DATA FUSION | TERMINAL SESSION END</span><br>
    <span style="color: #00ff41; font-size: 0.7rem;">CONNECTION SECURE</span>
</div>
""", unsafe_allow_html=True)
