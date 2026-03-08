import streamlit as st
from datetime import datetime

st.set_page_config(page_title="SecAI-Nexus GRC", layout="wide", page_icon="🔒", initial_sidebar_state="collapsed")

SENTENCE_STYLE_GREEN = "color: #00ff41; font-size: 1.15rem; line-height: 1.6; font-family: 'Courier New', monospace; font-weight: normal; text-transform: none; letter-spacing: normal;"

st.markdown(f"""
<style>
    .stApp {{ background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }}
    div[data-testid="stMarkdownContainer"] > p {{ {SENTENCE_STYLE_GREEN} }}
    h1, h2, h3, h4, h5, h6, label {{ color: #00ff41 !important; }}
    header, footer {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}
    .custom-metric {{ background-color: #0a0a0a; border: 1px solid #333; border-left: 4px solid #008aff; padding: 12px 15px; margin-bottom: 15px; font-family: 'Courier New', monospace; }}
    .metric-title a {{ color: #008aff; font-size: 0.85rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 0.5px; text-decoration: none; transition: 0.3s; display: inline-block; }}
    .metric-title a:hover {{ color: #00ff41; text-shadow: 0 0 5px #00ff41; border-bottom: 1px dashed #00ff41; }}
    .metric-value {{ color: #00ff41; font-size: 1.8rem; font-weight: bold; margin-bottom: 8px; }}
    .metric-deltas {{ font-size: 0.85rem; border-top: 1px dashed #333; padding-top: 8px; line-height: 1.5; }}
    .d-bad {{ color: #ff4b4b; font-weight: bold; }}
    .d-good {{ color: #00ff41; font-weight: bold; }}
    .d-neu {{ color: #008aff; font-weight: bold; }}
    .section-header-link {{ color: #00ff41; text-decoration: none; transition: 0.3s; }}
    .section-header-link:hover {{ color: #008aff; text-shadow: 0 0 5px #008aff; }}
    .source-link {{ color: #008aff; font-weight: bold; text-decoration: none; transition: 0.3s; border-bottom: 1px dashed #333; padding-bottom: 1px; }}
    .source-link:hover {{ color: #00ff41; border-bottom: 1px dashed #00ff41; text-shadow: 0 0 5px #00ff41; }}
    .map-title-link {{ color: #008aff; font-size: 1.0rem; font-weight: bold; text-transform: uppercase; text-decoration: none; transition: 0.3s; display: inline-block; margin-bottom: 8px; }}
    .map-title-link:hover {{ color: #00ff41; text-shadow: 0 0 5px #00ff41; }}
    .footer-license-link {{ color: #555; text-decoration: none; border-bottom: 1px dashed #555; transition: 0.3s; }}
    .footer-license-link:hover {{ color: #00ff41; border-bottom: 1px dashed #00ff41; }}
</style>
""", unsafe_allow_html=True)

def render_muted_iframe(url, height=480):
    st.markdown(f'<iframe src="{url}" width="100%" height="{height}" style="border:none;" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>', unsafe_allow_html=True)

def render_simple_link(num, title, url, desc):
    return (f'<div style="margin-bottom:18px;font-family:\'Courier New\',monospace;">'
            f'<span style="color:#00ff41;font-weight:bold;font-size:1.1rem;">{num}.</span> '
            f'<a href="{url}" target="_blank" style="color:#008aff;font-weight:bold;font-size:1.05rem;text-decoration:none;border-bottom:1px dashed #008aff;">{title}</a>'
            f'<div style="color:#00ff41;font-size:0.85rem;margin-top:4px;padding-left:32px;line-height:1.4;">{desc}</div></div>')

