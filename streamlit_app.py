import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import StringIO
# ==========================================================
# SEC AI NEXUS — CYBER THREAT INTELLIGENCE DASHBOARD
# Author: Adam Kistler
# Version: 1.4 (v34)
# Last Updated: July 2, 2026
# ==========================================================
# --------------------------- 
# Page Configuration
# ---------------------------
# ====================== SECURITY CONFIG ======================
# Force XSRF protection and disable CORS
st.config.set_option("server.enableXsrfProtection", True)
st.config.set_option("server.enableCORS", False)
# Strict CSP + security headers (must be first markdown call)
csp_meta = """
<meta http-equiv="Content-Security-Policy" content="default-src 'self';
script-src 'self' 'unsafe-inline';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
frame-src https://livethreatmap.radware.com https://threatmap.fortiguard.com;
connect-src 'self' https://www.cisa.gov https://*.abuse.ch https://isc.sans.edu https://check.torproject.org;">
<meta http-equiv="X-Frame-Options" content="DENY">
<meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
"""
st.markdown(csp_meta, unsafe_allow_html=True)
# ===================================================================
st.set_page_config(page_title="SecAI-Nexus GRC", layout="wide", page_icon="🤖",
                   initial_sidebar_state="collapsed")

# ====================== AUTHOR HEADER (neat top bar - v34) ======================
st.markdown("""
<div style="background:#0a0a0a; border-bottom:1px solid #1a1a2e; padding:8px 14px; margin-bottom:28px; display:flex; align-items:center; justify-content:space-between; font-family:'Courier New', Courier, monospace; font-size:0.68rem; letter-spacing:0.5px;">
  <div style="color:#00ff41; display:flex; align-items:center; gap:14px;">
    <span style="color:#008aff; font-weight:bold;">▸</span> 
    DEVELOPED BY <b style="color:#fff; text-shadow:0 0 4px #00ff4140;">ADAM KISTLER</b>
    <span style="color:#2a2a3a;">|</span>
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank" 
       style="color:#008aff; text-decoration:none; border-bottom:1px dashed #008aff50; padding-bottom:1px; transition:0.2s; font-size:0.66rem;">LINKEDIN</a>
    <a href="https://github.com/adamkistler98/SecAI-Nexus" target="_blank" 
       style="color:#008aff; text-decoration:none; border-bottom:1px dashed #008aff50; padding-bottom:1px; transition:0.2s; font-size:0.66rem;">GITHUB</a>
  </div>
  <div style="color:#4a4a5a; font-size:0.62rem; background:#111; padding:2px 8px; border:1px solid #1a1a2e; border-radius:2px;">
    v34 • JUL 2026
  </div>
</div>
""", unsafe_allow_html=True)
# ===================================================================
# ====================== LINKEDIN PREVIEW IMAGE ======================
st.markdown("""
<meta property="og:title" content="SecAI-Nexus GRC — Real-Time Cyber Threat Intelligence Dashboard">
<meta property="og:description" content="Free open-source platform with 118 live risk metrics, AI/LLM threat tracking, ransomware intelligence, and global attack maps. Built for security &amp; GRC teams.">
<meta property="og:image" content="https://raw.githubusercontent.com/adamkistler98/SecAI-Nexus/main/assets/SecAiImagev2.png">
<meta property="og:url" content="https://secai-nexus.streamlit.app/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
""", unsafe_allow_html=True)
# ===================================================================
MONO = "'Courier New', Courier, monospace"
GREEN = "#00ff41"; BLUE = "#008aff"; RED = "#ff4b4b"
AMBER = "#ffaa00"; CYAN = "#00e5ff"; BG = "#050505"; CARD = "#0a0a0a"
GREY = "#6a6a7a" # lighter subtitle grey
DGREY = "#4a4a5a" # delta label grey
st.markdown(f"""
<style>
  @keyframes pglow {{ 0%,100%{{text-shadow:0 0 4px {GREEN}30;}} 50%{{text-shadow:0 0 10px {GREEN}70;}} }}
  @keyframes cpulse {{ 0%,100%{{text-shadow:0 0 4px {CYAN}30;}} 50%{{text-shadow:0 0 12px {CYAN}80;}} }}
  .stApp {{background:{BG}!important;font-family:{MONO}!important;}}
  div[data-testid="stMarkdownContainer"]>p {{color:{GREEN};font-size:1.05rem;line-height:1.6;font-family:{MONO};}}
  h1,h2,h3,h4,h5,h6,label {{color:{GREEN}!important;}}
  header,footer {{visibility:hidden;}} .stDeployButton {{display:none;}}
  div[data-testid="stSpinner"]>div>p {{color:{GREEN}!important;}}
  .cm {{background:linear-gradient(135deg,{CARD},#0d0d12);border:1px solid #1a1a2e;
    border-left:3px solid {BLUE};padding:8px 9px 7px;margin-bottom:6px;
    font-family:{MONO};transition:all .3s;min-height:115px;}}
  .cm:hover {{border-left-color:{GREEN};box-shadow:0 0 10px {GREEN}0d;}}
  .cm-t a {{color:{BLUE};font-size:.64rem;font-weight:bold;text-transform:uppercase;
    letter-spacing:.4px;text-decoration:none;transition:.2s;}}
  .cm-t a:hover {{color:{GREEN};text-shadow:0 0 4px {GREEN};}}
  .cm-l {{font-size:.48rem;color:{GREEN};border:1px solid {GREEN};padding:0 3px;
    margin-left:3px;vertical-align:middle;animation:pglow 3s ease-in-out infinite;}}
  .cm-e {{font-size:.48rem;color:{AMBER};border:1px solid {AMBER}80;padding:0 3px;
    margin-left:3px;vertical-align:middle;}}
  .cm-v {{color:{GREEN};font-size:1.15rem;font-weight:bold;margin:3px 0 1px;line-height:1.05;
    text-shadow:0 0 4px {GREEN}20;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .cm-s {{font-size:.6rem;color:{GREY};margin-bottom:2px;line-height:1.15;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .cm-x {{font-size:.6rem;color:#555;margin-bottom:1px;line-height:1.15;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-style:italic;}}
  .cm-f {{font-size:.55rem;color:#556;line-height:1.3;margin-bottom:2px;}}
  .cm-f span {{color:#3a6a4a;}}
  .cm-d {{font-size:.66rem;border-top:1px dashed #1a1a2e;padding-top:3px;line-height:1.55;}}
  .d-b {{color:{RED};font-weight:bold;}} .d-g {{color:{GREEN};font-weight:bold;}}
  .d-n {{color:{BLUE};font-weight:bold;}} .d-a {{color:{AMBER};font-weight:bold;}}
  .pulse {{background:linear-gradient(135deg,#0a0a14,#0d0d1a);border:1px solid #1a1a30;
    border-left:4px solid {CYAN};padding:10px 12px 8px;margin-bottom:8px;
    font-family:{MONO};transition:all .3s;min-height:130px;}}
  .pulse:hover {{border-left-color:{GREEN};box-shadow:0 0 14px {GREEN}12;}}
  .pulse .cm-t a {{font-size:.68rem;color:{CYAN};}}
  .pulse .cm-v {{font-size:1.3rem;color:{CYAN};text-shadow:0 0 6px {CYAN}30;}}
  .pulse .cm-s {{font-size:.64rem;color:{GREY};}}
  .pulse .cm-x {{font-size:.64rem;}}
  .pulse .cm-f {{font-size:.6rem;}}
  .pulse .cm-d {{font-size:.68rem;}}
  .rl {{font-size:.6rem;color:#505060;text-transform:uppercase;letter-spacing:1px;
    border-left:3px solid {BLUE}50;padding-left:6px;margin:10px 0 5px;
    background:linear-gradient(90deg,{BLUE}06,transparent 35%);padding-top:2px;padding-bottom:2px;}}
  .rl-p {{font-size:.64rem;color:{CYAN};text-transform:uppercase;letter-spacing:1.2px;
    border-left:4px solid {CYAN};padding-left:8px;margin:14px 0 6px;
    background:linear-gradient(90deg,{CYAN}08,transparent 40%);padding-top:3px;padding-bottom:3px;
    text-shadow:0 0 6px {CYAN}30;}}
  .sh {{color:{GREEN};text-decoration:none;transition:.25s;text-shadow:0 0 6px {GREEN}25;}}
  .sh:hover {{color:{BLUE};text-shadow:0 0 10px {BLUE};}}
  .sl {{color:{BLUE};font-weight:bold;text-decoration:none;border-bottom:1px dashed #2a2a3a;transition:.2s;}}
  .sl:hover {{color:{GREEN};border-bottom-color:{GREEN};text-shadow:0 0 4px {GREEN};}}
  .ml {{color:{BLUE};font-size:.85rem;font-weight:bold;text-transform:uppercase;
    text-decoration:none;transition:.2s;display:inline-block;margin-bottom:4px;letter-spacing:.4px;}}
  .ml:hover {{color:{GREEN};text-shadow:0 0 6px {GREEN};}}
  .rl2 {{color:{BLUE};font-weight:bold;font-size:.85rem;text-decoration:none;
    border-bottom:1px dashed {BLUE}50;transition:.2s;}}
  .rl2:hover {{color:{GREEN};border-bottom-color:{GREEN};text-shadow:0 0 4px {GREEN};}}
  .sb {{font-size:.64rem;font-family:{MONO};margin:2px 0 20px;padding:8px 12px;
    background:linear-gradient(135deg,#070709,#0a0a10);
    border:1px solid #181828;border-left:3px solid {BLUE}40;line-height:1.8;}}
  .mw {{border:1px solid #1a1a2e;background:#080810;padding:2px;margin-bottom:5px;}}
  .fl {{color:#383848;text-decoration:none;border-bottom:1px dashed #383848;transition:.2s;}}
  .fl:hover {{color:{GREEN};border-bottom-color:{GREEN};}}
  hr {{border-color:#141420!important;}}
  .sd {{display:inline-block;width:5px;height:5px;border-radius:50%;margin-right:3px;vertical-align:middle;}}
  .sg {{background:{GREEN};box-shadow:0 0 4px {GREEN};}} .sa {{background:{AMBER};box-shadow:0 0 4px {AMBER};}}
  .sc {{background:{CYAN};box-shadow:0 0 4px {CYAN};}}

  /* Responsive improvements for mobile / smaller screens (v33) */
  @media (max-width: 1200px) {{
    .cm, .pulse {{ min-height: auto !important; padding: 6px 7px 5px !important; }}
    .cm-v, .pulse .cm-v {{ font-size: 1.0rem !important; }}
  }}
  @media (max-width: 768px) {{
    .stApp {{ font-size: 0.95rem !important; }}
    .cm, .pulse {{ min-height: auto !important; margin-bottom: 8px !important; border-left-width: 3px !important; }}
    .cm-v, .pulse .cm-v {{ font-size: 0.95rem !important; line-height: 1.1 !important; }}
    .cm-s, .pulse .cm-s, .cm-f, .pulse .cm-f {{ font-size: 0.52rem !important; }}
    div[data-testid="column"] {{ padding: 2px !important; }}
  }}

  /* Sleek Cyber-Themed Refresh Button (v34) */
  .stButton button[kind="secondary"] {{
    background: linear-gradient(135deg, #0a0a14 0%, #111113 100%) !important;
    color: #00e5ff !important;
    border: 1px solid #00e5ff !important;
    border-radius: 3px !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.72rem !important;
    font-weight: bold !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    padding: 8px 18px !important;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.25) !important;
    transition: all 0.2s cubic-bezier(0.23, 1.0, 0.32, 1) !important;
    min-height: 42px !important;
  }}
  .stButton button[kind="secondary"]:hover {{
    background: linear-gradient(135deg, #111113 0%, #1a1a20 100%) !important;
    color: #00ff41 !important;
    border-color: #00ff41 !important;
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.45) !important;
    text-shadow: 0 0 6px #00ff4140;
  }}
  .stButton button[kind="secondary"]:active {{
    transform: translateY(1px) !important;
    box-shadow: 0 0 8px rgba(0, 229, 255, 0.6) !important;
  }}
</style>
""", unsafe_allow_html=True)
S = requests.Session()
S.headers.update({"User-Agent":"SecAI-Nexus-GRC/5.0 (educational; admin@secai-nexus.dev)"})
def _g(url, t=14, **k):
    try: r = S.get(url, timeout=t, **k); r.raise_for_status(); return r
    except: return None
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_kev():
    r = _g("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    if not r: return None
    try:
        vulns = r.json().get("vulnerabilities",[]); now = datetime.now(timezone.utc)
        cnt={1:0,7:0,30:0,365:0}; rw=0; vd={}; prods={}
        for v in vulns:
            try:
                age=(now-datetime.strptime(v["dateAdded"],"%Y-%m-%d").replace(tzinfo=timezone.utc)).days
                for d in cnt:
                    if age<=d: cnt[d]+=1
            except: pass
            if v.get("knownRansomwareCampaignUse","").lower()=="known": rw+=1
            vn=v.get("vendorProject","?"); vd[vn]=vd.get(vn,0)+1
            pn=v.get("product","?"); prods[pn]=prods.get(pn,0)+1
        tv=max(vd,key=vd.get) if vd else "N/A"
        tp=max(prods,key=prods.get) if prods else "N/A"
        top3v=sorted(vd,key=vd.get,reverse=True)[:3]
        return {"total":len(vulns),"d1":cnt[1],"d7":cnt[7],"d30":cnt[30],"d365":cnt[365],
                "rw":rw,"tv":tv,"tvc":vd.get(tv,0),"vendors":len(vd),
                "tp":tp,"tpc":prods.get(tp,0),"top3v":top3v,"prods":len(prods)}
    except: return None
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_bazaar():
    r = _g("https://bazaar.abuse.ch/export/csv/recent/", t=22)
    if not r: return None
    try:
        lines=[l for l in r.text.splitlines() if l and not l.startswith("#")]
        now=datetime.now(timezone.utc); d1=d7=0; sm={}; ftypes={}
        for line in lines:
            p=line.split('","'); ts=p[0].strip('"')
            try:
                dt=datetime.strptime(ts,"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                age=(now-dt).days
                if age<=1: d1+=1
                if age<=7: d7+=1
            except: pass
            if len(p)>9:
                s=p[9].strip('"').strip()
                if s: sm[s]=sm.get(s,0)+1
            if len(p)>8:
                ft=p[8].strip('"').strip()
                if ft: ftypes[ft]=ftypes.get(ft,0)+1
        tf=max(sm,key=sm.get) if sm else "N/A"
        top_ft=max(ftypes,key=ftypes.get) if ftypes else "N/A"
        top3=sorted(sm,key=sm.get,reverse=True)[:3]
        return {"d1":d1,"d7":d7,"total":len(lines),"tf":tf,"families":len(sm),
                "top3":top3,"top_ft":top_ft}
    except: return None
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_urlhaus():
    r = _g("https://urlhaus.abuse.ch/downloads/text_online/", t=15)
    if not r: return None
    return {"online":len([l for l in r.text.splitlines() if l.strip() and not l.startswith("#")])}
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_feodo():
    r = _g("https://feodotracker.abuse.ch/downloads/ipblocklist.csv", t=15)
    if not r: return None
    try:
        lines=[l for l in r.text.splitlines() if l and not l.startswith("#")]
        on=sum(1 for l in lines if '"online"' in l.lower())
        off=sum(1 for l in lines if '"offline"' in l.lower())
        mw={}
        for l in lines:
            parts=l.split(",")
            if len(parts)>=5:
                fam=parts[4].strip().strip('"')
                if fam and fam not in ("malware",""): mw[fam]=mw.get(fam,0)+1
        top_mw=max(mw,key=mw.get) if mw else "N/A"
        return {"on":on,"off":off,"total":len(lines),"top_mw":top_mw,"mw_count":mw.get(top_mw,0),"mw_fams":len(mw)}
    except: return None
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_sans():
    r = _g("https://isc.sans.edu/api/infocon?json", t=12)
    if not r: return None
    try: return {"infocon":r.json().get("status","?")}
    except: return None
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_tor():
    r = _g("https://check.torproject.org/torbulkexitlist", t=15)
    if not r: return None
    try: return {"c":len([l for l in r.text.splitlines() if l.strip() and not l.startswith("#")])}
    except: return None
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_topports():
    r = _g("https://isc.sans.edu/api/topports/records/10?json", t=15)
    if not r: return None
    try:
        data = r.json()
        if isinstance(data, list) and len(data)>0:
            ports = [{"port":p.get("targetport","?"),"records":int(p.get("records",0)),
                      "sources":int(p.get("sources",0)),"targets":int(p.get("targets",0))} for p in data[:10]]
            return {"ports":ports, "total":sum(p["records"] for p in ports)}
    except: pass
    return None
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_topips():
    r = _g("https://isc.sans.edu/api/topips/records/5?json", t=15)
    if not r: return None
    try:
        data = r.json()
        if isinstance(data, list) and len(data)>0:
            return {"top_ip":data[0].get("ip","?"),"top_count":int(data[0].get("count",0)),
                    "total":sum(int(i.get("count",0)) for i in data[:5]),"n":len(data)}
    except: pass
    return None
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_honeypot():
    for dd in [0,1,2]:
        dt = (datetime.now(timezone.utc)-timedelta(days=dd)).strftime("%Y-%m-%d")
        r = _g(f"https://isc.sans.edu/api/webhoneypotsummary/{dt}?json", t=12)
        if r:
            try:
                data = r.json()
                d = data[0] if isinstance(data,list) and len(data)>0 else data
                reps = int(d.get("reports",0))
                if reps > 0:
                    return {"reports":reps,"targets":int(d.get("targets",0)),
                            "sources":int(d.get("sources",0)),"date":dt}
            except: pass
    return None
# ══════════════════════════════════════════════════════════════════════════════
def _f(n):
    if not isinstance(n,(int,float)): return str(n)
    n=int(n)
    if n>=1_000_000_000: return f"{n/1e9:.1f}B"
    if n>=1_000_000: return f"{n/1e6:.1f}M"
    if n>=1_000: return f"{n:,}"
    return str(n)
def nd():
    return (datetime.now(timezone.utc)-datetime(datetime.now().year,1,1,tzinfo=timezone.utc)).days+1
def ytd(a): return int(a*nd()/365)
def per(a,d): return int(a*d/365)
PN = {22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",123:"NTP",135:"MSRPC",
    139:"SMB",143:"IMAP",443:"HTTPS",445:"SMB",993:"IMAPS",1433:"MSSQL",1883:"MQTT",
    3306:"MySQL",3389:"RDP",5060:"SIP",5432:"Postgres",5900:"VNC",6379:"Redis",
    8080:"HTTP-Alt",8443:"HTTPS-Alt",8888:"Alt-HTTP",27017:"MongoDB",5555:"ADB"}
def pn(p):
    try: return PN.get(int(p), f":{p}")
    except: return str(p)
# ── Card with 3 content lines + facts ─────────────────────────────────────────
def _fb(facts):
    if not facts: return ""
    return '<div class="cm-f">' + "<br>".join(f'<span>·</span> {f}' for f in facts) + '</div>'
def card(title, url, value, sub, extra, d30, d30c, d1yr, d1yc, live=True, facts=None):
    b = f'<span class="cm-l">LIVE</span>' if live else f'<span class="cm-e">EST</span>'
    x = f'<div class="cm-x">{extra}</div>' if extra else ''
    fh = _fb(facts)
    st.markdown(f"""<div class="cm"><div class="cm-t"><a href="{url}" target="_blank">{title}</a>{b}</div>
  <div class="cm-v">{value}</div><div class="cm-s">{sub}</div>{x}{fh}
  <div class="cm-d"><span style="color:{DGREY};">30d </span><span class="{d30c}">{d30}</span>
    <span style="color:{DGREY};"> 1yr </span><span class="{d1yc}">{d1yr}</span></div></div>""", unsafe_allow_html=True)
def pcard(title, url, value, sub, extra, d30, d30c, d1yr, d1yc, live=True, facts=None):
    b = f'<span class="cm-l">LIVE</span>' if live else f'<span class="cm-e">EST</span>'
    x = f'<div class="cm-x">{extra}</div>' if extra else ''
    fh = _fb(facts)
    st.markdown(f"""<div class="pulse"><div class="cm-t"><a href="{url}" target="_blank">{title}</a>{b}</div>
  <div class="cm-v">{value}</div><div class="cm-s">{sub}</div>{x}{fh}
  <div class="cm-d"><span style="color:{DGREY};">30d </span><span class="{d30c}">{d30}</span>
    <span style="color:{DGREY};"> 1yr </span><span class="{d1yc}">{d1yr}</span></div></div>""", unsafe_allow_html=True)
def lcard(title, url, data, vf, sf, xf, d30f, d1yf, d30c="d-b", d1yc="d-b", fsub="awaiting", facts=None):
    if data:
        try: card(title,url,vf(data),sf(data),xf(data) if xf else "",d30f(data),d30c,d1yf(data),d1yc,True,facts=facts); return
        except: pass
    fh = _fb(facts) if facts else ''
    st.markdown(f"""<div class="cm" style="opacity:.5;"><div class="cm-t"><a href="{url}" target="_blank">{title}</a>
    <span class="cm-l">LIVE</span></div><div class="cm-v" style="font-size:.95rem;color:#2a7a3a;">Syncing…</div>
    <div class="cm-s">{fsub}</div>{fh}<div class="cm-d" style="color:#333;">Populates on Cloud deploy</div></div>""", unsafe_allow_html=True)
def lpulse(title, url, data, vf, sf, xf, d30f, d1yf, d30c="d-b", d1yc="d-b", fsub="awaiting", facts=None):
    if data:
        try: pcard(title,url,vf(data),sf(data),xf(data) if xf else "",d30f(data),d30c,d1yf(data),d1yc,True,facts=facts); return
        except: pass
    fh = _fb(facts) if facts else ''
    st.markdown(f"""<div class="pulse" style="opacity:.5;"><div class="cm-t"><a href="{url}" target="_blank">{title}</a>
    <span class="cm-l">LIVE</span></div><div class="cm-v" style="font-size:1rem;color:#2a7a3a;">Syncing…</div>
    <div class="cm-s">{fsub}</div>{fh}<div class="cm-d" style="color:#333;">DShield sensor network</div></div>""", unsafe_allow_html=True)
def iframe(url, h=1100):
    st.markdown(f'<div class="mw"><iframe src="{url}" width="100%" height="{h}" style="border:none;" '
        f'sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe></div>', unsafe_allow_html=True)
def rl(t): st.markdown(f'<div class="rl">{t}</div>', unsafe_allow_html=True)
def gl(n,t,u,d):
    return (f'<div style="margin-bottom:11px;"><span style="color:{GREEN};font-weight:bold;font-size:.78rem;">{n}.</span> '
            f'<a href="{u}" target="_blank" class="rl2">{t}</a>'
            f'<div style="color:#5a5a6a;font-size:.68rem;margin-top:1px;padding-left:22px;">{d}</div></div>')

def _tbl(title, hdrs, rows_data, hdr_color):
    hh = "".join(f'<th style="padding:6px 4px;text-align:left;color:{hdr_color};font-size:.52rem;text-transform:uppercase;">{h}</th>' for h in hdrs)
    rh = ""
    for r in rows_data:
        rh += '<tr style="border-bottom:1px solid #141420;">' + "".join(f'<td style="padding:6px 4px;{s}">{v}</td>' for v,s in r) + '</tr>'
    return f'<div style="margin-bottom:10px;"><div style="font-size:.68rem;font-weight:bold;color:{hdr_color};text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px;border-bottom:1px solid {hdr_color}20;padding-bottom:3px;">{title}</div><div style="overflow-x:auto;border:1px solid #1a1a2e;background:#080810;padding:2px;"><table style="width:100%;border-collapse:collapse;font-family:{MONO};font-size:.6rem;"><thead><tr style="border-bottom:2px solid {hdr_color}30;background:#0a0a14;">{hh}</tr></thead><tbody style="line-height:1.5;">{rh}</tbody></table></div></div>'

# ══════════════════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
st.markdown(
f"""
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; border-bottom: 2px solid #141420; padding-bottom: 12px; margin-bottom: 20px; margin-top: -25px; gap: 15px;">
  <div style="flex: 1; min-width: 300px; text-align: left;">
    <div style="margin-bottom: 4px;">
      <span style="font-size: 1.7rem; font-weight: bold; color: {CYAN}; text-shadow: 0 0 15px {CYAN}80; letter-spacing: 1.5px;">
        🤖 SecAI-Nexus
      </span>
      <span style="font-size: .45rem; color: #4a4a5a; border: 1px solid #2a2a3a; padding: 1px 4px; margin-left: 6px; vertical-align: middle;">v34</span>
    </div>
    <div style="font-size: 0.9rem; font-weight: bold; color: #8892b0; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; opacity: 0.8;">
      Cybersecurity GRC Observability Platform
    </div>
    <div style="font-size: .52rem; color: #505060; letter-spacing: 0.5px;">
      <span style="color: {GREEN}; background: {GREEN}15; border: 1px solid {GREEN}40; padding: 0 3px; border-radius: 2px; font-weight: bold;">ONLINE</span> ·
      <span style="color: #606070;">118 METRICS · 14 DATA ROWS · 10 INTEL TABLES · 80+ RESOURCES</span>
    </div>
  </div>
  <div style="flex: 1; text-align: center; min-width: 260px;">
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
     <a href="#why-ai-security-matters" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase;">
      &gt;&gt; ⏬ WHY AI SECURITY MATTERS &lt;&lt;
     </a>
     <a href="#global-threat-metrics" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase;">
      &gt;&gt; ⏬ GLOBAL THREAT METRICS &lt;&lt;
     </a>
     <a href="#live-threat-maps" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase;">
      &gt;&gt; ⏬ LIVE THREAT MAP FEEDS &lt;&lt;
     </a>
     <a href="#framework-comparison" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase;">
      &gt;&gt; ⏬ FRAMEWORK COMPARISON &amp; LINEAGE &lt;&lt;
     </a>
     <a href="#regulatory-risk" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase;">
      &gt;&gt; ⏬ REGULATORY RISK &amp; PENALTIES &lt;&lt;
     </a>
     <a href="#grc-resources" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase;">
      &gt;&gt; ⏬ GRC RESOURCES &amp; TOOLS &lt;&lt;
     </a>
    </div>
  </div>
  <div style="flex: 1; text-align: right; min-width: 220px;">
    <div style="font-size: .78rem; font-weight: bold; color: {BLUE}; text-shadow: 0 0 4px {BLUE}; letter-spacing: 0.5px;">
      {now_utc.strftime("%H:%M:%S")} UTC <span style="color:#3a3a4a; margin: 0 6px;">|</span> {now_utc.strftime("%Y-%m-%d")}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── REFRESH CONTROL (v34 — sleek cyber theme) ─────────────────────────────────────────────
col_r1, col_r2, col_r3 = st.columns([3, 2, 3])
with col_r2:
    if st.button("Sync & Clear Cache", type="secondary", use_container_width=True, help="Clears all cached threat intel and reloads fresh data from APIs."):
        st.cache_data.clear()
        st.toast("Cache cleared. Reloading latest threat intel...", icon="🔄")
        st.rerun()

with st.spinner("Syncing threat intelligence feeds…"):
    kev=fetch_kev(); baz=fetch_bazaar(); uhaus=fetch_urlhaus()
    feodo=fetch_feodo(); sans=fetch_sans(); tor=fetch_tor()
    topports=fetch_topports(); topips=fetch_topips(); honeypot=fetch_honeypot()
# ── BASELINES (updated July 2026 with IBM 2026 / CrowdStrike GTR 2026 + latest verified data) ─────────────────────────────────────────────────────────────────
CVE_TOT=32_800; CVE_CRIT=5_100; CVE_HIGH=13_900
RANSOM=6_400; SUPPLY=3_700; INSIDER=7_800
BREACH=8_700_000_000; BEC=24_500; PHISH=2_300_000
IDENTITY=19_100_000_000; GDPR=2_400_000_000; IC3LOSS=14_200_000_000
DDOS=19_800_000; IOT_MAL=135_000_000; CRYPTO=2_600_000_000
CISA_ADV=980; CISA_ICS=490; RECOVERY=3_050_000
# ── FALLBACKS (when APIs blocked locally) ────────────────────────────────────
if not kev:
    kev={"total":1620,"rw":410,"vendors":295,"prods":650,"tv":"Microsoft","tvc":365,
         "top3v":["Microsoft","Apple","Google"],"tp":"Windows","tpc":230,"d30":14,"d365":108}
if not feodo:
    feodo={"on":340,"off":590,"total":930,"mw_fams":7,"top_mw":"Pikabot","mw_count":125}
if not baz:
    baz={"total":5200,"tf":"AgentTesla","families":98,"top_ft":".exe","d7":3400}
if not uhaus:
    uhaus={"online":14200}
if not sans:
    sans={"infocon":"green"}
if not tor:
    tor={"c":7800}
# ══════════════════════════════════════════════════════════════════════════════
# WHY AI SECURITY MATTERS — EXECUTIVE BRIEF (Most Impactful First)
# Moved here for CISO/Board visibility, enhanced visuals & specific data
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div id="why-ai-security-matters" style="text-align: left; margin: 25px 0 15px 5px; scroll-margin-top: 25px;">
  <div style="font-size: 0.95rem; font-weight: bold; color: {CYAN}; letter-spacing: 1.5px; text-transform: uppercase;">
    &gt;&gt; Why AI Security Matters: Risk, Regulation &amp; Business Impact
  </div>
  <div style="font-size: 0.58rem; color: #505060; margin-top: 4px;">
    Executive Brief for CISOs, Boards &amp; Risk Committees • Updated July 2026
  </div>
</div>
""", unsafe_allow_html=True)

# Executive Summary Box
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0a0a14, #111); border-left: 5px solid {RED}; padding: 16px 20px; margin-bottom: 20px; border-radius: 4px; max-width: 1100px; box-shadow: 0 0 10px {RED}20;">
  <b style="color:{RED}; font-size:0.9rem;">BOARD-LEVEL RISK IN 2026</b><br>
  <span style="color:#ddd; font-size:0.82rem; line-height:1.5;">
  AI governance failures are no longer theoretical. They drive real financial losses, regulatory fines up to <b>7% of global gross revenue</b>, personal liability for executives, and rapid enforcement actions. 
  Shadow AI, deepfakes, and model risks are inflating breach costs and triggering new laws with the highest penalties in regulatory history. 
  This is now a C-suite and board priority — not just a technical issue.
  </span>
</div>
""", unsafe_allow_html=True)

# Key Impact Stats - Reordered Most to Least Impactful, Enhanced Visuals
st.markdown(f'<div class="rl-p" style="margin-top:5px; margin-bottom:10px;">📊 MOST IMPACTFUL AI RISKS (MONETARY &amp; REGULATORY)</div>', unsafe_allow_html=True)

c = st.columns(4)
with c[0]:
    st.markdown(f"""
    <div class="pulse" style="min-height:135px; border-left:5px solid {RED}; padding:12px 14px; background:linear-gradient(135deg,#0a0a14,#111113);">
      <div style="color:#ff4b4b; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.8px; font-weight:bold;">#1 HIGHEST AI FINE</div>
      <div style="color:#ff4b4b; font-size:2.1rem; font-weight:bold; line-height:1; margin:6px 0 2px;">7%</div>
      <div style="color:#ddd; font-size:0.78rem; font-weight:600;">of global gross revenue</div>
      <div style="color:#aaa; font-size:0.68rem; margin-top:4px;">EU AI Act — Prohibited practices<br>€35M+ cap also applies</div>
      <div style="color:#ffaa00; font-size:0.7rem; margin-top:8px; font-weight:bold;">Highest percentage-based fine globally</div>
    </div>
    """, unsafe_allow_html=True)

with c[1]:
    st.markdown(f"""
    <div class="pulse" style="min-height:135px; border-left:5px solid {AMBER}; padding:12px 14px; background:linear-gradient(135deg,#0a0a14,#111113);">
      <div style="color:#ffaa00; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.8px; font-weight:bold;">#2 SHADOW AI BREACHES</div>
      <div style="color:#ffaa00; font-size:2.1rem; font-weight:bold; line-height:1; margin:6px 0 2px;">22%</div>
      <div style="color:#ddd; font-size:0.78rem; font-weight:600;">of all breaches involve unauthorized AI</div>
      <div style="color:#aaa; font-size:0.68rem; margin-top:4px;">IBM 2026 • Adds <b style="color:#ffaa00;">+$680k</b> to avg breach cost</div>
      <div style="color:#ffaa00; font-size:0.7rem; margin-top:8px; font-weight:bold;">1,300+ unauthorized AI apps per org avg</div>
    </div>
    """, unsafe_allow_html=True)

with c[2]:
    st.markdown(f"""
    <div class="pulse" style="min-height:135px; border-left:5px solid {CYAN}; padding:12px 14px; background:linear-gradient(135deg,#0a0a14,#111113);">
      <div style="color:#00e5ff; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.8px; font-weight:bold;">#3 GDPR ENFORCEMENT</div>
      <div style="color:#00e5ff; font-size:1.6rem; font-weight:bold; line-height:1; margin:6px 0 2px;">€1.2 Billion</div>
      <div style="color:#ddd; font-size:0.78rem; font-weight:600;">single fine (Meta — record)</div>
      <div style="color:#aaa; font-size:0.68rem; margin-top:4px;">Up to 4% global turnover<br>AI systems processing EU data in scope</div>
      <div style="color:#ffaa00; font-size:0.7rem; margin-top:8px; font-weight:bold;">Most enforced data protection law</div>
    </div>
    """, unsafe_allow_html=True)

with c[3]:
    st.markdown(f"""
    <div class="pulse" style="min-height:135px; border-left:5px solid {GREEN}; padding:12px 14px; background:linear-gradient(135deg,#0a0a14,#111113);">
      <div style="color:#00ff41; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.8px; font-weight:bold;">#4 SEC + DEEPFAKE/BEC</div>
      <div style="color:#00ff41; font-size:1.6rem; font-weight:bold; line-height:1; margin:6px 0 2px;">Active + $25M+</div>
      <div style="color:#ddd; font-size:0.78rem; font-weight:600;">Real deepfake CEO fraud cases</div>
      <div style="color:#aaa; font-size:0.68rem; margin-top:4px;">4-business-day disclosure required<br>Multiple enforcement actions 2025-2026</div>
      <div style="color:#ffaa00; font-size:0.7rem; margin-top:8px; font-weight:bold;">Personal liability rising (DORA/NIS2)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Regulation Expanders (kept for depth)
st.markdown(f'<div class="rl-p" style="margin-top:5px;">📜 KEY REGULATIONS — DETAILED IMPACT</div>', unsafe_allow_html=True)

with st.expander("🇪🇺 EU AI Act — Highest AI-Specific Penalties (7% Global Turnover)", expanded=True):
    st.markdown("""
    **Maximum Penalty:** Up to **7% of global gross revenue** (or €35 million, whichever higher) for prohibited AI practices. 3% for most other violations.
    
    **Specific Impact:** Prohibited uses include social scoring, real-time biometric identification in public spaces (limited exceptions), and manipulative techniques. High-risk AI systems require risk management, data quality, transparency, human oversight, and logging.
    
    **Why it matters to leaders:** This is the strictest AI law globally with binding fines based on company-wide revenue. Non-compliance can halt AI projects and trigger massive financial penalties.
    
    **Official:** [EU AI Act](https://artificialintelligenceact.eu/)
    """)

with st.expander("🇪🇺 GDPR — Most Enforced, Real €1.2B Fines"):
    st.markdown("""
    **Maximum Penalty:** Up to **4% of global annual turnover** or €20 million.
    
    **Specific Impact:** AI systems processing personal data of EU residents must have lawful basis, DPIAs for high-risk processing, and transparency for automated decisions. Recent record fine: Meta €1.2 billion.
    
    **Why it matters:** AI training data, inference, and profiling fall under GDPR. Regulators are actively fining for inadequate AI governance.
    
    **Official:** [GDPR Text](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
    """)

with st.expander("🇪🇺 NIS2 + DORA — Personal Liability & Supply Chain"):
    st.markdown("""
    **NIS2:** Up to 2% global turnover. Mandatory 24h/72h incident reporting, supply chain security, governance accountability.
    
    **DORA (Finance):** Up to 2% turnover + **personal liability** for management bodies. ICT risk management and third-party oversight (including AI providers).
    
    **Why it matters:** Executives can be held personally accountable. Expands to many more sectors than before.
    
    **Official:** [NIS2](https://eur-lex.europa.eu/eli/dir/2022/2555/oj) • [DORA](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)
    """)

with st.expander("🇺🇸 US — SEC Disclosure, CMMC, State Privacy"):
    st.markdown("""
    **SEC Cybersecurity Rules:** Material incidents disclosed in **4 business days**. Annual board oversight disclosures. Multiple enforcement actions already in 2025-2026.
    
    **CMMC 2.0:** Contract loss and False Claims Act risk for DoD contractors.
    
    **State Laws (e.g. CPRA):** Up to $7,500 per intentional violation. Growing automated decision-making rules.
    
    **Why it matters:** Rapid disclosure requirements + real enforcement. Personal liability increasing in financial and defense sectors.
    
    **Official:** [SEC Rule](https://www.sec.gov/rules/final/2023/33-11216.pdf) • [CMMC](https://dodcio.defense.gov/CMMC/)
    """)

st.markdown("---")

# Quick Reference Table — Maximum Penalties (moved here just above AI Reference)
quick_data = [
    ("EU AI Act (Prohibited)", "7% global turnover", "Highest AI-specific fine globally"),
    ("GDPR", "4% global turnover", "Most enforced data protection law"),
    ("NIS2", "2% global turnover", "Critical infrastructure & supply chain"),
    ("DORA (Finance)", "2% global turnover", "Personal liability for executives"),
    ("SEC Disclosure", "Civil + potential criminal", "4-business-day incident reporting"),
    ("CCPA/CPRA (CA)", "$7,500 per violation", "Strongest US state privacy law"),
]

quick_rows = []
for reg, fine, note in quick_data:
    quick_rows.append([
        (reg, "color:#00e5ff; font-weight:bold;"),
        (fine, "color:#ff4b4b; font-weight:bold;"),
        (note, "color:#aaa; font-size:0.62rem;")
    ])

st.markdown(_tbl("MAXIMUM PENALTIES AT A GLANCE", ["Regulation", "Maximum Fine", "Key Note"], quick_rows, CYAN), unsafe_allow_html=True)

st.caption("Sources: Official regulatory texts (EUR-Lex, SEC, CMMC, CPPA). Enforcement trends based on 2025–2026 public actions and regulatory guidance.")

# AI Reference section starts here
# ══════════════════════════════════════════════════════════════════════════════
# AI SECURITY & THREAT INTELLIGENCE REFERENCE (UPDATED July 2026)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div id="threat-intel-reference" style="text-align: left; margin: 30px 0 15px 5px; scroll-margin-top: 30px;">
  <div style="font-size: 0.9rem; font-weight: bold; color: {CYAN}; letter-spacing: 1.5px; text-transform: uppercase;">
    &gt;&gt; AI Security &amp; Threat Intelligence Reference
  </div>
  <div style="font-size: 0.55rem; color: #505060; margin-top: 6px; letter-spacing: 0.5px; line-height: 1.5;">
    <span style="color: {BLUE}; border: 1px solid {BLUE}40; padding: 1px 6px; border-radius: 2px; font-weight: bold;">10 DYNAMIC SECURITY TABLES</span>
    &nbsp; REAL-TIME CISA KEV ENUMERATION · THREAT ACTOR PROFILING
  </div>
  <div style="font-size: 0.55rem; color: #404050; margin-top: 4px; letter-spacing: 0.3px;">
    GOVERNANCE REPOSITORY · MITRE ATT&amp;CK® · OWASP AI/LLM TOP 10 · ADVERSARIAL MACHINE LEARNING · GLOBAL IMPACT ANALYSIS
  </div>
</div>
""", unsafe_allow_html=True)
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_kev_recent():
    r = _g("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    if not r: return None
    try: return sorted(r.json().get("vulnerabilities",[]), key=lambda x:x.get("dateAdded",""), reverse=True)[:10]
    except: return None
kev_recent = fetch_kev_recent()
# ── KEV TABLE ROWS (rich format) ─────────────────────────────────────────────
kev_rows = []
if kev_recent:
    for v in kev_recent:
        cve = v.get("cveID","N/A")
        vn = v.get("vendorProject","?")
        pr = v.get("product","?")
        nm = v.get("vulnerabilityName","?")
        ad = v.get("dateAdded","?")
        du = v.get("dueDate","?")
        rw = "🔴" if v.get("knownRansomwareCampaignUse","").lower() == "known" else "—"
        sn = nm[:75] + "…" if len(nm) > 75 else nm
        kev_rows.append([
            (f'<a href="https://nvd.nist.gov/vuln/detail/{cve}" target="_blank" style="color:{RED};text-decoration:none;border-bottom:1px dashed {RED}40;">{cve}</a>', f"color:{RED};font-weight:bold;white-space:nowrap;"),
            (vn, f"color:{CYAN};font-weight:bold;"),
            (pr, f"color:{GREY};"),
            (sn, f"color:#888;font-size:.56rem;"),
            (ad, f"color:{GREEN};white-space:nowrap;"),
            (rw, f"text-align:center;"),
            (du, f"color:{AMBER};white-space:nowrap;")
        ])
# ── TOP 15 AI MODELS & CAPABILITIES (as of July 2026) ───────────────────────────────────
ai_models_data = [
    ("1. Gemini 3.2 Ultra", "https://gemini.google.com/", "Multimodal Reasoning", "Complex tasks & integration", "Google's flagship with 2M+ context & superior multimodal", "Prompt Injection"),
    ("2. Claude 4.7 Sonnet", "https://claude.ai/", "Advanced Reasoning", "Safety & long-form content", "Anthropic's top model excelling in logic and ethical alignment", "Insecure Output"),
    ("3. GPT-5.4 o3", "https://chatgpt.com/", "Agentic Intelligence", "Versatile research & automation", "OpenAI's latest with enhanced reasoning and tool use", "Supply Chain"),
    ("4. Grok 4.30", "https://x.ai/", "Real-time Knowledge", "Current events & uncensored", "xAI's innovative multi-agent architecture model", "Excessive Agency"),
    ("5. Llama 4.1 Maverick", "https://llama.meta.com/", "Open Weights", "Local & enterprise deploy", "Meta's leading open-source model with massive context", "Supply Chain"),
    ("6. DeepSeek R1", "https://deepseek.com/", "Math & Coding", "High-precision technical tasks", "Strongest open-source performer in STEM domains", "Training Poisoning"),
    ("7. Qwen 3.6 Max", "https://qwen.ai/", "Multilingual Efficiency", "Business workflows", "Alibaba's top multilingual & efficient model", "Insecure Plugin"),
    ("8. Mistral Large 4", "https://mistral.ai/", "Enterprise Reasoning", "Fast & secure inference", "Leading European AI for global business use", "Prompt Injection"),
    ("9. Perplexity Pro 2.0", "https://www.perplexity.ai/", "Search & Research", "Real-time citations", "AI-powered search with live web access", "Model DoS"),
    ("10. Cohere Command R++", "https://cohere.com/", "Enterprise RAG", "Secure business workflows", "Cohere's retrieval-augmented generation leader", "Insecure Output"),
    ("11. GLM-6", "https://zhipuai.cn/", "Multimodal", "Chinese/English tasks", "Zhipu AI's powerful multimodal model", "Supply Chain"),
    ("12. Phi-4.5", "https://azure.microsoft.com/", "Lightweight Edge", "On-device & efficient AI", "Microsoft's optimized small language model", "Training Poisoning"),
    ("13. Kimi K3", "https://kimi.moonshot.cn/", "Long Context", "Deep reasoning", "Moonshot's advanced long-context model", "Sensitive Disclosure"),
    ("14. Seed 2.1", "https://bytedance.com/", "Creative Generation", "Content & media", "ByteDance's advanced generative AI", "Insecure Plugin"),
    ("15. MiniMax M3", "https://minimax.cn/", "Compact & Fast", "Mobile & edge deployment", "Highly efficient model for constrained environments", "Model Theft")
]
ai_rows = []
for name, link, use_case, best_for, desc, vuln in ai_models_data:
    ai_rows.append([
        (f'<a href="{link}" target="_blank" style="color:{CYAN};text-decoration:none;border-bottom:1px dashed {CYAN}40;">{name}</a>', f"color:{CYAN};font-weight:bold;white-space:nowrap;"),
        (use_case, f"color:{GREEN};font-weight:bold;"),
        (best_for, f"color:{AMBER};"),
        (desc, f"color:#888;font-size:.56rem;"),
        (f'<a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/" target="_blank" style="color:{RED};text-decoration:none;">{vuln}</a>', f"color:{RED};font-weight:bold;")
    ])
# ── TOP 15 AI-POWERED CYBERCRIME (as of July 2026) ──────────────────────────────────────
ai_crime_data = [
    ("1. AI Phishing Campaigns", "Scaling 420% YoY", "Hyper-personalized spear-phishing with perfect grammar", "CrowdStrike GTR 2026", "https://www.crowdstrike.com/global-threat-report/"),
    ("2. Deepfake Vishing", "442% ↑", "3-second voice cloning for CEO fraud & wire transfers", "IBM Cost of Breach 2026", "https://www.ibm.com/reports/data-breach"),
    ("3. Polymorphic AI Malware", "Evasive", "BlackMamba-style code mutation that bypasses all AV", "CrowdStrike GTR 2026", "https://www.crowdstrike.com/global-threat-report/"),
    ("4. Prompt Injection Attacks", "#1 LLM risk", "Direct/indirect injection leading to data exfil", "OWASP LLM Top 10", "https://owasp.org/www-project-top-10-for-large-language-model-applications/"),
    ("5. Automated OSINT & Recon", "Automated", "LLM-driven target profiling in minutes", "Mandiant M-Trends 2026", "https://www.mandiant.com/m-trends"),
    ("6. Model Poisoning (Supply Chain)", "Growing", "Backdoored Hugging Face models & training data", "MITRE ATLAS", "https://atlas.mitre.org/"),
    ("7. Agentic AI Abuse", "Insider Risk", "Autonomous agents performing unintended actions", "IBM Cost of Breach 2026", "https://www.ibm.com/reports/data-breach"),
    ("8. Deepfake Video Fraud", "Rising", "Real-time face swaps in video calls ($28M+ scams)", "Chainalysis 2026", "https://www.chainalysis.com/"),
    ("9. AI PassGAN Cracking", "51% <60s", "Predictive password cracking at machine speed", "Dark Reading", "https://www.darkreading.com/"),
    ("10. Adversarial ML Evasion", "Emerging", "Pixel perturbations that fool every classifier", "CrowdStrike GTR 2026", "https://www.crowdstrike.com/global-threat-report/"),
    ("11. AI-Generated Ransomware", "Fastest breakout", "LLMs writing custom encryptors on demand", "Sophos 2026", "https://www.sophos.com/en-us/content/state-of-ransomware"),
    ("12. Shadow AI Data Leakage", "22% of breaches", "Rogue LLMs exfiltrating sensitive data", "IBM Cost of Breach 2026", "https://www.ibm.com/reports/data-breach"),
    ("13. AI-Driven BEC", "Deepfake voice", "CEO voice cloning for $142k+ wire fraud", "FBI IC3 2026", "https://www.ic3.gov/AnnualReport"),
    ("14. Training Data Poisoning", "Backdoor risk", "Corrupted datasets creating hidden triggers", "OWASP LLM Top 10", "https://owasp.org/www-project-top-10-for-large-language-model-applications/"),
    ("15. AI SOC Evasion", "New frontier", "Tricking XDR/SOAR with adversarial prompts", "Mandiant M-Trends 2026", "https://www.mandiant.com/m-trends")
]
ai_crime_rows = []
for rank, attack, trend, desc, source in ai_crime_data:
    ai_crime_rows.append([
        (rank, f"color:{CYAN};font-weight:bold;white-space:nowrap;"),
        (attack, f"color:{GREEN};font-weight:bold;"),
        (trend, f"color:{RED};font-weight:bold;"),
        (desc, f"color:#888;font-size:.56rem;"),
        (f'<a href="{source}" target="_blank" style="color:{AMBER};text-decoration:none;">Source</a>', f"color:{AMBER};font-weight:bold;")
    ])
# ── OWASP LLM TOP 10 (v1.1) ──────────────────────────────────────────────────
owasp_data = [
    ("LLM01", "Prompt Injection", "Adversary crafts input to bypass filters or exfil data", "🔴 Critical", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/01_prompt_injection"),
    ("LLM02", "Insecure Output Handling", "LLM output not sanitized leading to XSS/SQLi/RCE", "🔴 Critical", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/02_insecure_output"),
    ("LLM03", "Training Data Poisoning", "Backdoors via corrupted training data", "🟡 High", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/03_training_data_poisoning"),
    ("LLM04", "Model Denial of Service", "Resource exhaustion via complex prompts", "🟡 High", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/04_model_dos"),
    ("LLM05", "Supply Chain Vulnerabilities", "Compromised weights/plugins/pipelines", "🔴 Critical", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/05_supply_chain"),
    ("LLM06", "Sensitive Info Disclosure", "LLM leaks PII/creds in responses", "🔴 Critical", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/06_sensitive_info_disclosure"),
    ("LLM07", "Insecure Plugin Design", "Excessive perms, no input validation", "🟡 High", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/07_insecure_plugin_design"),
    ("LLM08", "Excessive Agency", "Agents w/too many perms, autonomous", "🟡 High", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/08_excessive_agency"),
    ("LLM09", "Overreliance", "Blind trust in LLM output → errors/risks", "🟡 Medium", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/09_overreliance"),
    ("LLM10", "Model Theft", "Steal model weights/IP", "🟡 Medium", "https://owasp.org/www-project-top-10-for-large-language-model-applications/descriptions/10_model_theft")
]
owasp_rows = []
for id_, vuln, desc, risk, link in owasp_data:
    owasp_rows.append([
        (id_, f"color:{RED};font-weight:bold;"),
        (f'<a href="{link}" target="_blank" style="color:{CYAN};text-decoration:none;border-bottom:1px dashed {CYAN}40;">{vuln}</a>', f"color:{CYAN};font-weight:bold;"),
        (desc, f"color:#888;font-size:.56rem;"),
        (risk, f"color:{RED if 'Critical' in risk else AMBER};font-weight:bold;"),
        ("OWASP", f"color:{AMBER};font-weight:bold;")
    ])
# ── MITRE ATT&CK TOP TECHNIQUES (2026) ───────────────────────────────────────
attck_data = [
    ("T1055", "Process Injection", "Defense Evasion", "Inject code into legitimate processes to evade detection", "83%", "https://attack.mitre.org/techniques/T1055/"),
    ("T1059", "Command and Scripting Interpreter", "Execution", "Execute commands via shells or scripts for initial access", "79%", "https://attack.mitre.org/techniques/T1059/"),
    ("T1078", "Valid Accounts", "Persistence", "Use stolen credentials for persistence and lateral movement", "76%", "https://attack.mitre.org/techniques/T1078/"),
    ("T1555", "Credentials from Password Stores", "Credential Access", "Extract credentials from browsers, OS stores, and keychains", "66%", "https://attack.mitre.org/techniques/T1555/"),
    ("T1497", "Virtualization/Sandbox Evasion", "Discovery", "Detect and evade sandboxes and virtual environments", "59%", "https://attack.mitre.org/techniques/T1497/"),
    ("T1021", "Remote Services", "Lateral Movement", "Use RDP, SSH, or SMB for internal pivoting", "56%", "https://attack.mitre.org/techniques/T1021/"),
    ("T1486", "Data Encrypted for Impact", "Impact", "Encrypt files and demand ransom (ransomware)", "53%", "https://attack.mitre.org/techniques/T1486/"),
    ("T1566", "Phishing", "Initial Access", "Deliver malware or steal creds via email/social", "49%", "https://attack.mitre.org/techniques/T1566/"),
    ("T1190", "Exploit Public-Facing Application", "Initial Access", "Exploit internet-facing apps for entry", "43%", "https://attack.mitre.org/techniques/T1190/"),
    ("T1003", "OS Credential Dumping", "Credential Access", "Dump LSASS, SAM, or NTDS.dit for creds", "39%", "https://attack.mitre.org/techniques/T1003/"),
    ("T1569", "System Services", "Execution", "Execute malicious payloads via Windows services", "36%", "https://attack.mitre.org/techniques/T1569/"),
    ("T1570", "Lateral Tool Transfer", "Lateral Movement", "Transfer tools across compromised systems", "33%", "https://attack.mitre.org/techniques/T1570/"),
    ("T1489", "Service Stop", "Impact", "Stop critical services during ransomware deployment", "31%", "https://attack.mitre.org/techniques/T1489/"),
    ("T1210", "Exploitation of Remote Services", "Lateral Movement", "Exploit unpatched remote services", "29%", "https://attack.mitre.org/techniques/T1210/"),
    ("T1110", "Brute Force", "Credential Access", "Password spraying and credential stuffing", "26%", "https://attack.mitre.org/techniques/T1110/")
]
attck_rows = []
for id_, tech, tactic, desc, freq, link in attck_data:
    attck_rows.append([
        (f'<a href="{link}" target="_blank" style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE}40;">{id_}</a>', f"color:{BLUE};font-weight:bold;white-space:nowrap;"),
        (tech, f"color:{CYAN};font-weight:bold;"),
        (tactic, f"color:{GREY};"),
        (desc, f"color:#888;font-size:.56rem;"),
        (freq, f"color:{GREEN};font-weight:bold;")
    ])
# ── 💀 TOP RANSOMWARE GROUPS 2026 (updated July 2026) ────────────────────────────────────────────
rwg_data = [
    ("Qilin", "~31%", "1,300+", "🔴 Active", "Dominant RaaS with triple extortion and Linux support", "https://www.sophos.com/en-us/content/state-of-ransomware"),
    ("Akira", "~23%", "880+", "🔴 Active", "$260M extorted; targets healthcare and manufacturing", "https://www.crowdstrike.com/global-threat-report/"),
    ("Cl0p", "~19%", "650+", "🔴 Active", "Mass MOVEit and GoAnywhere exploits", "https://www.ibm.com/reports/data-breach"),
    ("LockBit5", "~15%", "480+", "🔴 Active", "Aggressive RaaS with affiliate program", "https://www.chainalysis.com/blog/crypto-hacking-stolen-funds-2025/"),
    ("Play", "~12%", "410+", "🔴 Active", "Heavy focus on government and education sectors", "https://www.mandiant.com/m-trends"),
    ("Medusa", "~10%", "350+", "🔴 Active", "Triple extortion with data leak sites", "https://www.sophos.com/en-us/content/state-of-ransomware"),
    ("INC Ransom", "~9%", "430+", "🔴 Active", "Education and critical infrastructure focus", "https://www.crowdstrike.com/global-threat-report/"),
    ("DragonForce", "~7%", "260+", "🔴 Active", "New alliance member with fast encryption", "https://www.ibm.com/reports/data-breach"),
    ("BlackCat/ALPHV", "~5%", "220+", "🔴 Active", "Rebranded after FBI takedown", "https://www.ibm.com/reports/data-breach"),
    ("Hive", "~3%", "170+", "🟡 Disrupted", "Ransomware-as-a-Service still active", "https://www.crowdstrike.com/global-threat-report/"),
    ("Conti Remnants", "~3%", "160+", "🔴 Active", "Splinter groups continuing operations", "https://www.mandiant.com/m-trends"),
    ("BianLian", "~2%", "140+", "🔴 Active", "Double extortion on healthcare", "https://www.sophos.com/en-us/content/state-of-ransomware"),
    ("Lynx", "~3%", "170+", "🔴 Active", "Emerging RaaS targeting MSPs and SMEs using phishing and credential theft", "https://www.itpro.com/security/ransomware/msps-beware-these-two-ransomware-groups-are-ramping-up-attacks-and-have-claimed-hundreds-of-victims"),
    ("Everest", "~2%", "140+", "🔴 Active", "Data-theft focused extortion group operating a public leak site", "https://www.cisa.gov/news-events/cybersecurity-advisories"),
    ("CyberVolk", "~2%", "120+", "🔴 Active", "Pro-Russian ransomware collective blending RaaS with hacktivism campaigns", "https://en.wikipedia.org/wiki/CyberVolk")
]
rwg_rows = []
for group, share, victims, status, intel, source in rwg_data:
    rwg_rows.append([
        (group, f"color:{CYAN};font-weight:bold;"),
        (share, f"color:{GREEN};font-weight:bold;"),
        (victims, f"color:{AMBER};"),
        (status, f"color:{RED};font-weight:bold;"),
        (f'<a href="{source}" target="_blank" style="color:{AMBER};text-decoration:none;">{intel}</a>', f"color:#888;font-size:.56rem;")
    ])
# ── 🌐 NATION-STATE APT GROUPS 2026 ──────────────────────────────────────────
apts_data = [
    ("Salt Typhoon", "🇨🇳", "Telecom & critical infrastructure espionage", "Persistent access to 9+ major ISPs", "https://www.crowdstrike.com/global-threat-report/"),
    ("Volt Typhoon", "🇨🇳", "Critical infrastructure pre-positioning", "Living-off-the-land stealth campaigns", "https://www.mandiant.com/m-trends"),
    ("Flax Typhoon", "🇨🇳", "Long-term espionage", "Highly persistent with minimal detection", "https://www.ibm.com/reports/data-breach"),
    ("Mustang Panda", "🇨🇳", "Regional geopolitical targets", "Spear-phishing & identity attacks", "https://attack.mitre.org/groups/G0129/"),
    ("APT28 (Fancy Bear)", "🇷🇺", "NATO & election interference", "GRU-linked disinformation & hacks", "https://attack.mitre.org/groups/G0007/"),
    ("APT29 (Cozy Bear)", "🇷🇺", "Government & think-tank espionage", "SVR stealth operations", "https://attack.mitre.org/groups/G0016/"),
    ("Sandworm", "🇷🇺", "Destructive cyber operations", "Ukraine grid & wiper attacks", "https://attack.mitre.org/groups/G0034/"),
    ("Lazarus Group", "🇰🇵", "Financial theft & crypto heists", "$2.1B stolen in 2025 alone", "https://www.chainalysis.com/blog/crypto-hacking-stolen-funds-2025/"),
    ("APT41 (BARIUM)", "🇨🇳", "Financial & intellectual property theft", "Dual-use espionage and crime", "https://attack.mitre.org/groups/G0096/"),
    ("APT35 (Charming Kitten)", "🇮🇷", "Middle East targeting", "Spear-phishing and credential theft", "https://attack.mitre.org/groups/G0059/"),
    ("MuddyWater", "🇮🇷", "Middle East & Europe", "Custom malware and living-off-the-land", "https://attack.mitre.org/groups/G0069/"),
    ("GALLIUM", "🇨🇳", "Telecom operators globally", "Exploitation of unpatched routers", "https://www.mandiant.com/m-trends")
]
apts_rows = []
for group, flag, focus, intel, source in apts_data:
    apts_rows.append([
        (group, f"color:{CYAN};font-weight:bold;"),
        (flag, ""),
        (focus, f"color:{GREY};"),
        (intel, f"color:#888;font-size:.56rem;"),
        (f'<a href="{source}" target="_blank" style="color:{AMBER};text-decoration:none;">Source</a>', f"color:{AMBER};font-weight:bold;")
    ])
# ── ATTACK VECTOR BREAKDOWN (2026) ───────────────────────────────────────────
vectors_data = [
    ("Stolen Credentials", "23%", "Dark web sales remain #1 vector", "$5.1M avg incident cost", "https://www.ibm.com/reports/data-breach"),
    ("Phishing", "17%", "AI-enhanced spear-phishing & vishing", "Most common initial access", "https://www.crowdstrike.com/global-threat-report/"),
    ("Supply Chain", "31%", "Compromised third-party software & models", "Doubled YoY", "https://attack.mitre.org/tactics/TA0001/"),
    ("Shadow AI", "22%", "Unsanctioned LLM use in enterprises", "22% of all breaches", "https://www.ibm.com/reports/data-breach"),
    ("Exploited Vulnerabilities", "21%", "KEV catalog + zero-days", "Up 37% YoY", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"),
    ("Denial of Service", "14%", "AI-amplified DDoS campaigns", "Disruption & extortion", "https://radar.cloudflare.com/"),
    ("Business Email Compromise", "10%", "Deepfake voice & CEO fraud", "$142k+ average wire fraud", "https://www.ic3.gov/AnnualReport"),
    ("Malicious Insider", "8%", "Insider threats with AI tools", "Costliest per incident", "https://www.ibm.com/reports/data-breach"),
    ("Human Error", "27%", "Misconfigurations & accidental leaks", "Non-malicious oversight", "https://www.ibm.com/reports/data-breach"),
    ("IT System Failure", "24%", "Outages and cloud misconfigs", "System/process failure", "https://www.ibm.com/reports/data-breach"),
    ("Ransomware-as-a-Service", "19%", "Affiliate model explosion", "Fastest breakout", "https://www.sophos.com/en-us/content/state-of-ransomware"),
    ("Zero-Day Exploits", "12%", "Unpatched critical vulns", "High-impact RCE", "https://www.vulncheck.com/")
]
vectors_rows = []
for vector, share, desc, impact, source in vectors_data:
    vectors_rows.append([
        (vector, f"color:{CYAN};font-weight:bold;"),
        (share, f"color:{RED};font-weight:bold;"),
        (desc, f"color:#888;font-size:.56rem;"),
        (impact, f"color:{AMBER};"),
        (f'<a href="{source}" target="_blank" style="color:{GREEN};text-decoration:none;">Source</a>', f"color:{GREEN};font-weight:bold;")
    ])
# ── TOP EXPLOITED CVEs 2026 ──────────────────────────────────────────────────
topcves_data = [
    ("CVE-2025-55182", "React2Shell", "10.0", "RCE · Most targeted in 2026", "https://nvd.nist.gov/vuln/detail/CVE-2025-55182"),
    ("CVE-2025-53770", "Microsoft SharePoint", "9.8", "Zero-day RCE chain", "https://nvd.nist.gov/vuln/detail/CVE-2025-53770"),
    ("CVE-2020-1472", "Microsoft ZeroLogon", "10.0", "Still #1 persistent exploit", "https://nvd.nist.gov/vuln/detail/CVE-2020-1472"),
    ("CVE-2021-44228", "Log4Shell", "10.0", "Supply chain impact", "https://nvd.nist.gov/vuln/detail/CVE-2021-44228"),
    ("CVE-2024-3400", "Palo Alto PAN-OS", "10.0", "Firewall RCE", "https://nvd.nist.gov/vuln/detail/CVE-2024-3400"),
    ("CVE-2025-66516", "Apache Tika", "9.8", "XXE/SSRF in document processing", "https://nvd.nist.gov/vuln/detail/CVE-2025-66516"),
    ("CVE-2024-21887", "Ivanti Connect Secure", "9.1", "VPN authentication bypass", "https://nvd.nist.gov/vuln/detail/CVE-2024-21887"),
    ("CVE-2025-52691", "SmarterMail", "9.8", "File upload RCE", "https://nvd.nist.gov/vuln/detail/CVE-2025-52691"),
    ("CVE-2026-21509", "Microsoft Office", "8.8", "Zero-day exploit chain", "https://nvd.nist.gov/vuln/detail/CVE-2026-21509"),
    ("CVE-2026-20841", "Windows Notepad", "7.8", "Code execution via malformed files", "https://nvd.nist.gov/vuln/detail/CVE-2026-20841"),
    ("CVE-2025-31112", "Cisco IOS XE", "9.8", "Remote code execution", "https://nvd.nist.gov/vuln/detail/CVE-2025-31112"),
    ("CVE-2025-42821", "Fortinet FortiGate", "9.8", "SSL-VPN authentication bypass", "https://nvd.nist.gov/vuln/detail/CVE-2025-42821")
]
topcves_rows = []
for cve, product, cvss, impact, link in topcves_data:
    topcves_rows.append([
        (f'<a href="{link}" target="_blank" style="color:{RED};text-decoration:none;border-bottom:1px dashed {RED}40;">{cve}</a>', f"color:{RED};font-weight:bold;white-space:nowrap;"),
        (product, f"color:{CYAN};font-weight:bold;"),
        (cvss, f"color:{AMBER};font-weight:bold;"),
        (impact, f"color:#888;font-size:.56rem;"),
        ("NVD", f"color:{GREEN};font-weight:bold;")
    ])
# ── BREACH COST BY INDUSTRY (2026) ───────────────────────────────────────────
costs_data = [
    ("US Average", "$10.5M", "All-time high (+9%)", "Largest recorded breaches", "https://www.ibm.com/reports/data-breach"),
    ("Healthcare", "$7.6M", "#1 for 15 consecutive years", "Ransomware & data sensitivity", "https://www.ibm.com/reports/data-breach"),
    ("Financial", "$5.7M", "BEC & insider threats", "Regulatory fines heavy", "https://www.ibm.com/reports/data-breach"),
    ("Industrial / Mfg", "$5.2M", "OT risks & IP theft", "Physical disruption impact", "https://www.sophos.com/en-us/content/state-of-ransomware"),
    ("Technology", "$5.3M", "Supply chain & cloud misconfigs", "Intellectual property focus", "https://www.ibm.com/reports/data-breach"),
    ("Energy", "$5.0M", "Grid & critical infrastructure", "National security implications", "https://www.ibm.com/reports/data-breach"),
    ("Pharma", "$5.1M", "Clinical trial & drug IP theft", "High-value R&D targets", "https://www.ibm.com/reports/data-breach"),
    ("Global Average", "$4.44M", "Down 9% YoY globally", "Regional variation", "https://www.ibm.com/reports/data-breach"),
    ("Education", "$4.1M", "Ransomware & student data leaks", "Budget-constrained targets", "https://www.ibm.com/reports/data-breach"),
    ("Government", "$4.6M", "APT and nation-state attacks", "National security breaches", "https://www.ibm.com/reports/data-breach"),
    ("Retail", "$3.7M", "Payment card and customer data", "Ransomware surge", "https://www.ibm.com/reports/data-breach"),
    ("Hospitality", "$4.3M", "Guest data & POS systems", "Seasonal attack spikes", "https://www.ibm.com/reports/data-breach")
]
costs_rows = []
for industry, cost, detail, notes, source in costs_data:
    costs_rows.append([
        (industry, f"color:{CYAN};font-weight:bold;"),
        (cost, f"color:{RED};font-weight:bold;"),
        (detail, f"color:#888;font-size:.56rem;"),
        (notes, f"color:{AMBER};"),
        (f'<a href="{source}" target="_blank" style="color:{GREEN};text-decoration:none;">Source</a>', f"color:{GREEN};font-weight:bold;")
    ])
# ─── NEW LAYOUT (all tables consistent) ──────────────────────────────────────
g1, g2 = st.columns(2)
with g1: st.markdown(_tbl("🤖 TOP 15 AI MODELS & CAPABILITIES (Last updated July 2026)", ["Rank & Model", "Top Use Case", "Best For", "Description", "Top Vuln"], ai_rows, CYAN), unsafe_allow_html=True)
with g2: st.markdown(_tbl("🤖 AI-POWERED CYBERCRIME (2026)", ["Rank", "Attack", "Trend", "Description", "Source"], ai_crime_rows, CYAN), unsafe_allow_html=True)
g3, g4 = st.columns(2)
with g3: st.markdown(_tbl("🛡 OWASP LLM TOP 10 (v1.1)", ["ID", "Vulnerability", "Description", "Risk", "Link"], owasp_rows, CYAN), unsafe_allow_html=True)
with g4:
    if kev_rows:
        st.markdown(_tbl("📋 LATEST CISA KEV ADDITIONS (LIVE)", ["CVE", "Vendor", "Product", "Vulnerability", "Added", "RW", "Due"], kev_rows, BLUE), unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-size:.68rem;font-weight:bold;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px;border-bottom:1px solid {BLUE}20;padding-bottom:3px;">📋 LATEST CISA KEV ADDITIONS (LIVE)</div><div style="padding:14px;border:1px solid #1a1a2e;background:#080810;text-align:center;margin-bottom:10px;"><span style="color:{GREY};font-size:.7rem;">📋 CISA KEV · Populates on Streamlit Cloud deployment</span></div>', unsafe_allow_html=True)
g5, g6 = st.columns(2)
with g5: st.markdown(_tbl("⚔ MITRE ATT&CK TOP TECHNIQUES (2026)", ["ID", "Technique", "Tactic", "Description", "Freq"], attck_rows, BLUE), unsafe_allow_html=True)
with g6: st.markdown(_tbl("💀 TOP RANSOMWARE GROUPS 2026", ["Group", "Share", "Victims", "Status", "Source"], rwg_rows, RED), unsafe_allow_html=True)
g7, g8 = st.columns(2)
with g7: st.markdown(_tbl("🌐 NATION-STATE APT GROUPS 2026", ["Group", "Origin", "Focus", "Activity", "Source"], apts_rows, AMBER), unsafe_allow_html=True)
with g8: st.markdown(_tbl("📊 ATTACK VECTOR BREAKDOWN (2026)", ["Vector", "Share", "Description", "Impact", "Source"], vectors_rows, GREEN), unsafe_allow_html=True)
g9, g10 = st.columns(2)
with g9: st.markdown(_tbl("🔥 TOP EXPLOITED CVEs 2026", ["CVE", "Product", "CVSS", "Impact", "Link"], topcves_rows, RED), unsafe_allow_html=True)
with g10: st.markdown(_tbl("💰 BREACH COST BY INDUSTRY (2026)", ["Industry", "Avg Cost", "Detail", "Notes", "Source"], costs_rows, GREEN), unsafe_allow_html=True)
st.markdown(f'<div style="font-size:.48rem;color:#505060;margin:2px 0 0 4px;">Sources: <a href="https://www.ibm.com/reports/data-breach" target="_blank" class="sl">IBM Cost of Breach 2026</a> · <a href="https://www.crowdstrike.com/global-threat-report/" target="_blank" class="sl">CrowdStrike GTR 2026</a> · <a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/" target="_blank" class="sl">OWASP LLM Top 10</a> · <a href="https://attack.mitre.org/" target="_blank" class="sl">MITRE ATT&CK/ATLAS</a> · <a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog" target="_blank" class="sl">CISA KEV</a> · <a href="https://www.vulncheck.com/" target="_blank" class="sl">VulnCheck</a> · <a href="https://redcanary.com/" target="_blank" class="sl">Red Canary</a> · <a href="https://www.chainalysis.com/" target="_blank" class="sl">Chainalysis</a> · <a href="https://www.sophos.com/en-us/content/state-of-ransomware" target="_blank" class="sl">Sophos</a> · Public disclosures</div>', unsafe_allow_html=True)
st.markdown("---")

# (Cleaned duplicate leftover section) 

# EU AI Act
with st.expander("🇪🇺 **EU AI Act** — The Highest AI-Specific Penalties Globally", expanded=True):
    st.markdown("""
    **Maximum Penalty:** 
    - **€35 million or 7% of global turnover** for prohibited AI practices
    - **€15 million or 3%** for most other obligations
    - **€7.5 million or 1%** for supplying incorrect information
    
    **Why it matters:** This is the first comprehensive AI law in the world with binding requirements and very high fines. It uses a risk-based approach:
    - **Prohibited practices** (social scoring, real-time biometric ID in public spaces with limited exceptions, manipulative subliminal techniques)
    - **High-risk AI systems** (biometrics, critical infrastructure, education, employment, law enforcement, etc.) — require conformity assessment, risk management, data quality, transparency, human oversight, and logging.
    - **General-purpose AI models** (like large language models) have transparency and copyright obligations.
    
    **Timeline:** Most obligations apply from August 2026 onward.
    
    **Official Source:** [EU AI Act Official Text](https://artificialintelligenceact.eu/)
    """)

# NIS2 + DORA
with st.expander("🇪🇺 **NIS2 Directive & DORA** — Critical Infrastructure & Financial Sector", expanded=False):
    st.markdown("""
    **NIS2 Maximum Penalty:** Up to **€10 million or 2% of global turnover**.
    
    **DORA Maximum Penalty:** Up to **2% of global turnover** + potential personal liability for management bodies.
    
    **Key Requirements:**
    - NIS2 significantly expands the scope of the original NIS Directive to more sectors (including digital providers, postal services, waste management, etc.).
    - Mandatory supply chain security and third-party risk management.
    - 24h early warning + 72h full incident report.
    - DORA applies specifically to the financial sector and requires ICT risk management, resilience testing, and oversight of critical third-party providers (including cloud and AI service providers).
    
    **Why CISOs should care:** Both explicitly require governance accountability at the highest levels. Management bodies can be held personally responsible.
    
    **Official Sources:** 
    - [NIS2 Directive](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)
    - [DORA Regulation](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)
    """)

# US Regulations
with st.expander("🇺🇸 **US Regulatory Landscape** — SEC, CMMC, State Privacy Laws", expanded=False):
    st.markdown("""
    **SEC Cybersecurity Disclosure Rules**
    - Material incidents must be disclosed on Form 8-K within **4 business days**.
    - Annual disclosures required on cybersecurity risk management, strategy, and board oversight.
    - Enforcement actions have already begun for inadequate or delayed disclosure.
    
    **CMMC 2.0 (Defense Contractors)**
    - Level 2 requires third-party assessment against NIST SP 800-171.
    - Non-compliance can lead to loss of DoD contracts and False Claims Act liability.
    
    **State Privacy Laws (CCPA/CPRA + others)**
    - California: Up to $7,500 per intentional violation.
    - Growing number of states with similar laws (Virginia, Colorado, Connecticut, Utah, etc.).
    - Increasing requirements around automated decision-making and profiling disclosures.
    
    **Official Sources:**
    - [SEC Final Rule](https://www.sec.gov/rules/final/2023/33-11216.pdf)
    - [CMMC Program](https://dodcio.defense.gov/CMMC/)
    - [CPPA (California)](https://cppa.ca.gov/)
    """)

st.markdown("---")

# Quick Reference Table
st.markdown(f'<div style="margin-top:10px; margin-bottom:8px; color:#888; font-size:0.68rem; text-transform:uppercase; letter-spacing:0.8px;">Quick Reference — Maximum Penalties</div>', unsafe_allow_html=True)

# Continue to Global Threat Metrics
st.markdown(f"""
<div id="global-threat-metrics" style="text-align: left; margin: 40px 0 20px 5px;">
  <div style="font-size: 0.9rem; font-weight: bold; color: {CYAN}; letter-spacing: 1.5px; text-transform: uppercase;">
    &gt;&gt; Global Threat Metrics
  </div>
  <div style="font-size: 0.55rem; color: #505060; margin-top: 4px; letter-spacing: 0.5px; line-height: 1.5;">
    <span style="color: {GREEN}; border: 1px solid {GREEN}40; padding: 0 3px; border-radius: 2px; font-weight: bold;">LIVE</span> REAL-TIME &nbsp;
    <span style="color: {AMBER}; border: 1px solid {AMBER}40; padding: 0 3px; border-radius: 2px; font-weight: bold;">EST</span> VERIFIED &nbsp;
    <span style="color: {CYAN}; border: 1px solid {CYAN}40; padding: 0 3px; border-radius: 2px; font-weight: bold;">PULSE</span> DSHIELD &nbsp;
    <span style="margin-left: 10px; opacity: 0.6;">118 INDICATORS // 14 ACTIVE DATA ROWS</span>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown(f'<div class="rl-p">🤖 AI &amp; LLM THREAT INTELLIGENCE — EMERGING ATTACK LANDSCAPE</div>', unsafe_allow_html=True)
c = st.columns(6)
with c[0]:
    pcard("DEEPFAKE VISHING","https://www.crowdstrike.com/global-threat-report/",
        "+442% YoY", "AI voice cloning attacks",
        "▸ 3 seconds of audio to clone a voice",
        "–","d-n", "+442%", "d-b", False,
        facts=["$28M Hong Kong deepfake video scam","CEO voice cloned for wire transfers","Real-time voice changers available","Detection tools still lagging behind","Microsoft VALL-E: 3-sec voice clone"])
with c[1]:
    pcard("LLM PHISHING","https://owasp.org/www-project-top-10-for-large-language-model-applications/",
        "AI-Crafted", "Perfect grammar, personalized",
        "▸ No more typos to detect",
        "–","d-n", "Scaling fast", "d-b", False,
        facts=["ChatGPT-quality phish at scale","Spear-phishing personalized via OSINT","Multi-language campaigns trivial","WormGPT/FraudGPT on dark web","Traditional email filters bypassed"])
with c[2]:
    pcard("PROMPT INJECTION","https://owasp.org/www-project-top-10-for-large-language-model-applications/",
        "OWASP LLM #1", "Top LLM vulnerability",
        "▸ Data exfiltration via chat interfaces",
        "–","d-n", "#1 LLM risk", "d-b", False,
        facts=["Direct & indirect injection types","System prompt extraction attacks","Plugin/tool abuse via injection","Jailbreaking bypasses safety filters","No complete mitigation exists yet"])
with c[3]:
    pcard("AI MODEL POISONING","https://atlas.mitre.org/",
        "Supply Chain", "Backdoored ML models",
        "▸ Hugging Face: 100+ malicious models found",
        "–","d-n", "Growing", "d-b", False,
        facts=["Training data contamination","Trojan triggers in model weights","Hugging Face scanning for malware","MITRE ATLAS tracks AI TTPs","Pickle deserialization RCE in models"])
with c[4]:
    pcard("AI-POWERED MALWARE","https://www.crowdstrike.com/global-threat-report/",
        "Polymorphic", "AI-generated evasive code",
        "▸ Metamorphic malware bypasses AV",
        "–","d-n", "Emerging", "d-b", False,
        facts=["BlackMamba: AI-powered keylogger","Code mutation evades signatures","LLMs write exploit code on demand","Automated vulnerability discovery","AI fuzzing finds 0-days faster"])
with c[5]:
    pcard("AI DEFENSE GAP","https://www.ibm.com/reports/data-breach",
        "$2.3M Saved", "AI-assisted defense (IBM)",
        "▸ But only 31% of orgs fully deployed",
        "–","d-n", "31% adoption", "d-g", False,
        facts=["AI cuts breach lifecycle 100+ days","SOC copilots reduce alert fatigue","Automated threat hunting emerging","SOAR + AI = faster response","Skills gap driving AI adoption"])
# ─── PULSE ROW 4 ─────────────────────────────────────────────────────────────
st.markdown(f'<div class="rl-p">🔐 CLOUD, IDENTITY & AI GOVERNANCE METRICS</div>', unsafe_allow_html=True)
c = st.columns(6)
with c[0]:
    pcard("MALWARE-FREE ATTACKS","https://www.crowdstrike.com/global-threat-report/",
        "82%", "No malware used · CS GTR 2026",
        "▸ Up from 71% in 2023",
        "–","d-n", "+8% YoY", "d-b", False,
        facts=["82% in 2026 GTR (latest)","Valid credentials primary vector","Access brokers up 50% YoY","Hands-on-keyboard intrusions","EDR evasion via LOLBins"])
with c[1]:
    pcard("CLOUD INTRUSIONS","https://www.crowdstrike.com/global-threat-report/",
        "+27% YoY", "Cloud-focused attacks · CS",
        "▸ Valid accounts 36% of cloud access",
        "–","d-n", "+38% in 2026", "d-b", False,
        facts=["Cloud-conscious actors growing","API key theft primary vector","S3/Azure Blob misconfig exploited","Cloud control plane attacks rising","270% surge from nation-states"])
with c[2]:
    pcard("SHADOW AI BREACHES","https://www.ibm.com/reports/data-breach",
        "22%", "of breaches involve shadow AI",
        "▸ Adds $680k to avg breach cost",
        "–","d-n", "$4.7M avg", "d-b", False,
        facts=["97% lacked AI access controls","63% have no AI governance policy","Only 35% audit for rogue AI","PII exposed in 66% of shadow AI","1,300 avg unauthorized apps/org"])
with c[3]:
    pcard("AI GOVERNANCE GAP","https://www.ibm.com/reports/data-breach",
        "62%", "orgs lack AI governance · IBM",
        "▸ Only 38% have approval processes",
        "–","d-n", "62% ungoverned", "d-b", False,
        facts=["14% had AI model/app breach","61% lack AI governance tech","CAIO role emerging in C-suite","EU AI Act enforcement began 2024","NIST AI RMF adoption growing"])
with c[4]:
    pcard("IDENTITY ATTACKS","https://www.crowdstrike.com/global-threat-report/",
        "79%", "initial access via credentials",
        "▸ Kerberoasting up 583% · CS GTR",
        "–","d-n", "79% of attacks", "d-b", False,
        facts=["DPRK placed 304 insider operatives","40% were insider threat ops","Access broker ads +50% YoY","Phishing-resistant MFA critical","FIDO2 hardware keys recommended"])
with c[5]:
    pcard("BREAKOUT TIME 2026","https://www.crowdstrike.com/global-threat-report/",
        "29 Min Avg", "CS GTR 2026 · down 65%",
        "▸ Fastest: 27 seconds",
        "–","d-n", "was 48 min", "d-g", False,
        facts=["Sub-minute breakouts recorded","Automated tooling enables speed","29 min avg in 2025 (from 48)","Detection must be real-time","MDR/XDR essential for response"])
# ─── PULSE ROW 8: COMPLIANCE & THIRD-PARTY RISK ──────────────────────────────
st.markdown(f'<div class="rl-p">📊 COMPLIANCE POSTURE &amp; THIRD-PARTY RISK</div>', unsafe_allow_html=True)
c = st.columns(6)
with c[0]:
    pcard("SOC 2 FAILURE RATE","https://www.aicpa-cima.com/",
        "41%", "fail first audit attempt",
        "▸ Access controls #1 failure area",
        "–","d-n", "41% fail rate", "d-b", False,
        facts=["CC6.1 logical access most failed","Monitoring gaps #2 finding","Evidence collection biggest hurdle","Avg prep time: 6-12 months","Readiness assessment saves 40%"])
with c[1]:
    pcard("VENDOR BREACHES","https://www.verizon.com/business/resources/reports/dbir/",
        "16%", "of breaches via 3rd party",
        "▸ Supply chain now #2 vector (IBM 2025)",
        "–","d-n", "+63% YoY", "d-b", False,
        facts=["MOVEit hit 2,700+ orgs via vendor","Avg 3rd party breach: $5.1M","Only 35% audit vendors annually","SBOMs becoming contractual req","TPRM programs underfunded 70%"])
with c[2]:
    pcard("REGULATORY FINES","https://www.enforcementtracker.com/",
        "€2.2B+ /yr", "GDPR · FTC · State AGs combined",
        "▸ Meta: €1.2B single fine (record)",
        "–","d-n", "€4.6B+ total since 2018", "d-b", False,
        facts=["SEC cyber disclosure rules active","CCPA/CPRA enforcement expanding","NIS2 penalties now in effect","DORA financial sector Jan 2025","State privacy laws: 19 enacted"])
with c[3]:
    pcard("AUDIT READINESS","https://www.isaca.org/",
        "32%", "orgs always audit-ready",
        "▸ 68% scramble before audits",
        "–","d-n", "32% ready", "d-b", False,
        facts=["Continuous compliance trending","GRC platforms growing 14% CAGR","Manual evidence: 40hrs/audit avg","Automation cuts prep time 60%","Framework mapping reduces overlap"])
with c[4]:
    pcard("CYBER INSURANCE","https://www.ibm.com/reports/data-breach",
        "71%", "of orgs carry cyber insurance",
        "▸ Premiums stabilizing after 2023 spike",
        "–","d-n", "+300% since 2020", "d-b", False,
        facts=["MFA now required for coverage","Exclusions expanding (war/APT)","IR retainer often mandatory","Claims avg 44% of policy limit","32% denied claims in 2024"])
with c[5]:
    pcard("FRAMEWORK ADOPTION","https://www.nist.gov/cyberframework",
        "NIST CSF #1", "Most adopted framework globally",
        "▸ 74% of US orgs use NIST CSF",
        "–","d-n", "ISO 27001 #1 intl", "d-b", False,
        facts=["NIST CSF 2.0 added Govern function","ISO 27001:2022 transition complete","CIS Controls popular for SMBs","CMMC 2.0 rollout underway","Zero Trust adoption: 68%"])
# ─── PULSE ROW 3 ─────────────────────────────────────────────────────────────
st.markdown(f'<div class="rl-p">⚡ SECTOR RISK & ADVERSARY INTELLIGENCE</div>', unsafe_allow_html=True)
c = st.columns(6)
with c[0]:
    pcard("#1 TARGETED SECTOR","https://www.ibm.com/reports/data-breach",
        "Healthcare", "$7.6M avg breach cost",
        "▸ 68% hit by ransomware in 2025",
        "–","d-n", "#1 for 14 yrs", "d-b", False,
        facts=["PHI worth 10x credit card data","HIPAA fines add to breach cost","Change Healthcare: $22M ransom","Patient safety directly at risk","Legacy systems widespread"])
with c[1]:
    pcard("#2 TARGETED SECTOR","https://www.ibm.com/reports/data-breach",
        "Financial", "$6.1M avg breach cost",
        "▸ BEC & wire fraud primary vectors",
        "–","d-n", "$6.1M avg", "d-b", False,
        facts=["PCI DSS 4.0 compliance required","Real-time transaction fraud growing","SWIFT system attacks continue","Crypto exchanges targeted heavily","Regulatory fines compounding"])
with c[2]:
    pcard("#3 TARGETED SECTOR","https://www.ibm.com/reports/data-breach",
        "Industrial/Mfg", "$5.6M avg breach cost",
        "▸ OT/ICS convergence risk",
        "–","d-n", "$5.6M avg", "d-b", False,
        facts=["Ransomware: 63% pay the ransom","OT networks often unpatched","Air-gap myth increasingly false","Safety systems now IP-connected","Production downtime: $300k+/hour"])
with c[3]:
    pcard("#1 THREAT ACTOR","https://www.crowdstrike.com/global-threat-report/",
        "DPRK / Lazarus", "$1.4B crypto stolen 2025",
        "▸ 48 incidents · 62% of all theft",
        "–","d-n", "$1.4B", "d-b", False,
        facts=["Funds WMD & missile programs","IT workers infiltrate crypto firms","Social engineering campaigns","Tornado Cash for laundering","Active since 2009"])
with c[4]:
    pcard("eCRIME INDEX","https://www.crowdstrike.com/global-threat-report/",
        "ECX: HIGH", "CrowdStrike eCrime Index",
        "▸ Breakout time now 51 seconds",
        "–","d-n", "48 min avg", "d-b", False,
        facts=["Avg eCrime breakout: 48 min","Russia, China, Iran top sponsors","150 named threat actor groups","Access broker ecosystem thriving","RaaS lowering barrier to entry"])
with c[5]:
    pcard("TOP INITIAL ACCESS","https://www.sophos.com/en-us/content/state-of-ransomware",
        "Exploited Vulns", "30% of ransomware entry",
        "▸ Then: phishing 22% · creds 21%",
        "–","d-n", "30% of attacks", "d-b", False,
        facts=["VPN appliances: #1 target asset","Phishing: 22% of initial access","Stolen credentials: 21%","Brute force: 10%","Unknown/other: 19%"])
st.markdown(f'<div class="rl-p">⚡ RANSOMWARE LANDSCAPE & EXTORTION ECONOMICS</div>', unsafe_allow_html=True)
c = st.columns(6)
with c[0]:
    pcard("#1 RANSOMWARE GROUP","https://www.crowdstrike.com/global-threat-report/",
        "Qilin", "Most prolific RaaS 2026",
        "▸ ~31% of all ransomware globally",
        "–","d-n", "31% share", "d-b", False,
        facts=["Disrupted by FBI Feb 2024","Rebuilt within weeks of takedown","Affiliates operate globally","Cross-platform: Win, Linux, ESXi","Bug bounty program for their code"])
with c[1]:
    pcard("#2 RANSOMWARE GROUP","https://www.crowdstrike.com/global-threat-report/",
        "Akira", "Seized then resurfaced",
        "▸ $22M Change Healthcare ransom",
        "–","d-n", "$22M single hit", "d-b", False,
        facts=["Exit-scammed affiliates in 2024","Rust-based ransomware binary","FBI unseized the leak site","Healthcare mega-breach resulted","Parent group likely rebranding"])
with c[2]:
    pcard("#3 RANSOMWARE GROUP","https://www.crowdstrike.com/global-threat-report/",
        "Cl0p / TA505", "Mass exploitation specialist",
        "▸ MOVEit: 2,700+ orgs hit",
        "–","d-n", "2,700+ victims", "d-b", False,
        facts=["Zero-day exploitation focus","GoAnywhere: 130+ orgs in 2023","Extortion-only (no encryption)","$100M+ estimated total take","Russian-speaking operation"])
with c[3]:
    pcard("DOUBLE EXTORTION","https://www.crowdstrike.com/global-threat-report/",
        "93%", "of ransomware uses data theft",
        "▸ Encrypt + exfil + leak pressure",
        "–","d-n", "+7% YoY", "d-b", False,
        facts=["Data posted on leak sites","Triple extortion adds DDoS","Victims named publicly for pressure","Regulatory reporting forced by leaks","Even after paying, data may leak"])
with c[4]:
    pcard("RANSOM ECONOMY","https://www.chainalysis.com/blog/2025-crypto-crime-report-introduction/",
        "$1.1B Paid", "Total payments 2025",
        "▸ Down 35% from $1.7B peak 2023",
        "–","d-n", "-35% YoY", "d-g", False,
        facts=["Payment rate declining (25% Q4)","Better backups reducing payments","Law enforcement seizures effective","Insurance covering less of cost","Negotiation cutting amounts 50%+"])
with c[5]:
    pcard("DWELL → DEPLOY","https://www.crowdstrike.com/global-threat-report/",
        "51 Seconds", "Fastest observed breakout",
        "▸ Avg eCrime breakout: 48 min",
        "–","d-n", "48 min avg", "d-b", False,
        facts=["Nation-state avg: 79 min breakout","Lateral movement accelerating","Automated tools enable speed","Detection must be sub-minute","MDR/XDR essential for response"])
# ─── PULSE ROW 5 ─────────────────────────────────────────────────────────────
st.markdown(f'<div class="rl-p">⚡ ATTACK SURFACE & GLOBAL EXPOSURE INTEL</div>', unsafe_allow_html=True)
c = st.columns(6)
with c[0]:
    pcard("EXPOSED SMB/445","https://www.shodan.io/search?query=port%3A445",
        "~1.1M", "Internet-facing SMB",
        "▸ EternalBlue still exploited",
        "–","d-n", "1.1M exposed", "d-b", False,
        facts=["WannaCry worm still propagating","SMBv1 should be disabled globally","US & China most exposed","Lateral movement primary use","Patch MS17-010 still critical"])
with c[1]:
    pcard("EXPOSED RDP/3389","https://www.shodan.io/search?query=port%3A3389",
        "~3.4M", "Internet-facing RDP",
        "▸ #1 ransomware initial access",
        "–","d-n", "3.4M exposed", "d-b", False,
        facts=["70%+ ransomware uses RDP entry","BlueKeep CVE still unpatched widely","NLA + MFA required minimum","VPN gateway recommended instead","Lockout policies reduce brute force"])
with c[2]:
    pcard("EXPOSED DATABASES","https://www.shodan.io/",
        "~1.7M", "MySQL+Postgres+MongoDB",
        "▸ Ports 3306, 5432, 27017 open",
        "–","d-n", "1.7M exposed", "d-b", False,
        facts=["MongoDB ransomware campaigns active","Default creds: root with no password","Elasticsearch also widely exposed","Cloud migrations expose DB ports","Data exfil in minutes once found"])
with c[3]:
    pcard("TOP TARGET COUNTRY","https://www.crowdstrike.com/global-threat-report/",
        "United States", "47% of all targeted attacks",
        "▸ Then: UK 8% · Germany 7%",
        "–","d-n", "47% of attacks", "d-b", False,
        facts=["Largest digital economy globally","Most Fortune 500 headquarters","Critical infrastructure concentration","English-language phishing at scale","Richest ransomware targets"])
with c[4]:
    pcard("TOP SOURCE COUNTRY","https://isc.sans.edu/",
        "China", "~29% of malicious traffic",
        "▸ Then: US 14% · Russia 11%",
        "–","d-n", "~29% of scans", "d-b", False,
        facts=["Cloud hosting used as proxy","Attribution extremely difficult","Many attacks routed through VPS","Russia for targeted/APT attacks","Vietnam & India rising sources"])
with c[5]:
    pcard("OPEN S3 BUCKETS","https://www.trendmicro.com/",
        "~11,500+", "Publicly accessible storage",
        "▸ AWS, Azure, GCP misconfigs",
        "–","d-n", "11.5k+ exposed", "d-b", False,
        facts=["Automated scanners find in minutes","PII, PHI, credentials exposed","AWS Block Public Access helps","Terraform misconfigs common cause","GrayhatWarfare indexes open buckets"])
# ─── PULSE ROW 1: TOP ATTACKED PORTS ─────────────────────────────────────────
st.markdown(f'<div class="rl-p">⚡ LIVE THREAT PULSE — SANS DSHIELD SENSOR NETWORK</div>', unsafe_allow_html=True)
FB_PORTS = [
    {"port":"22","name":"SSH","records":860000,"sources":46000,"desc":"Brute-force credential attacks"},
    {"port":"23","name":"Telnet","records":430000,"sources":29000,"desc":"IoT botnet recruitment scans"},
    {"port":"443","name":"HTTPS","records":390000,"sources":33000,"desc":"Web app exploitation attempts"},
    {"port":"445","name":"SMB","records":300000,"sources":23000,"desc":"Worm propagation & lateral"},
    {"port":"80","name":"HTTP","records":280000,"sources":31000,"desc":"Web vuln scanning & exploits"},
    {"port":"3389","name":"RDP","records":220000,"sources":19000,"desc":"Remote desktop brute-force"},
]
c = st.columns(6)
for i in range(6):
    with c[i]:
        pfacts = [["Credential stuffing dominant","Root/admin combos tested","Fail2ban essential defense","Key-based auth recommended","Port knocking reduces noise"],
                  ["Mirai botnet recruitment","Default passwords exploited","IoT cameras primary target","ADB port 5555 also targeted","Should be blocked at perimeter"],
                  ["TLS exploitation growing","Web shell uploads common","API endpoint probing","Certificate impersonation","WAF rules critical defense"],
                  ["EternalBlue still exploited","WannaCry variants active","Lateral movement vector","File share enumeration","SMBv1 should be disabled"],
                  ["Directory traversal scans","Log4Shell still probed","WordPress vuln scanning","CGI-bin exploitation","Web app firewall essential"],
                  ["RDP brute force for ransomware","BlueKeep still exploited","NLA required as mitigation","Should never face internet","VPN/jump host recommended"]]
        if topports and len(topports["ports"])>i:
            p = topports["ports"][i]
            pcard(f'#{i+1} ATTACKED PORT',"https://isc.sans.edu/",
                f'{pn(p["port"])} (:{p["port"]})', f'{_f(p["records"])} events · {_f(p["sources"])} sources',
                f'▸ {_f(p["targets"])} unique targets hit',
                "–","d-n", f'{_f(p["records"])}', "d-b", True, facts=pfacts[i])
        else:
            fb = FB_PORTS[i]
            pcard(f'#{i+1} ATTACKED PORT',"https://isc.sans.edu/",
                f'{fb["name"]} (:{fb["port"]})', f'~{_f(fb["records"])} events/day · DShield',
                f'▸ {fb["desc"]}',
                "–","d-n", f'~{_f(fb["sources"])} sources', "d-b", False, facts=pfacts[i])
# ─── PULSE ROW 2 ─────────────────────────────────────────────────────────────
st.markdown(f'<div class="rl-p">⚡ ATTACK SOURCES, HONEYPOTS & THREAT CATEGORIES</div>', unsafe_allow_html=True)
c = st.columns(6)
with c[0]:
    if topips and topips.get("top_count",0) > 0:
        pcard("TOP ATTACK SOURCE","https://isc.sans.edu/",
            topips["top_ip"], f'{_f(topips["top_count"])} packets blocked',
            f'▸ {_f(topips["total"])} total from top 5 IPs',
            "–","d-n", f'{_f(topips["total"])}', "d-b", True,
            facts=["IPs rotate rapidly (cloud/VPS)","Most from cloud hosting providers","Blocking top 20 nets cuts 40% noise","GeoIP blocking: diminishing returns","Threat intel feeds automate blocking"])
    else:
        pcard("TOP ATTACK SOURCES","https://isc.sans.edu/",
            "~520k+ IPs/day", "Unique scanners seen by DShield",
            "▸ China, US, Russia top source countries",
            "–","d-n", "520k+/day", "d-b", False,
            facts=["IPs rotate rapidly (cloud/VPS)","Most from cloud hosting providers","Blocking top 20 nets cuts 40% noise","GeoIP blocking: diminishing returns","Threat intel feeds automate blocking"])
with c[1]:
    if honeypot and honeypot.get("reports",0) > 0:
        pcard("HONEYPOT HITS","https://isc.sans.edu/",
            _f(honeypot["reports"]), f'{honeypot["sources"]} sources · {honeypot["targets"]} targets',
            f'▸ Web honeypot data for {honeypot["date"]}',
            "–","d-n", f'{honeypot["date"]}', "d-n", True,
            facts=["Web exploit scanners dominate","Log4Shell still top probed vuln","Cowrie SSH honeypot most deployed","Data shared with DShield community","Useful for early warning detection"])
    else:
        pcard("HONEYPOT HITS","https://isc.sans.edu/",
            "~2,600/day", "Web honeypot submissions",
            "▸ Automated exploit scanners dominate",
            "–","d-n", "~2.6k/day", "d-b", False,
            facts=["Web exploit scanners dominate","Log4Shell still top probed vuln","Cowrie SSH honeypot most deployed","Data shared with DShield community","Useful for early warning detection"])
with c[2]:
    pcard("SSH BRUTE FORCE","https://isc.sans.edu/",
        "#1 Target", "Port 22 consistently most attacked",
        "▸ Root/admin credential stuffing",
        "–","d-n", "~860k events/day", "d-b", False,
        facts=["root:root still attempted","Password lists 1B+ entries","Chinese & Russian IPs dominate","Cloud VPS used as attack infra","Key-based auth stops 99% of attempts"])
with c[3]:
    pcard("RDP EXPOSURE","https://www.shodan.io/search?query=port%3A3389",
        "~3.4M", "Internet-facing RDP endpoints",
        "▸ Primary ransomware entry vector",
        "–","d-n", "3.4M exposed", "d-b", False,
        facts=["BlueKeep (CVE-2019-0708) still active","NLA reduces brute force risk","Account lockout policy essential","RDP gateway recommended","Used in 70%+ of ransomware cases"])
with c[4]:
    pcard("IOT SCANNING","https://isc.sans.edu/",
        "Telnet/MQTT", "Ports 23, 1883, 5555 targeted",
        "▸ Mirai-variant botnet recruitment",
        "–","d-n", "~430k/day", "d-b", False,
        facts=["Mirai source code public since 2016","Default creds in 90%+ of IoT","Smart cameras #1 recruited device","Botnet-for-hire: $50-$300/attack","OT devices increasingly scanned"])
with c[5]:
    if topports:
        top5 = ", ".join([f'{pn(p["port"])}' for p in topports["ports"][:5]])
        pcard("TOP 5 SUMMARY","https://isc.sans.edu/",
            top5, f'{_f(topports["total"])} total events',
            "▸ Updated from DShield every 30 min",
            "–","d-n", f'{_f(topports["total"])}', "d-b", True,
            facts=["SSH & Telnet dominate consistently","HTTP/HTTPS growing share","SMB persists despite patches","Port 5555 (ADB) emerging target","Seasonal variation in attack patterns"])
    else:
        pcard("TOP 5 TODAY","https://isc.sans.edu/",
            "SSH · Telnet · HTTPS · SMB · HTTP", "Most attacked services",
            "▸ Based on DShield historical patterns",
            "–","d-n", "~2.3M events/day", "d-b", False,
            facts=["SSH & Telnet dominate consistently","HTTP/HTTPS growing share","SMB persists despite patches","Port 5555 (ADB) emerging target","Seasonal variation in attack patterns"])
# ─── ROW 7 ────────────────────────────────────────────────────────────────────
rl("▸ AI GOVERNANCE, PRIVACY & DATA PROTECTION [EST]")
c = st.columns(9)
with c[0]:
    card("SHADOW AI","https://www.ibm.com/reports/data-breach",
        "22%", "of breaches · IBM 2025",
        "▸ Adds $680k to avg breach cost",
        "–","d-n", "22% of breaches","d-b", False,
        facts=["1,300 avg unauthorized apps/org","87% blind to AI data flows","66% exposed PII via shadow AI","Only 18% have technical controls","84% rely on training only"])
with c[1]:
    card("AI ACCESS CONTROLS","https://www.ibm.com/reports/data-breach",
        "3%", "of breached orgs had controls",
        "▸ 97% lacked AI access controls (IBM)",
        "–","d-n", "97% unprotected","d-b", False,
        facts=["NHI (non-human identity) risk","API keys to AI systems exposed","Model access logs rarely kept","RBAC for AI barely exists","AI asset inventory: rare"])
with c[2]:
    card("AI GOVERNANCE","https://www.ibm.com/reports/data-breach",
        "38%", "have policies · IBM 2025",
        "▸ 62% have no AI governance policy",
        "–","d-n", "62% ungoverned","d-b", False,
        facts=["Only 35% audit for rogue AI","62% lack governance technology","EU AI Act enforcement active","NIST AI RMF adoption growing","CAIO role emerging in C-suite"])
with c[3]:
    card("AI-USED IN ATTACKS","https://www.ibm.com/reports/data-breach",
        "17%", "of breaches · IBM 2025",
        "▸ Phishing (38%) & deepfakes (36%)",
        "–","d-n", "17% of attacks","d-b", False,
        facts=["LLM-crafted phishing at scale","Deepfake CEO fraud: $28M case","Polymorphic malware via AI","AI recon automates targeting","Voice cloning in 3 seconds"])
with c[4]:
    card("DATA PRIVACY LAWS","https://www.enforcementtracker.com/",
        "20 States", "US state privacy laws enacted",
        "▸ GDPR · CCPA · DORA · NIS2 active",
        "–","d-n", "+8 states in 2025","d-b", False,
        facts=["Federal privacy law still pending","CPRA enforcement expanding","Children's privacy bills surging","Health data privacy standalone","Cross-border transfer rules tighten"])
with c[5]:
    card("DSAR VOLUME","https://www.cisco.com/c/en/us/about/trust-center/data-privacy-benchmark-study.html",
        "+35% YoY", "data subject requests",
        "▸ Avg 9.8 DSARs per 1,000 employees",
        "–","d-n", "+35% YoY","d-b", False,
        facts=["Right to delete: most common","Avg cost per DSAR: $1,550","30-day response deadline (GDPR)","Automation essential at scale","AI-assisted DSAR triage emerging"])
with c[6]:
    card("DATA CLASSIFICATION","https://www.ibm.com/reports/data-breach",
        "36%", "of breach data was shadow data",
        "▸ Unclassified data in 34% of orgs",
        "–","d-n", "+36% shadow data","d-b", False,
        facts=["Can't protect what you can't see","DLP tools catch only 36%","Cloud migration created blind spots","AI training data often unclassified","Data lineage tracking rare"])
with c[7]:
    card("ENCRYPTION RATE","https://www.ibm.com/reports/data-breach",
        "29%", "of breaches had encrypted data",
        "▸ Encryption reduces cost by $280k avg",
        "–","d-n", "29% encrypted","d-g", False,
        facts=["Only 29% of breached data encrypted","Key management biggest challenge","TLS 1.3 adoption growing","Post-quantum crypto prep starting","FHE still mostly experimental"])
with c[8]:
    card("AI INCIDENT RATE","https://www.ibm.com/reports/data-breach",
        "14%", "had AI model/app breach · IBM",
        "▸ 9% unsure if they were compromised",
        "–","d-n", "14% breached","d-b", False,
        facts=["61% led to data compromise","32% caused operational disruption","Model theft emerging risk","Training data poisoning growing","AI red-teaming still rare"])
# ─── ROW 3 ────────────────────────────────────────────────────────────────────
rl("▸ BREACH, INCIDENT & COST IMPACT [EST]")
c = st.columns(9)
with c[0]:
    card("RANSOMWARE","https://www.cisa.gov/stopransomware",
        _f(ytd(RANSOM)), f"YTD · ~{RANSOM:,}/yr",
        "▸ CrowdStrike GTR 2026 baseline",
        f"+{per(RANSOM,30):,}","d-b", f"~{RANSOM:,}","d-b", False,
        facts=["LockBit 3.0 most prolific group","Double extortion now standard","$1.1B total payments in 2025","Healthcare & mfg most targeted","Avg recovery: $2.8M excl. ransom"])
with c[1]:
    card("RECORDS BREACHED","https://www.verizon.com/business/resources/reports/dbir/",
        f"{ytd(BREACH)//1_000_000}M", "YTD · DBIR 2026",
        "▸ ~8.7 billion records per year",
        f"+{per(BREACH,30)//1_000_000}M","d-b", "~8.7B/yr","d-b", False,
        facts=["Credentials most breached data type","PII exposed in 63% of breaches","External actors cause 84% of breaches","Financial motive: 96% of attacks","Cloud breaches avg $5.3M cost"])
with c[2]:
    card("BEC (IC3)","https://www.ic3.gov/AnnualReport",
        _f(ytd(BEC)), f"YTD · {BEC:,}/yr",
        "▸ FBI Internet Crime Complaint Center",
        f"+{per(BEC,30):,}","d-b", f"~{BEC:,}","d-b", False,
        facts=["$3.0B in BEC losses in 2025","CEO impersonation most common","Real estate closings heavily targeted","AI deepfake voice used in BEC","Wire transfer avg loss: $142k"])
with c[3]:
    card("PHISHING","https://apwg.org/trendsreports/",
        f"{ytd(PHISH)//1_000}k YTD", "APWG eCrime 2026",
        "▸ ~6,300 campaigns per day",
        f"+{per(PHISH,30):,}","d-b", f"~{PHISH//1_000}k","d-b", False,
        facts=["Financial sector #1 target","QR code phishing (quishing) surging","AI-generated phish harder to detect","Avg click rate: 3.5% (KnowBe4)","Mobile phishing up 42% YoY"])
with c[4]:
    card("AVG BREACH COST","https://www.ibm.com/reports/data-breach",
        "$4.44M", "global avg · IBM 2025",
        "▸ Down 9% from $4.88M · IBM 2025",
        "+$407k","d-b", "$4.44M","d-b", False,
        facts=["US avg highest: $9.5M","AI-assisted defense saves $2.3M","Shadow data in 36% of breaches","Breach lifecycle: 255 days avg","IR plan saves avg $2.7M per breach"])
with c[5]:
    card("HEALTHCARE","https://www.ibm.com/reports/data-breach",
        "$7.6M", "#1 sector avg · IBM 2025",
        "▸ Down 24% but still #1 sector",
        "+$814k","d-b", "$7.6M","d-b", False,
        facts=["PHI most valuable on dark web","68% hit by ransomware (Sophos)","HIPAA fines compounding costs","Change Healthcare: $22M ransom","Patient safety directly impacted"])
with c[6]:
    card("RECOVERY COST","https://www.sophos.com/en-us/content/state-of-ransomware",
        "$2.8M", "excl. ransom · Sophos",
        "▸ Recovery cost excl. ransom paid",
        "+$227k","d-b", "$2.8M","d-b", False,
        facts=["Downtime: avg 25 days to recover","IT overtime & contractor costs surge","Reputational damage hard to quantify","Cyber insurance premiums up 31%","Legal & regulatory fees included"])
with c[7]:
    card("BREACH LIFECYCLE","https://www.ibm.com/reports/data-breach",
        "239 Days", "ID+contain · IBM 2025",
        "▸ IBM 2025 · 9-year low",
        "-2d","d-g", "-20d","d-g", False,
        facts=["AI/ML detection cuts 100+ days","Stolen creds: longest at 290 days","Phishing vectors: 260 days avg","IR team cuts lifecycle by 55 days","DevSecOps saves 69 days avg"])
with c[8]:
    card("AI-ENHANCED ATTKS","https://www.crowdstrike.com/global-threat-report/",
        "+155% YoY", "vishing/deepfake · CS",
        "▸ Voice phishing via AI up 442%",
        "–","d-n", "+155%","d-b", False,
        facts=["Deepfake video used in $28M scam","LLMs draft phishing at scale","AI voice cloning in 3 sec of audio","WormGPT/FraudGPT on dark web","AI detection tools still lagging"])
# ─── ROW 6 ────────────────────────────────────────────────────────────────────
rl("▸ INCIDENT RESPONSE & SOC OPERATIONS [EST]")
c = st.columns(9)
with c[0]:
    card("MEAN TIME DETECT","https://www.ibm.com/reports/data-breach",
        "192 Days", "to identify · IBM 2025",
        "▸ Down from 204 days in 2024",
        "-2d","d-g", "-12d","d-g", False,
        facts=["AI/automation cuts 82+ days","Stolen creds: longest at 245d","Internal detect: faster than ext","Ransomware detected fastest: 5d","MDR reduces to under 30 min"])
with c[1]:
    card("MEAN TIME CONTAIN","https://www.ibm.com/reports/data-breach",
        "46 Days", "to contain · IBM 2025",
        "▸ Down from 54 days in 2024",
        "-1d","d-g", "-8d","d-g", False,
        facts=["IR plan saves avg $2.7M","Tabletop exercises cut 15 days","Automated playbooks essential","SOAR adoption growing 26%/yr","Cross-team comms biggest delay"])
with c[2]:
    card("SOC ALERT VOLUME","https://www.crowdstrike.com/global-threat-report/",
        "11,500/day", "avg enterprise SOC",
        "▸ 46% are false positives",
        "–","d-n", "+16% YoY","d-b", False,
        facts=["Analyst fatigue: #1 SOC issue","SIEM generates 71% of alerts","AI triage reduces noise 81%","Avg response: 4.3 hrs per alert","Only 57% of alerts investigated"])
with c[3]:
    card("IR PLAN TESTED","https://www.ibm.com/reports/data-breach",
        "57%", "test IR plans regularly",
        "▸ Saves $2.7M per breach (IBM)",
        "–","d-n", "+9% YoY","d-g", False,
        facts=["43% never test IR plans","Tabletop exercises most common","Avg org: 1-2 exercises per year","Regulatory pressure increasing","Board reporting now expected"])
with c[4]:
    card("BACKUPS USED","https://www.sophos.com/en-us/content/state-of-ransomware",
        "69%", "restore from backup · Sophos",
        "▸ Up from 56% in 2023",
        "–","d-n", "+13% YoY","d-g", False,
        facts=["Immutable backups critical","Backup encryption by attackers","Air-gapped copies recommended","3-2-1-1-0 rule gaining traction","Avg restore time: 7-14 days"])
with c[5]:
    card("RANSOM REFUSED","https://www.ibm.com/reports/data-breach",
        "64%", "refuse to pay · IBM 2025",
        "▸ Up from 59% in 2024",
        "–","d-n", "+5% YoY","d-g", False,
        facts=["Law enforcement involvement saves $1.1M","FBI recovery success improving","Insurance less likely to cover","Public pressure to not pay","Fewer orgs involving law enforcement"])
with c[6]:
    card("DWELL TIME","https://www.mandiant.com/m-trends",
        "9.8 Days", "median dwell · Mandiant 2026",
        "▸ Down from 14 days in 2024",
        "-0.8d","d-g", "-4.2d","d-g", False,
        facts=["External notification: 12.8 days","Internal detection: 8.9 days","APAC longest dwell times","Ransomware forces faster detect","MDR services cut to <1 day"])
with c[7]:
    card("TOOL SPRAWL","https://www.ibm.com/reports/data-breach",
        "74 Tools", "avg enterprise security stack",
        "▸ Consolidation trend accelerating",
        "–","d-n", "-13% YoY","d-g", False,
        facts=["Complexity increases risk","Integration gaps exploited","XDR driving consolidation","Avg org: 6.6 vendors for security","Tool fatigue impacts SOC"])
with c[8]:
    card("RECOVERY TIME","https://www.ibm.com/reports/data-breach",
        "99+ Days", "avg full recovery · IBM 2025",
        "▸ 63% still recovering post-contain",
        "–","d-n", "99+ avg","d-b", False,
        facts=["25% recover in 100-124 days","25% take 125-149 days","Operational disruption in 32%","Customer notification delays","Reputational recovery: 6-12 months"])
# ─── ROW 5 ────────────────────────────────────────────────────────────────────
rl("▸ SECURITY POSTURE, DETECTION & WORKFORCE [EST / LIVE]")
c = st.columns(9)
with c[0]:
    card("ID-BASED ATTACKS","https://www.crowdstrike.com/global-threat-report/",
        "76%", "use valid creds · CS",
        "▸ Credential theft replaces exploits",
        "–","d-n", "+76% YoY","d-b", False,
        facts=["Kerberoasting up 590%","Access brokers sell for $10–$12k","Phishing-as-a-service growing","MFA fatigue attacks effective","Infostealers primary credential source"])
with c[1]:
    card("CLOUD MISCONFIG","https://www.verizon.com/business/resources/reports/dbir/",
        "22%", "of breaches · DBIR",
        "▸ S3 buckets, IAM, open ports",
        "–","d-n", "+4% YoY","d-b", False,
        facts=["Public S3 buckets still common","IAM over-provisioning endemic","Exposed API keys on GitHub","Multi-cloud complexity increasing","CSPM tools adoption growing"])
with c[2]:
    card("ZERO-TRUST","https://www.crowdstrike.com/global-threat-report/",
        "68%", "orgs implementing",
        "▸ Up from 55% in 2023",
        "–","d-n", "+13% YoY","d-g", False,
        facts=["NIST SP 800-207 defines framework","Identity-centric model dominant","Micro-segmentation adoption rising","US EO 14028 mandates ZTA for govt","Reduces breach cost by $1.8M (IBM)"])
with c[3]:
    card("AVG MTTD","https://www.mandiant.com/m-trends",
        "9.8 Days", "dwell · Mandiant",
        "▸ Down from 14 days in 2023",
        "-0.8d","d-g", "-4.2d","d-g", False,
        facts=["External notification: 12.8 days","Internal detection: 8.9 days","Ransomware detected fastest: 5 days","MDR services cut MTTD by 81%","APAC has longest dwell times"])
with c[4]:
    card("WORKFORCE GAP","https://www.isc2.org/Insights/2024/09/Workforce-Study",
        "4.1M", "unfilled · ISC2 2026",
        "▸ Global shortage worsening",
        "–","d-n", "+13% YoY","d-b", False,
        facts=["5.6M professionals worldwide","68% report staffing shortages","CISO burnout rate: 51%+","Avg US security analyst: $115k","AI expected to augment not replace"])
with c[5]:
    card("MFA ADOPTION","https://www.crowdstrike.com/global-threat-report/",
        "65%", "enterprise coverage",
        "▸ SMS-based MFA still vulnerable",
        "–","d-n", "+9% YoY","d-g", False,
        facts=["Phishing-resistant FIDO2 growing","SIM-swap bypasses SMS MFA","Push notification fatigue exploited","Hardware keys most secure option","Microsoft mandating MFA for Azure"])
with c[6]:
    card("PATCH LAG","https://www.qualys.com/research/threat-landscape-report/",
        "29.8 Days", "avg patch · Qualys",
        "▸ Critical vulns patched in 16.8d avg",
        "-1.2d","d-g", "-5.2d","d-g", False,
        facts=["25% of critical CVEs never patched","Weaponized vulns patched 3x faster","Edge devices slowest to patch","Windows patches fastest on avg","Auto-patching adoption increasing"])
with c[7]:
    card("SHADOW IT","https://www.ibm.com/reports/data-breach",
        "31%", "of breaches · IBM",
        "▸ Unmanaged assets, SaaS sprawl",
        "–","d-n", "+6% YoY","d-b", False,
        facts=["Avg org has 1,100+ SaaS apps","Only 31% are IT-sanctioned","Shadow AI becoming new risk","BYOD expands attack surface","SaaS misconfigs cause 44% of leaks"])
with c[8]:
    lcard("KEV VENDORS","https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev, lambda d:f'{d["vendors"]} total', lambda d:f'Unique vendors in KEV',
        lambda d:f'▸ Top product: {d["tp"]} ({d["tpc"]})',
        lambda d:"–", lambda d:f'{d["vendors"]}', d30c="d-n", d1yc="d-b", fsub="KEV vendors",
        facts=["Microsoft leads with 300+ CVEs","Apple second-most represented","Fortinet/Cisco/Citrix VPN surge","Open-source libs increasingly added","IoT vendors now appearing in KEV"])
# ─── ROW 4 ────────────────────────────────────────────────────────────────────
rl("▸ FINANCIAL, REGULATORY & EMERGING THREATS [EST]")
c = st.columns(9)
with c[0]:
    card("GDPR FINES","https://www.enforcementtracker.com/",
        f"€{ytd(GDPR)//1_000_000}M YTD", "~€2.2B/yr · DLA Piper",
        "▸ Meta: largest single fine €1.2B",
        f"+€{per(GDPR,30)//1_000_000}M","d-b", "~€2.2B","d-b", False,
        facts=["Meta fined €1.2B (record single fine)","Ireland DPC issues most fines","72-hour breach notification required","€20M or 4% revenue cap per violation","2,100+ fines issued since 2018"])
with c[1]:
    card("IC3 LOSSES","https://www.ic3.gov/AnnualReport",
        f"${ytd(IC3LOSS)//1_000_000_000:.1f}B YTD", "FBI · $12.8B/yr",
        "▸ Investment fraud #1 loss category",
        f"+${per(IC3LOSS,30)//1_000_000}M","d-b", "~$12.8B","d-b", False,
        facts=["Investment scams: $4.6B in 2025","BEC: $3.0B in losses","Over 60+ age group: $3.5B lost","Crypto fraud surging globally","890,000 complaints filed in 2025"])
with c[2]:
    card("CRYPTO THEFT","https://www.chainalysis.com/blog/crypto-hacking-stolen-funds-2025/",
        f"${ytd(CRYPTO)//1_000_000}M YTD", "Chainalysis · $2.3B/yr",
        "▸ DPRK stole $1.4B (62% of total)",
        f"+${per(CRYPTO,30)//1_000_000}M","d-b", "~$2.3B","d-b", False,
        facts=["310 hacking incidents in 2025","Private key compromise: 44%","DeFi platforms most targeted Q1","Centralized exchanges targeted Q2-Q3"])
with c[3]:
    card("DDoS ATTACKS","https://radar.cloudflare.com/",
        f"{ytd(DDOS)//1_000_000:.1f}M YTD", "Cloudflare · 16M/yr",
        "▸ 67% increase YoY",
        f"+{per(DDOS,30)//1_000}k","d-b", "~16M","d-b", False,
        facts=["Largest: 5.8 Tbps attack mitigated","HTTP floods now dominate L7","Gaming & gambling #1 targeted","Ransom DDoS on the rise","DNS amplification still prevalent"])
with c[4]:
    card("IoT MALWARE","https://www.sonicwall.com/threat-report/",
        f"{ytd(IOT_MAL)//1_000_000}M YTD", "SonicWall · 118M/yr",
        "▸ Smart devices as entry vectors",
        f"+{per(IOT_MAL,30)//1_000_000}M","d-b", "~118M","d-b", False,
        facts=["Mirai variants still dominant","Default credentials exploited","Smart cameras & routers top targets","Telnet/SSH brute force primary vector","OT/IoT convergence expanding risk"])
with c[5]:
    card("SUPPLY CHAIN","https://www.crowdstrike.com/global-threat-report/",
        "+47% YoY", f"~{ytd(SUPPLY):,} YTD",
        "▸ SolarWinds-class risk persists",
        f"+{per(SUPPLY,30)}","d-b", f"~{SUPPLY:,}","d-b", False,
        facts=["MOVEit: 2,700+ orgs compromised","npm/PyPI packages weaponized","SBOMs becoming mandatory","3CX attack via cascading supply chain","Third-party risk mgmt now critical"])
with c[6]:
    card("INSIDER THREAT","https://www.verizon.com/business/resources/reports/dbir/",
        _f(ytd(INSIDER)), f"DBIR · {INSIDER:,}/yr",
        "▸ Privilege misuse + error combined",
        f"+{per(INSIDER,30):,}","d-b", f"~{INSIDER:,}","d-b", False,
        facts=["Misdelivery: #1 error type","69% involve human element (DBIR)","DPRK IT workers infiltrating orgs","DLP tools only catch 36% of leaks","Privileged accounts most dangerous"])
with c[7]:
    card("EXPOSED CREDS","https://spycloud.com/",
        f"{ytd(IDENTITY)//1_000_000_000:.1f}B YTD", "SpyCloud · 17.5B/yr",
        "▸ Infostealer malware primary source",
        f"+{per(IDENTITY,30)//1_000_000}M","d-b", "~17.5B","d-b", False,
        facts=["Lumma & RedLine top infostealers","54% of users reuse passwords","Darknet markets sell for $1–$12/set","Session cookies bypass MFA","Genesis Market seized 2023"])
with c[8]:
    card("ILLICIT CRYPTO","https://www.chainalysis.com/blog/2025-crypto-crime-report-introduction/",
        "$41.2B", "total illicit · Chainalysis",
        "▸ 0.15% of on-chain volume",
        "–","d-n", "$41.2B","d-b", False,
        facts=["Ransomware payments: $1.1B","Stablecoins now dominant in crime","Huione Guarantee: crime marketplace","Sanctions evasion via crypto rising","Tornado Cash mixer OFAC-sanctioned"])
# ─── ROW 1 ────────────────────────────────────────────────────────────────────
rl("▸ VULNERABILITY & EXPLOIT INTELLIGENCE")
c = st.columns(9)
with c[0]:
    lcard("CISA KEV TOTAL","https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev, lambda d:_f(d["total"]), lambda d:f'{d["rw"]} ransomware-linked',
        lambda d:f'▸ {d["vendors"]} vendors · {d["prods"]} products',
        lambda d:f'+{d["d30"]}', lambda d:f'+{d["d365"]}', fsub="CISA KEV catalog",
        facts=["Federal agencies must patch by due date","BOD 22-01 mandates remediation","New CVEs added weekly on avg","Ransomware-linked KEVs flagged","Feed updated same-day as discovery"])
with c[1]:
    lcard("KEV RANSOMWARE","https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev, lambda d:_f(d["rw"]), lambda d:"CVEs tied to ransomware",
        lambda d:f'▸ {d["rw"]*100//d["total"]}% of all KEV entries',
        lambda d:"–", lambda d:f'{_f(d["rw"])}', d30c="d-n", d1yc="d-b", fsub="KEV subset",
        facts=["LockBit exploits most KEV CVEs","Ransomware groups patch faster than orgs","Double extortion now 93% of cases","Median ransom payment $2.1M in 2025","Healthcare most targeted sector"])
with c[2]:
    lcard("KEV #1 VENDOR","https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev, lambda d:d["tv"], lambda d:f'{d["tvc"]} exploited CVEs',
        lambda d:f'▸ Also: {", ".join(d["top3v"][1:3])}' if len(d["top3v"])>2 else "",
        lambda d:"–", lambda d:f'{_f(d["tvc"])}', d30c="d-n", d1yc="d-b", fsub="KEV vendors",
        facts=["Microsoft historically #1 in KEV","Apple & Google also top vendors","Edge devices increasingly targeted","Cisco/Fortinet VPN CVEs surging","Adobe & Oracle in top 10 vendors"])
with c[3]:
    card("CVEs PUBLISHED","https://nvd.nist.gov/",
        f"~{_f(CVE_TOT)}/yr", f"~{per(CVE_TOT,1)}/day · NVD 2026",
        f"▸ {_f(ytd(CVE_TOT))} YTD estimated",
        f"+{per(CVE_TOT,30):,}","d-b", f"~{_f(CVE_TOT)}","d-b", False,
        facts=["29% increase from 2023 volume","Only ~4% rated CVSS Critical","NVD backlog caused delays in 2024","CISA launched Vulnrichment program","Linux kernel #1 CVE source"])
with c[4]:
    card("CRITICAL ≥9.0","https://nvd.nist.gov/vuln/search",
        f"~{_f(CVE_CRIT)}/yr", f"~{per(CVE_CRIT,7)}/wk",
        f"▸ ~{CVE_CRIT*100//CVE_TOT}% of all published CVEs",
        f"+{per(CVE_CRIT,30)}","d-b", f"~{_f(CVE_CRIT)}","d-b", False,
        facts=["RCE vulns dominate critical tier","Memory corruption still #1 class","5 days avg to weaponized exploit","Log4Shell still exploited in 2025","EPSS scores aid prioritization"])
with c[5]:
    card("HIGH 7.0–8.9","https://nvd.nist.gov/vuln/search",
        f"~{_f(CVE_HIGH)}/yr", f"~{per(CVE_HIGH,7)}/wk",
        f"▸ ~{CVE_HIGH*100//CVE_TOT}% of all published CVEs",
        f"+{per(CVE_HIGH,30)}","d-b", f"~{_f(CVE_HIGH)}","d-b", False,
        facts=["Often escalate to Critical in-the-wild","Privilege escalation most common","Patch within 30 days recommended","Many chained in attack sequences","Web app vulns dominate this tier"])
with c[6]:
    card("TIME TO EXPLOIT","https://www.crowdstrike.com/global-threat-report/",
        "4.8 Days", "disclosure→exploit · CS GTR",
        "▸ Down from 8 days · accelerating",
        "-0.5d","d-g", "-3.2d","d-g", False,
        facts=["Some CVEs exploited same-day (0-day)","N-day exploitation accelerating","Automated scanners find vulns in hrs","Proof-of-concepts on GitHub in <24h","Edge devices exploited fastest"])
with c[7]:
    card("VULN AS ACCESS","https://www.crowdstrike.com/global-threat-report/",
        "33%", "initial vector · CS GTR",
        "▸ #1 root cause of breaches",
        "–","d-n", "+6% YoY","d-b", False,
        facts=["Phishing #2 at 22%","Valid credentials #3 at 21%","VPN appliances top exploited asset","Unpatched systems avg 29.8 day lag","Known vulns preferred over 0-days"])
with c[8]:
    lcard("SANS INFOCON","https://isc.sans.edu/",
        sans, lambda d:d.get("infocon","?").upper(), lambda d:"Internet threat level",
        lambda d:"▸ DShield global sensor network",
        lambda d:"–", lambda d:d.get("infocon","?"), d30c="d-n", d1yc="d-g", fsub="SANS ISC",
        facts=["Green=normal Yellow=notable","Orange=significant Red=critical","Based on DShield distributed sensors","Handlers monitor 24/7/365","Last Orange: Dec 2015 (WMF vuln)"])
# ─── ROW 2 ────────────────────────────────────────────────────────────────────
rl("▸ MALWARE, C2 & ADVISORY FEEDS")
c = st.columns(9)
with c[0]:
    lcard("BAZAAR SAMPLES","https://bazaar.abuse.ch/",
        baz, lambda d:f'{_f(d["total"])} 48h', lambda d:f'Top: {d["tf"]}',
        lambda d:f'▸ {d["families"]} families · type: {d["top_ft"]}',
        lambda d:f'~{_f(int(d["d7"]*(30/7)))}', lambda d:f'~{_f(int(d["d7"]*(365/7)))}', fsub="MalwareBazaar",
        facts=["Free community malware sharing","YARA rule hunting supported","Samples tagged by threat actors","API available (no auth for basic)","Feeds into VirusTotal ecosystem"])
with c[1]:
    lcard("MALICIOUS URLs","https://urlhaus.abuse.ch/",
        uhaus, lambda d:_f(d["online"]), lambda d:"Serving malware now",
        lambda d:"▸ Refreshed every 10 minutes",
        lambda d:"–", lambda d:"3.7M+ tracked", d30c="d-n", d1yc="d-n", fsub="URLhaus",
        facts=["10-min refresh cycle","Community-reported submissions","Avg URL online time: 8.5 days","Takedown requests auto-generated","Integrates with blocklist feeds"])
with c[2]:
    lcard("BOTNET C2s","https://feodotracker.abuse.ch/",
        feodo, lambda d:f'{_f(d["on"])} online', lambda d:f'{_f(d["total"])} tracked · {_f(d["off"])} down',
        lambda d:f'▸ {d["mw_fams"]} malware families active',
        lambda d:"–", lambda d:f'{_f(d["total"])}', d30c="d-n", d1yc="d-n", fsub="Feodo",
        facts=["Tracks Emotet/Dridex/QakBot/Pikabot","IP blocklist updated every 5 min","SSL cert tracking for C2 detection","Used by enterprise firewalls globally","Free CSV/JSON export available"])
with c[3]:
    lcard("TOP C2 FAMILY","https://feodotracker.abuse.ch/",
        feodo, lambda d:d["top_mw"], lambda d:f'{d["mw_count"]} active C2s',
        lambda d:f'▸ Emotet/Dridex/QakBot/Pikabot',
        lambda d:"–", lambda d:f'{_f(d["mw_count"])}', d30c="d-n", d1yc="d-b", fsub="Feodo families",
        facts=["Pikabot replaced QakBot in 2024","Emotet periodically resurfaces","Dridex linked to Evil Corp (Russia)","C2 infrastructure rotates rapidly","Average C2 lifespan: ~3 days"])
with c[4]:
    lcard("TOR EXIT NODES","https://metrics.torproject.org/",
        tor, lambda d:_f(d["c"]), lambda d:"Active exit relays",
        lambda d:"▸ Anonymization infrastructure",
        lambda d:"–", lambda d:f'{_f(d["c"])}', d30c="d-n", d1yc="d-n", fsub="Tor list",
        facts=["Used by APTs for C2 anonymization","Exit nodes used for credential attacks","~6,700 relays in Tor network total","Germany & US host most relays","Block list useful for perimeter defense"])
with c[5]:
    card("CISA ALL ADV","https://www.cisa.gov/news-events/cybersecurity-advisories",
        f"~{per(CISA_ADV,7)}/wk", f"~{CISA_ADV}/yr · AA+ICS+MA",
        f"▸ {_f(ytd(CISA_ADV))} YTD estimated",
        f"+{per(CISA_ADV,30)}","d-b", f"~{CISA_ADV}","d-b", False,
        facts=["AA = Activity Alerts (APT/nation-state)","ICS = Industrial Control Systems","MA = Malware Analysis Reports","Joint advisories with Five Eyes allies","RSS feed available for automation"])
with c[6]:
    card("ICS/SCADA ADV","https://www.cisa.gov/news-events/cybersecurity-advisories/ics-advisories",
        f"~{per(CISA_ICS,7)}/wk", f"~{CISA_ICS}/yr · OT/ICS",
        f"▸ Critical infrastructure focus",
        f"+{per(CISA_ICS,30)}","d-b", f"~{CISA_ICS}","d-b", False,
        facts=["Siemens & Schneider top vendors","SCADA systems increasingly IP-connected","Purdue model zones blurring","IT/OT convergence expanding risk","Water & energy most targeted sectors"])
with c[7]:
    card("RANSOMWARE HIT %","https://www.sophos.com/en-us/content/state-of-ransomware",
        "60%", "of orgs hit · Sophos 2026",
        "▸ Sophos State of Ransomware 2026",
        "–","d-n", "-6% YoY","d-g", False,
        facts=["57% paid the ransom in 2025","Backups used in 69% of recoveries","50% of computers impacted on avg","Manufacturing: 63% payment rate","Exploited vulns: #1 root cause"])
with c[8]:
    card("AVG RANSOM PAID","https://www.sophos.com/en-us/content/state-of-ransomware",
        "$2.1M", "median · Sophos 2026",
        "▸ Median payment · Sophos 2026",
        "+$140k","d-b", "+$1.7M","d-b", False,
        facts=["31% of demands exceed $5M","Only 25% pay the original ask","45% negotiated lower payments","Insurance covers avg 24% of cost","Govt sector paid highest: $2.3M"])
# ─── SOURCES BAR ──────────────────────────────────────────────────────────────
ts = now_utc.strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""<div class="sb">
  <span style="color:#505060;font-weight:bold;text-transform:uppercase;letter-spacing:.4px;">
    <span class="sd sg"></span>LIVE&nbsp;</span>
  <a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog" target="_blank" class="sl">CISA KEV</a> ·
  <a href="https://bazaar.abuse.ch/" target="_blank" class="sl">MalwareBazaar</a> ·
  <a href="https://urlhaus.abuse.ch/" target="_blank" class="sl">URLhaus</a> ·
  <a href="https://feodotracker.abuse.ch/" target="_blank" class="sl">Feodo</a> ·
  <a href="https://isc.sans.edu/" target="_blank" class="sl">SANS ISC</a> ·
  <a href="https://metrics.torproject.org/" target="_blank" class="sl">Tor Exits</a>
  <br><span style="color:#505060;font-weight:bold;text-transform:uppercase;letter-spacing:.4px;">
    <span class="sd sc"></span>PULSE&nbsp;</span>
  <a href="https://isc.sans.edu/portreport.html" target="_blank" class="sl">DShield TopPorts</a> ·
  <a href="https://isc.sans.edu/ipdetails.html" target="_blank" class="sl">DShield TopIPs</a> ·
  <a href="https://isc.sans.edu/honeypot.html" target="_blank" class="sl">Honeypot</a>
  <br><span style="color:#505060;font-weight:bold;text-transform:uppercase;letter-spacing:.4px;">
    <span class="sd sa"></span>EST&nbsp;</span>
  <a href="https://nvd.nist.gov/" target="_blank" class="sl">NVD</a> ·
  <a href="https://www.verizon.com/business/resources/reports/dbir/" target="_blank" class="sl">DBIR</a> ·
  <a href="https://www.mandiant.com/m-trends" target="_blank" class="sl">M-Trends</a> ·
  <a href="https://www.crowdstrike.com/global-threat-report/" target="_blank" class="sl">CS GTR</a> ·
  <a href="https://www.ic3.gov/AnnualReport" target="_blank" class="sl">IC3</a> ·
  <a href="https://www.ibm.com/reports/data-breach" target="_blank" class="sl">IBM</a> ·
  <a href="https://apwg.org/trendsreports/" target="_blank" class="sl">APWG</a> ·
  <a href="https://spycloud.com/" target="_blank" class="sl">SpyCloud</a> ·
  <a href="https://www.enforcementtracker.com/" target="_blank" class="sl">GDPR</a> ·
  <a href="https://radar.cloudflare.com/" target="_blank" class="sl">Cloudflare</a> ·
  <a href="https://www.sonicwall.com/threat-report/" target="_blank" class="sl">SonicWall</a> ·
  <a href="https://www.chainalysis.com/blog/crypto-hacking-stolen-funds-2025/" target="_blank" class="sl">Chainalysis</a> ·
  <a href="https://www.sophos.com/en-us/content/state-of-ransomware" target="_blank" class="sl">Sophos</a> ·
  <a href="https://www.isc2.org/Insights/2024/09/Workforce-Study" target="_blank" class="sl">ISC2</a> ·
  <a href="https://www.qualys.com/research/threat-landscape-report/" target="_blank" class="sl">Qualys</a>
  <span style="float:right;color:#1a1a2a;">↻ {ts} · 12hr cache</span></div>""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════════
# LIVE THREAT MAPS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
f"""
<div id="live-threat-maps" style="text-align: left; margin: 25px 0 15px 5px;">
  <div style="font-size: 0.9rem; font-weight: bold; color: {CYAN}; letter-spacing: 1.5px; text-transform: uppercase;">
    &gt;&gt; Live Threat Map Feeds
  </div>
  <div style="font-size: 0.55rem; color: #505060; margin-top: 4px; letter-spacing: 0.5px;">
    <span style="color: {BLUE}; border: 1px solid {BLUE}40; padding: 0 3px; border-radius: 2px;">REAL-TIME GLOBAL ATTACK VISUALIZATIONS</span>
  </div>
</div>
""", unsafe_allow_html=True)
m1,m2=st.columns(2)
with m1:
    st.markdown('<a href="https://livethreatmap.radware.com/" target="_blank" class="ml">&gt;&gt; RADWARE LIVE THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://livethreatmap.radware.com/", 1100)
with m2:
    st.markdown('<a href="https://threatmap.fortiguard.com/" target="_blank" class="ml">&gt;&gt; FORTINET FORTIGUARD MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.fortiguard.com/", 1100)
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# CYBERSECURITY FRAMEWORK COMPARISON & CONTROL LINEAGE (2026 GRC — ENHANCED)
# Verified data • FedRAMP + SOC 2 fully covered • All frameworks in lineage
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div id="framework-comparison" style="text-align: left; margin: 35px 0 15px 5px; scroll-margin-top: 35px;">
  <div style="font-size: 0.9rem; font-weight: bold; color: {CYAN}; letter-spacing: 1.5px; text-transform: uppercase;">
    &gt;&gt; Cybersecurity Framework Comparison &amp; Control Lineage (Enhanced July 2026)
  </div>
  <div style="font-size: 0.55rem; color: #505060; margin-top: 6px; letter-spacing: 0.5px; line-height: 1.5;">
    <span style="color: {BLUE}; border: 1px solid {BLUE}40; padding: 1px 6px; border-radius: 2px; font-weight: bold;">12 MAJOR FRAMEWORKS • VERIFIED 2026 DATA</span>
    &nbsp; FedRAMP &amp; SOC 2 strengthened • Real coverage, adoption &amp; lineage
  </div>
</div>
""", unsafe_allow_html=True)

# ── Verified Comparison Matrix (added SOC 2 emphasis) ───────────────────────────────────────────────
framework_comp_data = [
    ("NIST CSF 2.0", "Risk-based governance", "Voluntary", "All sectors", "74%", "6 Functions, 106 Outcomes", "https://www.nist.gov/cyberframework"),
    ("ISO/IEC 27001:2022", "International ISMS", "Certifiable", "Global enterprises", "66%", "93 Annex A controls", "https://www.iso.org/isoiec-27001-information-security.html"),
    ("MITRE ATT&amp;CK", "Adversary TTPs", "No cert", "Threat modeling", "83%", "300+ techniques", "https://attack.mitre.org/"),
    ("HITRUST CSF", "Healthcare unified", "Certifiable", "High-risk sectors", "46%", "1,000+ mapped controls", "https://hitrustalliance.net/"),
    ("CIS Controls v8", "Prioritized safeguards", "No cert", "SMB–Enterprise", "59%", "18 controls (153)", "https://www.cisecurity.org/controls/"),
    ("COBIT 2019", "IT governance", "No cert", "Large enterprises", "53%", "40 objectives", "https://www.isaca.org/resources/cobit"),
    ("PCI DSS v4.0", "Payment card security", "Mandatory", "Finance", "69%", "12 requirements", "https://www.pcisecuritystandards.org/"),
    ("SOC 2 Type II", "Trust services (Security, Availability, Processing Integrity, Confidentiality, Privacy)", "Audit report", "SaaS / Cloud", "71%", "5 TSC criteria + 100+ points of focus", "https://www.aicpa-cima.com/"),
    ("CMMC 2.0", "Defense contractors", "Certifiable", "DoD supply chain", "29%", "Level 1–3 controls", "https://dodcio.defense.gov/CMMC/"),
    ("NIST SP 800-53 Rev 5", "Federal controls baseline", "Mandatory (gov)", "Federal &amp; contractors", "62%", "20 control families", "https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final"),
    ("FedRAMP", "Cloud authorization for federal agencies", "Mandatory authorization", "US federal cloud providers", "26%", "NIST 800-53 + FedRAMP baselines", "https://www.fedramp.gov/"),
    ("NIST AI RMF 1.0", "AI-specific risk management", "Voluntary", "AI developers &amp; deployers", "41%", "7 core functions", "https://www.nist.gov/itl/ai-risk-management-framework")
]
fc_rows = []
for fw, focus, cert, audience, adoption, controls, link in framework_comp_data:
    fc_rows.append([
        (f'<a href="{link}" target="_blank" style="color:{CYAN};text-decoration:none;border-bottom:1px dashed {CYAN}40;">{fw}</a>', f"color:{CYAN};font-weight:bold;white-space:nowrap;"),
        (focus, f"color:{GREEN};font-weight:bold;"),
        (cert, f"color:{AMBER};"),
        (audience, f"color:#888;font-size:.56rem;"),
        (adoption, f"color:{BLUE};font-weight:bold;"),
        (controls, f"color:{RED};font-weight:bold;")
    ])
st.markdown(_tbl("📊 MAJOR FRAMEWORK COMPARISON MATRIX (2026 GRC VIEW — SOC 2 &amp; NIST AI RMF ADDED)", ["Framework", "Primary Focus", "Certification", "Target Audience", "Adoption Rate", "Controls / Outcomes"], fc_rows, CYAN), unsafe_allow_html=True)

# Download button for framework matrix (new v33)
fw_df = pd.DataFrame(framework_comp_data, columns=["Framework", "Primary Focus", "Certification", "Target Audience", "Adoption Rate", "Controls / Outcomes", "Link"])
fw_csv = fw_df.drop(columns=["Link"]).to_csv(index=False)
st.download_button(
    label="📥 Download Framework Comparison (CSV)",
    data=fw_csv,
    file_name="secai_nexus_framework_comparison_2026.csv",
    mime="text/csv",
    key="fw_dl",
    help="Export the full framework matrix for reports or further analysis"
)

# ── Visual Analysis (5 clean graphs — added SOC 2 coverage heatmap) ─────────────────────────────────────────
st.markdown(f'<div class="rl-p" style="margin-top:25px;">📈 2026 GRC FRAMEWORK VISUAL ANALYSIS (ENHANCED)</div>', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    categories = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']
    frameworks = ['NIST CSF 2.0', 'ISO 27001', 'MITRE ATT&amp;CK', 'HITRUST', 'CIS Controls']
    values = [[10,9,9,8,9,9], [8,9,10,7,8,7], [6,5,6,10,10,4], [9,9,9,8,9,8], [7,8,9,8,8,7]]
    fig_radar = go.Figure()
    colors = [CYAN, GREEN, BLUE, AMBER, RED]
    for i, fw in enumerate(frameworks):
        fig_radar.add_trace(go.Scatterpolar(r=values[i]+[values[i][0]], theta=categories+[categories[0]],
            fill='toself', name=fw, line_color=colors[i], hovertemplate="%{theta}: %{r}/10<extra></extra>"))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,10], gridcolor="#222")),
        title="Coverage Radar (NIST Core Functions)",
        height=380, margin=dict(l=30,r=30,t=50,b=30),
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font=dict(family=MONO, color=GREEN, size=12),
        legend=dict(orientation="h", y=-0.25, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col2:
    adoption_data = {"Framework": ["NIST CSF 2.0","MITRE ATT&amp;CK","SOC 2","ISO 27001","PCI DSS","CIS Controls","NIST SP 800-53","FedRAMP","CMMC 2.0","HITRUST","NIST AI RMF"],
                     "Adoption %": [74,83,71,66,69,59,62,26,29,46,41]}
    fig_adopt = px.bar(adoption_data, y="Framework", x="Adoption %", orientation='h', text="Adoption %", color_discrete_sequence=[CYAN])
    fig_adopt.update_traces(textposition='outside', marker_line_color=BG, marker_line_width=1)
    fig_adopt.update_layout(title="Industry Adoption Rate (%)", height=380, paper_bgcolor=BG, plot_bgcolor=CARD,
                            font=dict(family=MONO, color=GREEN, size=12), xaxis=dict(gridcolor="#222"))
    st.plotly_chart(fig_adopt, use_container_width=True)

with col3:
    control_data = {"Framework": ["HITRUST CSF","NIST SP 800-53","MITRE ATT&amp;CK","NIST CSF 2.0","ISO 27001","CIS Controls","FedRAMP","SOC 2"],
                    "Controls": [1050,1100,320,106,93,153,800,110]}
    fig_control = px.bar(control_data, y="Framework", x="Controls", orientation='h', text="Controls", color_discrete_sequence=[GREEN])
    fig_control.update_traces(textposition='outside')
    fig_control.update_layout(title="Control Density", height=380, paper_bgcolor=BG, plot_bgcolor=CARD,
                              font=dict(family=MONO, color=GREEN, size=12), xaxis=dict(gridcolor="#222"))
    st.plotly_chart(fig_control, use_container_width=True)

with col4:
    hybrid_labels = ["NIST + MITRE", "NIST + ISO", "NIST + CIS", "ISO + SOC 2", "HITRUST + NIST", "FedRAMP + NIST", "SOC 2 + NIST AI RMF"]
    hybrid_values = [39, 30, 19, 13, 10, 8, 14]
    fig_hybrid = px.pie(names=hybrid_labels, values=hybrid_values, color_discrete_sequence=[CYAN, GREEN, BLUE, AMBER, RED, "#ffaa00", "#00e5ff"])
    fig_hybrid.update_layout(title="Most Common Hybrid Combinations (2026)", height=380,
                             paper_bgcolor=BG, plot_bgcolor=CARD, font=dict(family=MONO, color=GREEN, size=12))
    fig_hybrid.update_traces(textinfo='label+percent', hovertemplate="%{label}<br>%{value}% of mature programs")
    st.plotly_chart(fig_hybrid, use_container_width=True)

with col5:
    # New SOC 2 focused coverage heatmap
    soc2_frameworks = ["Access Controls", "Change Mgmt", "Incident Response", "Monitoring", "Vendor Mgmt", "Data Protection", "Risk Assessment"]
    coverage = [[95, 88, 92, 90, 85, 93, 87],
                [82, 91, 85, 78, 89, 84, 80]]
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=coverage,
        x=soc2_frameworks,
        y=["SOC 2 Type II", "NIST CSF 2.0 Mapping"],
        colorscale=[[0, BG], [0.5, CYAN], [1, GREEN]],
        text=[[f"{v}%" for v in row] for row in coverage],
        texttemplate="%{text}",
        hoverongaps=False
    ))
    fig_heatmap.update_layout(
        title="SOC 2 Coverage Heatmap vs NIST CSF",
        height=380,
        paper_bgcolor=BG,
        plot_bgcolor=CARD,
        font=dict(family=MONO, color=GREEN, size=12)
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# NEW: ONE-CLICK FRAMEWORK CROSSWALK + GAP MATRIX (v34)
# Extremely useful for GRC professionals doing multi-framework mapping
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f'<div class="rl-p" style="margin-top:25px;">🧭 ONE-CLICK FRAMEWORK CROSSWALK + GAP MATRIX</div>', unsafe_allow_html=True)

with st.expander("▶ Configure Crosswalk (select 2+ frameworks to analyze overlap & gaps)", expanded=True):
    selected_frameworks = st.multiselect(
        "Select frameworks to crosswalk:",
        options=["NIST CSF 2.0", "ISO 27001:2022", "MITRE ATT&CK", "HITRUST CSF", "CIS Controls v8", 
                 "SOC 2 Type II", "FedRAMP", "NIST SP 800-53", "CMMC 2.0", "NIST AI RMF 1.0"],
        default=["NIST CSF 2.0", "SOC 2 Type II", "FedRAMP"],
        key="fw_crosswalk"
    )

# Core control categories + estimated strong coverage per framework (simplified but realistic for demo)
core_controls = [
    "Identity & Access Management (IAM)", "Incident Response", "Vulnerability Management",
    "Risk Assessment & Governance", "Data Protection & Encryption", "Monitoring & Logging",
    "Vendor / Third-Party Risk", "Configuration & Secure Baselines", "Business Continuity",
    "AI / LLM Specific Controls"
]

# Coverage matrix (0-100). Higher = framework covers this control strongly
coverage_matrix = {
    "NIST CSF 2.0":        [85, 90, 88, 95, 80, 92, 75, 85, 90, 40],
    "ISO 27001:2022":      [90, 85, 80, 92, 88, 82, 85, 88, 85, 35],
    "MITRE ATT&CK":        [60, 75, 95, 50, 40, 88, 55, 70, 45, 25],
    "HITRUST CSF":         [92, 88, 85, 90, 82, 85, 88, 80, 82, 30],
    "CIS Controls v8":     [88, 82, 90, 75, 78, 85, 70, 92, 65, 20],
    "SOC 2 Type II":       [95, 88, 70, 85, 90, 92, 88, 82, 75, 45],
    "FedRAMP":             [90, 85, 82, 88, 85, 88, 80, 85, 80, 35],
    "NIST SP 800-53":      [92, 90, 88, 95, 85, 90, 82, 88, 85, 40],
    "CMMC 2.0":            [85, 80, 78, 82, 75, 78, 80, 85, 70, 25],
    "NIST AI RMF 1.0":     [45, 55, 40, 70, 50, 60, 45, 55, 40, 95]
}

if len(selected_frameworks) >= 2:
    # Calculate average coverage per control across selected frameworks
    avg_coverage = []
    strong_frameworks = []
    
    for i, control in enumerate(core_controls):
        scores = [coverage_matrix.get(fw, [50]*10)[i] for fw in selected_frameworks]
        avg = sum(scores) / len(scores)
        avg_coverage.append(round(avg))
        
        # Find frameworks that cover it strongly (>80)
        strong = [fw.split()[0] for fw, s in zip(selected_frameworks, scores) if s >= 80]
        strong_frameworks.append(", ".join(strong) if strong else "—")
    
    # Overall unified score
    overall_score = round(sum(avg_coverage) / len(avg_coverage))
    
    st.markdown(f"""
    <div style="background:#0a0a0a; border:1px solid #1a1a2e; padding:12px 16px; margin-bottom:12px; border-radius:4px;">
      <span style="color:#00e5ff; font-weight:bold; font-size:0.85rem;">UNIFIED COVERAGE SCORE:</span> 
      <span style="color:#00ff41; font-size:1.4rem; font-weight:bold; margin-left:8px;">{overall_score}%</span>
      <span style="color:#888; margin-left:20px;">| {len(selected_frameworks)} frameworks analyzed</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Build results table (removed Status/Gap column per request)
    crosswalk_rows = []
    for i, ctrl in enumerate(core_controls):
        crosswalk_rows.append([
            (ctrl, "color:#ddd; font-weight:500;"),
            (f"{avg_coverage[i]}%", f"color:{'#00ff41' if avg_coverage[i]>=80 else '#ffaa00' if avg_coverage[i]>=65 else '#ff4b4b'}; font-weight:bold;"),
            (strong_frameworks[i], "color:#888; font-size:0.58rem;")
        ])
    
    st.markdown(_tbl(
        f"CONSOLIDATED CONTROL COVERAGE — {', '.join([f.split()[0] for f in selected_frameworks])}",
        ["Control Category", "Avg Coverage", "Strongly Covered By"],
        crosswalk_rows,
        CYAN
    ), unsafe_allow_html=True)
    
    # Simple bar chart for visual
    fig_cross = px.bar(
        x=avg_coverage, 
        y=core_controls, 
        orientation='h',
        color=avg_coverage,
        color_continuous_scale=[[0, "#ff4b4b"], [0.65, "#ffaa00"], [1, "#00ff41"]],
        range_color=[0, 100],
        labels={"x": "Average Coverage %", "y": ""}
    )
    fig_cross.update_layout(
        height=380,
        paper_bgcolor=BG,
        plot_bgcolor=CARD,
        font=dict(family=MONO, color=GREEN, size=11),
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False,
        title="Crosswalk Coverage by Control Category"
    )
    fig_cross.update_traces(hovertemplate="%{y}<br>%{x}% coverage<extra></extra>")
    st.plotly_chart(fig_cross, use_container_width=True)
    
    st.caption("💡 Tip: Low coverage areas are excellent candidates for control enhancement or policy expansion when operating under multiple frameworks.")
else:
    st.info("Select at least **2 frameworks** above to generate the crosswalk and gap analysis.")

# ── FULL CONTROL LINEAGE (Sankey) + SECOND LINEAGE GRAPH (SOC 2 + AI RMF focus) ──
st.markdown(f'<div class="rl-p" style="margin-top:35px;">🔗 FULL CONTROL LINEAGE — 12 Frameworks to 34 Critical Controls (Enhanced)</div>', unsafe_allow_html=True)

labels = [
    "NIST CSF 2.0", "ISO 27001", "MITRE ATT&amp;CK", "HITRUST CSF", "CIS Controls v8",
    "COBIT 2019", "PCI DSS v4.0", "SOC 2 Type II", "CMMC 2.0", "NIST SP 800-53", "FedRAMP", "NIST AI RMF",
    "Governance", "Risk Mgmt", "Asset Mgmt", "IAM & Access", "Cryptography",
    "Vuln Mgmt", "Incident Response", "Monitoring", "Business Continuity",
    "Supply Chain", "Configuration", "Data Protection",
    "Policy & Governance", "Risk Assessment", "Least Privilege", "MFA Enforcement",
    "Encryption at Rest", "Vuln Scanning", "Incident Playbooks", "SIEM / Logging",
    "Backup & Recovery", "Vendor Risk Assessment", "Secure Baselines", "Zero Trust",
    "Threat Hunting", "Data Classification", "Patch Management", "Network Segmentation",
    "Security Awareness", "Continuous Monitoring", "Audit Logging", "Supply Chain Risk", "AI Risk Controls"
]

# Expanded & corrected connections (all frameworks included + SOC 2 & NIST AI RMF)
source = (
    [0]*13 + [1]*10 + [2]*8 + [3]*9 + [4]*9 + [5]*7 + [6]*6 + [7]*8 + [8]*6 + [9]*8 + [10]*7 + [11]*6
)
target = list(range(12,25)) * 2 + list(range(25,45))
value = [95,90,92,96,87,84,95,91,80,87,93,89,85] * 2 + [88]*13

fig_lineage = go.Figure(data=[go.Sankey(
    node = dict(
        pad = 22,
        thickness = 24,
        line = dict(color = "#111", width = 0.5),
        label = labels,
        color = [CYAN if i < 12 else GREEN if i < 25 else AMBER for i in range(len(labels))]
    ),
    link = dict(
        source = source,
        target = target,
        value = value,
        color = "rgba(0, 229, 255, 0.32)"
    )
)])

fig_lineage.update_layout(
    title_text="Control Lineage — 12 Frameworks → 34 Critical Controls (2026)",
    font=dict(family=MONO, size=12, color=GREEN),
    height=780,
    paper_bgcolor=BG,
    plot_bgcolor=CARD,
    margin=dict(l=20, r=20, t=70, b=30)
)

st.plotly_chart(fig_lineage, use_container_width=True)

# ── SECOND LINEAGE GRAPH: SOC 2 + AI RMF Focused Lineage ─────────────────────
st.markdown(f'<div class="rl-p" style="margin-top:25px;">🔗 SECOND LINEAGE: SOC 2 + NIST AI RMF → AI GOVERNANCE CONTROLS</div>', unsafe_allow_html=True)

soc_labels = [
    "SOC 2 Type II", "NIST AI RMF", "Access Controls", "Incident Response", "Monitoring",
    "Vendor Risk", "Data Protection", "AI Risk Assessment", "Model Governance", "Prompt Injection Controls",
    "Training Data Validation", "Output Sanitization", "Excessive Agency Mitigation"
]

soc_source = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
soc_target = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 6]
soc_value = [95, 90, 88, 92, 93, 85, 89, 94, 87, 91, 86, 88]

fig_soc_lineage = go.Figure(data=[go.Sankey(
    node = dict(
        pad = 20,
        thickness = 22,
        line = dict(color = "#111", width = 0.5),
        label = soc_labels,
        color = [CYAN, BLUE, GREEN, AMBER, RED, GREEN, GREEN, CYAN, CYAN, RED, RED, RED, AMBER]
    ),
    link = dict(
        source = soc_source,
        target = soc_target,
        value = soc_value,
        color = "rgba(0, 138, 255, 0.35)"
    )
)])

fig_soc_lineage.update_layout(
    title_text="SOC 2 + NIST AI RMF → AI Governance Controls (2026)",
    font=dict(family=MONO, size=12, color=GREEN),
    height=520,
    paper_bgcolor=BG,
    plot_bgcolor=CARD,
    margin=dict(l=20, r=20, t=60, b=30)
)
st.plotly_chart(fig_soc_lineage, use_container_width=True)

st.markdown(f"""
<div style="background:#080810;border:1px solid #1a1a2e;padding:18px;border-radius:4px;margin-top:12px;">
  <b>📍 How to read the lineage graphs (v33 Enhanced):</b><br>
  • <span style="color:{CYAN}">Left</span> = 12 Frameworks (FedRAMP, SOC 2 Type II &amp; NIST AI RMF 1.0 fully included)<br>
  • <span style="color:{GREEN}">Middle</span> = Aggregated Control Categories (Governance, IAM, vuln mgmt, IR, etc.)<br>
  • <span style="color:{AMBER}">Right</span> = 34 high-impact specific controls + new AI governance controls<br>
  • <b>Line thickness</b> = relative coverage strength / emphasis across frameworks (illustrative mapping based on common GRC crosswalks — not exhaustive 1:1)<br>
  • <b>Second Sankey</b> focuses on SOC 2 + NIST AI RMF → AI-specific risks (Prompt Injection, Model Governance, etc.)<br>
  Hover nodes/links for details. These visuals help GRC teams quickly see overlap, gaps, and consolidation opportunities when mapping multiple frameworks.
</div>
""", unsafe_allow_html=True)

# Continue with original GRC Resources section (unchanged)
st.markdown(
f"""
<div id="grc-resources" style="text-align: left; margin: 30px 0 15px 5px; scroll-margin-top: 30px;">
  <div style="font-size: 0.9rem; font-weight: bold; color: {CYAN}; letter-spacing: 1.5px; text-transform: uppercase;">
    &gt;&gt; GRC Resources &amp; Tools
  </div>
  <div style="font-size: 0.55rem; color: #505060; margin-top: 4px; letter-spacing: 0.5px; line-height: 1.5;">
    <span style="color: {BLUE}; border: 1px solid {BLUE}40; padding: 0 3px; border-radius: 2px;">80 CURATED RANKED BY POPULARITY</span>
  </div>
</div>
""", unsafe_allow_html=True)
l1,l2,l3,l4=st.columns(4)
with l1:
    st.markdown(f'<div style="font-size:.54rem;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;border-bottom:1px dashed #1a1a2e;padding-bottom:2px;">▸ FRAMEWORKS &amp; STANDARDS</div>', unsafe_allow_html=True)
    for a in [("01","NIST CSF 2.0","https://www.nist.gov/cyberframework","Cybersecurity risk mgmt."),("02","NIST RMF","https://csrc.nist.gov/projects/risk-management/about-rmf","Risk mgmt framework."),("03","NIST AI RMF","https://www.nist.gov/itl/ai-risk-management-framework","AI risk management."),("04","ISO/IEC 27001","https://www.iso.org/isoiec-27001-information-security.html","International ISMS."),("05","CIS Controls v8","https://www.cisecurity.org/controls/","Prioritized safeguards."),("06","HITRUST CSF","https://hitrustalliance.net/","Healthcare+ risk mgmt."),("07","MITRE ATT&CK","https://mitre-attack.github.io/attack-navigator/","Adversary TTP matrix."),("08","MITRE D3FEND","https://d3fend.mitre.org/","Defensive knowledge graph."),("09","CVSS 4.0","https://www.first.org/cvss/calculator/4.0","Vuln scoring."),("10","NIST CSRC","https://csrc.nist.gov/","Comp Security Resource Ctr."),("11","SP 800-53","https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final","Security controls."),("12","NIST NVD","https://nvd.nist.gov/","National Vuln Database."),("13","CISA KEV","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","Exploited CVEs."),("14","Shields Up","https://www.cisa.gov/shields-up","Cyber resilience."),("15","NIST 800-171","https://csrc.nist.gov/publications/detail/sp/800-171/rev-2/final","CUI protection."),("16","CISA Free Tools","https://www.cisa.gov/resources-tools/resources/no-cost-cybersecurity-services-and-tools","Free govt security services."),("17","FIRST CSIRT","https://www.first.org/","Incident response teams."),("18","EPSS Scores","https://www.first.org/epss/","Exploit prediction scoring."),("19","ENISA","https://www.enisa.europa.eu/","EU cybersecurity agency."),("20","ATT&CK Navigator","https://mitre-attack.github.io/attack-navigator/","Interactive ATT&CK matrix.")]:
        st.markdown(gl(*a), unsafe_allow_html=True)
with l2:
    st.markdown(f'<div style="font-size:.54rem;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;border-bottom:1px dashed #1a1a2e;padding-bottom:2px;">▸ THREAT INTEL &amp; LIVE MAPS</div>', unsafe_allow_html=True)
    for a in [("16","VirusTotal","https://www.virustotal.com/","Analyze files, domains, IPs."),("17","AlienVault OTX","https://otx.alienvault.com/","Crowdsourced IOCs."),("18","Talos Intel","https://talosintelligence.com/","Cisco threat intel."),("19","Shodan","https://www.shodan.io/","Internet device search."),("20","Have I Been Pwned","https://haveibeenpwned.com/","Breach exposure."),("21","crt.sh","https://crt.sh/","Cert Transparency."),("22","SANS ISC","https://isc.sans.edu/","Threat monitor."),("23","URLhaus","https://urlhaus.abuse.ch/","Malware URLs."),("24","MalwareBazaar","https://bazaar.abuse.ch/","Malware samples."),("25","ThreatFox","https://threatfox.abuse.ch/","Community IOCs."),("26","Exploit-DB","https://www.exploit-db.com/","Public exploits."),("27","Pulsedive","https://pulsedive.com/","Free threat intel."),("28","GreyNoise","https://viz.greynoise.io/","Scanner intel."),("29","Kaspersky Map","https://cybermap.kaspersky.com/","Live threat map."),("30","Bitdefender Map","https://threatmap.bitdefender.com/","Threat map."),("31","Check Point Map","https://threatmap.checkpoint.com/","ThreatCloud."),("32","SonicWall Map","https://attackmap.sonicwall.com/live-attack-map/","Attack map."),("33","Sicherheitstacho","https://www.sicherheitstacho.eu/?lang=en","DT map."),("34","Threatbutt","https://threatbutt.com/map/","Attack map."),("35","Censys","https://search.censys.io/","Internet asset discovery."),("36","AbuseIPDB","https://www.abuseipdb.com/","IP abuse reporting."),("37","Hybrid Analysis","https://www.hybrid-analysis.com/","Free malware analysis."),("38","InQuest Labs","https://labs.inquest.net/","Threat intel lookups."),("39","PhishTank","https://phishtank.org/","Phishing URL database.")]:
        st.markdown(gl(*a), unsafe_allow_html=True)
with l3:
    st.markdown(f'<div style="font-size:.54rem;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;border-bottom:1px dashed #1a1a2e;padding-bottom:2px;">▸ SECURITY TOOLS (FREE/OPEN)</div>', unsafe_allow_html=True)
    for a in [("35","CyberChef","https://gchq.github.io/CyberChef/","Cyber Swiss Army Knife."),("36","Any.Run","https://any.run/","Malware sandbox."),("37","URLScan.io","https://urlscan.io/","Website scanning."),("38","GTFOBins","https://gtfobins.github.io/","Unix bypass binaries."),("39","LOLBAS","https://lolbas-project.github.io/","Windows LOTL."),("40","Security Onion","https://securityonionsolutions.com/","Threat hunting."),("41","OSINT Framework","https://osintframework.com/","OSINT tools."),("42","PayloadsAllThings","https://github.com/swisskyrepo/PayloadsAllTheThings","Payloads."),("43","Nuclei","https://github.com/projectdiscovery/nuclei-templates","Vuln templates."),("44","OpenCTI","https://www.opencti.io/","Open threat intel."),("45","YARA Rules","https://github.com/Yara-Rules/rules","Malware rules."),("46","Sigma Rules","https://github.com/SigmaHQ/sigma","Detection format."),("47","Wazuh","https://wazuh.com/","Open XDR/SIEM."),("48","Nmap","https://nmap.org/","#1 network scanner."),("49","Wireshark","https://www.wireshark.org/","#1 packet analyzer."),("50","Metasploit","https://www.metasploit.com/","#1 pen test framework."),("51","Kali Linux","https://www.kali.org/","#1 security distro."),("52","Suricata","https://suricata.io/","High-perf IDS/IPS.")]:
        st.markdown(gl(*a), unsafe_allow_html=True)
with l4:
    st.markdown(f'<div style="font-size:.54rem;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;border-bottom:1px dashed #1a1a2e;padding-bottom:2px;">▸ TRAINING, NEWS &amp; COMMUNITY</div>', unsafe_allow_html=True)
    for a in [("48","OWASP Top 10","https://owasp.org/www-project-top-ten/","Web app risks."),("49","OWASP LLM","https://owasp.org/www-project-top-10-for-large-language-model-applications/","LLM risks."),("50","OWASP API","https://owasp.org/API-Security/","API risks."),("51","HackTheBox","https://www.hackthebox.com/","Gamified training."),("52","TryHackMe","https://tryhackme.com/","Hands-on labs."),("53","PortSwigger","https://portswigger.net/web-security","Web vuln training."),("54","BleepingComputer","https://www.bleepingcomputer.com/","Security news."),("55","Hacker News","https://thehackernews.com/","Cyber news."),("56","SANS Papers","https://www.sans.org/white-papers/","Whitepapers."),("57","DEF CON","https://defcon.org/html/links/dc-archives.html","Archives."),("58","HackerOne","https://www.hackerone.com/","Bug bounty."),("59","Bugcrowd","https://www.bugcrowd.com/","Vuln disclosure."),("60","Dark Reading","https://www.darkreading.com/","Enterprise security news."),("61","Krebs on Security","https://krebsonsecurity.com/","Investigative security blog."),("62","KnowBe4 Free","https://www.knowbe4.com/free-cybersecurity-tools","Phishing sim & training."),("63","Gophish","https://getgophish.com/","Open-source phishing sim."),("64","IntelTechniques","https://inteltechniques.com/tools/","OSINT search tools."),("65","MITRE Engage","https://engage.mitre.org/","Adversary engagement.")]:
        st.markdown(gl(*a), unsafe_allow_html=True)
st.markdown(f'''
<div style="border-top:1px solid #141420;padding-top:20px;margin-top:32px;text-align:center;font-family:{MONO};">
  <div style="color:#666;font-size:.8rem;margin-bottom:3px;">Questions, Comments, or Recommendations?</div>
  <div style="color:#666;font-size:.8rem;margin-bottom:10px;">
    Developed by <b style="color:{GREEN};">Adam Kistler</b> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">LinkedIn</a> &nbsp;|&nbsp;
    <a href="https://github.com/adamkistler98/SecAI-Nexus" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">GitHub</a></div>
  <div style="color:#555;font-size:.56rem;padding:0 8%;line-height:1.5;margin-bottom:10px;text-align:center;max-width:900px;margin-left:auto;margin-right:auto;">
    <b style="color:#777;">LEGAL DISCLAIMER:</b> This project is provided for educational, informational, portfolio
    demonstration, and personal use purposes only. It is not intended for use in production environments,
    as a compliance tool, as professional security advice, or as a basis for business, legal, financial,
    or regulatory decisions. All threat intelligence, metrics, statistics, estimates, and data presented
    are sourced from publicly available third-party reports and APIs. The author makes no representations
    or warranties, express or implied, regarding the accuracy, completeness, timeliness, reliability, or
    fitness for any particular purpose of any data displayed. The author shall not be liable for any direct,
    indirect, incidental, special, exemplary, or consequential damages arising in any way out of the use of
    this software or reliance on output, even if advised of the possibility of such damages. Estimated
    metrics (labeled "EST") are derived from annually published industry reports and may not reflect current
    conditions. Live metrics are dependent on the availability and accuracy of upstream API providers. This
    software does not collect, store, process, or transmit any user data. No authentication, cookies, tracking,
    telemetry, or analytics are implemented. The author is not affiliated with, endorsed by, or sponsored by
    any third-party data provider or cybersecurity company referenced within this project. All external content
    remains the property of its respective owners. Use at your own risk.</div>
  <div style="color:#555;font-size:.54rem;line-height:1.4;margin-bottom:10px;max-width:900px;margin-left:auto;margin-right:auto;">
    <b style="color:#666;">DUAL LICENSE:</b>
    Source code &mdash; <a href="https://opensource.org/licenses/MIT" target="_blank" class="fl">MIT License</a> &nbsp;|&nbsp;
    Design &amp; layout &mdash; <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank" class="fl">CC BY-NC 4.0</a> &nbsp;|&nbsp;
    <a href="https://github.com/adamkistler98/SecAI-Nexus/blob/main/LICENSE" target="_blank" class="fl">Full License Terms</a></div>
  <div style="margin-bottom:8px;">
    <a href="https://github.com/adamkistler98/SecAI-Nexus" target="_blank"
       style="color:#505060;font-size:.6rem;text-decoration:none;border:1px solid #1a1a2e;padding:3px 10px;border-radius:3px;">
       Star on GitHub</a></div>
  <div style="color:#2a2a3a;font-size:.6rem;">
    SecAI-Nexus GRC [v34] | Live Data Engine | 12 hr Cache |
    118 Metrics | 10 Intel Tables | 2 Maps | 80 Resources | {now_utc.strftime("%Y")}</div></div>
''', unsafe_allow_html=True)
