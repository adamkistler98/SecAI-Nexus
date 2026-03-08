import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SecAI-Nexus GRC",
    layout="wide",
    page_icon="🔒",
    initial_sidebar_state="collapsed"
)

# ── THEME ─────────────────────────────────────────────────────────────────────
MONO  = "'Courier New', Courier, monospace"
GREEN = "#00ff41"
BLUE  = "#008aff"
RED   = "#ff4b4b"
AMBER = "#ffaa00"
CYAN  = "#00e5ff"
BG    = "#050505"
CARD  = "#0a0a0a"

st.markdown(f"""
<style>
  @keyframes pulse-glow {{
    0%, 100% {{ text-shadow: 0 0 6px {GREEN}40; }}
    50% {{ text-shadow: 0 0 12px {GREEN}80; }}
  }}

  .stApp {{
      background-color:{BG} !important;
      font-family:{MONO} !important;
  }}
  div[data-testid="stMarkdownContainer"] > p {{
      color:{GREEN};font-size:1.05rem;line-height:1.6;font-family:{MONO};font-weight:normal;
  }}
  h1,h2,h3,h4,h5,h6,label {{color:{GREEN} !important;}}
  header,footer {{visibility:hidden;}}
  .stDeployButton {{display:none;}}
  div[data-testid="stSpinner"] > div > p {{color:{GREEN} !important;}}

  /* ── COMPACT METRIC CARD ── */
  .cm {{
      background: linear-gradient(135deg, {CARD} 0%, #0d0d12 100%);
      border:1px solid #1a1a2e;
      border-left:3px solid {BLUE};
      padding:10px 11px 8px 11px;
      margin-bottom:8px;
      font-family:{MONO};
      transition: all 0.3s ease;
      min-height: 120px;
  }}
  .cm:hover {{
      border-left-color:{GREEN};
      box-shadow: 0 0 12px {GREEN}10, inset 0 0 20px {GREEN}04;
  }}
  .cm-title {{line-height:1.2;}}
  .cm-title a {{
      color:{BLUE};font-size:0.62rem;font-weight:bold;
      text-transform:uppercase;letter-spacing:0.5px;
      text-decoration:none;transition:0.2s;
  }}
  .cm-title a:hover {{color:{GREEN};text-shadow:0 0 5px {GREEN};}}
  .cm-live {{
      font-size:0.5rem;color:{GREEN};border:1px solid {GREEN};
      padding:0px 4px;margin-left:4px;vertical-align:middle;
      letter-spacing:0.4px;
      animation: pulse-glow 3s ease-in-out infinite;
  }}
  .cm-est {{
      font-size:0.5rem;color:{AMBER};border:1px solid {AMBER}80;
      padding:0px 4px;margin-left:4px;vertical-align:middle;letter-spacing:0.4px;
  }}
  .cm-val {{
      color:{GREEN};font-size:1.35rem;font-weight:bold;
      margin:4px 0 1px 0;line-height:1.1;
      text-shadow:0 0 5px {GREEN}25;
  }}
  .cm-sub {{font-size:0.6rem;color:#4a4a5a;margin-bottom:5px;line-height:1.2;
            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .cm-deltas {{
      font-size:0.65rem;border-top:1px dashed #1a1a2e;padding-top:4px;line-height:1.6;
  }}
  .d-bad  {{color:{RED};font-weight:bold;}}
  .d-good {{color:{GREEN};font-weight:bold;}}
  .d-neu  {{color:{BLUE};font-weight:bold;}}
  .d-amb  {{color:{AMBER};font-weight:bold;}}

  /* ── ROW LABEL ── */
  .row-label {{
      font-size:0.6rem;color:#3a3a4a;text-transform:uppercase;letter-spacing:1.2px;
      border-left:3px solid {BLUE}50;padding-left:7px;margin:12px 0 6px 0;
      background: linear-gradient(90deg, {BLUE}06, transparent 40%);
      padding-top:2px;padding-bottom:2px;
  }}

  /* ── SECTION HEADER ── */
  .sec-hdr {{
      color:{GREEN};text-decoration:none;transition:0.25s;
      text-shadow:0 0 8px {GREEN}30;
  }}
  .sec-hdr:hover {{color:{BLUE};text-shadow:0 0 12px {BLUE};}}

  /* ── LINKS ── */
  .src-link {{
      color:{BLUE};font-weight:bold;text-decoration:none;
      border-bottom:1px dashed #2a2a3a;padding-bottom:1px;transition:0.2s;
  }}
  .src-link:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};text-shadow:0 0 5px {GREEN};}}
  .map-lnk {{
      color:{BLUE};font-size:0.88rem;font-weight:bold;text-transform:uppercase;
      text-decoration:none;transition:0.2s;display:inline-block;margin-bottom:5px;
      letter-spacing:0.5px;
  }}
  .map-lnk:hover {{color:{GREEN};text-shadow:0 0 8px {GREEN};}}
  .res-link {{
      color:{BLUE};font-weight:bold;font-size:0.88rem;
      text-decoration:none;border-bottom:1px dashed {BLUE}50;transition:0.2s;
  }}
  .res-link:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};text-shadow:0 0 5px {GREEN};}}

  /* ── SOURCES BAR ── */
  .src-bar {{
      font-size:0.68rem;font-family:{MONO};margin:2px 0 22px 0;
      padding:10px 14px;
      background: linear-gradient(135deg, #070709 0%, #0a0a10 100%);
      border:1px solid #181828;border-left:3px solid {BLUE}40;line-height:1.9;
  }}

  /* ── MAP CONTAINER ── */
  .map-wrap {{
      border:1px solid #1a1a2e;background:#080810;padding:2px;margin-bottom:6px;
  }}

  /* ── FOOTER ── */
  .footer-lic {{color:#383848;text-decoration:none;border-bottom:1px dashed #383848;transition:0.2s;}}
  .footer-lic:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};}}
  hr {{border-color:#141420 !important;}}

  /* ── STATUS DOT ── */
  .sdot {{
      display:inline-block;width:5px;height:5px;border-radius:50%;
      margin-right:4px;vertical-align:middle;
  }}
  .sdot-g {{background:{GREEN};box-shadow:0 0 5px {GREEN};}}
  .sdot-a {{background:{AMBER};box-shadow:0 0 5px {AMBER};}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHERS
# ══════════════════════════════════════════════════════════════════════════════
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "SecAI-Nexus-GRC/4.0 (educational-dashboard; contact@secai-nexus.dev)"
})

def _get(url, timeout=14, **kw):
    try:
        r = SESSION.get(url, timeout=timeout, **kw)
        r.raise_for_status()
        return r
    except Exception:
        return None


# ── CISA KEV ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_kev():
    r = _get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    if not r: return None
    try:
        vulns = r.json().get("vulnerabilities", [])
        now   = datetime.now(timezone.utc)
        cnt   = {1:0, 7:0, 30:0, 365:0}
        ransomware = 0
        vendors = {}
        for v in vulns:
            try:
                age = (now - datetime.strptime(v["dateAdded"], "%Y-%m-%d")
                       .replace(tzinfo=timezone.utc)).days
                for d in cnt:
                    if age <= d: cnt[d] += 1
            except Exception: pass
            if v.get("knownRansomwareCampaignUse","").lower() == "known":
                ransomware += 1
            vend = v.get("vendorProject","Unknown")
            vendors[vend] = vendors.get(vend, 0) + 1
        top_vendor = max(vendors, key=vendors.get) if vendors else "N/A"
        return {"total": len(vulns), "d1": cnt[1], "d7": cnt[7],
                "d30": cnt[30], "d365": cnt[365],
                "ransomware": ransomware, "top_vendor": top_vendor,
                "top_vendor_count": vendors.get(top_vendor, 0)}
    except Exception: return None


# ── MalwareBazaar CSV ─────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_bazaar():
    r = _get("https://bazaar.abuse.ch/export/csv/recent/", timeout=22)
    if not r: return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        now = datetime.now(timezone.utc)
        d1 = d7 = 0
        sig_map = {}
        for line in lines:
            parts = line.split('","')
            ts_raw = parts[0].strip('"')
            try:
                dt  = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                age = (now - dt).days
                if age <= 1: d1 += 1
                if age <= 7: d7 += 1
            except Exception: pass
            if len(parts) > 9:
                sig = parts[9].strip('"').strip()
                if sig: sig_map[sig] = sig_map.get(sig, 0) + 1
        top_family = max(sig_map, key=sig_map.get) if sig_map else "N/A"
        return {"d1": d1, "d7": d7, "total": len(lines), "top_family": top_family}
    except Exception: return None


# ── URLhaus online feed ───────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_urlhaus():
    r = _get("https://urlhaus.abuse.ch/downloads/text_online/", timeout=15)
    if not r: return None
    lines = [l.strip() for l in r.text.splitlines() if l.strip() and not l.startswith("#")]
    return {"online": len(lines)}


# ── Feodo Tracker CSV ─────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_feodo():
    r = _get("https://feodotracker.abuse.ch/downloads/ipblocklist.csv", timeout=15)
    if not r: return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        online  = sum(1 for l in lines if '"online"' in l.lower())
        offline = sum(1 for l in lines if '"offline"' in l.lower())
        return {"online": online, "offline": offline, "total": len(lines)}
    except Exception: return None


# ── CISA ICS Advisories RSS ───────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ics():
    r = _get("https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml", timeout=15)
    if not r: return None
    try:
        root = ET.fromstring(r.content)
        now  = datetime.now(timezone.utc)
        cnt  = {1:0, 7:0, 30:0, 365:0}
        for item in root.findall(".//item"):
            pub = item.findtext("pubDate", "")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt = datetime.strptime(pub.strip(), fmt)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    for d in cnt:
                        if age <= d: cnt[d] += 1
                    break
                except ValueError: continue
        return cnt
    except Exception: return None


# ── CISA All Advisories RSS ───────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cisa_all():
    r = _get("https://www.cisa.gov/cybersecurity-advisories/all.xml", timeout=15)
    if not r: return None
    try:
        root = ET.fromstring(r.content)
        now  = datetime.now(timezone.utc)
        cnt  = {1:0, 7:0, 30:0, 365:0}
        total = 0
        for item in root.findall(".//item"):
            total += 1
            pub = item.findtext("pubDate", "")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt = datetime.strptime(pub.strip(), fmt)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    for d in cnt:
                        if age <= d: cnt[d] += 1
                    break
                except ValueError: continue
        cnt["total"] = total
        return cnt
    except Exception: return None


# ── SANS ISC InfoCON ──────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_sans_isc():
    r = _get("https://isc.sans.edu/api/infocon?json", timeout=12)
    if not r: return None
    try:
        data = r.json()
        return {"infocon": data.get("status", "unknown")}
    except Exception: return None


# ── Tor Exit Nodes ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tor_exits():
    r = _get("https://check.torproject.org/torbulkexitlist", timeout=15)
    if not r: return None
    try:
        nodes = [l.strip() for l in r.text.splitlines() if l.strip() and not l.startswith("#")]
        return {"count": len(nodes)}
    except Exception: return None


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _fmt(n):
    if not isinstance(n, (int, float)): return str(n)
    n = int(n)
    if   n >= 1_000_000_000: return f"{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:     return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:         return f"{n:,}"
    return str(n)

def now_day():
    y = datetime.now().year
    return (datetime.now(timezone.utc) - datetime(y, 1, 1, tzinfo=timezone.utc)).days + 1

def ytd(annual):   return int(annual * now_day() / 365)
def per(annual,d): return int(annual * d / 365)


# ── CARD RENDERERS ────────────────────────────────────────────────────────────
def card(title, url, value, subtitle,
         d1, d1c, d7, d7c, d30, d30c, d365, d365c,
         live=True):
    badge = f'<span class="cm-live">LIVE</span>' if live else f'<span class="cm-est">EST</span>'
    st.markdown(f"""
<div class="cm">
  <div class="cm-title"><a href="{url}" target="_blank">{title}</a>{badge}</div>
  <div class="cm-val">{value}</div>
  <div class="cm-sub">{subtitle}</div>
  <div class="cm-deltas">
    <span style="color:#2a2a3a;">1d </span><span class="{d1c}">{d1}</span>
    <span style="color:#2a2a3a;"> 7d </span><span class="{d7c}">{d7}</span>
    <span style="color:#2a2a3a;"> 30d </span><span class="{d30c}">{d30}</span>
    <span style="color:#2a2a3a;"> 1yr </span><span class="{d365c}">{d365}</span>
  </div>
</div>""", unsafe_allow_html=True)


def live_card(title, url, data, val_fn, sub_fn,
              d1_fn, d7_fn, d30_fn, d365_fn,
              d1c="d-bad", d7c="d-bad", d30c="d-bad", d365c="d-bad",
              fallback_sub="awaiting feed"):
    if data:
        try:
            card(title, url, val_fn(data), sub_fn(data),
                 d1_fn(data), d1c, d7_fn(data), d7c,
                 d30_fn(data), d30c, d365_fn(data), d365c, live=True)
            return
        except Exception: pass
    st.markdown(f"""
<div class="cm" style="opacity:0.5;">
  <div class="cm-title"><a href="{url}" target="_blank">{title}</a>
    <span class="cm-live">LIVE</span></div>
  <div class="cm-val" style="font-size:1rem;color:#2a7a3a;">Syncing…</div>
  <div class="cm-sub">{fallback_sub}</div>
  <div class="cm-deltas" style="color:#2a2a3a;">Populates on Streamlit Cloud</div>
</div>""", unsafe_allow_html=True)


def iframe(url, h=1100):
    st.markdown(
        f'<div class="map-wrap">'
        f'<iframe src="{url}" width="100%" height="{h}" style="border:none;" '
        f'sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe></div>',
        unsafe_allow_html=True)

def row_label(text):
    st.markdown(f'<div class="row-label">{text}</div>', unsafe_allow_html=True)

def grc_link(num, title, url, desc):
    return (f'<div style="margin-bottom:12px;">'
            f'<span style="color:{GREEN};font-weight:bold;font-size:0.8rem;">{num}.</span> '
            f'<a href="{url}" target="_blank" class="res-link">{title}</a>'
            f'<div style="color:#4a4a5a;font-size:0.72rem;margin-top:2px;'
            f'padding-left:24px;line-height:1.3;">{desc}</div></div>')


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
st.markdown(f"""
<div style="border-bottom:2px solid #141420;padding-bottom:10px;
            margin-bottom:18px;margin-top:-50px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;">
    <div>
      <span style="font-size:1.45rem;font-weight:bold;color:{GREEN};
                   text-shadow:0 0 14px {GREEN}80;letter-spacing:1px;">🔒 SecAI-Nexus</span>
      <span style="font-size:0.82rem;color:{BLUE};margin-left:10px;
                   font-weight:bold;letter-spacing:0.5px;">// CYBER THREAT OBSERVABILITY PLATFORM</span>
      <span style="font-size:0.52rem;color:#3a3a4a;border:1px solid #2a2a3a;
                   padding:1px 5px;margin-left:6px;vertical-align:middle;">v17.0</span>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.82rem;font-weight:bold;color:{BLUE};text-shadow:0 0 5px {BLUE};">
        SYS_TIME: {now_utc.strftime("%H:%M:%S")} UTC · {now_utc.strftime("%Y-%m-%d")}
      </div>
      <div style="font-size:0.58rem;color:#3a3a4a;margin-top:2px;">
        <span class="sdot sdot-g"></span>FEEDS NOMINAL · 32 INDICATORS · 8 MAPS
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FETCH LIVE DATA
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("Syncing threat intelligence feeds…"):
    kev       = fetch_kev()
    baz       = fetch_bazaar()
    uhaus     = fetch_urlhaus()
    feodo     = fetch_feodo()
    ics       = fetch_ics()
    cisa_all  = fetch_cisa_all()
    sans_isc  = fetch_sans_isc()
    tor_exits = fetch_tor_exits()


# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL THREAT METRICS  —  32 COMPACT CARDS IN 8 ROWS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:2px 0 12px 0;">
  <span style="font-size:1.05rem;font-weight:bold;text-transform:uppercase;letter-spacing:1px;">
    <a href="https://www.cisa.gov/" target="_blank" class="sec-hdr">&gt;&gt; GLOBAL THREAT METRICS</a>
  </span><br>
  <span style="font-size:0.62rem;color:#3a3a4a;">
    <span class="sdot sdot-g"></span><span style="color:{GREEN};">LIVE</span> = real-time feed
    &ensp;<span class="sdot sdot-a"></span><span style="color:{AMBER};">EST</span> = annual-report baseline
    &ensp;Deltas: 1d · 7d · 30d · 1yr
  </span>
</div>
""", unsafe_allow_html=True)


# ── EST baselines (published report sources) ─────────────────────────────────
ANN_CVE_TOTAL    = 29_000
ANN_CVE_CRIT     = 4_200
ANN_CVE_HIGH     = 12_500
ANN_RANSOMWARE   = 5_500
ANN_BREACH_REC   = 8_000_000_000
ANN_BEC          = 21_489
ANN_PHISH        = 1_970_000
ANN_SUPPLY       = 3_000
ANN_INSIDER      = 6_800
ANN_IDENTITY     = 17_000_000_000
ANN_GDPR_FINES   = 2_100_000_000
ANN_IC3_LOSSES   = 12_500_000_000
ANN_DDOS         = 15_400_000
ANN_IOT_MAL      = 112_000_000
ANN_CRYPTO       = 3_800_000_000


# ─── ROW 1: VULNERABILITY INTELLIGENCE ───────────────────────────────────────
row_label("▸ VULNERABILITY INTELLIGENCE")
r1a, r1b, r1c, r1d = st.columns(4)

with r1a:
    live_card("CISA KEV EXPLOITS", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev,
        val_fn  = lambda d: _fmt(d["total"]),
        sub_fn  = lambda d: f"{d['ransomware']} ransomware · top: {d['top_vendor']}",
        d1_fn   = lambda d: f"+{d['d1']}" if d['d1']>0 else "±0",
        d7_fn   = lambda d: f"+{d['d7']}",
        d30_fn  = lambda d: f"+{d['d30']}",
        d365_fn = lambda d: f"+{d['d365']}",
        fallback_sub="CISA known-exploited vulns catalog")

with r1b:
    card("NEW CVEs (NVD)", "https://nvd.nist.gov/",
         f"~{per(ANN_CVE_TOTAL,1)}/day",
         f"~{_fmt(ANN_CVE_TOTAL)}/yr · NVD 2024 published total",
         f"+{per(ANN_CVE_TOTAL,1)}","d-bad",
         f"+{per(ANN_CVE_TOTAL,7)}","d-bad",
         f"+{per(ANN_CVE_TOTAL,30):,}","d-bad",
         f"~{_fmt(ANN_CVE_TOTAL)}","d-bad", live=False)

with r1c:
    card("CRITICAL CVEs (≥9.0)", "https://nvd.nist.gov/vuln/search",
         f"~{per(ANN_CVE_CRIT,7)}/week",
         f"~{_fmt(ANN_CVE_CRIT)}/yr · NVD CVSS ≥ 9.0",
         f"+{per(ANN_CVE_CRIT,1)}","d-bad",
         f"+{per(ANN_CVE_CRIT,7)}","d-bad",
         f"+{per(ANN_CVE_CRIT,30)}","d-bad",
         f"~{_fmt(ANN_CVE_CRIT)}","d-bad", live=False)

with r1d:
    card("HIGH CVEs (7.0-8.9)", "https://nvd.nist.gov/vuln/search",
         f"~{per(ANN_CVE_HIGH,7)}/week",
         f"~{_fmt(ANN_CVE_HIGH)}/yr · NVD CVSS HIGH",
         f"+{per(ANN_CVE_HIGH,1)}","d-bad",
         f"+{per(ANN_CVE_HIGH,7)}","d-bad",
         f"+{per(ANN_CVE_HIGH,30)}","d-bad",
         f"~{_fmt(ANN_CVE_HIGH)}","d-bad", live=False)


# ─── ROW 2: MALWARE & ACTIVE THREATS ─────────────────────────────────────────
row_label("▸ MALWARE & ACTIVE THREAT FEEDS")
r2a, r2b, r2c, r2d = st.columns(4)

with r2a:
    live_card("MALWARE SAMPLES (BAZAAR)", "https://bazaar.abuse.ch/",
        baz,
        val_fn  = lambda d: f"{_fmt(d['total'])} in 48h",
        sub_fn  = lambda d: f"Top: {d['top_family']} · {d['d1']} today",
        d1_fn   = lambda d: f"+{_fmt(d['d1'])}",
        d7_fn   = lambda d: f"+{_fmt(d['d7'])}",
        d30_fn  = lambda d: f"~{_fmt(int(d['d7']*(30/7)))}",
        d365_fn = lambda d: f"~{_fmt(int(d['d7']*(365/7)))}",
        fallback_sub="MalwareBazaar 48h CSV export")

with r2b:
    live_card("ACTIVE MALICIOUS URLs", "https://urlhaus.abuse.ch/",
        uhaus,
        val_fn  = lambda d: _fmt(d["online"]),
        sub_fn  = lambda d: "URLs serving malware now",
        d1_fn   = lambda d: "–", d7_fn=lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: "3.6M+ tracked",
        d365c="d-neu",
        fallback_sub="URLhaus online feed")

with r2c:
    live_card("BOTNET C2s (FEODO)", "https://feodotracker.abuse.ch/",
        feodo,
        val_fn  = lambda d: f"{_fmt(d['online'])} online",
        sub_fn  = lambda d: f"{_fmt(d['total'])} tracked · {_fmt(d['offline'])} down",
        d1_fn   = lambda d: "–", d7_fn=lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['total'])} total",
        d365c="d-neu",
        fallback_sub="Feodo Tracker C2 blocklist")

with r2d:
    live_card("TOR EXIT NODES", "https://metrics.torproject.org/",
        tor_exits,
        val_fn  = lambda d: _fmt(d["count"]),
        sub_fn  = lambda d: "Active exit relays · anonymization infra",
        d1_fn   = lambda d: "–", d7_fn=lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['count'])} nodes",
        d365c="d-neu",
        fallback_sub="Tor Project bulk exit list")


# ─── ROW 3: ADVISORY & RESPONSE ──────────────────────────────────────────────
row_label("▸ ADVISORIES & INCIDENT RESPONSE")
r3a, r3b, r3c, r3d = st.columns(4)

with r3a:
    live_card("CISA ADVISORIES (ALL)", "https://www.cisa.gov/news-events/cybersecurity-advisories",
        cisa_all,
        val_fn  = lambda d: f"{d[7]}/week",
        sub_fn  = lambda d: f"AA·ICS·MA · {d.get('total',0)} in feed",
        d1_fn   = lambda d: f"+{d[1]}", d7_fn=lambda d: f"+{d[7]}",
        d30_fn  = lambda d: f"+{d[30]}",
        d365_fn = lambda d: f"+{d[365]}",
        fallback_sub="CISA all advisory RSS")

with r3b:
    live_card("ICS/SCADA ADVISORIES", "https://www.cisa.gov/news-events/cybersecurity-advisories/ics-advisories",
        ics,
        val_fn  = lambda d: f"{d[7]}/week",
        sub_fn  = lambda d: "OT/ICS critical-infrastructure alerts",
        d1_fn   = lambda d: f"+{d[1]}", d7_fn=lambda d: f"+{d[7]}",
        d30_fn  = lambda d: f"+{d[30]}",
        d365_fn = lambda d: f"+{d[365]}",
        fallback_sub="CISA ICS advisory RSS")

with r3c:
    live_card("SANS ISC INFOCON", "https://isc.sans.edu/",
        sans_isc,
        val_fn  = lambda d: d.get("infocon","?").upper(),
        sub_fn  = lambda d: "Internet threat level · DShield sensors",
        d1_fn   = lambda d: "–", d7_fn=lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f'{d.get("infocon","?")}',
        d365c="d-good",
        fallback_sub="SANS DShield threat level")

with r3d:
    live_card("KEV RANSOMWARE-LINKED", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev,
        val_fn  = lambda d: _fmt(d["ransomware"]),
        sub_fn  = lambda d: "CVEs tied to ransomware campaigns",
        d1_fn   = lambda d: "–", d7_fn=lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['ransomware'])} total",
        d365c="d-bad",
        fallback_sub="CISA KEV ransomware subset")


# ─── ROW 4: INCIDENT & BREACH RISK ───────────────────────────────────────────
row_label("▸ INCIDENT & BREACH RISK  [EST]")
r4a, r4b, r4c, r4d = st.columns(4)

with r4a:
    card("RANSOMWARE INCIDENTS", "https://www.cisa.gov/stopransomware",
         _fmt(ytd(ANN_RANSOMWARE)), f"YTD · ~{ANN_RANSOMWARE:,}/yr · CrowdStrike GTR",
         f"+{per(ANN_RANSOMWARE,1)}","d-bad",
         f"+{per(ANN_RANSOMWARE,7)}","d-bad",
         f"+{per(ANN_RANSOMWARE,30):,}","d-bad",
         f"~{ANN_RANSOMWARE:,}","d-bad", live=False)

with r4b:
    card("DATA RECORDS BREACHED", "https://www.verizon.com/business/resources/reports/dbir/",
         f"{ytd(ANN_BREACH_REC)//1_000_000}M", "YTD · Verizon DBIR 2024",
         f"+{per(ANN_BREACH_REC,1)//1_000_000}M","d-bad",
         f"+{per(ANN_BREACH_REC,7)//1_000_000}M","d-bad",
         f"+{per(ANN_BREACH_REC,30)//1_000_000}M","d-bad",
         "~8B/yr","d-bad", live=False)

with r4c:
    card("BEC INCIDENTS (IC3)", "https://www.ic3.gov/AnnualReport",
         _fmt(ytd(ANN_BEC)), f"YTD · FBI IC3: {ANN_BEC:,}/yr",
         f"+{per(ANN_BEC,1)}","d-bad",
         f"+{per(ANN_BEC,7):,}","d-bad",
         f"+{per(ANN_BEC,30):,}","d-bad",
         f"~{ANN_BEC:,}/yr","d-bad", live=False)

with r4d:
    card("PHISHING CAMPAIGNS", "https://apwg.org/trendsreports/",
         f"{ytd(ANN_PHISH)//1_000}k YTD", "APWG eCrime 2024",
         f"+{per(ANN_PHISH,1):,}","d-bad",
         f"+{per(ANN_PHISH,7):,}","d-bad",
         f"+{per(ANN_PHISH,30):,}","d-bad",
         f"~{ANN_PHISH//1_000}k/yr","d-bad", live=False)


# ─── ROW 5: FINANCIAL & COMPLIANCE ───────────────────────────────────────────
row_label("▸ FINANCIAL & COMPLIANCE RISK  [EST]")
r5a, r5b, r5c, r5d = st.columns(4)

with r5a:
    card("AVG BREACH COST", "https://www.ibm.com/security/data-breach",
         "$4.88M", "global avg · IBM 2024",
         "+$13k","d-bad", "+$94k","d-bad", "+$407k","d-bad", "+$4.88M","d-bad", live=False)

with r5b:
    card("HEALTHCARE BREACH COST", "https://www.ibm.com/security/data-breach",
         "$9.77M", "highest sector · IBM 2024",
         "+$27k","d-bad", "+$188k","d-bad", "+$814k","d-bad", "+$9.77M","d-bad", live=False)

with r5c:
    card("GDPR FINES ISSUED", "https://www.enforcementtracker.com/",
         f"€{ytd(ANN_GDPR_FINES)//1_000_000}M YTD", "DLA Piper 2024 · ~€2.1B/yr",
         f"+€{per(ANN_GDPR_FINES,1)//1_000_000}M","d-bad",
         f"+€{per(ANN_GDPR_FINES,7)//1_000_000}M","d-bad",
         f"+€{per(ANN_GDPR_FINES,30)//1_000_000}M","d-bad",
         "~€2.1B/yr","d-bad", live=False)

with r5d:
    card("CYBERCRIME LOSSES", "https://www.ic3.gov/AnnualReport",
         f"${ytd(ANN_IC3_LOSSES)//1_000_000_000:.1f}B YTD", "FBI IC3 · $12.5B/yr",
         f"+${per(ANN_IC3_LOSSES,1)//1_000_000}M","d-bad",
         f"+${per(ANN_IC3_LOSSES,7)//1_000_000}M","d-bad",
         f"+${per(ANN_IC3_LOSSES,30)//1_000_000}M","d-bad",
         "~$12.5B/yr","d-bad", live=False)


# ─── ROW 6: THREAT ACTORS & CAMPAIGNS ────────────────────────────────────────
row_label("▸ THREAT ACTOR & CAMPAIGN CONTEXT  [EST]")
r6a, r6b, r6c, r6d = st.columns(4)

with r6a:
    card("SUPPLY CHAIN ATTACKS", "https://www.crowdstrike.com/global-threat-report/",
         "+45% YoY", f"~{ytd(ANN_SUPPLY):,} YTD · CrowdStrike GTR",
         f"+{per(ANN_SUPPLY,1)}","d-bad", f"+{per(ANN_SUPPLY,7)}","d-bad",
         f"+{per(ANN_SUPPLY,30)}","d-bad", f"~{ANN_SUPPLY:,}/yr","d-bad", live=False)

with r6b:
    card("INSIDER THREATS", "https://www.verizon.com/business/resources/reports/dbir/",
         _fmt(ytd(ANN_INSIDER)), f"YTD · DBIR: {ANN_INSIDER:,}/yr",
         f"+{per(ANN_INSIDER,1)}","d-bad", f"+{per(ANN_INSIDER,7)}","d-bad",
         f"+{per(ANN_INSIDER,30):,}","d-bad", f"~{ANN_INSIDER:,}/yr","d-bad", live=False)

with r6c:
    card("EXPOSED CREDENTIALS", "https://spycloud.com/resource/2024-annual-identity-exposure-report/",
         f"{ytd(ANN_IDENTITY)//1_000_000_000:.1f}B YTD", "SpyCloud 2024 · ~17B/yr",
         f"+{per(ANN_IDENTITY,1)//1_000_000}M","d-bad",
         f"+{per(ANN_IDENTITY,7)//1_000_000}M","d-bad",
         f"+{per(ANN_IDENTITY,30)//1_000_000}M","d-bad",
         "~17B/yr","d-bad", live=False)

with r6d:
    card("IDENTITY-BASED ATTACKS", "https://www.crowdstrike.com/global-threat-report/",
         "75%", "use valid credentials · CrowdStrike",
         "–","d-neu", "–","d-neu", "–","d-neu", "+75% YoY","d-bad", live=False)


# ─── ROW 7: EMERGING THREATS ─────────────────────────────────────────────────
row_label("▸ EMERGING THREATS  [EST]")
r7a, r7b, r7c, r7d = st.columns(4)

with r7a:
    card("DDoS ATTACKS", "https://radar.cloudflare.com/reports/ddos-2024-q4",
         f"{ytd(ANN_DDOS)//1_000_000:.1f}M YTD", "Cloudflare 2024 · 15.4M/yr",
         f"+{per(ANN_DDOS,1)//1_000}k","d-bad",
         f"+{per(ANN_DDOS,7)//1_000}k","d-bad",
         f"+{per(ANN_DDOS,30)//1_000}k","d-bad",
         "~15.4M/yr","d-bad", live=False)

with r7b:
    card("IoT MALWARE ATTACKS", "https://www.sonicwall.com/threat-report/",
         f"{ytd(ANN_IOT_MAL)//1_000_000}M YTD", "SonicWall 2024 · 112M/yr",
         f"+{per(ANN_IOT_MAL,1)//1_000}k","d-bad",
         f"+{per(ANN_IOT_MAL,7)//1_000}k","d-bad",
         f"+{per(ANN_IOT_MAL,30)//1_000_000}M","d-bad",
         "~112M/yr","d-bad", live=False)

with r7c:
    card("CRYPTO THEFT LOSSES", "https://www.chainalysis.com/blog/crypto-crime-report/",
         f"${ytd(ANN_CRYPTO)//1_000_000_000:.1f}B YTD", "Chainalysis 2024 · $3.8B/yr",
         f"+${per(ANN_CRYPTO,1)//1_000_000}M","d-bad",
         f"+${per(ANN_CRYPTO,7)//1_000_000}M","d-bad",
         f"+${per(ANN_CRYPTO,30)//1_000_000}M","d-bad",
         "~$3.8B/yr","d-bad", live=False)

with r7d:
    card("AVG TIME TO EXPLOIT", "https://www.crowdstrike.com/global-threat-report/",
         "5 Days", "disclosure-to-exploit · CrowdStrike",
         "–","d-neu", "–","d-neu", "-0.5d","d-good", "-3d","d-good", live=False)


# ─── ROW 8: DETECTION & POSTURE ──────────────────────────────────────────────
row_label("▸ DETECTION, RESPONSE & ADOPTION  [EST / LIVE]")
r8a, r8b, r8c, r8d = st.columns(4)

with r8a:
    card("AVG MTTD (DWELL TIME)", "https://www.mandiant.com/m-trends",
         "10 Days", "global median · Mandiant M-Trends",
         "-0.03d","d-good", "-0.2d","d-good", "-0.8d","d-good", "-4d","d-good", live=False)

with r8b:
    card("ZERO-TRUST ADOPTION", "https://www.crowdstrike.com/global-threat-report/",
         "67%", "orgs implementing · CrowdStrike",
         "–","d-neu", "–","d-neu", "–","d-neu", "+12% YoY","d-good", live=False)

with r8c:
    card("CLOUD MISCONFIG RATE", "https://www.verizon.com/business/resources/reports/dbir/",
         "21%", "of breaches involve misconfig · DBIR",
         "–","d-neu", "–","d-neu", "–","d-neu", "+3% YoY","d-bad", live=False)

with r8d:
    live_card("KEV TOP VENDOR", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev,
        val_fn  = lambda d: d["top_vendor"],
        sub_fn  = lambda d: f"{d['top_vendor_count']} exploited CVEs",
        d1_fn   = lambda d: "–", d7_fn=lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['top_vendor_count'])}",
        d365c="d-bad",
        fallback_sub="CISA KEV vendor breakdown")


# ─── SOURCES BAR ──────────────────────────────────────────────────────────────
refresh_ts = now_utc.strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""
<div class="src-bar">
  <span style="color:#3a3a4a;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">
    <span class="sdot sdot-g"></span>LIVE FEEDS&nbsp;</span>
  <a href="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
     target="_blank" class="src-link">CISA KEV</a> ·
  <a href="https://bazaar.abuse.ch/export/csv/recent/"
     target="_blank" class="src-link">MalwareBazaar</a> ·
  <a href="https://urlhaus.abuse.ch/downloads/text_online/"
     target="_blank" class="src-link">URLhaus</a> ·
  <a href="https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
     target="_blank" class="src-link">Feodo Tracker</a> ·
  <a href="https://isc.sans.edu/api/"
     target="_blank" class="src-link">SANS ISC API</a> ·
  <a href="https://check.torproject.org/torbulkexitlist"
     target="_blank" class="src-link">Tor Exit List</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml"
     target="_blank" class="src-link">CISA ICS RSS</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/all.xml"
     target="_blank" class="src-link">CISA All RSS</a>
  <br>
  <span style="color:#3a3a4a;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">
    <span class="sdot sdot-a"></span>EST BASELINES&nbsp;</span>
  <a href="https://nvd.nist.gov/" target="_blank" class="src-link">NVD 2024</a> ·
  <a href="https://www.verizon.com/business/resources/reports/dbir/"
     target="_blank" class="src-link">Verizon DBIR</a> ·
  <a href="https://www.mandiant.com/m-trends"
     target="_blank" class="src-link">Mandiant M-Trends</a> ·
  <a href="https://www.crowdstrike.com/global-threat-report/"
     target="_blank" class="src-link">CrowdStrike GTR</a> ·
  <a href="https://www.ic3.gov/AnnualReport"
     target="_blank" class="src-link">FBI IC3</a> ·
  <a href="https://www.ibm.com/security/data-breach"
     target="_blank" class="src-link">IBM Breach Report</a> ·
  <a href="https://apwg.org/trendsreports/"
     target="_blank" class="src-link">APWG eCrime</a> ·
  <a href="https://spycloud.com/resource/2024-annual-identity-exposure-report/"
     target="_blank" class="src-link">SpyCloud</a> ·
  <a href="https://www.enforcementtracker.com/"
     target="_blank" class="src-link">GDPR Tracker</a> ·
  <a href="https://radar.cloudflare.com/reports/ddos-2024-q4"
     target="_blank" class="src-link">Cloudflare DDoS</a> ·
  <a href="https://www.sonicwall.com/threat-report/"
     target="_blank" class="src-link">SonicWall</a> ·
  <a href="https://www.chainalysis.com/blog/crypto-crime-report/"
     target="_blank" class="src-link">Chainalysis</a>
  <span style="float:right;color:#1a1a2a;">↻ {refresh_ts}</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LIVE THREAT MAPS  —  8 EMBEDDABLE MAPS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:6px 0 12px 0;">
  <span style="font-size:1.05rem;font-weight:bold;text-transform:uppercase;letter-spacing:1px;">
    <a href="https://livethreatmap.radware.com/" target="_blank" class="sec-hdr">
      &gt;&gt; LIVE THREAT MAP FEEDS</a>
  </span>
  <span style="font-size:0.6rem;color:#3a3a4a;margin-left:10px;">
    REAL-TIME GLOBAL ATTACK VISUALIZATION · 8 SOURCES
  </span>
</div>""", unsafe_allow_html=True)

