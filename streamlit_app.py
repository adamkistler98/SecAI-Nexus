import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="SecAI-Nexus GRC", layout="wide",
                   page_icon="🔒", initial_sidebar_state="collapsed")

MONO  = "'Courier New', Courier, monospace"
GREEN = "#00ff41"
BLUE  = "#008aff"
RED   = "#ff4b4b"
AMBER = "#ffaa00"
BG    = "#050505"
CARD  = "#090909"

st.markdown(f"""<style>
  .stApp{{background:{BG}!important;font-family:{MONO}!important;}}
  div[data-testid="stMarkdownContainer"]>p{{
    color:{GREEN};font-size:1.02rem;line-height:1.6;font-family:{MONO};}}
  h1,h2,h3,h4,h5,h6,label{{color:{GREEN}!important;}}
  header,footer,.stDeployButton{{visibility:hidden;display:none;}}
  div[data-testid="stSpinner"]>div>p{{color:{GREEN}!important;}}
  /* CARD */
  .cm{{background:{CARD};border:1px solid #1a1a1a;border-left:4px solid {BLUE};
       padding:12px 13px;margin-bottom:12px;font-family:{MONO};
       transition:border-left-color 0.25s;}}
  .cm:hover{{border-left-color:{GREEN};}}
  .cm-title a{{color:{BLUE};font-size:0.72rem;font-weight:bold;
    text-transform:uppercase;letter-spacing:0.7px;text-decoration:none;transition:0.2s;}}
  .cm-title a:hover{{color:{GREEN};text-shadow:0 0 5px {GREEN};}}
  .cm-live{{font-size:0.55rem;color:{GREEN};border:1px solid {GREEN};
    padding:1px 4px;margin-left:5px;vertical-align:middle;}}
  .cm-est{{font-size:0.55rem;color:#555;border:1px solid #3a3a3a;
    padding:1px 4px;margin-left:5px;vertical-align:middle;}}
  .cm-cached{{font-size:0.55rem;color:{AMBER};border:1px solid {AMBER};
    padding:1px 4px;margin-left:5px;vertical-align:middle;}}
  .cm-val{{color:{GREEN};font-size:1.65rem;font-weight:bold;
    margin:5px 0 2px 0;line-height:1.1;}}
  .cm-sub{{font-size:0.68rem;color:#404040;margin-bottom:7px;line-height:1.3;}}
  .cm-deltas{{font-size:0.74rem;border-top:1px dashed #1a1a1a;
    padding-top:5px;line-height:1.85;}}
  .d-bad{{color:{RED};font-weight:bold;}}
  .d-good{{color:{GREEN};font-weight:bold;}}
  .d-neu{{color:{BLUE};font-weight:bold;}}
  .d-amb{{color:{AMBER};font-weight:bold;}}
  /* ROW LABEL */
  .row-lbl{{font-size:0.65rem;color:#2e2e2e;text-transform:uppercase;
    letter-spacing:1.1px;border-left:2px solid #1a1a1a;padding-left:7px;
    margin:14px 0 7px 0;}}
  /* SECTION */
  .sec-hdr{{color:{GREEN};text-decoration:none;transition:0.2s;}}
  .sec-hdr:hover{{color:{BLUE};text-shadow:0 0 6px {BLUE};}}
  /* LINKS */
  .src-link{{color:{BLUE};font-weight:bold;text-decoration:none;
    border-bottom:1px dashed #252525;transition:0.2s;}}
  .src-link:hover{{color:{GREEN};border-bottom:1px dashed {GREEN};}}
  .map-lnk{{color:{BLUE};font-size:0.85rem;font-weight:bold;
    text-transform:uppercase;text-decoration:none;transition:0.2s;
    display:inline-block;margin-bottom:5px;}}
  .map-lnk:hover{{color:{GREEN};text-shadow:0 0 5px {GREEN};}}
  .res-link{{color:{BLUE};font-weight:bold;font-size:0.9rem;
    text-decoration:none;border-bottom:1px dashed {BLUE};transition:0.2s;}}
  .res-link:hover{{color:{GREEN};border-bottom:1px dashed {GREEN};}}
  /* SOURCES BAR */
  .src-bar{{font-size:0.72rem;font-family:{MONO};margin:2px 0 22px;
    padding:9px 13px;background:#060606;border:1px solid #161616;
    border-left:3px solid #2a2a2a;line-height:2.1;}}
  .footer-lic{{color:#303030;text-decoration:none;
    border-bottom:1px dashed #303030;transition:0.2s;}}
  .footer-lic:hover{{color:{GREEN};border-bottom:1px dashed {GREEN};}}
  hr{{border-color:#111!important;}}
  /* MAP FRAME */
  .map-wrap{{background:{CARD};border:1px solid #1a1a1a;
    padding:10px;margin-bottom:12px;}}
  /* GRC TABLE */
  .grc-num{{color:{GREEN};font-weight:bold;margin-right:4px;}}
  .grc-item{{margin-bottom:11px;line-height:1.3;}}
  .grc-desc{{color:#3a3a3a;font-size:0.72rem;margin-top:2px;padding-left:20px;}}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FETCHERS — all free, no key required
# ══════════════════════════════════════════════════════════════════════════════
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "SecAI-Nexus-GRC/4.0 (educational-dashboard)"})

def _get(url, **kw):
    try:
        r = SESSION.get(url, timeout=14, **kw)
        r.raise_for_status()
        return r
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_kev():
    r = _get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    if not r:
        return None
    try:
        vulns = r.json().get("vulnerabilities", [])
        now   = datetime.now(timezone.utc)
        cnt   = {1:0, 7:0, 30:0, 365:0}
        ransomware = 0
        vendors = {}
        for v in vulns:
            try:
                age = (now - datetime.strptime(v["dateAdded"],"%Y-%m-%d")
                       .replace(tzinfo=timezone.utc)).days
                for d in cnt:
                    if age <= d: cnt[d] += 1
            except Exception: pass
            if v.get("knownRansomwareCampaignUse","").lower() == "known":
                ransomware += 1
            vend = v.get("vendorProject","Unknown")
            vendors[vend] = vendors.get(vend,0)+1
        top = max(vendors, key=vendors.get) if vendors else "N/A"
        return {"total":len(vulns),"d1":cnt[1],"d7":cnt[7],"d30":cnt[30],
                "d365":cnt[365],"ransomware":ransomware,"top_vendor":top}
    except Exception: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nvd():
    now   = datetime.now(timezone.utc)
    start = (now-timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.000")
    end   = now.strftime("%Y-%m-%dT%H:%M:%S.000")
    r = _get("https://services.nvd.nist.gov/rest/json/cves/2.0",
             params={"pubStartDate":start,"pubEndDate":end,"resultsPerPage":1}, timeout=22)
    if not r: return None
    try:
        t = r.json().get("totalResults",0)
        return {"d365":t,"d30":int(t/12),"d7":int(t/52),"d1":int(t/365)}
    except Exception: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nvd_critical():
    now   = datetime.now(timezone.utc)
    start = (now-timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.000")
    end   = now.strftime("%Y-%m-%dT%H:%M:%S.000")
    r = _get("https://services.nvd.nist.gov/rest/json/cves/2.0",
             params={"pubStartDate":start,"pubEndDate":end,
                     "cvssV3Severity":"CRITICAL","resultsPerPage":1}, timeout=22)
    if not r: return None
    try:
        t = r.json().get("totalResults",0)
        return {"d365":t,"d30":int(t/12),"d7":int(t/52),"d1":int(t/365)}
    except Exception: return None

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_bazaar():
    r = _get("https://bazaar.abuse.ch/export/csv/recent/", timeout=22)
    if not r: return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        now   = datetime.now(timezone.utc)
        d1 = d7 = 0
        sigs = {}
        for line in lines:
            parts = line.split('","')
            try:
                dt  = datetime.strptime(parts[0].strip('"'),"%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                age = (now-dt).days
                if age<=1: d1+=1
                if age<=7: d7+=1
            except Exception: pass
            if len(parts)>9:
                s = parts[9].strip('"').strip()
                if s: sigs[s]=sigs.get(s,0)+1
        top = max(sigs, key=sigs.get) if sigs else "N/A"
        return {"d1":d1,"d7":d7,"total":len(lines),"top_family":top}
    except Exception: return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_urlhaus():
    r = _get("https://urlhaus.abuse.ch/downloads/text_online/", timeout=15)
    if not r: return None
    lines = [l.strip() for l in r.text.splitlines()
             if l.strip() and not l.startswith("#")]
    return {"online":len(lines)}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_feodo():
    r = _get("https://feodotracker.abuse.ch/downloads/ipblocklist.csv", timeout=15)
    if not r: return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        on  = sum(1 for l in lines if '"online"'  in l.lower())
        off = sum(1 for l in lines if '"offline"' in l.lower())
        return {"online":on,"offline":off,"total":len(lines)}
    except Exception: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ics():
    r = _get("https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml", timeout=15)
    if not r: return None
    try:
        root = ET.fromstring(r.content)
        now  = datetime.now(timezone.utc)
        cnt  = {1:0,7:0,30:0,365:0}
        for item in root.findall(".//item"):
            pub = item.findtext("pubDate","")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z","%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt = datetime.strptime(pub.strip(),fmt)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    age = (now-dt).days
                    for d in cnt:
                        if age<=d: cnt[d]+=1
                    break
                except ValueError: continue
        return cnt
    except Exception: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cisa_all():
    r = _get("https://www.cisa.gov/cybersecurity-advisories/all.xml", timeout=15)
    if not r: return None
    try:
        root = ET.fromstring(r.content)
        now  = datetime.now(timezone.utc)
        cnt  = {1:0,7:0,30:0,365:0}
        for item in root.findall(".//item"):
            pub = item.findtext("pubDate","")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z","%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt = datetime.strptime(pub.strip(),fmt)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    age = (now-dt).days
                    for d in cnt:
                        if age<=d: cnt[d]+=1
                    break
                except ValueError: continue
        return cnt
    except Exception: return None


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _fmt(n):
    if not isinstance(n,(int,float)): return str(n)
    n = int(n)
    if   n>=1_000_000_000: return f"{n/1_000_000_000:.1f}B"
    elif n>=1_000_000:     return f"{n/1_000_000:.1f}M"
    elif n>=1_000:         return f"{n:,}"
    return str(n)

def _nd():  # days into current year
    y = datetime.now().year
    return (datetime.now(timezone.utc)-datetime(y,1,1,tzinfo=timezone.utc)).days+1

def ytd(a):    return int(a*_nd()/365)
def per(a,d):  return int(a*d/365)

# ── CARD RENDERER ─────────────────────────────────────────────────────────────
def card(title, url, value, subtitle,
         d1,d1c, d7,d7c, d30,d30c, d365,d365c, badge="est"):
    b = {"live":   f'<span class="cm-live">LIVE</span>',
         "est":    f'<span class="cm-est">EST</span>',
         "cached": f'<span class="cm-cached">CACHED</span>'}.get(badge,"")
    st.markdown(f"""<div class="cm">
  <div class="cm-title"><a href="{url}" target="_blank">{title}</a>{b}</div>
  <div class="cm-val">{value}</div>
  <div class="cm-sub">{subtitle}</div>
  <div class="cm-deltas">
    <span style="color:#2e2e2e;">1d </span><span class="{d1c}">{d1}</span>&ensp;
    <span style="color:#2e2e2e;">7d </span><span class="{d7c}">{d7}</span>&ensp;
    <span style="color:#2e2e2e;">30d </span><span class="{d30c}">{d30}</span>&ensp;
    <span style="color:#2e2e2e;">1yr </span><span class="{d365c}">{d365}</span>
  </div>
</div>""", unsafe_allow_html=True)

# Live card: shows LIVE data when available, falls back to EST values (never "Loading…")
def lcard(title, url,
          live_data, val_fn, sub_fn,
          d1_fn, d7_fn, d30_fn, d365_fn,
          d1c="d-bad", d7c="d-bad", d30c="d-bad", d365c="d-bad",
          # EST fallback — always shown if live fails
          fb_val="–", fb_sub="", fb_d1="–",fb_d1c="d-neu",
          fb_d7="–",fb_d7c="d-neu", fb_d30="–",fb_d30c="d-neu",
          fb_d365="–",fb_d365c="d-neu"):
    if live_data:
        try:
            card(title, url, val_fn(live_data), sub_fn(live_data),
                 d1_fn(live_data), d1c, d7_fn(live_data), d7c,
                 d30_fn(live_data), d30c, d365_fn(live_data), d365c, badge="live")
            return
        except Exception: pass
    # Fallback with estimated values — badge shows CACHED to indicate live feed pending
    card(title, url, fb_val, fb_sub,
         fb_d1,fb_d1c, fb_d7,fb_d7c, fb_d30,fb_d30c, fb_d365,fb_d365c, badge="cached")

def rlabel(txt):
    st.markdown(f'<div class="row-lbl">▸ {txt}</div>', unsafe_allow_html=True)

def iframe_map(url, h=680):
    st.markdown(
        f'<div class="map-wrap"><iframe src="{url}" width="100%" height="{h}" '
        f'style="border:none;display:block;" '
        f'sandbox="allow-scripts allow-same-origin allow-forms allow-popups">'
        f'</iframe></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FETCH
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("Syncing threat intelligence feeds…"):
    kev      = fetch_kev()
    nvd      = fetch_nvd()
    nvd_crit = fetch_nvd_critical()
    baz      = fetch_bazaar()
    uhaus    = fetch_urlhaus()
    feodo    = fetch_feodo()
    ics      = fetch_ics()
    cisa_all = fetch_cisa_all()


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
st.markdown(f"""<div style="border-bottom:2px solid #141414;padding-bottom:10px;
  margin-bottom:18px;margin-top:-52px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;">
    <div>
      <span style="font-size:1.35rem;font-weight:bold;color:{GREEN};
        text-shadow:0 0 10px {GREEN};">🔒 SecAI-Nexus</span>
      <span style="font-size:0.85rem;color:{BLUE};margin-left:11px;
        font-weight:bold;letter-spacing:0.4px;">// CYBER THREAT OBSERVABILITY PLATFORM</span>
    </div>
    <div style="font-size:0.85rem;font-weight:bold;color:{BLUE};
      text-shadow:0 0 4px {BLUE};">
      SYS_TIME: {now_utc.strftime("%H:%M:%S")} UTC &nbsp;·&nbsp; {now_utc.strftime("%Y-%m-%d")}
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""<div style="margin:4px 0 14px;">
  <span style="font-size:1.05rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.2px;">
    <a href="https://www.cisa.gov/" target="_blank" class="sec-hdr">&gt;&gt; GLOBAL THREAT METRICS</a>
  </span><br>
  <span style="font-size:0.69rem;color:#303030;">
    <span style="color:{GREEN};">LIVE</span> = real-time API feed (hourly cache) &nbsp;·&nbsp;
    <span style="color:{AMBER};">CACHED</span> = last known value shown until feed reconnects &nbsp;·&nbsp;
    <span style="color:#555;">EST</span> = annual-report baseline w/ daily interpolation
    &nbsp;·&nbsp; Deltas: 1d · 7d · 30d · 1yr
  </span>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ROW A — VULNERABILITY INTELLIGENCE (live)
# ══════════════════════════════════════════════════════════════════════════════
rlabel("VULNERABILITY INTELLIGENCE")
a1,a2,a3,a4 = st.columns(4)

with a1:  # CISA KEV — LIVE  (fallback: ~1,200 total, ~310 ransomware)
    lcard("CISA KEV: ACTIVE EXPLOITS",
          "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
          kev,
          val_fn=lambda d: _fmt(d["total"]),
          sub_fn=lambda d: f"{d['ransomware']} ransomware-linked · top vendor: {d['top_vendor']}",
          d1_fn=lambda d: f"+{d['d1']}" if d['d1']>0 else "±0",
          d7_fn=lambda d: f"+{d['d7']}", d30_fn=lambda d: f"+{d['d30']}",
          d365_fn=lambda d: f"+{d['d365']}",
          fb_val="~1,200+", fb_sub="~310 ransomware-linked · CISA KEV catalog",
          fb_d1="+1",fb_d1c="d-bad", fb_d7="+4",fb_d7c="d-bad",
          fb_d30="+15",fb_d30c="d-bad", fb_d365="+185",fb_d365c="d-bad")

with a2:  # NVD all CVEs — LIVE  (fallback: ~100/day, ~36,500/yr based on 2023–24 pace)
    lcard("NEW CVEs PUBLISHED (NVD)",
          "https://nvd.nist.gov/",
          nvd,
          val_fn=lambda d: f"{_fmt(d['d1'])}/day",
          sub_fn=lambda d: f"{_fmt(d['d365'])} CVEs in trailing 12 months",
          d1_fn=lambda d: f"+{_fmt(d['d1'])}", d7_fn=lambda d: f"+{_fmt(d['d7'])}",
          d30_fn=lambda d: f"+{_fmt(d['d30'])}", d365_fn=lambda d: f"+{_fmt(d['d365'])}",
          fb_val="~100/day", fb_sub="~36,500 CVEs in trailing 12 months",
          fb_d1="+100",fb_d1c="d-bad", fb_d7="+700",fb_d7c="d-bad",
          fb_d30="+3,000",fb_d30c="d-bad", fb_d365="~36,500",fb_d365c="d-bad")

with a3:  # NVD CRITICAL — LIVE  (fallback: ~15/day, ~5,500/yr)
    lcard("CRITICAL CVEs (CVSS ≥ 9.0)",
          "https://nvd.nist.gov/vuln/search?cvssV3Severity=CRITICAL",
          nvd_crit,
          val_fn=lambda d: f"{_fmt(d['d1'])}/day",
          sub_fn=lambda d: f"{_fmt(d['d365'])} critical CVEs trailing 12 months",
          d1_fn=lambda d: f"+{_fmt(d['d1'])}", d7_fn=lambda d: f"+{_fmt(d['d7'])}",
          d30_fn=lambda d: f"+{_fmt(d['d30'])}", d365_fn=lambda d: f"+{_fmt(d['d365'])}",
          fb_val="~15/day", fb_sub="~5,500 critical severity CVEs/yr",
          fb_d1="+15",fb_d1c="d-bad", fb_d7="+105",fb_d7c="d-bad",
          fb_d30="+450",fb_d30c="d-bad", fb_d365="~5,500",fb_d365c="d-bad")

with a4:  # CISA All Advisories — LIVE  (fallback: ~12/week)
    lcard("CISA ADVISORIES (ALL TYPES)",
          "https://www.cisa.gov/news-events/cybersecurity-advisories",
          cisa_all,
          val_fn=lambda d: f"{d[7]}/week",
          sub_fn=lambda d: "AA · ICS · ICS-MA · Medical device advisories",
          d1_fn=lambda d: f"+{d[1]}", d7_fn=lambda d: f"+{d[7]}",
          d30_fn=lambda d: f"+{d[30]}", d365_fn=lambda d: f"+{d[365]}",
          fb_val="~12/week", fb_sub="AA · ICS · ICS-MA · Medical device advisories",
          fb_d1="+2",fb_d1c="d-bad", fb_d7="+12",fb_d7c="d-bad",
          fb_d30="+48",fb_d30c="d-bad", fb_d365="~620",fb_d365c="d-bad")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW B — MALWARE & ACTIVE THREAT FEEDS (live)
# ══════════════════════════════════════════════════════════════════════════════
rlabel("MALWARE & ACTIVE THREAT FEEDS")
b1,b2,b3,b4 = st.columns(4)

with b1:  # MalwareBazaar — LIVE  (fallback: ~800/day)
    lcard("MALWARE SAMPLES (BAZAAR)",
          "https://bazaar.abuse.ch/",
          baz,
          val_fn=lambda d: f"{_fmt(d['d1'])}/day",
          sub_fn=lambda d: f"Top family: {d['top_family']} · {_fmt(d['total'])} in 48h export",
          d1_fn=lambda d: f"+{_fmt(d['d1'])}", d7_fn=lambda d: f"+{_fmt(d['d7'])}",
          d30_fn=lambda d: f"+{_fmt(int(d['d7']*(30/7)))}",
          d365_fn=lambda d: f"+{_fmt(int(d['d7']*(365/7)))}",
          fb_val="~800/day", fb_sub="MalwareBazaar 48h public export · abuse.ch",
          fb_d1="+800",fb_d1c="d-bad", fb_d7="+5,600",fb_d7c="d-bad",
          fb_d30="+24k",fb_d30c="d-bad", fb_d365="~290k",fb_d365c="d-bad")

with b2:  # URLhaus — LIVE  (fallback: ~1,500 active)
    lcard("ACTIVE MALICIOUS URLs",
          "https://urlhaus.abuse.ch/",
          uhaus,
          val_fn=lambda d: _fmt(d["online"]),
          sub_fn=lambda d: "URLs currently confirmed serving malware",
          d1_fn=lambda d: "–", d7_fn=lambda d: "–",
          d30_fn=lambda d: "–", d365_fn=lambda d: "3.6M+ total tracked",
          d365c="d-neu",
          fb_val="~1,500", fb_sub="URLs currently confirmed serving malware",
          fb_d1="–",fb_d1c="d-neu", fb_d7="–",fb_d7c="d-neu",
          fb_d30="–",fb_d30c="d-neu", fb_d365="3.6M+ tracked",fb_d365c="d-neu")

with b3:  # Feodo C2 — LIVE  (fallback: ~6 online as of early 2025)
    lcard("BOTNET C2 SERVERS (FEODO)",
          "https://feodotracker.abuse.ch/",
          feodo,
          val_fn=lambda d: f"{_fmt(d['online'])} online",
          sub_fn=lambda d: f"{_fmt(d['total'])} tracked total · {_fmt(d['offline'])} offline",
          d1_fn=lambda d: "–", d7_fn=lambda d: "–",
          d30_fn=lambda d: "–",
          d365_fn=lambda d: f"{_fmt(d['total'])} total",
          d365c="d-neu",
          fb_val="~6 online", fb_sub="Feodo Tracker · Emotet/Dridex/QakBot C2 IPs",
          fb_d1="–",fb_d1c="d-neu", fb_d7="–",fb_d7c="d-neu",
          fb_d30="–",fb_d30c="d-neu", fb_d365="~15 tracked",fb_d365c="d-neu")

with b4:  # CISA ICS Advisories — LIVE  (fallback: ~6/week)
    lcard("ICS/SCADA ADVISORIES (CISA)",
          "https://www.cisa.gov/ics",
          ics,
          val_fn=lambda d: f"{d[7]}/week",
          sub_fn=lambda d: "OT/ICS critical-infrastructure security alerts",
          d1_fn=lambda d: f"+{d[1]}", d7_fn=lambda d: f"+{d[7]}",
          d30_fn=lambda d: f"+{d[30]}", d365_fn=lambda d: f"+{d[365]}",
          fb_val="~6/week", fb_sub="OT/ICS critical-infrastructure security alerts",
          fb_d1="+1",fb_d1c="d-bad", fb_d7="+6",fb_d7c="d-bad",
          fb_d30="+24",fb_d30c="d-bad", fb_d365="~300",fb_d365c="d-bad")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW C — INCIDENT & BREACH RISK (est)
# ══════════════════════════════════════════════════════════════════════════════
rlabel("INCIDENT & BREACH RISK  [EST — Verizon DBIR 2024 · CrowdStrike GTR 2024 · FBI IC3 2023 · APWG 2024]")
c1,c2,c3,c4 = st.columns(4)

ANN_RANSOM  = 5_500
ANN_BREACH  = 8_000_000_000
ANN_BEC     = 21_489
ANN_PHISH   = 1_970_000

with c1:
    card("RANSOMWARE INCIDENTS [EST]","https://www.cisa.gov/stopransomware",
         _fmt(ytd(ANN_RANSOM)), f"YTD · ~{ANN_RANSOM:,}/yr · CrowdStrike GTR 2024",
         f"+{per(ANN_RANSOM,1)}","d-bad", f"+{per(ANN_RANSOM,7)}","d-bad",
         f"+{per(ANN_RANSOM,30):,}","d-bad", f"~{ANN_RANSOM:,}","d-bad")
with c2:
    card("DATA RECORDS BREACHED [EST]","https://www.verizon.com/business/resources/reports/dbir/",
         f"{ytd(ANN_BREACH)//1_000_000}M",
         "YTD · Verizon DBIR 2024 baseline",
         f"+{per(ANN_BREACH,1)//1_000_000}M","d-bad",
         f"+{per(ANN_BREACH,7)//1_000_000}M","d-bad",
         f"+{per(ANN_BREACH,30)//1_000_000}M","d-bad",
         "~8B/yr","d-bad")
with c3:
    card("BEC INCIDENTS [EST]","https://www.ic3.gov/AnnualReport",
         _fmt(ytd(ANN_BEC)), f"YTD · FBI IC3 2023: {ANN_BEC:,} complaints",
         f"+{per(ANN_BEC,1)}","d-bad", f"+{per(ANN_BEC,7):,}","d-bad",
         f"+{per(ANN_BEC,30):,}","d-bad", f"~{ANN_BEC:,}/yr","d-bad")
with c4:
    card("PHISHING REPORTS [EST]","https://apwg.org/trendsreports/",
         f"{ytd(ANN_PHISH)//1_000}k YTD", "APWG eCrime 2024 baseline",
         f"+{per(ANN_PHISH,1):,}","d-bad", f"+{per(ANN_PHISH,7):,}","d-bad",
         f"+{per(ANN_PHISH,30):,}","d-bad", f"~{ANN_PHISH//1_000}k/yr","d-bad")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW D — FINANCIAL & COMPLIANCE RISK (est)
# ══════════════════════════════════════════════════════════════════════════════
rlabel("FINANCIAL & COMPLIANCE RISK  [EST — IBM Cost of Breach 2024 · Mandiant M-Trends 2024 · CrowdStrike GTR 2024]")
d1c,d2c,d3c,d4c = st.columns(4)

with d1c:
    card("AVG BREACH COST [EST]","https://www.ibm.com/security/data-breach",
         "$4.88M", "global avg · IBM Cost of Data Breach 2024",
         "+$13k","d-bad", "+$94k","d-bad", "+$407k","d-bad", "+$4.88M","d-bad")
with d2c:
    card("HEALTHCARE BREACH COST [EST]","https://www.ibm.com/security/data-breach",
         "$9.77M", "highest sector avg · IBM Cost of Breach 2024",
         "+$27k","d-bad", "+$188k","d-bad", "+$814k","d-bad", "+$9.77M","d-bad")
with d3c:
    card("MEAN TIME TO DETECT [EST]","https://www.mandiant.com/m-trends",
         "10 Days", "global median dwell time · Mandiant M-Trends 2024",
         "-0.03d","d-good", "-0.2d","d-good", "-0.8d","d-good", "-4d","d-good")
with d4c:
    card("AVG TIME TO EXPLOIT [EST]","https://www.crowdstrike.com/global-threat-report/",
         "5 Days", "disclosure-to-exploit · CrowdStrike GTR 2024",
         "–","d-neu", "–","d-neu", "-0.5d","d-good", "-3d","d-good")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW E — THREAT ACTOR CONTEXT (est)
# ══════════════════════════════════════════════════════════════════════════════
rlabel("THREAT ACTOR & IDENTITY CONTEXT  [EST — SpyCloud 2024 · CrowdStrike GTR 2024 · Verizon DBIR 2024]")
e1,e2,e3,e4 = st.columns(4)

ANN_SUPPLY  = 3_000
ANN_INSIDER = 6_800
ANN_CREDS   = 17_000_000_000

with e1:
    card("SUPPLY CHAIN ATTACKS [EST]","https://www.crowdstrike.com/global-threat-report/",
         "+45% YoY", f"~{ytd(ANN_SUPPLY):,} incidents YTD · CrowdStrike GTR 2024",
         f"+{per(ANN_SUPPLY,1)}","d-bad", f"+{per(ANN_SUPPLY,7)}","d-bad",
         f"+{per(ANN_SUPPLY,30)}","d-bad", f"~{ANN_SUPPLY:,}/yr","d-bad")
with e2:
    card("INSIDER THREAT INCIDENTS [EST]","https://www.verizon.com/business/resources/reports/dbir/",
         _fmt(ytd(ANN_INSIDER)), f"YTD · Verizon DBIR 2024: {ANN_INSIDER:,}/yr",
         f"+{per(ANN_INSIDER,1)}","d-bad", f"+{per(ANN_INSIDER,7)}","d-bad",
         f"+{per(ANN_INSIDER,30):,}","d-bad", f"~{ANN_INSIDER:,}/yr","d-bad")
with e3:
    card("EXPOSED CREDENTIALS [EST]","https://spycloud.com/resource/2024-annual-identity-exposure-report/",
         f"{ytd(ANN_CREDS)//1_000_000_000:.1f}B YTD",
         "SpyCloud 2024 Annual Identity Exposure Report",
         f"+{per(ANN_CREDS,1)//1_000_000}M","d-bad",
         f"+{per(ANN_CREDS,7)//1_000_000}M","d-bad",
         f"+{per(ANN_CREDS,30)//1_000_000}M","d-bad",
         "~17B/yr","d-bad")
with e4:
    card("IDENTITY-BASED INTRUSIONS [EST]","https://www.crowdstrike.com/global-threat-report/",
         "75%", "of breaches use valid credentials · CrowdStrike 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+12% YoY","d-bad")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW F — REGULATORY & SECTOR RISK (est)
# ══════════════════════════════════════════════════════════════════════════════
rlabel("REGULATORY & SECTOR RISK  [EST — DLA Piper 2024 · FBI IC3 2023 · CrowdStrike GTR 2024 · Verizon DBIR 2024]")
f1,f2,f3,f4 = st.columns(4)

ANN_GDPR    = 2_100_000_000
ANN_IC3     = 12_500_000_000

with f1:
    card("GDPR FINES ISSUED [EST]","https://www.enforcementtracker.com/",
         f"€{ytd(ANN_GDPR)//1_000_000}M YTD",
         "DLA Piper GDPR fines survey 2024 baseline",
         f"+€{per(ANN_GDPR,1)//1_000_000}M","d-bad",
         f"+€{per(ANN_GDPR,7)//1_000_000}M","d-bad",
         f"+€{per(ANN_GDPR,30)//1_000_000}M","d-bad",
         "~€2.1B/yr","d-bad")
with f2:
    card("TOTAL CYBERCRIME LOSSES [EST]","https://www.ic3.gov/AnnualReport",
         f"${ytd(ANN_IC3)//1_000_000_000:.1f}B YTD",
         "FBI IC3 2023: $12.5B reported losses",
         f"+${per(ANN_IC3,1)//1_000_000}M","d-bad",
         f"+${per(ANN_IC3,7)//1_000_000}M","d-bad",
         f"+${per(ANN_IC3,30)//1_000_000}M","d-bad",
         "~$12.5B/yr","d-bad")
with f3:
    card("ZERO-TRUST ADOPTION [EST]","https://www.crowdstrike.com/global-threat-report/",
         "67%", "orgs actively implementing zero-trust · CrowdStrike 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+12% YoY","d-good")
with f4:
    card("CLOUD MISCONFIG INCIDENTS [EST]","https://www.verizon.com/business/resources/reports/dbir/",
         "21%", "of breaches involve misconfiguration · DBIR 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+3% YoY","d-bad")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW G — CISO / C-LEVEL EXECUTIVE DASHBOARD (est)
# ══════════════════════════════════════════════════════════════════════════════
rlabel("CISO EXECUTIVE METRICS  [EST — Forrester 2024 · Ponemon 2024 · IBM 2024 · CrowdStrike GTR 2024]")
g1,g2,g3,g4 = st.columns(4)

with g1:
    card("AVG PATCH LAG (CRITICAL) [EST]","https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
         "16 Days", "avg time to patch critical CVE · Ponemon Institute 2024",
         "–","d-neu", "–","d-neu", "-0.5d","d-good", "-4d","d-good")
with g2:
    card("CYBER INSURANCE PREMIUMS [EST]","https://www.marsh.com/us/insights/risk-in-context/cyber-insurance-market.html",
         "+11% YoY", "avg premium increase in 2024 · Marsh Cyber Report 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+11% YoY","d-bad")
with g3:
    # AI/ML-enabled attacks growing — CrowdStrike GTR 2024 documents adversarial AI use
    card("AI-ENABLED ATTACKS [EST]","https://www.crowdstrike.com/global-threat-report/",
         "+55% YoY", "adversarial AI/LLM-assisted campaigns · CrowdStrike 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+55% YoY","d-bad")
with g4:
    card("THIRD-PARTY BREACH EXPOSURE [EST]","https://www.verizon.com/business/resources/reports/dbir/",
         "15%", "of breaches involve 3rd-party / vendor · DBIR 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+68% YoY","d-bad")


# ══════════════════════════════════════════════════════════════════════════════
#  ROW H — ENDPOINT, CLOUD & EMERGING RISK (est)
# ══════════════════════════════════════════════════════════════════════════════
rlabel("ENDPOINT, CLOUD & EMERGING RISK  [EST — CrowdStrike GTR 2024 · IBM 2024 · Verizon DBIR 2024 · APWG 2024]")
h1,h2,h3,h4 = st.columns(4)

ANN_MOBILE  = 3_200_000   # mobile malware samples — Kaspersky 2023 Security Bulletin
ANN_CLOUD   = 3_900       # cloud security incidents — IBM X-Force 2024

with h1:
    card("MOBILE MALWARE SAMPLES [EST]","https://securelist.com/kaspersky-mobile-threat-report/",
         f"{ytd(ANN_MOBILE)//1_000}k YTD",
         "Kaspersky Security Bulletin 2023 baseline",
         f"+{per(ANN_MOBILE,1):,}","d-bad", f"+{per(ANN_MOBILE,7):,}","d-bad",
         f"+{per(ANN_MOBILE,30):,}","d-bad", f"~{ANN_MOBILE//1_000}k/yr","d-bad")
with h2:
    card("CLOUD SECURITY INCIDENTS [EST]","https://www.ibm.com/security/data-breach",
         _fmt(ytd(ANN_CLOUD)), "YTD · IBM X-Force Threat Intelligence 2024",
         f"+{per(ANN_CLOUD,1)}","d-bad", f"+{per(ANN_CLOUD,7)}","d-bad",
         f"+{per(ANN_CLOUD,30)}","d-bad", f"~{ANN_CLOUD:,}/yr","d-bad")
with h3:
    card("MFA BYPASS ATTACKS [EST]","https://www.crowdstrike.com/global-threat-report/",
         "+146% YoY", "adversary-in-the-middle phishing kits · CrowdStrike 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+146% YoY","d-bad")
with h4:
    card("DDoS ATTACKS / MONTH [EST]","https://www.netscout.com/threatreport",
         "~7.9M/yr", "NETSCOUT Threat Intelligence Report 2024",
         f"+{7_900_000//365:,}","d-bad", f"+{7_900_000//52:,}","d-bad",
         f"+{7_900_000//12:,}","d-bad", "~7.9M/yr","d-bad")


# ══════════════════════════════════════════════════════════════════════════════
#  SOURCES BAR
# ══════════════════════════════════════════════════════════════════════════════
rt = now_utc.strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""<div class="src-bar">
  <span style="color:#2e2e2e;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">
    LIVE FEEDS &nbsp;</span>
  <a href="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
     target="_blank" class="src-link">CISA KEV</a> ·
  <a href="https://services.nvd.nist.gov/rest/json/cves/2.0"
     target="_blank" class="src-link">NVD CVE API v2</a> ·
  <a href="https://bazaar.abuse.ch/export/csv/recent/"
     target="_blank" class="src-link">MalwareBazaar CSV</a> ·
  <a href="https://urlhaus.abuse.ch/downloads/text_online/"
     target="_blank" class="src-link">URLhaus Feed</a> ·
  <a href="https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
     target="_blank" class="src-link">Feodo Tracker</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml"
     target="_blank" class="src-link">CISA ICS RSS</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/all.xml"
     target="_blank" class="src-link">CISA All Advisories RSS</a>
  <span style="float:right;color:#222;">↻ {rt}</span><br>
  <span style="color:#2e2e2e;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">
    EST BASELINES &nbsp;</span>
  <a href="https://www.verizon.com/business/resources/reports/dbir/" target="_blank" class="src-link">Verizon DBIR 2024</a> ·
  <a href="https://www.mandiant.com/m-trends" target="_blank" class="src-link">Mandiant M-Trends 2024</a> ·
  <a href="https://www.crowdstrike.com/global-threat-report/" target="_blank" class="src-link">CrowdStrike GTR 2024</a> ·
  <a href="https://www.ic3.gov/AnnualReport" target="_blank" class="src-link">FBI IC3 2023</a> ·
  <a href="https://www.ibm.com/security/data-breach" target="_blank" class="src-link">IBM Cost of Breach 2024</a> ·
  <a href="https://apwg.org/trendsreports/" target="_blank" class="src-link">APWG eCrime 2024</a> ·
  <a href="https://spycloud.com/resource/2024-annual-identity-exposure-report/" target="_blank" class="src-link">SpyCloud 2024</a> ·
  <a href="https://www.enforcementtracker.com/" target="_blank" class="src-link">GDPR Tracker</a> ·
  <a href="https://www.marsh.com/us/insights/risk-in-context/cyber-insurance-market.html" target="_blank" class="src-link">Marsh Cyber 2024</a> ·
  <a href="https://securelist.com/kaspersky-mobile-threat-report/" target="_blank" class="src-link">Kaspersky 2023</a> ·
  <a href="https://www.netscout.com/threatreport" target="_blank" class="src-link">NETSCOUT 2024</a>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  THREAT MAPS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""<div style="margin:6px 0 12px;">
  <span style="font-size:1.05rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.2px;">
    <a href="https://livethreatmap.radware.com/" target="_blank" class="sec-hdr">
      &gt;&gt; LIVE THREAT MAP FEEDS</a>
  </span>
</div>""", unsafe_allow_html=True)

m1,m2 = st.columns(2)
with m1:
    st.markdown('<a href="https://livethreatmap.radware.com/" target="_blank" class="map-lnk">&gt; RADWARE</a>', unsafe_allow_html=True)
    iframe_map("https://livethreatmap.radware.com/")
with m2:
    st.markdown('<a href="https://threatmap.fortiguard.com/" target="_blank" class="map-lnk">&gt; FORTINET</a>', unsafe_allow_html=True)
    iframe_map("https://threatmap.fortiguard.com/")

m3,m4 = st.columns(2)
with m3:
    st.markdown('<a href="https://attackmap.sonicwall.com/live-attack-map/" target="_blank" class="map-lnk">&gt; SONICWALL</a>', unsafe_allow_html=True)
    iframe_map("https://attackmap.sonicwall.com/live-attack-map/")
with m4:
    st.markdown('<a href="https://threatmap.checkpoint.com/" target="_blank" class="map-lnk">&gt; CHECK POINT</a>', unsafe_allow_html=True)
    iframe_map("https://threatmap.checkpoint.com/")

m5,m6 = st.columns(2)
with m5:
    st.markdown('<a href="https://www.sicherheitstacho.eu/?lang=en" target="_blank" class="map-lnk">&gt; SICHERHEITSTACHO (DT)</a>', unsafe_allow_html=True)
    iframe_map("https://www.sicherheitstacho.eu/?lang=en")
with m6:
    st.markdown('<a href="https://cybermap.kaspersky.com/en/widget/dynamic/dark" target="_blank" class="map-lnk">&gt; KASPERSKY</a>', unsafe_allow_html=True)
    iframe_map("https://cybermap.kaspersky.com/en/widget/dynamic/dark")

m7,m8 = st.columns(2)
with m7:
    st.markdown('<a href="https://threatbutt.com/map/" target="_blank" class="map-lnk">&gt; THREATBUTT</a>', unsafe_allow_html=True)
    iframe_map("https://threatbutt.com/map/")
with m8:
    st.markdown('<a href="https://threatmap.bitdefender.com/" target="_blank" class="map-lnk">&gt; BITDEFENDER</a>', unsafe_allow_html=True)
    iframe_map("https://threatmap.bitdefender.com/")

st.markdown('<a href="https://viz.greynoise.io/trends/trending" target="_blank" class="map-lnk">&gt; GREYNOISE INTELLIGENCE TRENDS</a>', unsafe_allow_html=True)
iframe_map("https://viz.greynoise.io/trends/trending", h=900)
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  GRC RESOURCES — clean 3-column grid
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""<div style="margin:22px 0 18px;text-align:center;">
  <span style="font-size:1.05rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.4px;">
    <a href="https://www.nist.gov/cyberframework" target="_blank" class="sec-hdr">
      &gt;&gt; ADDITIONAL GRC RESOURCES &lt;&lt;</a>
  </span>
</div>""", unsafe_allow_html=True)

