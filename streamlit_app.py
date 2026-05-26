import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# SEC AI NEXUS — CYBER THREAT INTELLIGENCE DASHBOARD
# Author: Adam Kistler
# Version: 1.2
# Last Updated: May 26, 2026
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

# ====================== LINKEDIN PREVIEW IMAGE ======================
st.markdown("""
<meta property="og:title" content="SecAI-Nexus GRC — Real-Time Cyber Threat Intelligence Dashboard">
<meta property="og:description" content="Free open-source platform with 112 live risk metrics, AI/LLM threat tracking, ransomware intelligence, and global attack maps. Built for security & GRC teams.">
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

@st.cache_data(ttl=3600, show_spinner=False)
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

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_urlhaus():
    r = _g("https://urlhaus.abuse.ch/downloads/text_online/", t=15)
    if not r: return None
    return {"online":len([l for l in r.text.splitlines() if l.strip() and not l.startswith("#")])}

@st.cache_data(ttl=3600, show_spinner=False)
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

@st.cache_data(ttl=3600, show_spinner=False)
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

# ══════════════════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
st.markdown(
f"""
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; border-bottom: 2px solid #141420; padding-bottom: 12px; margin-bottom: 20px; margin-top: -50px; gap: 15px;">
  <div style="flex: 1; min-width: 300px; text-align: left;">
    <div style="margin-bottom: 4px;">
      <span style="font-size: 1.7rem; font-weight: bold; color: {CYAN}; text-shadow: 0 0 15px {CYAN}80; letter-spacing: 1.5px;">
        🤖 SecAI-Nexus
      </span>
      <span style="font-size: .45rem; color: #4a4a5a; border: 1px solid #2a2a3a; padding: 1px 4px; margin-left: 6px; vertical-align: middle;">v1.2</span>
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
     <a href="#global-threat-metrics" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase; margin-bottom: 12px;">
      &gt;&gt; ⏬ JUMP TO GLOBAL THREAT METRICS &lt;&lt;
     </a><br>
     <a href="#live-threat-maps" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase; margin-bottom: 12px;">
      &gt;&gt; ⏬ JUMP TO LIVE THREAT MAP FEEDS &lt;&lt;
     </a><br>
     <a href="#framework-comparison" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase; margin-bottom: 12px;">
      &gt;&gt; ⏬ JUMP TO FRAMEWORK COMPARISON &amp; LINEAGE &lt;&lt;
     </a><br>
     <a href="#grc-resources" style="display: inline-block; padding: 8px 18px; border: 1px solid {CYAN}; border-radius: 4px; color: {CYAN}; font-size: 0.68rem; font-weight: bold; text-decoration: none; background: rgba(0, 229, 255, 0.1); box-shadow: 0 0 15px {CYAN}40; letter-spacing: 1px; transition: 0.3s; text-transform: uppercase;">
      &gt;&gt; ⏬ JUMP TO GRC RESOURCES &amp; TOOLS &lt;&lt;
     </a>
  </div>
  <div style="flex: 1; text-align: right; min-width: 220px;">
    <div style="font-size: .78rem; font-weight: bold; color: {BLUE}; text-shadow: 0 0 4px {BLUE}; letter-spacing: 0.5px;">
      {now_utc.strftime("%H:%M:%S")} UTC <span style="color:#3a3a4a; margin: 0 6px;">|</span> {now_utc.strftime("%Y-%m-%d")}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.spinner("Syncing threat intelligence feeds…"):
    kev=fetch_kev(); baz=fetch_bazaar(); uhaus=fetch_urlhaus()
    feodo=fetch_feodo(); sans=fetch_sans(); tor=fetch_tor()
    topports=fetch_topports(); topips=fetch_topips(); honeypot=fetch_honeypot()

# ── BASELINES (updated May 2026 with IBM 2026 / CrowdStrike 2026 GTR) ─────────────────────────────────────────────────────────────────
CVE_TOT=31_500; CVE_CRIT=4_800; CVE_HIGH=13_200
RANSOM=6_100; SUPPLY=3_400; INSIDER=7_200
BREACH=8_400_000_000; BEC=23_100; PHISH=2_150_000
IDENTITY=18_200_000_000; GDPR=2_300_000_000; IC3LOSS=13_800_000_000
DDOS=18_200_000; IOT_MAL=128_000_000; CRYPTO=2_400_000_000
CISA_ADV=920; CISA_ICS=460; RECOVERY=2_910_000

# ── FALLBACKS (when APIs blocked locally) ────────────────────────────────────
if not kev:
    kev={"total":1555,"rw":380,"vendors":278,"prods":620,"tv":"Microsoft","tvc":340,
         "top3v":["Microsoft","Apple","Google"],"tp":"Windows","tpc":210,"d30":11,"d365":102}
if not feodo:
    feodo={"on":310,"off":550,"total":860,"mw_fams":6,"top_mw":"Pikabot","mw_count":110}
if not baz:
    baz={"total":4800,"tf":"AgentTesla","families":92,"top_ft":".exe","d7":3100}
if not uhaus:
    uhaus={"online":13800}
if not sans:
    sans={"infocon":"green"}
if not tor:
    tor={"c":7600}

# ══════════════════════════════════════════════════════════════════════════════
# AI SECURITY & THREAT INTELLIGENCE REFERENCE 
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
    GOVERNANCE REPOSITORY · MITRE ATT&amp;CK&reg; · OWASP AI/LLM TOP 10 · ADVERSARIAL MACHINE LEARNING · GLOBAL IMPACT ANALYSIS
  </div>
</div>
""", unsafe_allow_html=True)

def _tbl(title, hdrs, rows_data, hdr_color):
    hh = "".join(f'<th style="padding:6px 4px;text-align:left;color:{hdr_color};font-size:.52rem;text-transform:uppercase;">{h}</th>' for h in hdrs)
    rh = ""
    for r in rows_data:
        rh += '<tr style="border-bottom:1px solid #141420;">' + "".join(f'<td style="padding:6px 4px;{s}">{v}</td>' for v,s in r) + '</tr>'
    return f'<div style="margin-bottom:10px;"><div style="font-size:.68rem;font-weight:bold;color:{hdr_color};text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px;border-bottom:1px solid {hdr_color}20;padding-bottom:3px;">{title}</div><div style="overflow-x:auto;border:1px solid #1a1a2e;background:#080810;padding:2px;"><table style="width:100%;border-collapse:collapse;font-family:{MONO};font-size:.6rem;"><thead><tr style="border-bottom:2px solid {hdr_color}30;background:#0a0a14;">{hh}</tr></thead><tbody style="line-height:1.5;">{rh}</tbody></table></div></div>'

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

# ── TOP 15 AI MODELS & CAPABILITIES (May 2026) ───────────────────────────────────
ai_models_data = [
    ("1. Gemini 3.1 Pro", "https://gemini.google.com/", "Multimodal Reasoning", "Complex tasks & integration", "Google's flagship with 2M+ context & superior multimodal", "LLM01: Prompt Injection"),
    ("2. Claude 4.6 Opus", "https://claude.ai/", "Advanced Reasoning", "Safety & long-form content", "Anthropic's top model excelling in logic and ethical alignment", "LLM02: Insecure Output Handling"),
    ("3. GPT-5.3", "https://chatgpt.com/", "Agentic Intelligence", "Versatile research & automation", "OpenAI's latest with enhanced reasoning and tool use", "LLM08: Supply Chain Vulnerabilities"),
    ("4. Grok 4.20", "https://x.ai/", "Real-time Knowledge", "Current events & uncensored", "xAI's innovative multi-agent architecture model", "LLM06: Sensitive Information Disclosure"),
    ("5. Llama 4 Scout", "https://llama.meta.com/", "Open Weights", "Local & enterprise deploy", "Meta's leading open-source model with massive context", "LLM08: Supply Chain Vulnerabilities"),
    ("6. DeepSeek V3.2", "https://deepseek.com/", "Math & Coding", "High-precision technical tasks", "Strongest open-source performer in STEM domains", "LLM03: Training Data Poisoning"),
    ("7. Qwen 3.5 Max", "https://qwen.ai/", "Multilingual Efficiency", "Business workflows", "Alibaba's top multilingual & efficient model", "LLM07: Insecure Plugin Design"),
    ("8. Mistral Large 3", "https://mistral.ai/", "Enterprise Reasoning", "Fast & secure inference", "Leading European AI for global business use", "LLM01: Prompt Injection"),
    ("9. Perplexity Pro", "https://www.perplexity.ai/", "Search & Research", "Real-time citations", "AI-powered search with live web access", "LLM04: Model Denial of Service"),
    ("10. Cohere Command R+", "https://cohere.com/", "Enterprise RAG", "Secure business workflows", "Cohere's retrieval-augmented generation leader", "LLM02: Insecure Output Handling"),
    ("11. GLM-5", "https://zhipuai.cn/", "Multimodal", "Chinese/English tasks", "Zhipu AI's powerful multimodal model", "LLM08: Supply Chain Vulnerabilities"),
    ("12. Phi-4", "https://azure.microsoft.com/", "Lightweight Edge", "On-device & efficient AI", "Microsoft's optimized small language model", "LLM03: Training Data Poisoning"),
    ("13. Kimi K2 Thinking", "https://kimi.moonshot.cn/", "Long Context", "Deep reasoning", "Moonshot's advanced long-context model", "LLM06: Sensitive Information Disclosure"),
    ("14. Seed 2.0", "https://bytedance.com/", "Creative Generation", "Content & media", "ByteDance's advanced generative AI", "LLM07: Insecure Plugin Design"),
    ("15. MiniMax M2.5", "https://minimax.cn/", "Compact & Fast", "Mobile & edge deployment", "Highly efficient model for constrained environments", "LLM10: Model Theft")
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

# ── TOP 15 AI-POWERED CYBERCRIME (May 2026) ──────────────────────────────────────
ai_crime_data = [
    ("1. AI Phishing Campaigns", "Scaling 400% YoY", "Hyper-personalized spear-phishing with perfect grammar", "CrowdStrike GTR 2026", "https://www.crowdstrike.com/global-threat-report/"),
    ("2. Deepfake Vishing", "442% ↑", "3-second voice cloning for CEO fraud & wire transfers", "IBM Cost of Breach 2026", "https://www.ibm.com/reports/data-breach"),
    ("3. Polymorphic AI Malware", "Evasive", "BlackMamba-style code mutation that bypasses all AV", "CrowdStrike GTR 2026", "https://www.crowdstrike.com/global-threat-report/"),
    ("4. Prompt Injection Attacks", "#1 LLM risk", "Direct/indirect injection leading to data exfil", "OWASP LLM Top 10", "https://owasp.org/www-project-top-10-for-large-language-model-applications/"),
    ("5. Automated OSINT & Recon", "Automated", "LLM-driven target profiling in minutes", "Mandiant M-Trends 2026", "https://www.mandiant.com/m-trends"),
    ("6. Model Poisoning (Supply Chain)", "Growing", "Backdoored Hugging Face models & training data", "MITRE ATLAS", "https://atlas.mitre.org/"),
    ("7. Agentic AI Abuse", "Insider Risk", "Autonomous agents performing unintended actions", "IBM Cost of Breach 2026", "https://www.ibm.com/reports/data-breach"),
    ("8. Deepfake Video Fraud", "Rising", "Real-time face swaps in video calls ($25M+ scams)", "Chainalysis 2026", "https://www.chainalysis.com/"),
    ("9. AI PassGAN Cracking", "51% <60s", "Predictive password cracking at machine speed", "Dark Reading", "https://www.darkreading.com/"),
    ("10. Adversarial ML Evasion", "Emerging", "Pixel perturbations that fool every classifier", "CrowdStrike GTR 2026", "https://www.crowdstrike.com/global-threat-report/"),
    ("11. AI-Generated Ransomware", "Fastest breakout", "LLMs writing custom encryptors on demand", "Sophos 2026", "https://www.sophos.com/en-us/content/state-of-ransomware"),
    ("12. Shadow AI Data Leakage", "20% of breaches", "Rogue LLMs exfiltrating sensitive data", "IBM Cost of Breach 2026", "https://www.ibm.com/reports/data-breach"),
    ("13. AI-Driven BEC", "Deepfake voice", "CEO voice cloning for $137k+ wire fraud", "FBI IC3 2026", "https://www.ic3.gov/AnnualReport"),
    ("14. Training Data Poisoning", "Backdoor risk", "Corrupted datasets creating hidden triggers", "OWASP LLM Top 10", "https://owasp.org/www-project-top-10-for-large-language-model-applications/"),
    ("15. Autonomous Agent Hijacking", "Critical", "Rogue LLM agents executing unauthorized API calls", "IBM Cost of Breach 2026", "https://www.ibm.com/reports/data-breach")
]

crime_rows = []
for name, trend, desc, source, link in ai_crime_data:
    crime_rows.append([
        (name, f"color:{RED};font-weight:bold;white-space:nowrap;"),
        (trend, f"color:{AMBER};"),
        (desc, f"color:#888;font-size:.56rem;"),
        (f'<a href="{link}" target="_blank" style="color:{BLUE};">{source}</a>', "")
    ])

# Render AI Tables Side by Side
col1, col2 = st.columns(2)
with col1:
    st.markdown(_tbl("Top 15 AI Models & Vulnerability Mappings", ["Model", "Use Case", "Best For", "Description", "Primary LLM Risk"], ai_rows, CYAN), unsafe_allow_html=True)
with col2:
    st.markdown(_tbl("Top 15 AI-Powered Cyber Threats", ["Threat Vector", "Trend", "Description", "Source Intelligence"], crime_rows, RED), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FRAMEWORK COMPARISON & LINEAGE (PLOTLY VISUALIZATIONS)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div id="framework-comparison" style="margin-top: 40px; scroll-margin-top: 30px;">
  <span style="font-size: 1.4rem; font-weight: bold; color: #00e5ff; text-shadow: 0 0 10px #00e5ff80; letter-spacing: 1.2px;">
    📊 Framework Comparison & Threat Lineage
  </span>
  <hr style="border-color:#141420; margin-top: 5px; margin-bottom: 20px;">
</div>
""", unsafe_allow_html=True)