# ── RADWARE & FORTIGUARD (hero maps — full 1100px) ───────────────────────────
col_rad, col_fort = st.columns(2)
with col_rad:
    st.markdown('<a href="https://livethreatmap.radware.com/" target="_blank" class="map-lnk">&gt;&gt; RADWARE LIVE THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://livethreatmap.radware.com/", h=1100)
with col_fort:
    st.markdown('<a href="https://threatmap.fortiguard.com/" target="_blank" class="map-lnk">&gt;&gt; FORTINET FORTIGUARD MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.fortiguard.com/", h=1100)
st.markdown("---")

# ── KASPERSKY & BITDEFENDER ──────────────────────────────────────────────────
col_kas, col_bit = st.columns(2)
with col_kas:
    st.markdown('<a href="https://cybermap.kaspersky.com/" target="_blank" class="map-lnk">&gt;&gt; KASPERSKY CYBERMAP</a>', unsafe_allow_html=True)
    iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", h=520)
with col_bit:
    st.markdown('<a href="https://threatmap.bitdefender.com/" target="_blank" class="map-lnk">&gt;&gt; BITDEFENDER THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.bitdefender.com/", h=520)
st.markdown("---")

# ── SICHERHEITSTACHO & CHECK POINT ───────────────────────────────────────────
col_sich, col_cp = st.columns(2)
with col_sich:
    st.markdown('<a href="https://www.sicherheitstacho.eu/?lang=en" target="_blank" class="map-lnk">&gt;&gt; SICHERHEITSTACHO (DEUTSCHE TELEKOM)</a>', unsafe_allow_html=True)
    iframe("https://www.sicherheitstacho.eu/?lang=en", h=520)
with col_cp:
    st.markdown('<a href="https://threatmap.checkpoint.com/" target="_blank" class="map-lnk">&gt;&gt; CHECK POINT THREATCLOUD</a>', unsafe_allow_html=True)
    iframe("https://threatmap.checkpoint.com/", h=520)
st.markdown("---")

# ── SONICWALL & THREATBUTT ───────────────────────────────────────────────────
col_son, col_tb = st.columns(2)
with col_son:
    st.markdown('<a href="https://attackmap.sonicwall.com/live-attack-map/" target="_blank" class="map-lnk">&gt;&gt; SONICWALL LIVE ATTACK MAP</a>', unsafe_allow_html=True)
    iframe("https://attackmap.sonicwall.com/live-attack-map/", h=520)
with col_tb:
    st.markdown('<a href="https://threatbutt.com/map/" target="_blank" class="map-lnk">&gt;&gt; THREATBUTT INTERNET HACKING</a>', unsafe_allow_html=True)
    iframe("https://threatbutt.com/map/", h=520)
st.markdown("---")

# ── GREYNOISE (full width) ───────────────────────────────────────────────────
st.markdown('<a href="https://viz.greynoise.io/trends/trending" target="_blank" class="map-lnk">&gt;&gt; GREYNOISE INTELLIGENCE TRENDS</a>', unsafe_allow_html=True)
iframe("https://viz.greynoise.io/trends/trending", h=1200)
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  GRC RESOURCES  —  52 LINKS IN 4 CATEGORIZED COLUMNS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin-top:28px;margin-bottom:18px;text-align:center;">
  <span style="font-size:1.1rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;">
    <a href="https://www.nist.gov/cyberframework" target="_blank" class="sec-hdr">
      &gt;&gt; GRC RESOURCES &amp; TOOLS &lt;&lt;</a>
  </span>
  <div style="font-size:0.6rem;color:#3a3a4a;margin-top:3px;">
    52 CURATED RESOURCES · FRAMEWORKS · TOOLS · TRAINING · THREAT INTEL
  </div>
</div>""", unsafe_allow_html=True)

l1, l2, l3, l4 = st.columns(4)

with l1:
    st.markdown(f'<div style="font-size:0.58rem;color:{BLUE};text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:8px;border-bottom:1px dashed #1a1a2e;'
                f'padding-bottom:3px;">▸ FRAMEWORKS &amp; STANDARDS</div>', unsafe_allow_html=True)
    for a in [
        ("01","NIST CSF 2.0","https://www.nist.gov/cyberframework","Cybersecurity risk management framework."),
        ("02","NIST AI RMF","https://www.nist.gov/itl/ai-risk-management-framework","AI risk management framework."),
        ("03","ISO/IEC 27001","https://www.iso.org/isoiec-27001-information-security.html","International ISMS standard."),
        ("04","CIS Controls v8","https://www.cisecurity.org/controls/","Prioritized cyber safeguards."),
        ("05","HITRUST Alliance","https://hitrustalliance.net/","Information risk management."),
        ("06","MITRE ATT&CK","https://mitre-attack.github.io/attack-navigator/","Adversary TTP matrix."),
        ("07","MITRE D3FEND","https://d3fend.mitre.org/","Defensive technique knowledge graph."),
        ("08","CVSS 4.0 Calc","https://www.first.org/cvss/calculator/4.0","Vulnerability scoring system."),
        ("09","NIST CSRC","https://csrc.nist.gov/","Computer Security Resource Center."),
        ("10","NIST SP 800-53","https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final","Security &amp; privacy controls."),
        ("11","NIST NVD","https://nvd.nist.gov/","National Vulnerability Database."),
        ("12","CISA KEV Catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","Actively exploited CVEs."),
        ("13","CISA Shields Up","https://www.cisa.gov/shields-up","Resilience against cyberattacks."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)

with l2:
    st.markdown(f'<div style="font-size:0.58rem;color:{BLUE};text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:8px;border-bottom:1px dashed #1a1a2e;'
                f'padding-bottom:3px;">▸ THREAT INTEL &amp; ANALYSIS</div>', unsafe_allow_html=True)
    for a in [
        ("14","VirusTotal","https://www.virustotal.com/","Analyze files, domains, IPs, URLs."),
        ("15","AlienVault OTX","https://otx.alienvault.com/","Crowdsourced threat intel IOCs."),
        ("16","Talos Intelligence","https://talosintelligence.com/","Cisco threat intelligence."),
        ("17","Shodan Search","https://www.shodan.io/","Internet-connected device search."),
        ("18","Have I Been Pwned","https://haveibeenpwned.com/","Check breach exposure."),
        ("19","crt.sh Search","https://crt.sh/","Certificate Transparency logs."),
        ("20","SANS ISC","https://isc.sans.edu/","Cyber threat monitor &amp; diary."),
        ("21","Abuse.ch URLhaus","https://urlhaus.abuse.ch/","Malware distribution URLs."),
        ("22","MalwareBazaar","https://bazaar.abuse.ch/","Malware sample repository."),
        ("23","ThreatFox IOCs","https://threatfox.abuse.ch/","Community IOC sharing."),
        ("24","Exploit Database","https://www.exploit-db.com/","Public exploits archive."),
        ("25","Pulsedive","https://pulsedive.com/","Free threat intelligence platform."),
        ("26","GreyNoise","https://viz.greynoise.io/","Internet scanner intelligence."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)

with l3:
    st.markdown(f'<div style="font-size:0.58rem;color:{BLUE};text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:8px;border-bottom:1px dashed #1a1a2e;'
                f'padding-bottom:3px;">▸ SECURITY TOOLS</div>', unsafe_allow_html=True)
    for a in [
        ("27","CyberChef","https://gchq.github.io/CyberChef/","Cyber Swiss Army Knife."),
        ("28","Any.Run Sandbox","https://any.run/","Interactive malware sandbox."),
        ("29","URLScan.io","https://urlscan.io/","Website scanning &amp; analysis."),
        ("30","GTFOBins","https://gtfobins.github.io/","Unix security bypass binaries."),
        ("31","LOLBAS Project","https://lolbas-project.github.io/","Living off the land (Windows)."),
        ("32","Security Onion","https://securityonionsolutions.com/","Threat hunting &amp; monitoring."),
        ("33","OSINT Framework","https://osintframework.com/","OSINT tool collection."),
        ("34","PayloadsAllThings","https://github.com/swisskyrepo/PayloadsAllTheThings","Payloads &amp; bypasses."),
        ("35","Nuclei Templates","https://github.com/projectdiscovery/nuclei-templates","Vulnerability scanner templates."),
        ("36","OpenCTI","https://www.opencti.io/","Open threat intelligence platform."),
        ("37","YARA Rules","https://github.com/Yara-Rules/rules","Malware detection rules."),
        ("38","Sigma Rules","https://github.com/SigmaHQ/sigma","Generic detection format."),
        ("39","Wazuh SIEM","https://wazuh.com/","Open-source XDR and SIEM."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)

with l4:
    st.markdown(f'<div style="font-size:0.58rem;color:{BLUE};text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:8px;border-bottom:1px dashed #1a1a2e;'
                f'padding-bottom:3px;">▸ TRAINING &amp; NEWS</div>', unsafe_allow_html=True)
    for a in [
        ("40","OWASP Top 10 Web","https://owasp.org/www-project-top-ten/","Web app security risks."),
        ("41","OWASP LLM Top 10","https://owasp.org/www-project-top-10-for-large-language-model-applications/","LLM security risks."),
        ("42","OWASP API Top 10","https://owasp.org/API-Security/","API security risks."),
        ("43","HackTheBox","https://www.hackthebox.com/","Gamified security training."),
        ("44","TryHackMe","https://tryhackme.com/","Hands-on security labs."),
        ("45","PortSwigger Academy","https://portswigger.net/web-security","Web vuln training."),
        ("46","BleepingComputer","https://www.bleepingcomputer.com/","Security &amp; ransomware news."),
        ("47","The Hacker News","https://thehackernews.com/","Cybersecurity news platform."),
        ("48","SANS Reading Room","https://www.sans.org/white-papers/","Security whitepapers."),
        ("49","DEF CON Archives","https://defcon.org/html/links/dc-archives.html","DEF CON presentations."),
        ("50","HackerOne","https://www.hackerone.com/","Bug bounty platform."),
        ("51","Bugcrowd","https://www.bugcrowd.com/","Crowdsourced vuln disclosure."),
        ("52","VulnHub","https://www.vulnhub.com/","Digital security practice envs."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="border-top:1px solid #141420;padding-top:22px;margin-top:36px;
            text-align:center;font-family:{MONO};">
  <div style="color:#555;font-size:0.82rem;margin-bottom:4px;">
    Questions, Comments, or Recommendations?</div>
  <div style="color:#555;font-size:0.82rem;margin-bottom:16px;">
    Developed by <b style="color:{GREEN};">Adam Kistler</b> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">LinkedIn</a>
  </div>
  <div style="color:#333;font-size:0.68rem;padding:0 10%;line-height:1.5;margin-bottom:10px;">
    <b>LEGAL DISCLAIMER:</b> Educational and portfolio purposes only. All threat maps and data
    are property of their respective owners. SecAI-Nexus does not host or process third-party content.<br>
    <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank"
       class="footer-lic">Code and layout licensed CC BY-NC 4.0.</a>
  </div>
  <div style="color:#1a1a2a;font-size:0.68rem;">
    SecAI-Nexus GRC [v17.0] · Live Data Engine ·
    32 Indicators · 8 Live Feeds · 8 Threat Maps · {now_utc.strftime("%Y")}
  </div>
</div>
""", unsafe_allow_html=True)
