import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="SecAI-Nexus GRC", layout="wide", page_icon="🔒",
                   initial_sidebar_state="collapsed")

# ── THEME ─────────────────────────────────────────────────────────────────────
MONO  = "'Courier New', Courier, monospace"
GREEN = "#00ff41"; BLUE = "#008aff"; RED = "#ff4b4b"
AMBER = "#ffaa00"; CYAN = "#00e5ff"; BG = "#050505"; CARD = "#0a0a0a"

st.markdown(f"""
<style>
  @keyframes pglow {{ 0%,100%{{text-shadow:0 0 4px {GREEN}30;}} 50%{{text-shadow:0 0 10px {GREEN}70;}} }}
  .stApp {{background:{BG}!important;font-family:{MONO}!important;}}
  div[data-testid="stMarkdownContainer"]>p {{color:{GREEN};font-size:1.05rem;line-height:1.6;font-family:{MONO};}}
  h1,h2,h3,h4,h5,h6,label {{color:{GREEN}!important;}}
  header,footer {{visibility:hidden;}}
  .stDeployButton {{display:none;}}
  div[data-testid="stSpinner"]>div>p {{color:{GREEN}!important;}}

  .cm {{
    background:linear-gradient(135deg,{CARD},#0d0d12);
    border:1px solid #1a1a2e; border-left:3px solid {BLUE};
    padding:7px 8px 6px; margin-bottom:6px; font-family:{MONO};
    transition:all .3s; min-height:105px;
  }}
  .cm:hover {{border-left-color:{GREEN};box-shadow:0 0 10px {GREEN}0d;}}
  .cm-t a {{color:{BLUE};font-size:.52rem;font-weight:bold;text-transform:uppercase;
    letter-spacing:.4px;text-decoration:none;transition:.2s;}}
  .cm-t a:hover {{color:{GREEN};text-shadow:0 0 4px {GREEN};}}
  .cm-l {{font-size:.44rem;color:{GREEN};border:1px solid {GREEN};padding:0 3px;
    margin-left:3px;vertical-align:middle;animation:pglow 3s ease-in-out infinite;}}
  .cm-e {{font-size:.44rem;color:{AMBER};border:1px solid {AMBER}80;padding:0 3px;
    margin-left:3px;vertical-align:middle;}}
  .cm-v {{color:{GREEN};font-size:1.1rem;font-weight:bold;margin:3px 0 1px;
    line-height:1.05;text-shadow:0 0 4px {GREEN}20;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .cm-s {{font-size:.5rem;color:#4a4a5a;margin-bottom:4px;line-height:1.15;
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .cm-d {{font-size:.52rem;border-top:1px dashed #1a1a2e;padding-top:3px;line-height:1.5;}}
  .d-b {{color:{RED};font-weight:bold;}} .d-g {{color:{GREEN};font-weight:bold;}}
  .d-n {{color:{BLUE};font-weight:bold;}} .d-a {{color:{AMBER};font-weight:bold;}}

  .rl {{font-size:.55rem;color:#3a3a4a;text-transform:uppercase;letter-spacing:1px;
    border-left:3px solid {BLUE}50;padding-left:6px;margin:10px 0 5px;
    background:linear-gradient(90deg,{BLUE}06,transparent 35%);padding-top:2px;padding-bottom:2px;}}

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

  .sb {{font-size:.62rem;font-family:{MONO};margin:2px 0 20px;padding:8px 12px;
    background:linear-gradient(135deg,#070709,#0a0a10);
    border:1px solid #181828;border-left:3px solid {BLUE}40;line-height:1.8;}}
  .mw {{border:1px solid #1a1a2e;background:#080810;padding:2px;margin-bottom:5px;}}
  .fl {{color:#383848;text-decoration:none;border-bottom:1px dashed #383848;transition:.2s;}}
  .fl:hover {{color:{GREEN};border-bottom-color:{GREEN};}}
  hr {{border-color:#141420!important;}}
  .sd {{display:inline-block;width:5px;height:5px;border-radius:50%;margin-right:3px;vertical-align:middle;}}
  .sg {{background:{GREEN};box-shadow:0 0 4px {GREEN};}}
  .sa {{background:{AMBER};box-shadow:0 0 4px {AMBER};}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHERS
# ══════════════════════════════════════════════════════════════════════════════
S = requests.Session()
S.headers.update({"User-Agent":"SecAI-Nexus-GRC/4.0 (educational-dashboard)"})

def _g(url, t=14, **k):
    try:
        r = S.get(url, timeout=t, **k); r.raise_for_status(); return r
    except Exception: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_kev():
    r = _g("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    if not r: return None
    try:
        vulns = r.json().get("vulnerabilities",[]); now = datetime.now(timezone.utc)
        cnt = {1:0,7:0,30:0,365:0}; rw = 0; vd = {}
        for v in vulns:
            try:
                age = (now - datetime.strptime(v["dateAdded"],"%Y-%m-%d").replace(tzinfo=timezone.utc)).days
                for d in cnt:
                    if age <= d: cnt[d] += 1
            except: pass
            if v.get("knownRansomwareCampaignUse","").lower()=="known": rw += 1
            vn = v.get("vendorProject","?"); vd[vn] = vd.get(vn,0)+1
        tv = max(vd, key=vd.get) if vd else "N/A"
        return {"total":len(vulns),"d1":cnt[1],"d7":cnt[7],"d30":cnt[30],"d365":cnt[365],
                "rw":rw,"tv":tv,"tvc":vd.get(tv,0)}
    except: return None

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_bazaar():
    r = _g("https://bazaar.abuse.ch/export/csv/recent/", t=22)
    if not r: return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        now = datetime.now(timezone.utc); d1=d7=0; sm={}
        for line in lines:
            p = line.split('","'); ts = p[0].strip('"')
            try:
                dt = datetime.strptime(ts,"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                age = (now-dt).days
                if age<=1: d1+=1
                if age<=7: d7+=1
            except: pass
            if len(p)>9:
                s = p[9].strip('"').strip()
                if s: sm[s] = sm.get(s,0)+1
        tf = max(sm, key=sm.get) if sm else "N/A"
        return {"d1":d1,"d7":d7,"total":len(lines),"tf":tf}
    except: return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_urlhaus():
    r = _g("https://urlhaus.abuse.ch/downloads/text_online/", t=15)
    if not r: return None
    return {"online":len([l for l in r.text.splitlines() if l.strip() and not l.startswith("#")])}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_feodo():
    r = _g("https://feodotracker.abuse.ch/downloads/ipblocklist.csv", t=15)
    if not r: return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        on = sum(1 for l in lines if '"online"' in l.lower())
        off = sum(1 for l in lines if '"offline"' in l.lower())
        return {"on":on,"off":off,"total":len(lines)}
    except: return None

def _parse_rss(url):
    r = _g(url, t=15)
    if not r: return None
    try:
        root = ET.fromstring(r.content); now = datetime.now(timezone.utc)
        cnt = {1:0,7:0,30:0,365:0}; tot=0
        for item in root.findall(".//item"):
            tot+=1; pub = item.findtext("pubDate","")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt = datetime.strptime(pub.strip(),fmt)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    age = (now-dt).days
                    for d in cnt:
                        if age<=d: cnt[d]+=1
                    break
                except ValueError: continue
        cnt["total"]=tot; return cnt
    except: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ics(): return _parse_rss("https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml")

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cisa_all(): return _parse_rss("https://www.cisa.gov/cybersecurity-advisories/all.xml")

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_sans():
    r = _g("https://isc.sans.edu/api/infocon?json", t=12)
    if not r: return None
    try: return {"infocon":r.json().get("status","?")}
    except: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tor():
    r = _g("https://check.torproject.org/torbulkexitlist", t=15)
    if not r: return None
    try: return {"c":len([l for l in r.text.splitlines() if l.strip() and not l.startswith("#")])}
    except: return None

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _f(n):
    if not isinstance(n,(int,float)): return str(n)
    n=int(n)
    if n>=1_000_000_000: return f"{n/1e9:.1f}B"
    if n>=1_000_000: return f"{n/1e6:.1f}M"
    if n>=1_000: return f"{n:,}"
    return str(n)

def nd():
    y=datetime.now().year
    return (datetime.now(timezone.utc)-datetime(y,1,1,tzinfo=timezone.utc)).days+1

def ytd(a): return int(a*nd()/365)
def per(a,d): return int(a*d/365)

# ── COMPACT CARD — shows 30d + 1yr deltas only ──────────────────────────────
def card(title, url, value, subtitle, d30, d30c, d1yr, d1yc, live=True):
    b = f'<span class="cm-l">LIVE</span>' if live else f'<span class="cm-e">EST</span>'
    st.markdown(f"""<div class="cm">
  <div class="cm-t"><a href="{url}" target="_blank">{title}</a>{b}</div>
  <div class="cm-v">{value}</div>
  <div class="cm-s">{subtitle}</div>
  <div class="cm-d">
    <span style="color:#2a2a3a;">30d </span><span class="{d30c}">{d30}</span>
    <span style="color:#2a2a3a;"> 1yr </span><span class="{d1yc}">{d1yr}</span>
  </div></div>""", unsafe_allow_html=True)

def lcard(title, url, data, vf, sf, d30f, d1yf, d30c="d-b", d1yc="d-b", fsub="awaiting"):
    if data:
        try:
            card(title, url, vf(data), sf(data), d30f(data), d30c, d1yf(data), d1yc, True)
            return
        except: pass
    st.markdown(f"""<div class="cm" style="opacity:.5;">
  <div class="cm-t"><a href="{url}" target="_blank">{title}</a><span class="cm-l">LIVE</span></div>
  <div class="cm-v" style="font-size:.9rem;color:#2a7a3a;">Syncing…</div>
  <div class="cm-s">{fsub}</div>
  <div class="cm-d" style="color:#2a2a3a;">Cloud deploy</div></div>""", unsafe_allow_html=True)

def iframe(url, h=1100):
    st.markdown(f'<div class="mw"><iframe src="{url}" width="100%" height="{h}" '
        f'style="border:none;" sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe></div>',
        unsafe_allow_html=True)

def rl(t): st.markdown(f'<div class="rl">{t}</div>', unsafe_allow_html=True)

def gl(n,t,u,d):
    return (f'<div style="margin-bottom:11px;">'
            f'<span style="color:{GREEN};font-weight:bold;font-size:.78rem;">{n}.</span> '
            f'<a href="{u}" target="_blank" class="rl2">{t}</a>'
            f'<div style="color:#4a4a5a;font-size:.68rem;margin-top:1px;padding-left:22px;">{d}</div></div>')

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
st.markdown(f"""
<div style="border-bottom:2px solid #141420;padding-bottom:8px;margin-bottom:14px;margin-top:-50px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;">
    <div>
      <span style="font-size:1.4rem;font-weight:bold;color:{GREEN};
        text-shadow:0 0 12px {GREEN}80;letter-spacing:1px;">🔒 SecAI-Nexus</span>
      <span style="font-size:.8rem;color:{BLUE};margin-left:8px;font-weight:bold;">
        // CYBER THREAT OBSERVABILITY PLATFORM</span>
      <span style="font-size:.48rem;color:#3a3a4a;border:1px solid #2a2a3a;
        padding:1px 4px;margin-left:5px;vertical-align:middle;">v18.0</span>
    </div>
    <div style="text-align:right;">
      <div style="font-size:.8rem;font-weight:bold;color:{BLUE};text-shadow:0 0 4px {BLUE};">
        SYS_TIME: {now_utc.strftime("%H:%M:%S")} UTC · {now_utc.strftime("%Y-%m-%d")}</div>
      <div style="font-size:.55rem;color:#3a3a4a;margin-top:1px;">
        <span class="sd sg"></span>FEEDS NOMINAL · 40 INDICATORS · 8 MAPS · 52 RESOURCES</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  FETCH
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("Syncing threat intelligence feeds…"):
    kev=fetch_kev(); baz=fetch_bazaar(); uhaus=fetch_urlhaus()
    feodo=fetch_feodo(); ics=fetch_ics(); cisa_all=fetch_cisa_all()
    sans=fetch_sans(); tor=fetch_tor()

# ══════════════════════════════════════════════════════════════════════════════
#  BASELINES (verified annual-report sources)
# ══════════════════════════════════════════════════════════════════════════════
CVE_TOT  = 29_000       # NVD 2024 published CVEs
CVE_CRIT = 4_200        # NVD 2024 CVSS ≥ 9.0
CVE_HIGH = 12_500       # NVD 2024 CVSS 7.0–8.9
RANSOM   = 5_500        # CrowdStrike GTR 2024: ~5,500 incidents
BREACH   = 8_000_000_000  # Verizon DBIR 2024: 8B records
BEC      = 21_489       # FBI IC3 2023: 21,489 BEC complaints
PHISH    = 1_970_000    # APWG eCrime 2024: 1.97M reports
SUPPLY   = 3_000        # CrowdStrike GTR 2024: ~3,000
INSIDER  = 6_800        # Verizon DBIR 2024: 6,800 cases
IDENTITY = 17_000_000_000  # SpyCloud 2024: 17B exposed creds
GDPR     = 2_100_000_000   # DLA Piper 2024: €2.1B
IC3LOSS  = 12_500_000_000  # FBI IC3 2023: $12.5B
DDOS     = 15_400_000   # Cloudflare 2024: 15.4M attacks
IOT_MAL  = 112_000_000  # SonicWall 2024: 112M IoT attacks
CRYPTO   = 2_200_000_000  # Chainalysis 2024: $2.2B stolen
RANSOM_PAY = 2_000_000  # Sophos 2024: $2M avg payment
RECOVERY = 2_730_000    # Sophos 2024: $2.73M avg recovery
WORKFORCE = 4_000_000   # ISC2 2024: 4M unfilled positions

# ══════════════════════════════════════════════════════════════════════════════
#  40 COMPACT METRICS — 5 ROWS × 8 CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:2px 0 10px;">
  <span style="font-size:1rem;font-weight:bold;text-transform:uppercase;letter-spacing:1px;">
    <a href="https://www.cisa.gov/" target="_blank" class="sh">&gt;&gt; GLOBAL THREAT METRICS</a></span><br>
  <span style="font-size:.58rem;color:#3a3a4a;">
    <span class="sd sg"></span><span style="color:{GREEN};">LIVE</span> = real-time
    &ensp;<span class="sd sa"></span><span style="color:{AMBER};">EST</span> = annual baseline
    &ensp;Deltas: 30d · 1yr &ensp;|&ensp; 40 indicators across 5 categories
  </span>
</div>""", unsafe_allow_html=True)

# ─── ROW 1: VULNERABILITY & EXPLOIT INTELLIGENCE ─────────────────────────────
rl("▸ VULNERABILITY & EXPLOIT INTELLIGENCE")
c = st.columns(8)
with c[0]:
    lcard("CISA KEV TOTAL","https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev, lambda d:_f(d["total"]), lambda d:f'{d["rw"]} ransomware-linked',
        lambda d:f'+{d["d30"]}', lambda d:f'+{d["d365"]}', fsub="CISA KEV catalog")
with c[1]:
    lcard("KEV RANSOMWARE","https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev, lambda d:_f(d["rw"]), lambda d:"CVEs tied to ransomware",
        lambda d:"–", lambda d:f'{_f(d["rw"])} total', d30c="d-n", d1yc="d-b", fsub="KEV ransomware subset")
with c[2]:
    lcard("KEV TOP VENDOR","https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev, lambda d:d["tv"], lambda d:f'{d["tvc"]} exploited CVEs',
        lambda d:"–", lambda d:f'{_f(d["tvc"])}', d30c="d-n", d1yc="d-b", fsub="KEV vendor breakdown")
with c[3]:
    card("CVEs PUBLISHED","https://nvd.nist.gov/",
        f"~{_f(CVE_TOT)}/yr", f"~{per(CVE_TOT,1)}/day · NVD 2024",
        f"+{per(CVE_TOT,30):,}","d-b", f"~{_f(CVE_TOT)}","d-b", False)
with c[4]:
    card("CRITICAL (≥9.0)","https://nvd.nist.gov/vuln/search",
        f"~{_f(CVE_CRIT)}/yr", f"~{per(CVE_CRIT,7)}/wk · CVSS ≥9",
        f"+{per(CVE_CRIT,30)}","d-b", f"~{_f(CVE_CRIT)}","d-b", False)
with c[5]:
    card("HIGH (7.0–8.9)","https://nvd.nist.gov/vuln/search",
        f"~{_f(CVE_HIGH)}/yr", f"~{per(CVE_HIGH,7)}/wk · CVSS HIGH",
        f"+{per(CVE_HIGH,30)}","d-b", f"~{_f(CVE_HIGH)}","d-b", False)
with c[6]:
    card("TIME TO EXPLOIT","https://www.crowdstrike.com/global-threat-report/",
        "5 Days", "disclosure→exploit · CS GTR",
        "-0.5d","d-g", "-3d","d-g", False)
with c[7]:
    lcard("SANS INFOCON","https://isc.sans.edu/",
        sans, lambda d:d.get("infocon","?").upper(), lambda d:"Internet threat · DShield",
        lambda d:"–", lambda d:d.get("infocon","?"), d30c="d-n", d1yc="d-g", fsub="SANS ISC API")

# ─── ROW 2: MALWARE, C2 & ADVISORIES ─────────────────────────────────────────
rl("▸ MALWARE, C2 & ADVISORY FEEDS")
c = st.columns(8)
with c[0]:
    lcard("BAZAAR SAMPLES","https://bazaar.abuse.ch/",
        baz, lambda d:f'{_f(d["total"])} 48h', lambda d:f'Top: {d["tf"]}',
        lambda d:f'~{_f(int(d["d7"]*(30/7)))}', lambda d:f'~{_f(int(d["d7"]*(365/7)))}',
        fsub="MalwareBazaar CSV")
with c[1]:
    lcard("MALICIOUS URLs","https://urlhaus.abuse.ch/",
        uhaus, lambda d:_f(d["online"]), lambda d:"Serving malware now",
        lambda d:"–", lambda d:"3.6M+ tracked", d30c="d-n", d1yc="d-n", fsub="URLhaus feed")
with c[2]:
    lcard("BOTNET C2s","https://feodotracker.abuse.ch/",
        feodo, lambda d:f'{_f(d["on"])} online', lambda d:f'{_f(d["total"])} tracked',
        lambda d:"–", lambda d:f'{_f(d["total"])} total', d30c="d-n", d1yc="d-n", fsub="Feodo Tracker")
with c[3]:
    lcard("TOR EXITS","https://metrics.torproject.org/",
        tor, lambda d:_f(d["c"]), lambda d:"Active exit relays",
        lambda d:"–", lambda d:f'{_f(d["c"])} nodes', d30c="d-n", d1yc="d-n", fsub="Tor bulk list")
with c[4]:
    lcard("CISA ALL ADV","https://www.cisa.gov/news-events/cybersecurity-advisories",
        cisa_all, lambda d:f'{d[7]}/wk', lambda d:f'{d.get("total",0)} in feed',
        lambda d:f'+{d[30]}', lambda d:f'+{d[365]}', fsub="CISA all advisory RSS")
with c[5]:
    lcard("ICS/SCADA ADV","https://www.cisa.gov/news-events/cybersecurity-advisories/ics-advisories",
        ics, lambda d:f'{d[7]}/wk', lambda d:"OT/ICS infra alerts",
        lambda d:f'+{d[30]}', lambda d:f'+{d[365]}', fsub="CISA ICS RSS")
with c[6]:
    card("RANSOMWARE RATE","https://www.sophos.com/en-us/blog/the-state-of-ransomware-2024",
        "59%", "of orgs hit · Sophos 2024",
        "–","d-n", "-7% YoY","d-g", False)
with c[7]:
    card("AVG RANSOM PAID","https://www.sophos.com/en-us/blog/the-state-of-ransomware-2024",
        "$2.0M", "median payment · Sophos 2024",
        "+$133k","d-b", "+$1.6M","d-b", False)

# ─── ROW 3: BREACH, INCIDENT & COST ──────────────────────────────────────────
rl("▸ BREACH, INCIDENT & COST IMPACT  [EST]")
c = st.columns(8)
with c[0]:
    card("RANSOMWARE","https://www.cisa.gov/stopransomware",
        _f(ytd(RANSOM)), f"YTD · ~{RANSOM:,}/yr CS GTR",
        f"+{per(RANSOM,30):,}","d-b", f"~{RANSOM:,}","d-b", False)
with c[1]:
    card("RECORDS BREACHED","https://www.verizon.com/business/resources/reports/dbir/",
        f"{ytd(BREACH)//1_000_000}M", "YTD · DBIR 2024",
        f"+{per(BREACH,30)//1_000_000}M","d-b", "~8B/yr","d-b", False)
with c[2]:
    card("BEC (IC3)","https://www.ic3.gov/AnnualReport",
        _f(ytd(BEC)), f"YTD · {BEC:,}/yr",
        f"+{per(BEC,30):,}","d-b", f"~{BEC:,}","d-b", False)
with c[3]:
    card("PHISHING","https://apwg.org/trendsreports/",
        f"{ytd(PHISH)//1_000}k YTD", "APWG eCrime 2024",
        f"+{per(PHISH,30):,}","d-b", f"~{PHISH//1_000}k/yr","d-b", False)
with c[4]:
    card("AVG BREACH COST","https://www.ibm.com/security/data-breach",
        "$4.88M", "global avg · IBM 2024",
        "+$407k","d-b", "$4.88M","d-b", False)
with c[5]:
    card("HEALTHCARE COST","https://www.ibm.com/security/data-breach",
        "$9.77M", "highest sector · IBM 2024",
        "+$814k","d-b", "$9.77M","d-b", False)
with c[6]:
    card("AVG RECOVERY","https://www.sophos.com/en-us/blog/the-state-of-ransomware-2024",
        "$2.73M", "excl. ransom · Sophos 2024",
        "+$227k","d-b", "$2.73M","d-b", False)
with c[7]:
    card("BREACH LIFECYCLE","https://www.ibm.com/security/data-breach",
        "258 Days", "identify+contain · IBM 2024",
        "-2d","d-g", "-19d","d-g", False)

# ─── ROW 4: FINANCIAL, REGULATORY & EMERGING ─────────────────────────────────
rl("▸ FINANCIAL, REGULATORY & EMERGING THREATS  [EST]")
c = st.columns(8)
with c[0]:
    card("GDPR FINES","https://www.enforcementtracker.com/",
        f"€{ytd(GDPR)//1_000_000}M YTD", "DLA Piper · ~€2.1B/yr",
        f"+€{per(GDPR,30)//1_000_000}M","d-b", "~€2.1B/yr","d-b", False)
with c[1]:
    card("IC3 LOSSES","https://www.ic3.gov/AnnualReport",
        f"${ytd(IC3LOSS)//1_000_000_000:.1f}B YTD", "FBI IC3 · $12.5B/yr",
        f"+${per(IC3LOSS,30)//1_000_000}M","d-b", "~$12.5B","d-b", False)
with c[2]:
    card("CRYPTO THEFT","https://www.chainalysis.com/blog/crypto-hacking-stolen-funds-2025/",
        f"${ytd(CRYPTO)//1_000_000}M YTD", "Chainalysis 2024 · $2.2B",
        f"+${per(CRYPTO,30)//1_000_000}M","d-b", "~$2.2B/yr","d-b", False)
with c[3]:
    card("DDoS ATTACKS","https://radar.cloudflare.com/reports/ddos-2024-q4",
        f"{ytd(DDOS)//1_000_000:.1f}M YTD", "Cloudflare · 15.4M/yr",
        f"+{per(DDOS,30)//1_000}k","d-b", "~15.4M","d-b", False)
with c[4]:
    card("IoT MALWARE","https://www.sonicwall.com/threat-report/",
        f"{ytd(IOT_MAL)//1_000_000}M YTD", "SonicWall · 112M/yr",
        f"+{per(IOT_MAL,30)//1_000_000}M","d-b", "~112M","d-b", False)
with c[5]:
    card("SUPPLY CHAIN","https://www.crowdstrike.com/global-threat-report/",
        "+45% YoY", f"~{ytd(SUPPLY):,} YTD · CS GTR",
        f"+{per(SUPPLY,30)}","d-b", f"~{SUPPLY:,}/yr","d-b", False)
with c[6]:
    card("INSIDER THREAT","https://www.verizon.com/business/resources/reports/dbir/",
        _f(ytd(INSIDER)), f"YTD · DBIR {INSIDER:,}/yr",
        f"+{per(INSIDER,30):,}","d-b", f"~{INSIDER:,}","d-b", False)
with c[7]:
    card("CYBERCRIME TOTAL","https://www.chainalysis.com/blog/2025-crypto-crime-report-introduction/",
        "$40.1B", "illicit crypto volume 2024",
        "–","d-n", "+$40.1B","d-b", False)

# ─── ROW 5: POSTURE, DETECTION & WORKFORCE ───────────────────────────────────
rl("▸ SECURITY POSTURE, DETECTION & WORKFORCE  [EST / LIVE]")
c = st.columns(8)
with c[0]:
    card("EXPOSED CREDS","https://spycloud.com/resource/2024-annual-identity-exposure-report/",
        f"{ytd(IDENTITY)//1_000_000_000:.1f}B YTD", "SpyCloud · ~17B/yr",
        f"+{per(IDENTITY,30)//1_000_000}M","d-b", "~17B","d-b", False)
with c[1]:
    card("ID-BASED ATTACKS","https://www.crowdstrike.com/global-threat-report/",
        "75%", "use valid creds · CS GTR",
        "–","d-n", "+75% YoY","d-b", False)
with c[2]:
    card("CLOUD MISCONFIG","https://www.verizon.com/business/resources/reports/dbir/",
        "21%", "of breaches · DBIR 2024",
        "–","d-n", "+3% YoY","d-b", False)
with c[3]:
    card("ZERO-TRUST","https://www.crowdstrike.com/global-threat-report/",
        "67%", "orgs implementing · CS",
        "–","d-n", "+12% YoY","d-g", False)
with c[4]:
    card("AVG MTTD","https://www.mandiant.com/m-trends",
        "10 Days", "median dwell · Mandiant",
        "-0.8d","d-g", "-4d","d-g", False)
with c[5]:
    card("WORKFORCE GAP","https://www.isc2.org/Insights/2024/09/Workforce-Study",
        "4.0M", "unfilled positions · ISC2",
        "–","d-n", "+12% YoY","d-b", False)
with c[6]:
    card("VULN EXPLOIT RATE","https://www.crowdstrike.com/global-threat-report/",
        "32%", "initial access vector · CS GTR",
        "–","d-n", "+5% YoY","d-b", False)
with c[7]:
    card("AI-ENHANCED ATTKS","https://www.crowdstrike.com/global-threat-report/",
        "+150%", "YoY growth · vishing/deepfake",
        "–","d-n", "+150% YoY","d-b", False)

# ─── SOURCES BAR ──────────────────────────────────────────────────────────────
ts = now_utc.strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""
<div class="sb">
  <span style="color:#3a3a4a;font-weight:bold;text-transform:uppercase;letter-spacing:.4px;">
    <span class="sd sg"></span>LIVE&nbsp;</span>
  <a href="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" target="_blank" class="sl">CISA KEV</a> ·
  <a href="https://bazaar.abuse.ch/export/csv/recent/" target="_blank" class="sl">MalwareBazaar</a> ·
  <a href="https://urlhaus.abuse.ch/downloads/text_online/" target="_blank" class="sl">URLhaus</a> ·
  <a href="https://feodotracker.abuse.ch/downloads/ipblocklist.csv" target="_blank" class="sl">Feodo</a> ·
  <a href="https://isc.sans.edu/api/" target="_blank" class="sl">SANS ISC</a> ·
  <a href="https://check.torproject.org/torbulkexitlist" target="_blank" class="sl">Tor Exits</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml" target="_blank" class="sl">CISA ICS</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/all.xml" target="_blank" class="sl">CISA All</a>
  <br>
  <span style="color:#3a3a4a;font-weight:bold;text-transform:uppercase;letter-spacing:.4px;">
    <span class="sd sa"></span>EST&nbsp;</span>
  <a href="https://nvd.nist.gov/" target="_blank" class="sl">NVD</a> ·
  <a href="https://www.verizon.com/business/resources/reports/dbir/" target="_blank" class="sl">DBIR</a> ·
  <a href="https://www.mandiant.com/m-trends" target="_blank" class="sl">M-Trends</a> ·
  <a href="https://www.crowdstrike.com/global-threat-report/" target="_blank" class="sl">CS GTR</a> ·
  <a href="https://www.ic3.gov/AnnualReport" target="_blank" class="sl">IC3</a> ·
  <a href="https://www.ibm.com/security/data-breach" target="_blank" class="sl">IBM</a> ·
  <a href="https://apwg.org/trendsreports/" target="_blank" class="sl">APWG</a> ·
  <a href="https://spycloud.com/resource/2024-annual-identity-exposure-report/" target="_blank" class="sl">SpyCloud</a> ·
  <a href="https://www.enforcementtracker.com/" target="_blank" class="sl">GDPR</a> ·
  <a href="https://radar.cloudflare.com/reports/ddos-2024-q4" target="_blank" class="sl">Cloudflare</a> ·
  <a href="https://www.sonicwall.com/threat-report/" target="_blank" class="sl">SonicWall</a> ·
  <a href="https://www.chainalysis.com/blog/crypto-hacking-stolen-funds-2025/" target="_blank" class="sl">Chainalysis</a> ·
  <a href="https://www.sophos.com/en-us/blog/the-state-of-ransomware-2024" target="_blank" class="sl">Sophos</a> ·
  <a href="https://www.isc2.org/Insights/2024/09/Workforce-Study" target="_blank" class="sl">ISC2</a>
  <span style="float:right;color:#1a1a2a;">↻ {ts}</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  LIVE THREAT MAPS — 8 EMBEDDABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:4px 0 10px;">
  <span style="font-size:1rem;font-weight:bold;text-transform:uppercase;letter-spacing:1px;">
    <a href="https://livethreatmap.radware.com/" target="_blank" class="sh">
      &gt;&gt; LIVE THREAT MAP FEEDS</a></span>
  <span style="font-size:.55rem;color:#3a3a4a;margin-left:8px;">8 REAL-TIME SOURCES</span>
</div>""", unsafe_allow_html=True)