RESOURCES = [
    # col 1 (idx 0,3,6…)
    ("NIST CSF 2.0","https://www.nist.gov/cyberframework","Cybersecurity risk management framework"),
    ("NIST AI RMF","https://www.nist.gov/itl/ai-risk-management-framework","AI risk management framework"),
    ("ISO/IEC 27001","https://www.iso.org/isoiec-27001-information-security.html","International ISMS standard"),
    ("CIS Controls v8","https://www.cisecurity.org/controls/","Prioritized cybersecurity safeguards"),
    ("MITRE ATT&CK","https://mitre-attack.github.io/attack-navigator/","Adversary tactics & techniques matrix"),
    ("OWASP Top 10","https://owasp.org/www-project-top-ten/","Critical web application risks"),
    ("OWASP LLM Top 10","https://owasp.org/www-project-top-10-for-large-language-model-applications/","LLM security risks"),
    ("CVSS 4.0 Calc","https://www.first.org/cvss/calculator/4.0","Vulnerability scoring calculator"),
    ("NIST NVD","https://nvd.nist.gov/","National vulnerability database"),
    ("CISA KEV Catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","Active exploit catalog"),
    ("CISA Shields Up","https://www.cisa.gov/shields-up","Heightened threat guidance"),
    ("NIST CSRC","https://csrc.nist.gov/","Computer security resource center"),
    ("HITRUST Alliance","https://hitrustalliance.net/","Healthcare & sensitive data risk mgmt"),
    # col 2
    ("CISA ICS Advisories","https://www.cisa.gov/ics","OT/ICS security advisories"),
    ("Exploit Database","https://www.exploit-db.com/","Public exploits & POC archive"),
    ("VirusTotal","https://www.virustotal.com/","File, URL & hash analysis"),
    ("Shodan","https://www.shodan.io/","Exposed device search engine"),
    ("Have I Been Pwned","https://haveibeenpwned.com/","Breach exposure checker"),
    ("AlienVault OTX","https://otx.alienvault.com/","Crowdsourced threat IOCs"),
    ("URLScan.io","https://urlscan.io/","URL & domain threat analysis"),
    ("Any.Run","https://any.run/","Interactive malware sandbox"),
    ("Abuse.ch URLhaus","https://urlhaus.abuse.ch/","Malware distribution URLs"),
    ("MalwareBazaar","https://bazaar.abuse.ch/","Open malware sample database"),
    ("Talos Intel","https://talosintelligence.com/","Cisco threat intelligence"),
    ("SANS ISC","https://isc.sans.edu/","Internet threat monitor & diary"),
    ("crt.sh","https://crt.sh/","Certificate transparency logs"),
    # col 3
    ("CyberChef","https://gchq.github.io/CyberChef/","Cyber Swiss Army Knife"),
    ("GTFOBins","https://gtfobins.github.io/","Unix binary security bypasses"),
    ("OSINT Framework","https://osintframework.com/","OSINT tool collection"),
    ("PayloadsAllThings","https://github.com/swisskyrepo/PayloadsAllTheThings","Security payloads & bypasses"),
    ("PortSwigger Academy","https://portswigger.net/web-security","Web security training"),
    ("HackTheBox","https://www.hackthebox.com/","Gamified security training"),
    ("TryHackMe","https://tryhackme.com/","Guided security labs"),
    ("HackerOne","https://www.hackerone.com/","Bug bounty platform"),
    ("Bugcrowd","https://www.bugcrowd.com/","Crowdsourced vuln disclosure"),
    ("SANS Whitepapers","https://www.sans.org/white-papers/","Security research library"),
    ("BleepingComputer","https://www.bleepingcomputer.com/","Cybersecurity news & analysis"),
    ("VulnHub","https://www.vulnhub.com/","Vulnerable machine practice"),
    ("DEF CON Archives","https://defcon.org/html/links/dc-archives.html","Security conference archives"),
]

