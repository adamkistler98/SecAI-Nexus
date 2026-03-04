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

st.markdown(f"""
<style>
    .stApp {{ background-color: #050505 !important; font-family: 'Courier New', Courier, monospace !important; }}
    div[data-testid="stMarkdownContainer"] > p {{ {SENTENCE_STYLE_GREEN} }}
    h1, h2, h3, h4, h5, h6, label {{ color: #00ff41 !important; }}
    header, footer, .stDeployButton {{ visibility: hidden; display: none; }}
</style>
""", unsafe_allow_html=True)

def render_muted_iframe(url, height=480):
    iframe_html = f'<iframe src="{url}" width="100%" height="{height}" style="border:none; background-color: #050505;" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>'
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
st.markdown(f'<div style="{GREEN_SUBTITLE}"><span style="color: #008aff;">>> GREYNOISE INTELLIGENCE</span> - <span style="{SENTENCE_STYLE_GREEN}">Internet-wide scan data and trending cyberattack patterns. (TRENDS VIEW)</span></div>', unsafe_allow_html=True)
render_muted_iframe("https://viz.greynoise.io/trends/trending", height=1400)

st.markdown("---")

# === RESEARCH & EXPOSURE (2x3 GRID) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> OPEN SOURCE ANALYSIS & RESEARCH FRAMEWORKS</div>', unsafe_allow_html=True)
os_col1, os_col2 = st.columns(2)

with os_col1:
    st.markdown(f'<div style="{BLUE_LABEL}">MITRE ATT&CK NAVIGATOR</div>', unsafe_allow_html=True)
    render_muted_iframe("https://mitre-attack.github.io/attack-navigator/", height=700)
    
    st.markdown(f'<div style="{BLUE_LABEL_MT}">EXPLOIT DATABASE (PUBLIC POCs)</div>', unsafe_allow_html=True)
    render_muted_iframe("https://www.exploit-db.com/", height=700)

    st.markdown(f'<div style="{BLUE_LABEL_MT}">OWASP TOP 10 PROJECT</div>', unsafe_allow_html=True)
    render_muted_iframe("https://owasp.org/www-project-top-ten/", height=800)

with os_col2:
    st.markdown(f'<div style="{BLUE_LABEL}">SHODAN SEARCH (DEVICES)</div>', unsafe_allow_html=True)
    render_muted_iframe("https://www.shodan.io/", height=700)
    
    st.markdown(f'<div style="{BLUE_LABEL_MT}">CRT.SH (CERTIFICATE OSINT)</div>', unsafe_allow_html=True)
    render_muted_iframe("https://crt.sh/", height=700)

    st.markdown(f'<div style="{BLUE_LABEL_MT}">SECURITY ONION SOLUTIONS</div>', unsafe_allow_html=True)
    render_muted_iframe("https://securityonionsolutions.com/", height=800)

st.markdown("---")

# === ADDITIONAL GRC RESOURCES (TOP 20 - FREE & OPEN SOURCE) ===
st.markdown(f'<div style="{GREEN_SUBTITLE}">>> ADDITIONAL OPEN SOURCE GRC & RESEARCH RESOURCES</div>', unsafe_allow_html=True)
l_col1, l_col2 = st.columns(2)

with l_col1:
    st.markdown(render_simple_link("01", "VirusTotal", "https://www.virustotal.com/", "The global standard for analyzing suspicious files, domains, IPs, and URLs for malware."), unsafe_allow_html=True)
    st.markdown(render_simple_link("02", "NIST NVD", "https://nvd.nist.gov/", "The primary US Government repository of standards-based vulnerability management data."), unsafe_allow_html=True)
    st.markdown(render_simple_link("03", "CISA KEV Catalog", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "Authoritative source for vulnerabilities currently being actively exploited in the wild."), unsafe_allow_html=True)
    st.markdown(render_simple_link("04", "AlienVault OTX", "https://otx.alienvault.com/", "The largest open community for gathering and sharing real-time crowdsourced IOCs."), unsafe_allow_html=True)
    st.markdown(render_simple_link("05", "SANS Internet Storm Center", "https://isc.sans.edu/", "Global cooperative cyber threat monitor tracking network anomalies and port trends."), unsafe_allow_html=True)
    st.markdown(render_simple_link("06", "CyberChef", "https://gchq.github.io/CyberChef/", "The GCHQ 'Swiss Army Knife' for analyzing and decoding data locally in-browser."), unsafe_allow_html=True)
    st.markdown(render_simple_link("07", "Abuse.ch URLhaus", "https://urlhaus.abuse.ch/", "A project dedicated to sharing and tracking malware distribution sites and payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("08", "MalwareBazaar", "https://bazaar.abuse.ch/", "A massive open-source repository of malware samples for researchers."), unsafe_allow_html=True)
    st.markdown(render_simple_link("09", "Pulsedive", "https://pulsedive.com/", "A community-driven threat intelligence platform with high-quality IOC pivoting."), unsafe_allow_html=True)
    st.markdown(render_simple_link("10", "FIRST CVSS Calculator", "https://www.first.org/cvss/calculator/4.0", "The official tool for scoring vulnerability severity and environmental risk."), unsafe_allow_html=True)

with l_col2:
    st.markdown(render_simple_link("11", "Triage Sandbox", "https://triage.com/", "A modern, free-tier friendly public malware sandbox for automated analysis."), unsafe_allow_html=True)
    st.markdown(render_simple_link("12", "URLScan.io", "https://urlscan.io/", "A free service to scan and analyze websites to see what a site is actually doing."), unsafe_allow_html=True)
    st.markdown(render_simple_link("13", "Any.Run Sandbox", "https://any.run/", "Interactive online malware analysis sandbox allowing live observation of payloads."), unsafe_allow_html=True)
    st.markdown(render_simple_link("14", "GTFOBins", "https://gtfobins.github.io/", "A curated list of Unix binaries that can be used to bypass local security restrictions."), unsafe_allow_html=True)
    st.markdown(render_simple_link("15", "LOLBAS Project", "https://lolbas-project.github.io/", "Living Off The Land Binaries and Scripts for Windows environments."), unsafe_allow_html=True)
    st.markdown(render_simple_link("16", "NIST Cybersecurity Framework", "https://www.nist.gov/cyberframework", "Voluntary guidance based on existing standards to better manage cybersecurity risk."), unsafe_allow_html=True)
    st.markdown(render_simple_link("17", "CIS Critical Security Controls", "https://www.cisecurity.org/controls/", "A prioritized set of actions that collectively form a defense-in-depth set of best practices."), unsafe_allow_html=True)
    st.markdown(render_simple_link("18", "BleepingComputer", "https://www.bleepingcomputer.com/", "Premier news source for tracking ransomware attacks, breaches, and industry events."), unsafe_allow_html=True)
    st.markdown(render_simple_link("19", "The Hacker News", "https://thehackernews.com/", "Trusted and widely-read cybersecurity news platform covering the latest breaches."), unsafe_allow_html=True)
    st.markdown(render_simple_link("20", "Cloudflare Radar", "https://radar.cloudflare.com/", "Free real-time insights into global internet traffic, security attacks, and adoption."), unsafe_allow_html=True)

st.markdown("---")