f_col1, f_col2 = st.columns(2)

with f_col1:
    st.markdown("<div style='color:#00ff41; font-weight:bold; margin-bottom:10px; font-family:\"Courier New\", Courier, monospace; font-size:0.85rem; text-transform:uppercase;'>GRC Framework Coverage Map</div>", unsafe_allow_html=True)
    categories = ['Governance', 'Asset Management', 'Access Control', 'Incident Response', 'Supply Chain Risk']
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[5, 4, 3, 5, 4],
        theta=categories,
        fill='toself',
        name='NIST CSF 2.0',
        line_color='#00e5ff'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[4, 5, 5, 4, 3],
        theta=categories,
        fill='toself',
        name='ISO/IEC 27001:2022',
        line_color='#00ff41'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], color='#6a6a7a'),
            bgcolor='#050505'
        ),
        showlegend=True,
        paper_bgcolor='#050505',
        font=dict(color='#00ff41'),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with f_col2:
    st.markdown("<div style='color:#00ff41; font-weight:bold; margin-bottom:10px; font-family:\"Courier New\", Courier, monospace; font-size:0.85rem; text-transform:uppercase;'>Attack Vector Lineage & Data Impact</div>", unsafe_allow_html=True)
    
    fig_sankey = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "#1a1a2e", width = 0.5),
          label = ["AI Phishing", "Deepfake Vishing", "Credential Compromise", "Identity Provider", "Data Exfiltration"],
          color = ["#ffaa00", "#ffaa00", "#ff4b4b", "#008aff", "#ff4b4b"]
        ),
        link = dict(
          source = [0, 1, 2, 3], 
          target = [2, 2, 3, 4],
          value = [8, 4, 12, 10],
          color="rgba(106, 106, 122, 0.3)"
      ))])

    fig_sankey.update_layout(
        font=dict(size=10, color='#6a6a7a'),
        paper_bgcolor='#050505',
        margin=dict(l=10, r=10, t=20, b=20)
    )
    st.plotly_chart(fig_sankey, use_container_width=True)
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
st.markdown(f"""
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
    Source code &mdash; <a href="https://opensource.org/licenses/MIT" target="_blank" class="fl">MIT License</a> &nbsp;·&nbsp;
    Design &amp; layout &mdash; <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank" class="fl">CC BY-NC 4.0</a> &nbsp;·&nbsp;
    <a href="https://github.com/adamkistler98/SecAI-Nexus/blob/main/LICENSE" target="_blank" class="fl">Full License Terms</a></div>
  <div style="margin-bottom:8px;">
    <a href="https://github.com/adamkistler98/SecAI-Nexus" target="_blank"
       style="color:#505060;font-size:.6rem;text-decoration:none;border:1px solid #1a1a2e;padding:3px 10px;border-radius:3px;">
       ⭐ Star on GitHub</a></div>
  <div style="color:#2a2a3a;font-size:.6rem;">
    SecAI-Nexus GRC [v31.0] · Live Data Engine · 12hr Cache ·
    112 Metrics · 8 Intel Tables · 2 Maps · 80 Resources · {now_utc.strftime("%Y")}</div></div>""", unsafe_allow_html=True)
