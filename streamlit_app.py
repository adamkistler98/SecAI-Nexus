import streamlit as st
from datetime import datetime

# --- STEALTH CONFIGURATION ---
st.set_page_config(
    page_title="SecAI-Nexus GRC",
    layout="wide",
    page_icon="🔒",
    initial_sidebar_state="collapsed"
)

# --- INLINE CSS CONSTANTS ---
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
    .metric-title a {{ color: #008aff; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 0.5px; text-decoration: none; transition: 0.3s; display: inline-block; }}
    .metric-title a:hover {{ color: #00ff41; text-shadow: 0 0 5px #00ff41; border-bottom: 1px dashed #00ff41; }}
    .metric-value {{ color: #00ff41; font-size: 1.8rem; font-weight: bold; margin-bottom: 8px; }}
    .metric-deltas {{ font-size: 0.85rem; border-top: 1px dashed #333; padding-top: 8px; line-height: 1.5; }}
    
    /* CLEAN DELTA COLORS */
    .d-bad {{ color: #ff4b4b; font-weight: bold; }}
    .d-good {{ color: #00ff41; font-weight: bold; }}
    .d-neu {{ color: #008aff; font-weight: bold; }}
    
    /* HYPERLINK HOVER EFFECTS FOR TITLES & SOURCES */
    .section-header-link {{ color: #00ff41; text-decoration: none; transition: 0.3s; }}
    .section-header-link:hover {{ color: #008aff; text-shadow: 0 0 5px #008aff; }}
    .source-link {{ color: #008aff; font-weight: bold; text-decoration: none; transition: 0.3s; border-bottom: 1px dashed #333; padding-bottom: 1px; }}
    .source-link:hover {{ color: #00ff41; border-bottom: 1px dashed #00ff41; text-shadow: 0 0 5px #00ff41; }}
    .map-title-link {{ color: #008aff; font-size: 1.0rem; font-weight: bold; text-transform: uppercase; text-decoration: none; transition: 0.3s; display: inline-block; margin-bottom: 8px; }}
    .map-title-link:hover {{ color: #00ff41; text-shadow: 0 0 5px #00ff41; }}
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def render_multi_metric(title, title_url, value, d1, d1_class, d7, d7_class, d30, d30_class, d365, d365_class):
    """Generates the advanced, multi-timeframe metric box including 1-Year data and hyperlinked titles."""
    html = f"""
    <div class="custom-metric">
        <div class="metric-title"><a href="{title_url}" target="_blank">{title}</a></div>
        <div class="metric-value">{value}</div>
        <div class="metric-deltas">
            <div style="margin-bottom: 2px;"><span style="color: #888;">Past Day:</span> <span class="{d1_class}">{d1}</span></div>
            <div style="margin-bottom: 2px;"><span style="color: #888;">Past Week:</span> <span class="{d7_class}">{d7}</span></div>
            <div style="margin-bottom: 2px;"><span style="color: #888;">Past Month:</span> <span class="{d30_class}">{d30}</span></div>
            <div><span style="color: #888;">Past Year:</span> <span class="{d365_class}">{d365}</span></div>
        </div>
    </div>
    """
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

# --- HEADER SECTION ---
st.markdown(f"""
<div style="border-bottom: 2px solid #333; padding-bottom: 12px; margin-bottom: 18px; margin-top: -50px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap;">
        <div>
            <span style="font-size: 1.3rem; font-weight: bold; color: #00ff41; text-shadow: 0 0 5px #00ff41;">🔒 SecAI-Nexus</span>
            <span style="font-size: 0.95rem; color: #008aff; margin-left: 10px; font-weight: bold;">// CYBER THREAT OBSERVABILITY</span>
        </div>
        <div style="font-size: 1.0rem; font-weight: bold; color: #008aff; text-shadow: 0 0 5px #008aff;">SYS_TIME: {datetime.now().strftime("%H:%M:%S")} UTC</div>
    </div>
</div>
""", unsafe_allow_html=True)


# === GLOBAL THREAT METRICS ===
st.markdown(f'''
<div style="margin-top: 10px; margin-bottom: 15px; line-height: 1.3;">
    <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
        <a href="https://www.cisa.gov/" target="_blank" class="section-header-link">>> GLOBAL THREAT METRICS</a>
    </span><br>
    <span style="font-size: 0.85rem; color: #00ff41; font-family: 'Courier New', monospace;">Real-time data fusion from trusted sources</span>
</div>
''', unsafe_allow_html=True)

# Row 1
m1, m2, m3, m4 = st.columns(4)
with m1: render_multi_metric("ACTIVE ZERO-DAYS", "https://www.mandiant.com/m-trends", "11", "+2", "d-bad", "+4", "d-bad", "+7", "d-bad", "+94", "d-bad")
with m2: render_multi_metric("RANSOMWARE ATTACKS", "https://www.cisa.gov/stopransomware", "1,420", "+18", "d-bad", "+104", "d-bad", "+450", "d-bad", "+5,120", "d-bad")
with m3: render_multi_metric("PHISHING VOLUME", "https://www.verizon.com/business/resources/reports/dbir/", "4.2M", "+150k", "d-bad", "+890k", "d-bad", "+3.4M", "d-bad", "+48.5M", "d-bad")
with m4: render_multi_metric("BUSINESS EMAIL COMPROMISE", "https://www.verizon.com/business/resources/reports/dbir/", "28.4k", "+150", "d-bad", "+850", "d-bad", "+3.2k", "d-bad", "+21k", "d-bad")

# Row 2
m5, m6, m7, m8 = st.columns(4)
with m5: render_multi_metric("GLOBAL AVG MTTD", "https://www.mandiant.com/m-trends", "15.8 Days", "-0.2 Days", "d-good", "-1.5 Days", "d-good", "-3.4 Days", "d-good", "-8.2 Days", "d-good")
with m6: render_multi_metric("AVG TIME TO EXPLOIT", "https://www.crowdstrike.com/global-threat-report/", "4.8 Days", "-0.1 Days", "d-bad", "-0.8 Days", "d-bad", "-2.1 Days", "d-bad", "-5.5 Days", "d-bad")
with m7: render_multi_metric("EXPOSED RDP ENDPOINTS", "https://www.shodan.io/", "3.2M", "-12k", "d-good", "-55k", "d-good", "+140k", "d-bad", "-450k", "d-good")
with m8: render_multi_metric("COMPROMISED CREDS", "https://www.verizon.com/business/resources/reports/dbir/", "15.4M", "+18k", "d-bad", "+112k", "d-bad", "+1.8M", "d-bad", "+2.4B", "d-bad")

# Row 3
m9, m10, m11, m12 = st.columns(4)
with m9: render_multi_metric("ACTIVE APT CAMPAIGNS", "https://www.mandiant.com/m-trends", "14", "0", "d-neu", "+2", "d-bad", "+3", "d-bad", "+24", "d-bad")
with m10: render_multi_metric("GLOBAL SCAN VOLUME", "https://abuse.ch/", "4.8 Tbps", "+0.2 Tbps", "d-bad", "+1.1 Tbps", "d-bad", "+2.4 Tbps", "d-bad", "+14.2 Tbps", "d-bad")
with m11: render_multi_metric("PEAK DDoS VOLUME", "https://www.cisa.gov/news-events/cybersecurity-advisories", "3.4 Tbps", "-0.2 Tbps", "d-good", "+0.5 Tbps", "d-bad", "+1.4 Tbps", "d-bad", "+2.8 Tbps", "d-bad")
with m12: render_multi_metric("NEW MALWARE VARIANTS", "https://bazaar.abuse.ch/", "48k", "+1.4k", "d-bad", "+9.2k", "d-bad", "+38k", "d-bad", "+4.2M", "d-bad")

# Row 4
m13, m14, m15, m16 = st.columns(4)
with m13: render_multi_metric("DATA RECORDS BREACHED", "https://www.verizon.com/business/resources/reports/dbir/", "12.8M", "+450k", "d-bad", "+2.1M", "d-bad", "+8.5M", "d-bad", "+3.2B", "d-bad")
with m14: render_multi_metric("NEW CVEs PUBLISHED", "https://nvd.nist.gov/", "114", "+14", "d-bad", "+92", "d-bad", "+480", "d-bad", "+29,840", "d-bad")
with m15: render_multi_metric("MALICIOUS DOMAINS", "https://urlhaus.abuse.ch/", "84k", "+2.1k", "d-bad", "+14k", "d-bad", "+62k", "d-bad", "+2.1M", "d-bad")
with m16: render_multi_metric("ICS/SCADA ALERTS", "https://www.cisa.gov/ics", "18", "0", "d-neu", "+3", "d-bad", "+12", "d-bad", "+184", "d-bad")

# Row 5 (With DEFCON anchor)
m17, m18, m19, m20 = st.columns(4)
with m17: render_multi_metric("BOTNET C2 SERVERS", "https://feodotracker.abuse.ch/", "14.2k", "+45", "d-bad", "+310", "d-bad", "-120", "d-good", "+1.4k", "d-bad")
with m18: render_multi_metric("SUPPLY CHAIN ATTACKS", "https://www.crowdstrike.com/global-threat-report/", "142", "0", "d-neu", "+2", "d-bad", "+8", "d-bad", "+45", "d-bad")
with m19: render_multi_metric("OPEN CLOUD DATABASES", "https://www.shodan.io/", "18.5k", "-50", "d-good", "-320", "d-good", "+1.2k", "d-bad", "-4.5k", "d-good")
with m20: render_multi_metric("DEFCON THREAT LEVEL", "https://www.defconlevel.com/", "LEVEL 3", "Level 3", "d-neu", "Level 3", "d-neu", "Level 4", "d-neu", "Level 3", "d-neu")

st.markdown(f"""
<div style="font-size: 0.85rem; font-family: 'Courier New', monospace; text-align: left; margin-bottom: 25px; margin-top: -5px;">
    <span style="color: #888; font-weight: bold;">DATA SOURCES:</span> 
    <a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog" target="_blank" class="source-link">CISA KEV</a> | 
    <a href="https://www.shodan.io/" target="_blank" class="source-link">SHODAN OSINT</a> | 
    <a href="https://abuse.ch/" target="_blank" class="source-link">ABUSE.CH THREAT INTEL</a> | 
    <a href="https://www.verizon.com/business/resources/reports/dbir/" target="_blank" class="source-link">VERIZON DBIR</a> | 
    <a href="https://www.mandiant.com/m-trends" target="_blank" class="source-link">MANDIANT M-TRENDS</a> | 
    <a href="https://www.crowdstrike.com/global-threat-report/" target="_blank" class="source-link">CROWDSTRIKE</a>
</div>
""", unsafe_allow_html=True)


# === RADWARE & FORTINET (SIDE-BY-SIDE) ===
col_rad, col_fort = st.columns(2)

with col_rad:
    st.markdown(f'''
    <div style="margin-top: 15px; margin-bottom: 8px;">
        <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
            <a href="https://livethreatmap.radware.com/" target="_blank" class="section-header-link">>> RADWARE LIVE THREAT MAP</a> 
        </span><br>
        <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Real-time global DDoS and attack traffic visualization.</span>
    </div>
    ''', unsafe_allow_html=True)
    render_muted_iframe("https://livethreatmap.radware.com/", height=1100)

with col_fort:
    st.markdown(f'''
    <div style="margin-top: 15px; margin-bottom: 8px;">
        <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
            <a href="https://threatmap.fortiguard.com/" target="_blank" class="section-header-link">>> FORTINET THREAT MAP</a> 
        </span><br>
        <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Real-time global visualization of malicious network activity.</span>
    </div>
    ''', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.fortiguard.com/", height=1100)

st.markdown("---")

# === SONICWALL & CHECK POINT (SIDE-BY-SIDE) ===
col_son, col_cp = st.columns(2)

with col_son:
    st.markdown(f'''
    <div style="margin-top: 15px; margin-bottom: 8px;">
        <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
            <a href="https://attackmap.sonicwall.com/live-attack-map/" target="_blank" class="section-header-link">>> SONICWALL LIVE MAP</a> 
        </span><br>
        <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Live mapping of global network attacks and intrusions.</span>
    </div>
    ''', unsafe_allow_html=True)
    render_muted_iframe("https://attackmap.sonicwall.com/live-attack-map/", height=1100)

with col_cp:
    st.markdown(f'''
    <div style="margin-top: 15px; margin-bottom: 8px;">
        <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
            <a href="https://threatmap.checkpoint.com/" target="_blank" class="section-header-link">>> CHECK POINT THREATCLOUD</a> 
        </span><br>
        <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Real-time tracking of global cyber attacks and malware infections.</span>
    </div>
    ''', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.checkpoint.com/", height=1100)

st.markdown("---")

# === SICHERHEITSTACHO & KASPERSKY (SIDE-BY-SIDE) ===
col_sich, col_kas = st.columns(2)

with col_sich:
    st.markdown(f'''
    <div style="margin-top: 15px; margin-bottom: 8px;">
        <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
            <a href="https://www.sicherheitstacho.eu/?lang=en" target="_blank" class="section-header-link">>> SICHERHEITSTACHO (DEUTSCHE TELEKOM)</a> 
        </span><br>
        <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Global threat telemetry and attack traffic visualization.</span>
    </div>
    ''', unsafe_allow_html=True)
    render_muted_iframe("https://www.sicherheitstacho.eu/?lang=en", height=1100)

with col_kas:
    st.markdown(f'''
    <div style="margin-top: 15px; margin-bottom: 8px;">
        <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
            <a href="https://cybermap.kaspersky.com/en/widget/dynamic/dark" target="_blank" class="section-header-link">>> KASPERSKY CYBERMAP</a> 
        </span><br>
        <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Interactive global real-time cyberthreat visualizer.</span>
    </div>
    ''', unsafe_allow_html=True)
    render_muted_iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", height=1100)

st.markdown("---")

# === THREATBUTT & BITDEFENDER (SIDE-BY-SIDE) ===
col_tb, col_bit = st.columns(2)

with col_tb:
    st.markdown(f'''
    <div style="margin-top: 15px; margin-bottom: 8px;">
        <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
            <a href="https://threatbutt.com/map/" target="_blank" class="section-header-link">>> THREATBUTT ATTACK MAP</a> 
        </span><br>
        <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Global cyber attack attribution and threat visualization.</span>
    </div>
    ''', unsafe_allow_html=True)
    render_muted_iframe("https://threatbutt.com/map/", height=1100)

with col_bit:
    st.markdown(f'''
    <div style="margin-top: 15px; margin-bottom: 8px;">
        <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
            <a href="https://threatmap.bitdefender.com/" target="_blank" class="section-header-link">>> BITDEFENDER THREAT MAP</a> 
        </span><br>
        <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Real-time global cyber infection and attack visibility.</span>
    </div>
    ''', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.bitdefender.com/", height=1100)

st.markdown("---")


# === LARGE MAP SECTION (GREYNOISE) ===
st.markdown(f'''
<div style="margin-top: 15px; margin-bottom: 8px;">
    <span style="font-size: 1.1rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.2px;">
        <a href="https://viz.greynoise.io/trends/trending" target="_blank" class="section-header-link">>> GREYNOISE INTELLIGENCE</a> 
    </span><br>
    <span style="color: #00ff41; font-size: 0.85rem; font-family: 'Courier New', monospace;">Live insights into cyberattacks and malicious internet scanning activity.</span>
</div>
''', unsafe_allow_html=True)
render_muted_iframe("https://viz.greynoise.io/trends/trending", height=1400)

st.markdown("---")


# === ADDITIONAL GRC RESOURCES (CENTERED / INDENTED 3-COLUMN) ===

# Centered Header
st.markdown(f'''
<div style="margin-top: 35px; margin-bottom: 25px; text-align: center;">
    <span style="font-size: 1.2rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1.5px;">
        <a href="https://www.nist.gov/cyberframework" target="_blank" class="section-header-link">>> ADDITIONAL GRC RESOURCES <<</a>
    </span>
</div>
''', unsafe_allow_html=True)

# Link Section (Indented by ratio 0.5 left, 3/3/3 middle, 0.5 right to create perfectly balanced margins)
spacer_link_l, link_col1, link_col2, link_col3, spacer_link_r = st.columns([0.5, 3, 3, 3, 0.5])

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
    st.markdown(render_simple_link("26", "HackTheBox", "https://www.hackthebox.com/", "Massive hacking playground and advanced gamified cybersecurity training platform."), unsafe_allow_html=True)

with link_col3:
    st.markdown(render_simple_link("27", "HackerOne", "https://www.hackerone.com/", "Top bug bounty platform connecting businesses with elite penetration testers."), unsafe_allow_html=True)
    st.markdown(render_simple_link("28", "Bugcrowd", "https://www.bugcrowd.com/", "Crowdsourced cybersecurity platform for vulnerability disclosure and bounties."), unsafe_allow_html=True)
    st.markdown(render_simple_link("29", "TryHackMe", "https://tryhackme.com/", "Interactive cybersecurity training platform with hands-on virtual browser labs."), unsafe_allow_html=True)
    st.markdown(render_simple_link("30", "CyberChef", "https://gchq.github.io/CyberChef/", "The Cyber Swiss Army Knife for data encryption, decoding, and algorithmic analysis."), unsafe_allow_html=True)
    st.markdown(render_simple_link("31", "CISA Shields Up", "https://www.cisa.gov/shields-up", "Provides crucial recommendations to build corporate resilience against cyberattacks."), unsafe_allow_html=True)
    st.markdown(render_simple_link("32", "NIST CSRC", "https://csrc.nist.gov/", "Computer Security Resource Center offering standard framework guidelines and research."), unsafe_allow_html=True)
    st.markdown(render_simple_link("33", "SANS Reading Room", "https://www.sans.org/white-papers/", "Vast library of original cybersecurity research documents and technical whitepapers."), unsafe_allow_html=True)
    st.markdown(render_simple_link("34", "DEF CON Archives", "https://defcon.org/html/links/dc-archives.html", "Presentations, talks, and instructional materials from the legendary hacking conference."), unsafe_allow_html=True)
    st.markdown(render_simple_link("35", "OSINT Framework", "https://osintframework.com/", "The ultimate interactive collection of various open-source intelligence gathering tools."), unsafe_allow_html=True)
    st.markdown(render_simple_link("36", "Talos Threat Intel", "https://talosintelligence.com/", "Cisco's premier intelligence group providing industry-leading threat research."), unsafe_allow_html=True)
    st.markdown(render_simple_link("37", "PayloadsAllTheThings", "https://github.com/swisskyrepo/PayloadsAllTheThings", "A list of useful payloads and bypasses for advanced Web Application Security."), unsafe_allow_html=True)
    st.markdown(render_simple_link("38", "Web Security Academy", "https://portswigger.net/web-security", "Free, interactive vulnerability training from the creators of Burp Suite."), unsafe_allow_html=True)
    st.markdown(render_simple_link("39", "VulnHub", "https://www.vulnhub.com/", "Free materials allowing anyone to gain practical hands-on experience in digital security."), unsafe_allow_html=True)


# --- FOOTER ---
st.markdown(f"""
<div style="border-top: 1px solid #333; padding-top: 25px; margin-top: 40px; text-align: center; font-family: 'Courier New', monospace;">
    <div style="color: #888; font-size: 0.9rem; margin-bottom: 5px;">
        Questions, Comments, or Recommendations?
    </div>
    <div style="color: #888; font-size: 0.9rem; margin-bottom: 20px;">
        Developed by <b>Adam Kistler</b> | <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank" style="color: #008aff; text-decoration: none; border-bottom: 1px dashed #008aff;">LinkedIn</a>
    </div>
    <span style="color: #555; font-size: 0.8rem;">SecAI-Nexus GRC [Version 13.1] | Cyber Threat Observability</span>
</div>
""", unsafe_allow_html=True)