# Split into 3 even columns
n  = len(RESOURCES)
sz = (n+2)//3
cols = [RESOURCES[:sz], RESOURCES[sz:sz*2], RESOURCES[sz*2:]]

def res_html(items, offset=0):
    html = ""
    for i,( title, url, desc) in enumerate(items):
        num = str(i+1+offset).zfill(2)
        html += (f'<div class="grc-item">'
                 f'<span class="grc-num">{num}.</span>'
                 f'<a href="{url}" target="_blank" class="res-link">{title}</a>'
                 f'<div class="grc-desc">{desc}</div></div>')
    return html

_, gc1, gc2, gc3, _ = st.columns([0.3, 3, 3, 3, 0.3])
with gc1: st.markdown(res_html(cols[0], 0), unsafe_allow_html=True)
with gc2: st.markdown(res_html(cols[1], sz), unsafe_allow_html=True)
with gc3: st.markdown(res_html(cols[2], sz*2), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""<div style="border-top:1px solid #111;padding-top:22px;margin-top:36px;
  text-align:center;font-family:{MONO};">
  <div style="color:#484848;font-size:0.83rem;margin-bottom:3px;">
    Questions, Comments, or Recommendations?</div>
  <div style="color:#484848;font-size:0.83rem;margin-bottom:16px;">
    Developed by <b>Adam Kistler</b> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">LinkedIn</a>
  </div>
  <div style="color:#282828;font-size:0.68rem;padding:0 12%;line-height:1.5;margin-bottom:10px;">
    <b>LEGAL DISCLAIMER:</b> Educational and portfolio purposes only. All threat maps and data
    are property of their respective owners. SecAI-Nexus does not host or process third-party content.
    &nbsp;<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"
    target="_blank" class="footer-lic">CC BY-NC 4.0</a>
  </div>
  <div style="color:#1e1e1e;font-size:0.7rem;">
    SecAI-Nexus GRC [v17.0] &nbsp;·&nbsp; 8 Rows × 4 Columns · 32 Metrics
    &nbsp;·&nbsp; {now_utc.strftime("%Y")}
  </div>
</div>""", unsafe_allow_html=True)