st.markdown(f"""
<div style="border-bottom:2px solid #333;padding-bottom:12px;margin-bottom:18px;margin-top:-50px;">
    <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;">
        <div>
            <span style="font-size:1.3rem;font-weight:bold;color:#00ff41;text-shadow:0 0 5px #00ff41;">🔒 SecAI-Nexus</span>
            <span style="font-size:0.95rem;color:#008aff;margin-left:10px;font-weight:bold;">// CYBER THREAT OBSERVABILITY</span>
        </div>
        <div style="font-size:1.0rem;font-weight:bold;color:#008aff;text-shadow:0 0 5px #008aff;">SYS_TIME: {datetime.now().strftime("%H:%M:%S")} UTC</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# LIVE METRICS — drop in live_metrics.py alongside this file
# ============================================================
from live_metrics import render_live_metrics_section
render_live_metrics_section()

# === THREAT MAPS ===
col_rad, col_fort = st.columns(2)
with col_rad:
    st.markdown('<div><a href="https://livethreatmap.radware.com/" target="_blank" class="map-title-link">>> RADWARE LIVE THREAT MAP</a></div>', unsafe_allow_html=True)
    render_muted_iframe("https://livethreatmap.radware.com/", height=1100)
with col_fort:
    st.markdown('<div><a href="https://threatmap.fortiguard.com/" target="_blank" class="map-title-link">>> FORTINET THREAT MAP</a></div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.fortiguard.com/", height=1100)
st.markdown("---")
col_son, col_cp = st.columns(2)
with col_son:
    st.markdown('<div><a href="https://attackmap.sonicwall.com/live-attack-map/" target="_blank" class="map-title-link">>> SONICWALL LIVE MAP</a></div>', unsafe_allow_html=True)
    render_muted_iframe("https://attackmap.sonicwall.com/live-attack-map/", height=1100)
with col_cp:
    st.markdown('<div><a href="https://threatmap.checkpoint.com/" target="_blank" class="map-title-link">>> CHECK POINT THREATCLOUD</a></div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.checkpoint.com/", height=1100)
st.markdown("---")
col_sich, col_kas = st.columns(2)
with col_sich:
    st.markdown('<div><a href="https://www.sicherheitstacho.eu/?lang=en" target="_blank" class="map-title-link">>> SICHERHEITSTACHO (DT)</a></div>', unsafe_allow_html=True)
    render_muted_iframe("https://www.sicherheitstacho.eu/?lang=en", height=1100)
with col_kas:
    st.markdown('<div><a href="https://cybermap.kaspersky.com/en/widget/dynamic/dark" target="_blank" class="map-title-link">>> KASPERSKY CYBERMAP</a></div>', unsafe_allow_html=True)
    render_muted_iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", height=1100)
st.markdown("---")
col_tb, col_bit = st.columns(2)
with col_tb:
    st.markdown('<div><a href="https://threatbutt.com/map/" target="_blank" class="map-title-link">>> THREATBUTT ATTACK MAP</a></div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatbutt.com/map/", height=1100)
with col_bit:
    st.markdown('<div><a href="https://threatmap.bitdefender.com/" target="_blank" class="map-title-link">>> BITDEFENDER THREAT MAP</a></div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.bitdefender.com/", height=1100)
st.markdown("---")
st.markdown('<div><a href="https://viz.greynoise.io/trends/trending" target="_blank" class="map-title-link">>> GREYNOISE INTELLIGENCE</a></div>', unsafe_allow_html=True)
render_muted_iframe("https://viz.greynoise.io/trends/trending", height=1400)
st.markdown("---")

# === ADDITIONAL GRC RESOURCES ===
st.markdown('<div style="margin-top:35px;margin-bottom:25px;text-align:center;"><span style="font-size:1.2rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;"><a href="https://www.nist.gov/cyberframework" target="_blank" class="section-header-link">>> ADDITIONAL GRC RESOURCES <<</a></span></div>', unsafe_allow_html=True)

spacer_l, l1, l2, l3, spacer_r = st.columns([0.5, 3, 3, 3, 0.5])
with l1:
    for args in [
        ("01","NIST AI RMF","https://www.nist.gov/itl/ai-risk-management-framework","Framework to manage AI-related risks to individuals and organizations."),
        ("02","HITRUST Alliance","https://hitrustalliance.net/","Safeguarding sensitive data and managing information risk."),
        ("03","OWASP LLM Top 10","https://owasp.org/www-project-top-10-for-large-language-model-applications/","Critical security risks in Large Language Models."),
        ("04","NIST CSF","https://www.nist.gov/cyberframework","Standards to manage and reduce cybersecurity risk."),
        ("05","ISO/IEC 27001","https://www.iso.org/isoiec-27001-information-security.html","International standard for ISMS management."),
        ("06","OWASP Top 10 Web","https://owasp.org/www-project-top-ten/","Critical web application security risks awareness."),
        ("07","NIST NVD","https://nvd.nist.gov/","US repository of standards-based vulnerability data."),
        ("08","CIS Controls","https://www.cisecurity.org/controls/","Prioritized safeguards against prevalent cyber-attacks."),
        ("09","CISA KEV Catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","Authoritative source for vulnerabilities exploited in the wild."),
        ("10","MITRE ATT&CK","https://mitre-attack.github.io/attack-navigator/","Matrix for mapping adversary tactics and procedures."),
        ("11","CVSS 4.0 Calc","https://www.first.org/cvss/calculator/4.0","Home of the Common Vulnerability Scoring System."),
        ("12","VirusTotal","https://www.virustotal.com/","Analyzing suspicious files, domains, IPs, and URLs."),
        ("13","Exploit Database","https://www.exploit-db.com/","Archive of public exploits and vulnerable software POCs."),
    ]:
        st.markdown(render_simple_link(*args), unsafe_allow_html=True)
with l2:
    for args in [
        ("14","Shodan Search","https://www.shodan.io/","Search engine for exposed internet-connected devices."),
        ("15","Have I Been Pwned","https://haveibeenpwned.com/","Checking if email/domain was in a data breach."),
        ("16","Security Onion","https://securityonionsolutions.com/","Platform for threat hunting and enterprise security."),
        ("17","AlienVault OTX","https://otx.alienvault.com/","Gathering and sharing real-time crowdsourced IOCs."),
        ("18","crt.sh Search","https://crt.sh/","Certificate Transparency log search for attack surface mapping."),
        ("19","SANS ISC","https://isc.sans.edu/","Cooperative cyber threat monitor tracking network trends."),
        ("20","BleepingComputer","https://www.bleepingcomputer.com/","Trusted news source for tracking ransomware attacks."),
        ("21","Abuse.ch URLhaus","https://urlhaus.abuse.ch/","Project dedicated to tracking malware distribution sites."),
        ("22","Any.Run Sandbox","https://any.run/","Interactive online malware analysis sandbox."),
        ("23","URLScan.io","https://urlscan.io/","Analyze websites to see background executions."),
        ("24","GTFOBins","https://gtfobins.github.io/","List of Unix binaries used to bypass security."),
        ("25","MalwareBazaar","https://bazaar.abuse.ch/","Open-source repository of malware samples."),
        ("26","HackTheBox","https://www.hackthebox.com/","Gamified cybersecurity training playground."),
    ]:
        st.markdown(render_simple_link(*args), unsafe_allow_html=True)
with l3:
    for args in [
        ("27","HackerOne","https://www.hackerone.com/","Bug bounty platform for elite pen testers."),
        ("28","Bugcrowd","https://www.bugcrowd.com/","Crowdsourced vulnerability disclosure and bounties."),
        ("29","TryHackMe","https://tryhackme.com/","Interactive training with hands-on virtual labs."),
        ("30","CyberChef","https://gchq.github.io/CyberChef/","The Cyber Swiss Army Knife for data analysis."),
        ("31","CISA Shields Up","https://www.cisa.gov/shields-up","Building corporate resilience against cyberattacks."),
        ("32","NIST CSRC","https://csrc.nist.gov/","Resource Center for framework guidelines."),
        ("33","SANS Reading Room","https://www.sans.org/white-papers/","Cybersecurity research documents and whitepapers."),
        ("34","DEF CON Archives","https://defcon.org/html/links/dc-archives.html","Presentations from the legendary hacking conference."),
        ("35","OSINT Framework","https://osintframework.com/","Interactive collection of OSINT gathering tools."),
        ("36","Talos Threat Intel","https://talosintelligence.com/","Cisco's premier threat research group."),
        ("37","PayloadsAllThings","https://github.com/swisskyrepo/PayloadsAllTheThings","List of useful payloads and bypasses."),
        ("38","Web Sec Academy","https://portswigger.net/web-security","Vulnerability training from Burp Suite creators."),
        ("39","VulnHub","https://www.vulnhub.com/","Hands-on experience in digital security."),
    ]:
        st.markdown(render_simple_link(*args), unsafe_allow_html=True)

st.markdown("""<div style="border-top:1px solid #333;padding-top:25px;margin-top:40px;text-align:center;font-family:'Courier New',monospace;">
<div style="color:#888;font-size:0.9rem;margin-bottom:5px;">Questions, Comments, or Recommendations?</div>
<div style="color:#888;font-size:0.9rem;margin-bottom:20px;">Developed by <b>Adam Kistler</b> | <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank" style="color:#008aff;text-decoration:none;border-bottom:1px dashed #008aff;">LinkedIn</a></div>
<div style="color:#555;font-size:0.75rem;margin-bottom:20px;padding:0 10%;line-height:1.4;"><b>LEGAL DISCLAIMER:</b> This dashboard is strictly for <b>educational and portfolio purposes</b>. All embedded threat maps and data sources are the property of their respective owners.<br><a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank" class="footer-license-link">CC BY-NC 4.0 License.</a></div>
<div style="color:#555;font-size:0.8rem;margin-top:10px;">SecAI-Nexus GRC [Version 14.0] | Live Data Engine Active</div>
</div>""", unsafe_allow_html=True)
