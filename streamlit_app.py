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
BLUE_LABEL = "font-size: 1.1rem; font-weight: bold; color: #008aff; margin-bottom: 8px; text-transform: uppercase;"
BLUE_LABEL_MT = "font-size: 1.1rem; font-weight: bold; color: #008aff; margin-top: 20px; margin-bottom: 8px; text-transform: uppercase;"
SENTENCE_STYLE_GREEN = "color: #00ff41; font-size: 1.25rem; line-height: 1.6; font-family: 'Courier New', monospace;"
LINK_STYLE_BLUE = "color: #008aff; font-weight: bold; text-decoration: none; border-bottom: 1px dashed #008aff;"

# --- ADVANCED GRC CSS ---
st.markdown(f"""
<style>
    /* GLOBAL DARK THEME */
    .stApp {{ background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }}
    
    /* UNIVERSAL READABILITY */
    div[data-testid="stMarkdownContainer"] > p {{ {SENTENCE_STYLE_GREEN} }}
    h1, h2, h3, h4, h5, h6, label {{ color: #00ff41 !important; }}
    
    /* REMOVE WHITE ELEMENTS */
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
    div[data-testid="stMetricLabel"] {{ color: #008aff !important; font-size: 0.95rem; text-transform: uppercase; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

def render_muted_iframe(url, height=480):
    """Bulletproof embed wrapper for iframes."""
    iframe_html = f'<iframe src="{url}" width="100%" height="{height}" style="border:none; background-color: #050505;" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>'
    st.markdown(iframe_html, unsafe_allow_html=True)

def render_simple_link(num, title, url, desc):
    """Helper for the Top 20 list."""
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
st.markdown(f'<div style="{GREEN_SUBTITLE}"><span style="color: #008aff;">>> GREYNOISE INTELLIGENCE</span> - <span style="{SENTENCE_STYLE_GREEN}">Internet-wide scan data and trending cyberattack patterns. (TRENDS VIEW)</span></div>', unsafe_allow_html=True)
render_muted_iframe("https://viz.greynoise.io/trends/trending", height=1400)

st.markdown("---")

# === RESEARCH & EXPOSURE (2x2 GRID) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> OSINT & LIVE ATTACK VISUALIZATION</div>', unsafe_allow_html=True)
os_col1, os_col2 = st.columns(2)

with os_col1:
    st.markdown(f'<div style="{BLUE_LABEL}">MITRE ATT&CK NAVIGATOR</div>', unsafe_allow_html=True)
    render_muted_iframe("https://mitre-attack.github.io/attack-navigator/", height=700)
    
    st.markdown(f'<div style="{BLUE_LABEL_MT}">KASPERSKY CYBERMAP (LIVE)</div>', unsafe_allow_html=True)
    render_muted_iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", height=700)

with os_col2:
    st.markdown(f'<div style="{BLUE_LABEL}">SHODAN SEARCH (DEVICES)</div>', unsafe_allow_html=True)
    render_muted_iframe("https://www.shodan.io/", height=700)
    
    st.markdown(f'<div style="{BLUE_LABEL_MT}">CHECK POINT THREATCLOUD (LIVE)</div>', unsafe_allow_html=True)
    render_muted_iframe("https://threatmap.checkpoint.com/", height=700)

st.markdown("---")

# === ADDITIONAL GRC RESOURCES (TOP 20 - FREE & OPEN SOURCE) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> ADDITIONAL OPEN SOURCE GRC & RESEARCH RESOURCES</div>', unsafe_allow_html=True)
l_col1, l_col2 = st.columns(2)

with l_col1:
    st.markdown(render_simple_link("01", "OWASP Top 10 Project", "https://owasp.org/www-project-top-ten/", "The foundational awareness document for critical web application security risks."), unsafe_allow_html=True)
    st.markdown(render_simple_link("02", "NIST Cybersecurity Framework (CSF)", "https://www.nist.gov/cyberframework", "Voluntary guidance based on existing standards to better manage and reduce cybersecurity risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("03", "ISO/IEC 27000 Family", "https://www.iso.org/isoiec-27001-information-security.html", "The international standard for establishing Information Security Management Systems."), unsafe_allow_html=True)
    st.markdown(render_simple_link("04", "Security Onion Solutions", "https://securityonionsolutions.com/", "A free and open-source platform for threat hunting and enterprise security monitoring."), unsafe_allow_html=True)
    st.markdown(render_simple_link("05", "Exploit Database (Exploit-DB)", "https://www.exploit-db.com/", "The ultimate archive of public exploits and corresponding vulnerable software POCs."), unsafe_allow_html=True)
    st.markdown(render_simple_link("06", "VirusTotal", "https://www.virustotal.com/", "The global standard for analyzing suspicious files, domains, IPs, and URLs for malware."), unsafe_allow_html=True)
    st.markdown(render_simple_link("07", "NIST National Vulnerability Database (NVD)", "https://nvd.nist.gov/", "The primary US Government repository of standards-based vulnerability management data."), unsafe_allow_html=True)
    st.markdown(render_simple_link("08", "CISA KEV Catalog", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "Authoritative source for vulnerabilities currently being actively exploited in the wild."), unsafe_allow_html=True)
    st.markdown(render_simple_link("09", "AlienVault Open Threat Exchange (OTX)", "https://otx.alienvault.com/", "The largest open community for gathering and sharing real-time crowdsourced IOCs."), unsafe_allow_html=True)
    st.markdown(render_simple_link("10", "SANS Internet Storm Center (ISC)", "https://isc.sans.edu/", "Global cooperative cyber threat monitor tracking network anomalies and port trends."), unsafe_allow_html=True)

with l_col2:
    st.markdown(render_simple_link("11", "CyberChef", "https://gchq.github.io/CyberChef/", "The GCHQ 'Swiss Army Knife' for analyzing and decoding data locally in-browser."), unsafe_allow_html=True)
    st.markdown(render_simple_link("12", "Abuse.ch URLhaus", "https://urlhaus.abuse.ch/", "A project dedicated to sharing and tracking malware distribution sites and payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("13", "MalwareBazaar", "https://bazaar.abuse.ch/", "A massive open-source repository of malware samples for researchers."), unsafe_allow_html=True)
    st.markdown(render_simple_link("14", "Pulsedive", "https://pulsedive.com/", "A community-driven threat intelligence platform with high-quality IOC pivoting."), unsafe_allow_html=True)
    st.markdown(render_simple_link("15", "FIRST CVSS 4.0 Calculator", "https://www.first.org/cvss/calculator/4.0", "The official tool for scoring vulnerability severity and environmental risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("16", "Any.Run Interactive Sandbox", "https://any.run/", "Online malware analysis sandbox allowing live observation of payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("17", "URLScan.io", "https://urlscan.io/", "A free service to scan and analyze websites to see what a site is actually doing."), unsafe_allow_html=True)
    st.markdown(render_simple_link("18", "GTFOBins", "https://gtfobins.github.io/", "A curated list of Unix binaries that can be used to bypass local security restrictions."), unsafe_allow_html=True)
    st.markdown(render_simple_link("19", "LOLBAS Project", "https://lolbas-project.github.io/", "Living Off The Land Binaries and Scripts for Windows environments."), unsafe_allow_html=True)
    st.markdown(render_simple_link("20", "Cloudflare Radar", "https://radar.cloudflare.com/", "Free real-time insights into global internet traffic and security attacks."), unsafe_allow_html=True)

st.markdown("---")
