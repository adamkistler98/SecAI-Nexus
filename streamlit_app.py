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

# --- INLINE CSS CONSTANTS (MAX VISIBILITY NEON THEME) ---
GREEN_SUBTITLE = "font-size: 1.2rem; font-weight: bold; color: #00ff41; margin-top: 25px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1.2px;"
BLUE_LABEL = "font-size: 1.1rem; font-weight: bold; color: #008aff; margin-bottom: 8px; text-transform: uppercase;"
BLUE_LABEL_MT = "font-size: 1.1rem; font-weight: bold; color: #008aff; margin-top: 20px; margin-bottom: 8px; text-transform: uppercase;"
SENTENCE_STYLE_GREEN = "color: #00ff41; font-size: 1.25rem; line-height: 1.6; font-family: 'Courier New', monospace;"
LINK_STYLE_BLUE = "color: #008aff; font-weight: bold; text-decoration: none; border-bottom: 1px dashed #008aff;"

st.markdown(f"""
<style>
    .stApp {{ background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }}
    div[data-testid="stMarkdownContainer"] > p {{ {SENTENCE_STYLE_GREEN} }}
    h1, h2, h3, h4, h5, h6, label {{ color: #00ff41 !important; }}
    header, footer, .stDeployButton {{ visibility: hidden; display: none; }}
    
    div[data-testid="stMetric"] {{
        background-color: #0a0a0a !important;
        border: 1px solid #333;
        border-left: 4px solid #008aff !important;
    }}
</style>
""", unsafe_allow_html=True)

def render_muted_iframe(url, height=480):
    iframe_html = f'<iframe src="{url}" width="100%" height="{height}" style="border:none;" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>'
    st.markdown(iframe_html, unsafe_allow_html=True)

def render_simple_link(num, title, url, desc):
    return f"""
    <div style="margin-bottom: 28px; font-family: 'Courier New', monospace;">
        <span style="color: #00ff41; font-weight: bold; font-size: 1.5rem;">{num}.</span> 
        <a href="{url}" target="_blank" style="color: #008aff; font-weight: bold; font-size: 1.4rem; text-decoration: none; border-bottom: 1px dashed #008aff;">{title}</a>
        <div style="color: #00ff41; font-size: 1.2rem; margin-top: 8px; padding-left: 50px; line-height: 1.5;">{desc}</div>
    </div>
    """

# --- HEADER ---
st.markdown(f"""
<div style="border-bottom: 2px solid #333; padding-bottom: 12px; margin-bottom: 18px; margin-top: -50px; display: flex; justify-content: space-between; align-items: flex-end;">
    <div>
        <span style="font-size: 1.4rem; font-weight: bold; color: #00ff41; text-shadow: 0 0 5px #00ff41;">🔒 SecAI-Nexus</span>
        <span style="font-size: 1.0rem; color: #008aff; margin-left: 10px; font-weight: bold;">// GLOBAL THREAT VISIBILITY</span>
    </div>
    <div style="font-size: 1.1rem; font-weight: bold; color: #008aff;">SYS_TIME: {datetime.now().strftime("%H:%M:%S")} UTC</div>
</div>
""", unsafe_allow_html=True)

# === GREYNOISE TRENDS ===
st.markdown(f'<div style="{GREEN_SUBTITLE}"><span style="color: #008aff;">>> GREYNOISE INTELLIGENCE</span> - <span style="{SENTENCE_STYLE_GREEN}">Real-time insights into global cyberattacks and internet scanning trends. (TRENDS VIEW)</span></div>', unsafe_allow_html=True)
render_muted_iframe("https://viz.greynoise.io/trends/trending", height=1400)

st.markdown("---")

# === RESEARCH & EXPOSURE (2x3 GRID) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> OSINT, EXPOSURE & ANALYSIS FRAMEWORKS</div>', unsafe_allow_html=True)
os_col1, os_col2 = st.columns(2)

with os_col1:
    st.markdown(f'<div style="{BLUE_LABEL}">MITRE ATT&CK NAVIGATOR</div>', unsafe_allow_html=True)
    render_muted_iframe("https://mitre-attack.github.io/attack-navigator/", height=700)
    
    st.markdown(f'<div style="{BLUE_LABEL_MT}">SHODAN SEARCH</div>', unsafe_allow_html=True)
    render_muted_iframe("https://www.shodan.io/", height=700)

    st.markdown(f'<div style="{BLUE_LABEL_MT}">PULSEDIVE THREAT INTEL</div>', unsafe_allow_html=True)
    render_muted_iframe("https://pulsedive.com/feed/", height=800)