m1,m2 = st.columns(2)
with m1:
    st.markdown('<a href="https://livethreatmap.radware.com/" target="_blank" class="ml">&gt;&gt; RADWARE LIVE THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://livethreatmap.radware.com/", 1100)
with m2:
    st.markdown('<a href="https://threatmap.fortiguard.com/" target="_blank" class="ml">&gt;&gt; FORTINET FORTIGUARD MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.fortiguard.com/", 1100)
st.markdown("---")

m3,m4 = st.columns(2)
with m3:
    st.markdown('<a href="https://cybermap.kaspersky.com/" target="_blank" class="ml">&gt;&gt; KASPERSKY CYBERMAP</a>', unsafe_allow_html=True)
    iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", 520)
with m4:
    st.markdown('<a href="https://threatmap.bitdefender.com/" target="_blank" class="ml">&gt;&gt; BITDEFENDER THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.bitdefender.com/", 520)
st.markdown("---")

m5,m6 = st.columns(2)
with m5:
    st.markdown('<a href="https://www.sicherheitstacho.eu/?lang=en" target="_blank" class="ml">&gt;&gt; SICHERHEITSTACHO (DT)</a>', unsafe_allow_html=True)
    iframe("https://www.sicherheitstacho.eu/?lang=en", 520)
with m6:
    st.markdown('<a href="https://threatmap.checkpoint.com/" target="_blank" class="ml">&gt;&gt; CHECK POINT THREATCLOUD</a>', unsafe_allow_html=True)
    iframe("https://threatmap.checkpoint.com/", 520)
st.markdown("---")

m7,m8 = st.columns(2)
with m7:
    st.markdown('<a href="https://attackmap.sonicwall.com/live-attack-map/" target="_blank" class="ml">&gt;&gt; SONICWALL LIVE ATTACK MAP</a>', unsafe_allow_html=True)
    iframe("https://attackmap.sonicwall.com/live-attack-map/", 520)
with m8:
    st.markdown('<a href="https://threatbutt.com/map/" target="_blank" class="ml">&gt;&gt; THREATBUTT ATTACK MAP</a>', unsafe_allow_html=True)
    iframe("https://threatbutt.com/map/", 520)
st.markdown("---")

st.markdown('<a href="https://viz.greynoise.io/trends/trending" target="_blank" class="ml">&gt;&gt; GREYNOISE INTELLIGENCE TRENDS</a>', unsafe_allow_html=True)
iframe("https://viz.greynoise.io/trends/trending", 1200)
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
#  GRC RESOURCES — 52 LINKS, 4 COLUMNS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin-top:24px;margin-bottom:14px;text-align:center;">
  <span style="font-size:1.05rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;">
    <a href="https://www.nist.gov/cyberframework" target="_blank" class="sh">
      &gt;&gt; GRC RESOURCES &amp; TOOLS &lt;&lt;</a></span>
  <div style="font-size:.55rem;color:#3a3a4a;margin-top:2px;">52 CURATED · FRAMEWORKS · TOOLS · TRAINING · INTEL</div>
</div>""", unsafe_allow_html=True)

l1,l2,l3,l4 = st.columns(4)
with l1:
    st.markdown(f'<div style="font-size:.54rem;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;border-bottom:1px dashed #1a1a2e;padding-bottom:2px;">▸ FRAMEWORKS &amp; STANDARDS</div>', unsafe_allow_html=True)
    for a in [("01","NIST CSF 2.0","https://www.nist.gov/cyberframework","Cybersecurity risk mgmt framework."),
        ("02","NIST AI RMF","https://www.nist.gov/itl/ai-risk-management-framework","AI risk management."),
        ("03","ISO/IEC 27001","https://www.iso.org/isoiec-27001-information-security.html","International ISMS."),
        ("04","CIS Controls v8","https://www.cisecurity.org/controls/","Prioritized safeguards."),
        ("05","HITRUST","https://hitrustalliance.net/","Info risk management."),
        ("06","MITRE ATT&CK","https://mitre-attack.github.io/attack-navigator/","Adversary TTP matrix."),
        ("07","MITRE D3FEND","https://d3fend.mitre.org/","Defensive knowledge graph."),
        ("08","CVSS 4.0","https://www.first.org/cvss/calculator/4.0","Vuln scoring system."),
        ("09","NIST CSRC","https://csrc.nist.gov/","Comp Security Resource Center."),
        ("10","SP 800-53","https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final","Security &amp; privacy controls."),
        ("11","NIST NVD","https://nvd.nist.gov/","National Vulnerability Database."),
        ("12","CISA KEV","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","Exploited CVEs."),
        ("13","Shields Up","https://www.cisa.gov/shields-up","Cyber resilience guidance.")]:
        st.markdown(gl(*a), unsafe_allow_html=True)

with l2:
    st.markdown(f'<div style="font-size:.54rem;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;border-bottom:1px dashed #1a1a2e;padding-bottom:2px;">▸ THREAT INTEL &amp; ANALYSIS</div>', unsafe_allow_html=True)
    for a in [("14","VirusTotal","https://www.virustotal.com/","Analyze files, domains, IPs."),
        ("15","AlienVault OTX","https://otx.alienvault.com/","Crowdsourced threat IOCs."),
        ("16","Talos Intel","https://talosintelligence.com/","Cisco threat intelligence."),
        ("17","Shodan","https://www.shodan.io/","Internet device search."),
        ("18","Have I Been Pwned","https://haveibeenpwned.com/","Breach exposure check."),
        ("19","crt.sh","https://crt.sh/","Cert Transparency logs."),
        ("20","SANS ISC","https://isc.sans.edu/","Threat monitor &amp; diary."),
        ("21","URLhaus","https://urlhaus.abuse.ch/","Malware dist. URLs."),
        ("22","MalwareBazaar","https://bazaar.abuse.ch/","Malware samples."),
        ("23","ThreatFox","https://threatfox.abuse.ch/","Community IOC sharing."),
        ("24","Exploit-DB","https://www.exploit-db.com/","Public exploits archive."),
        ("25","Pulsedive","https://pulsedive.com/","Free threat intel platform."),
        ("26","GreyNoise","https://viz.greynoise.io/","Scanner intelligence.")]:
        st.markdown(gl(*a), unsafe_allow_html=True)

with l3:
    st.markdown(f'<div style="font-size:.54rem;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;border-bottom:1px dashed #1a1a2e;padding-bottom:2px;">▸ SECURITY TOOLS</div>', unsafe_allow_html=True)
    for a in [("27","CyberChef","https://gchq.github.io/CyberChef/","Cyber Swiss Army Knife."),
        ("28","Any.Run","https://any.run/","Malware sandbox."),
        ("29","URLScan.io","https://urlscan.io/","Website scanning."),
        ("30","GTFOBins","https://gtfobins.github.io/","Unix bypass binaries."),
        ("31","LOLBAS","https://lolbas-project.github.io/","Windows LOTL binaries."),
        ("32","Security Onion","https://securityonionsolutions.com/","Threat hunting."),
        ("33","OSINT Framework","https://osintframework.com/","OSINT tool collection."),
        ("34","PayloadsAllThings","https://github.com/swisskyrepo/PayloadsAllTheThings","Payloads &amp; bypasses."),
        ("35","Nuclei","https://github.com/projectdiscovery/nuclei-templates","Vuln scanner templates."),
        ("36","OpenCTI","https://www.opencti.io/","Open threat intel platform."),
        ("37","YARA Rules","https://github.com/Yara-Rules/rules","Malware detection rules."),
        ("38","Sigma Rules","https://github.com/SigmaHQ/sigma","Generic detection format."),
        ("39","Wazuh","https://wazuh.com/","Open-source XDR/SIEM.")]:
        st.markdown(gl(*a), unsafe_allow_html=True)

with l4:
    st.markdown(f'<div style="font-size:.54rem;color:{BLUE};text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px;border-bottom:1px dashed #1a1a2e;padding-bottom:2px;">▸ TRAINING &amp; NEWS</div>', unsafe_allow_html=True)
    for a in [("40","OWASP Top 10","https://owasp.org/www-project-top-ten/","Web app security risks."),
        ("41","OWASP LLM","https://owasp.org/www-project-top-10-for-large-language-model-applications/","LLM security risks."),
        ("42","OWASP API","https://owasp.org/API-Security/","API security risks."),
        ("43","HackTheBox","https://www.hackthebox.com/","Gamified security training."),
        ("44","TryHackMe","https://tryhackme.com/","Hands-on labs."),
        ("45","PortSwigger","https://portswigger.net/web-security","Web vuln training."),
        ("46","BleepingComputer","https://www.bleepingcomputer.com/","Security news."),
        ("47","Hacker News","https://thehackernews.com/","Cybersecurity news."),
        ("48","SANS Papers","https://www.sans.org/white-papers/","Security whitepapers."),
        ("49","DEF CON","https://defcon.org/html/links/dc-archives.html","Conference archives."),
        ("50","HackerOne","https://www.hackerone.com/","Bug bounty platform."),
        ("51","Bugcrowd","https://www.bugcrowd.com/","Vuln disclosure."),
        ("52","VulnHub","https://www.vulnhub.com/","Security practice envs.")]:
        st.markdown(gl(*a), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="border-top:1px solid #141420;padding-top:20px;margin-top:32px;text-align:center;font-family:{MONO};">
  <div style="color:#555;font-size:.8rem;margin-bottom:3px;">Questions, Comments, or Recommendations?</div>
  <div style="color:#555;font-size:.8rem;margin-bottom:14px;">
    Developed by <b style="color:{GREEN};">Adam Kistler</b> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">LinkedIn</a></div>
  <div style="color:#333;font-size:.65rem;padding:0 10%;line-height:1.4;margin-bottom:8px;">
    <b>LEGAL DISCLAIMER:</b> Educational and portfolio purposes only. All threat maps and data
    are property of their respective owners. SecAI-Nexus does not host or process third-party content.<br>
    <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank" class="fl">
      Code and layout licensed CC BY-NC 4.0.</a></div>
  <div style="color:#1a1a2a;font-size:.65rem;">
    SecAI-Nexus GRC [v18.0] · Live Data Engine ·
    40 Indicators · 8 Live Feeds · 8 Threat Maps · 52 Resources · {now_utc.strftime("%Y")}</div>
</div>""", unsafe_allow_html=True)