with os_col2:
    st.markdown(f'<div style="{BLUE_LABEL}">CRT.SH CERTIFICATE SEARCH</div>', unsafe_allow_html=True)
    render_muted_iframe("https://crt.sh/", height=700)
    
    st.markdown(f'<div style="{BLUE_LABEL_MT}">URLSCAN.IO RECENT SCANS</div>', unsafe_allow_html=True)
    render_muted_iframe("https://urlscan.io/search/#*", height=700)

    st.markdown(f'<div style="{BLUE_LABEL_MT}">CYBEXER THREAT VISUALIZER</div>', unsafe_allow_html=True)
    render_muted_iframe("https://cybexer.com/", height=800)

st.markdown("---")

# === ADDITIONAL GRC RESOURCES (TOP 20) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> ADDITIONAL GRC & RESEARCH RESOURCES</div>', unsafe_allow_html=True)
l_col1, l_col2 = st.columns(2)

with l_col1:
    st.markdown(render_simple_link("01", "VirusTotal", "https://www.virustotal.com/", "The global standard for analyzing suspicious files, domains, IPs, and URLs for malware."), unsafe_allow_html=True)
    st.markdown(render_simple_link("02", "NIST NVD", "https://nvd.nist.gov/", "The primary US Government repository of standards-based vulnerability management data."), unsafe_allow_html=True)
    st.markdown(render_simple_link("03", "CISA KEV Catalog", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "Authoritative source for vulnerabilities currently being actively exploited in the wild."), unsafe_allow_html=True)
    st.markdown(render_simple_link("04", "Exploit Database", "https://www.exploit-db.com/", "The ultimate archive of public exploits and corresponding vulnerable software."), unsafe_allow_html=True)
    st.markdown(render_simple_link("05", "AlienVault OTX", "https://otx.alienvault.com/", "The largest open threat exchange community for gathering crowdsourced IOCs."), unsafe_allow_html=True)
    st.markdown(render_simple_link("06", "SANS Internet Storm Center", "https://isc.sans.edu/", "Global cooperative cyber threat monitor tracking network anomalies and port trends."), unsafe_allow_html=True)
    st.markdown(render_simple_link("07", "FIRST CVSS Calculator", "https://www.first.org/cvss/calculator/4.0", "Official home of the Common Vulnerability Scoring System for calculating environmental risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("08", "CyberChef", "https://gchq.github.io/CyberChef/", "The 'Cyber Swiss Army Knife' for analyzing suspicious payloads and decoding data."), unsafe_allow_html=True)
    st.markdown(render_simple_link("09", "Abuse.ch URLhaus", "https://urlhaus.abuse.ch/", "Project for sharing and tracking malware distribution sites and payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("10", "BleepingComputer", "https://www.bleepingcomputer.com/", "Premier news source for tracking ransomware, data breaches, and industry events."), unsafe_allow_html=True)

with l_col2:
    st.markdown(render_simple_link("11", "Any.Run Sandbox", "https://any.run/", "Interactive malware analysis sandbox to safely detonate and observe payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("12", "NIST Cybersecurity Framework", "https://www.nist.gov/cyberframework", "Voluntary guidance standards to better manage and reduce cybersecurity risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("13", "ISO/IEC 27000 Family", "https://www.iso.org/isoiec-27001-information-security.html", "International standard for Information Security Management Systems (ISMS)."), unsafe_allow_html=True)
    st.markdown(render_simple_link("14", "OWASP Top 10", "https://owasp.org/www-project-top-ten/", "The foundational awareness document for web application security risks."), unsafe_allow_html=True)
    st.markdown(render_simple_link("15", "Tenable Nessus", "https://www.tenable.com/products/nessus", "Global standard for vulnerability assessment and infrastructure scanning."), unsafe_allow_html=True)
    st.markdown(render_simple_link("16", "The Hacker News", "https://thehackernews.com/", "Widely-read cybersecurity news platform covering breaches and vulnerabilities."), unsafe_allow_html=True)
    st.markdown(render_simple_link("17", "Dark Reading", "https://www.darkreading.com/", "Trusted community site for enterprise security news and technology trends."), unsafe_allow_html=True)
    st.markdown(render_simple_link("18", "Security Onion", "https://securityonion.net/", "Open-source software for threat hunting, enterprise security monitoring, and log management."), unsafe_allow_html=True)
    st.markdown(render_simple_link("19", "Cisco Talos", "https://talosintelligence.com/", "One of the largest commercial threat intelligence teams in the world."), unsafe_allow_html=True)
    st.markdown(render_simple_link("20", "Cloudflare Radar", "https://radar.cloudflare.com/", "Real-time insights into global internet traffic, security attacks, and adoption."), unsafe_allow_html=True)

st.markdown("---")
# Dashboard data tables continue below as per previous logic...
