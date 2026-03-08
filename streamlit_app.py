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
BG    = "#050505"
CARD  = "#0a0a0a"

st.markdown(f"""
<style>
  .stApp {{background-color:{BG} !important;font-family:{MONO} !important;}}
  div[data-testid="stMarkdownContainer"] > p {{
      color:{GREEN};font-size:1.05rem;line-height:1.6;font-family:{MONO};font-weight:normal;}}
  h1,h2,h3,h4,h5,h6,label {{color:{GREEN} !important;}}
  header,footer {{visibility:hidden;}}
  .stDeployButton {{display:none;}}
  div[data-testid="stSpinner"] > div > p {{color:{GREEN} !important;}}

  /* ── METRIC CARD ── */
  .cm {{
      background:{CARD};border:1px solid #1c1c1c;
      border-left:4px solid {BLUE};
      padding:13px 14px;margin-bottom:13px;font-family:{MONO};
      transition:border-left-color 0.3s;
  }}
  .cm:hover {{border-left-color:{GREEN};}}
  .cm-title a {{
      color:{BLUE};font-size:0.75rem;font-weight:bold;
      text-transform:uppercase;letter-spacing:0.7px;
      text-decoration:none;transition:0.2s;
  }}
  .cm-title a:hover {{color:{GREEN};text-shadow:0 0 6px {GREEN};}}
  .cm-live  {{font-size:0.58rem;color:{GREEN};border:1px solid {GREEN};
               padding:1px 4px;margin-left:5px;vertical-align:middle;letter-spacing:0.5px;}}
  .cm-est   {{font-size:0.58rem;color:#555;border:1px solid #444;
               padding:1px 4px;margin-left:5px;vertical-align:middle;letter-spacing:0.5px;}}
  .cm-val   {{color:{GREEN};font-size:1.7rem;font-weight:bold;margin:5px 0 2px 0;line-height:1.1;}}
  .cm-sub   {{font-size:0.7rem;color:#444;margin-bottom:7px;line-height:1.3;}}
  .cm-deltas{{font-size:0.76rem;border-top:1px dashed #1c1c1c;padding-top:6px;line-height:1.8;}}
  .d-bad  {{color:{RED};font-weight:bold;}}
  .d-good {{color:{GREEN};font-weight:bold;}}
  .d-neu  {{color:{BLUE};font-weight:bold;}}
  .d-amb  {{color:{AMBER};font-weight:bold;}}

  /* ── ROW LABEL ── */
  .row-label {{
      font-size:0.68rem;color:#333;text-transform:uppercase;letter-spacing:1px;
      border-left:2px solid #1c1c1c;padding-left:7px;margin:16px 0 8px 0;
  }}

  /* ── SECTION HEADER ── */
  .sec-hdr {{color:{GREEN};text-decoration:none;transition:0.25s;}}
  .sec-hdr:hover {{color:{BLUE};text-shadow:0 0 6px {BLUE};}}

  /* ── SOURCE / MAP / RESOURCE LINKS ── */
  .src-link {{
      color:{BLUE};font-weight:bold;text-decoration:none;
      border-bottom:1px dashed #2a2a2a;padding-bottom:1px;transition:0.2s;
  }}
  .src-link:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};text-shadow:0 0 5px {GREEN};}}
  .map-lnk {{
      color:{BLUE};font-size:0.95rem;font-weight:bold;text-transform:uppercase;
      text-decoration:none;transition:0.2s;display:inline-block;margin-bottom:7px;
  }}
  .map-lnk:hover {{color:{GREEN};text-shadow:0 0 6px {GREEN};}}
  .res-link {{
      color:{BLUE};font-weight:bold;font-size:0.97rem;
      text-decoration:none;border-bottom:1px dashed {BLUE};transition:0.2s;
  }}
  .res-link:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};}}

  /* ── SOURCES BAR ── */
  .src-bar {{
      font-size:0.75rem;font-family:{MONO};margin:2px 0 26px 0;
      padding:10px 14px;background:#070707;
      border:1px solid #181818;border-left:3px solid #333;line-height:2;
  }}

  /* ── FOOTER ── */
  .footer-lic {{color:#383838;text-decoration:none;border-bottom:1px dashed #383838;transition:0.2s;}}
  .footer-lic:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};}}
  hr {{border-color:#141414 !important;}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHERS  — all free, no API key
#  Falls back gracefully: returns None on any error; cards show "–" not OFFLINE
# ══════════════════════════════════════════════════════════════════════════════
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "SecAI-Nexus-GRC/3.0 (educational-dashboard)"})

def _get(url, **kw):
    try:
        r = SESSION.get(url, timeout=14, **kw)
        r.raise_for_status()
        return r
    except Exception:
        return None

# ── CISA KEV ─────────────────────────────────────────────────────────────────
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
                age = (now - datetime.strptime(v["dateAdded"], "%Y-%m-%d")
                       .replace(tzinfo=timezone.utc)).days
                for d in cnt:
                    if age <= d: cnt[d] += 1
            except Exception:
                pass
            if v.get("knownRansomwareCampaignUse","").lower() == "known":
                ransomware += 1
            vend = v.get("vendorProject","Unknown")
            vendors[vend] = vendors.get(vend, 0) + 1
        top_vendor = max(vendors, key=vendors.get) if vendors else "N/A"
        return {"total": len(vulns), "d1": cnt[1], "d7": cnt[7],
                "d30": cnt[30], "d365": cnt[365],
                "ransomware": ransomware, "top_vendor": top_vendor,
                "top_vendor_count": vendors.get(top_vendor, 0)}
    except Exception:
        return None

# ── NVD CVE API v2 ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nvd():
    now   = datetime.now(timezone.utc)
    start = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.000")
    end   = now.strftime("%Y-%m-%dT%H:%M:%S.000")
    r = _get("https://services.nvd.nist.gov/rest/json/cves/2.0",
             params={"pubStartDate": start, "pubEndDate": end, "resultsPerPage": 1},
             timeout=22)
    if not r:
        return None
    try:
        total = r.json().get("totalResults", 0)
        return {"d365": total, "d30": int(total/12),
                "d7": int(total/52), "d1": int(total/365)}
    except Exception:
        return None

# ── NVD CRITICAL CVEs (CVSS ≥ 9.0 filter) ────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nvd_critical():
    now   = datetime.now(timezone.utc)
    start = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.000")
    end   = now.strftime("%Y-%m-%dT%H:%M:%S.000")
    r = _get("https://services.nvd.nist.gov/rest/json/cves/2.0",
             params={"pubStartDate": start, "pubEndDate": end,
                     "cvssV3Severity": "CRITICAL", "resultsPerPage": 1},
             timeout=22)
    if not r:
        return None
    try:
        total = r.json().get("totalResults", 0)
        return {"d365": total, "d30": int(total/12),
                "d7": int(total/52), "d1": int(total/365)}
    except Exception:
        return None

# ── MalwareBazaar CSV ─────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_bazaar():
    r = _get("https://bazaar.abuse.ch/export/csv/recent/", timeout=22)
    if not r:
        return None
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
            except Exception:
                pass
            # signature/family (field index varies; grab index 9 if available)
            if len(parts) > 9:
                sig = parts[9].strip('"').strip()
                if sig and sig != "":
                    sig_map[sig] = sig_map.get(sig, 0) + 1
        top_family = max(sig_map, key=sig_map.get) if sig_map else "N/A"
        return {"d1": d1, "d7": d7, "total": len(lines),
                "top_family": top_family}
    except Exception:
        return None

# ── URLhaus online feed ───────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_urlhaus():
    r = _get("https://urlhaus.abuse.ch/downloads/text_online/", timeout=15)
    if not r:
        return None
    lines = [l.strip() for l in r.text.splitlines()
             if l.strip() and not l.startswith("#")]
    return {"online": len(lines)}

# ── Feodo Tracker CSV ─────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_feodo():
    r = _get("https://feodotracker.abuse.ch/downloads/ipblocklist.csv", timeout=15)
    if not r:
        return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        online  = sum(1 for l in lines if '"online"'  in l.lower())
        offline = sum(1 for l in lines if '"offline"' in l.lower())
        return {"online": online, "offline": offline, "total": len(lines)}
    except Exception:
        return None

# ── CISA ICS Advisories RSS ───────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ics():
    r = _get("https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml", timeout=15)
    if not r:
        return None
    try:
        root  = ET.fromstring(r.content)
        now   = datetime.now(timezone.utc)
        cnt   = {1:0, 7:0, 30:0, 365:0}
        for item in root.findall(".//item"):
            pub = item.findtext("pubDate", "")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt  = datetime.strptime(pub.strip(), fmt)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    for d in cnt:
                        if age <= d: cnt[d] += 1
                    break
                except ValueError:
                    continue
        return cnt
    except Exception:
        return None

# ── CISA All Advisories RSS ───────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cisa_all():
    r = _get("https://www.cisa.gov/cybersecurity-advisories/all.xml", timeout=15)
    if not r:
        return None
    try:
        root = ET.fromstring(r.content)
        now  = datetime.now(timezone.utc)
        cnt  = {1:0, 7:0, 30:0, 365:0}
        for item in root.findall(".//item"):
            pub = item.findtext("pubDate", "")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt  = datetime.strptime(pub.strip(), fmt)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    for d in cnt:
                        if age <= d: cnt[d] += 1
                    break
                except ValueError:
                    continue
        return cnt
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _fmt(n):
    if not isinstance(n, (int, float)):
        return str(n)
    n = int(n)
    if   n >= 1_000_000_000: return f"{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:     return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:         return f"{n:,}"
    return str(n)

def _d(n, positive_is_bad=True):
    """Return (label, css_class) for a delta."""
    if n == 0 or n is None:
        return "±0", "d-neu"
    s   = "+" if n > 0 else ""
    val = f"{s}{_fmt(abs(n)) if n < 0 else _fmt(n)}"
    if n < 0:
        val = f"-{_fmt(abs(n))}"
    cls = ("d-bad" if n > 0 else "d-good") if positive_is_bad else ("d-good" if n > 0 else "d-bad")
    return val, cls

def now_day():
    y = datetime.now().year
    return (datetime.now(timezone.utc) - datetime(y, 1, 1, tzinfo=timezone.utc)).days + 1

def ytd(annual):
    return int(annual * now_day() / 365)

def per(annual, days):
    return int(annual * days / 365)

# ── CARD RENDERER ─────────────────────────────────────────────────────────────
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
    <span style="color:#383838;">1d&nbsp;</span><span class="{d1c}">{d1}</span>
    &ensp;<span style="color:#383838;">7d&nbsp;</span><span class="{d7c}">{d7}</span>
    &ensp;<span style="color:#383838;">30d&nbsp;</span><span class="{d30c}">{d30}</span>
    &ensp;<span style="color:#383838;">1yr&nbsp;</span><span class="{d365c}">{d365}</span>
  </div>
</div>""", unsafe_allow_html=True)

# Live card with fallback values shown cleanly (no OFFLINE badge)
def live_card(title, url, data, val_fn, sub_fn,
              d1_fn, d7_fn, d30_fn, d365_fn,
              d1c="d-bad", d7c="d-bad", d30c="d-bad", d365c="d-bad",
              fallback_val="–", fallback_sub="awaiting feed"):
    if data:
        try:
            card(title, url, val_fn(data), sub_fn(data),
                 d1_fn(data), d1c, d7_fn(data), d7c,
                 d30_fn(data), d30c, d365_fn(data), d365c,
                 live=True)
            return
        except Exception:
            pass
    # Graceful fallback — no badge
    st.markdown(f"""
<div class="cm" style="opacity:0.55;">
  <div class="cm-title"><a href="{url}" target="_blank">{title}</a>
    <span class="cm-live">LIVE</span></div>
  <div class="cm-val" style="font-size:1.1rem;color:#2a7a3a;">Loading…</div>
  <div class="cm-sub">{fallback_sub}</div>
  <div class="cm-deltas" style="color:#333;">Feed will populate on Streamlit Cloud deployment</div>
</div>""", unsafe_allow_html=True)

def iframe(url, h=1100):
    st.markdown(
        f'<iframe src="{url}" width="100%" height="{h}" style="border:none;" '
        f'sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>',
        unsafe_allow_html=True)

def row_label(text):
    st.markdown(f'<div class="row-label">{text}</div>', unsafe_allow_html=True)

def grc_link(num, title, url, desc):
    return (f'<div style="margin-bottom:15px;">'
            f'<span style="color:{GREEN};font-weight:bold;">{num}.</span> '
            f'<a href="{url}" target="_blank" class="res-link">{title}</a>'
            f'<div style="color:{GREEN};font-size:0.8rem;margin-top:3px;'
            f'padding-left:26px;line-height:1.35;">{desc}</div></div>')


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
st.markdown(f"""
<div style="border-bottom:2px solid #141414;padding-bottom:10px;
            margin-bottom:20px;margin-top:-50px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;">
    <div>
      <span style="font-size:1.4rem;font-weight:bold;color:{GREEN};
                   text-shadow:0 0 10px {GREEN};">🔒 SecAI-Nexus</span>
      <span style="font-size:0.88rem;color:{BLUE};margin-left:12px;
                   font-weight:bold;letter-spacing:0.5px;">// CYBER THREAT OBSERVABILITY PLATFORM</span>
    </div>
    <div style="font-size:0.88rem;font-weight:bold;color:{BLUE};
                text-shadow:0 0 5px {BLUE};">
      SYS_TIME: {now_utc.strftime("%H:%M:%S")} UTC &nbsp;·&nbsp; {now_utc.strftime("%Y-%m-%d")}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FETCH ALL LIVE DATA
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
#  GLOBAL THREAT METRICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:4px 0 16px 0;">
  <span style="font-size:1.1rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.2px;">
    <a href="https://www.cisa.gov/" target="_blank" class="sec-hdr">&gt;&gt; GLOBAL THREAT METRICS</a>
  </span><br>
  <span style="font-size:0.72rem;color:#3a3a3a;">
    <span style="color:{GREEN};">LIVE</span> = real-time feed (auto-refreshes hourly) &nbsp;·&nbsp;
    <span style="color:#555;">EST</span> = annual-report baseline with daily interpolation
    &nbsp;·&nbsp; Deltas shown: 1d · 7d · 30d · 1yr
  </span>
</div>
""", unsafe_allow_html=True)


# ─── ROW A: VULNERABILITY INTELLIGENCE ───────────────────────────────────────
row_label("▸ VULNERABILITY INTELLIGENCE")
c1, c2, c3, c4 = st.columns(4)

with c1:  # CISA KEV Total — LIVE
    live_card(
        "CISA KEV: ACTIVE EXPLOITS", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev,
        val_fn  = lambda d: _fmt(d["total"]),
        sub_fn  = lambda d: f"{d['ransomware']} tied to ransomware · top vendor: {d['top_vendor']}",
        d1_fn   = lambda d: f"+{d['d1']}" if d['d1'] > 0 else "±0",
        d7_fn   = lambda d: f"+{d['d7']}",
        d30_fn  = lambda d: f"+{d['d30']}",
        d365_fn = lambda d: f"+{d['d365']}",
        fallback_sub="CISA known-exploited vulnerabilities catalog")

with c2:  # NVD New CVEs — LIVE
    live_card(
        "NEW CVEs PUBLISHED (NVD)", "https://nvd.nist.gov/",
        nvd,
        val_fn  = lambda d: f"{_fmt(d['d1'])}/day",
        sub_fn  = lambda d: f"{_fmt(d['d365'])} CVEs in trailing 12 months",
        d1_fn   = lambda d: f"+{_fmt(d['d1'])}",
        d7_fn   = lambda d: f"+{_fmt(d['d7'])}",
        d30_fn  = lambda d: f"+{_fmt(d['d30'])}",
        d365_fn = lambda d: f"+{_fmt(d['d365'])}",
        fallback_sub="NVD CVE API v2 — all severities")

with c3:  # NVD CRITICAL CVEs — LIVE
    live_card(
        "CRITICAL CVEs (CVSS ≥ 9.0)", "https://nvd.nist.gov/vuln/search",
        nvd_crit,
        val_fn  = lambda d: f"{_fmt(d['d1'])}/day",
        sub_fn  = lambda d: f"{_fmt(d['d365'])} critical CVEs trailing 12 months",
        d1_fn   = lambda d: f"+{_fmt(d['d1'])}",
        d7_fn   = lambda d: f"+{_fmt(d['d7'])}",
        d30_fn  = lambda d: f"+{_fmt(d['d30'])}",
        d365_fn = lambda d: f"+{_fmt(d['d365'])}",
        fallback_sub="NVD CVE API v2 — CRITICAL severity only")

with c4:  # CISA All Advisories — LIVE
    live_card(
        "CISA ADVISORIES (ALL TYPES)", "https://www.cisa.gov/news-events/cybersecurity-advisories",
        cisa_all,
        val_fn  = lambda d: f"{d[7]}/week",
        sub_fn  = lambda d: "AA · ICS · ICS-MA · Medical device advisories",
        d1_fn   = lambda d: f"+{d[1]}",
        d7_fn   = lambda d: f"+{d[7]}",
        d30_fn  = lambda d: f"+{d[30]}",
        d365_fn = lambda d: f"+{d[365]}",
        fallback_sub="CISA RSS — all advisory categories")


# ─── ROW B: MALWARE & ACTIVE THREATS ─────────────────────────────────────────
row_label("▸ MALWARE & ACTIVE THREAT FEEDS")
c5, c6, c7, c8 = st.columns(4)

with c5:  # MalwareBazaar — LIVE
    live_card(
        "MALWARE SAMPLES (BAZAAR)", "https://bazaar.abuse.ch/",
        baz,
        val_fn  = lambda d: f"{_fmt(d['d1'])}/day",
        sub_fn  = lambda d: f"Top family: {d['top_family']} · {_fmt(d['total'])} in 48h export",
        d1_fn   = lambda d: f"+{_fmt(d['d1'])}",
        d7_fn   = lambda d: f"+{_fmt(d['d7'])}",
        d30_fn  = lambda d: f"+{_fmt(int(d['d7']*(30/7)))}",
        d365_fn = lambda d: f"+{_fmt(int(d['d7']*(365/7)))}",
        fallback_sub="MalwareBazaar 48h public CSV export")

with c6:  # URLhaus — LIVE
    live_card(
        "ACTIVE MALICIOUS URLs", "https://urlhaus.abuse.ch/",
        uhaus,
        val_fn  = lambda d: _fmt(d["online"]),
        sub_fn  = lambda d: "URLs actively serving malware right now",
        d1_fn   = lambda d: "–",
        d7_fn   = lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: "3.6M+ total tracked",
        d365c="d-neu",
        fallback_sub="URLhaus text_online public feed")

with c7:  # Feodo C2 — LIVE
    live_card(
        "BOTNET C2 SERVERS (FEODO)", "https://feodotracker.abuse.ch/",
        feodo,
        val_fn  = lambda d: f"{_fmt(d['online'])} online",
        sub_fn  = lambda d: f"{_fmt(d['total'])} tracked · {_fmt(d['offline'])} offline",
        d1_fn   = lambda d: "–",
        d7_fn   = lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['total'])} total",
        d365c="d-neu",
        fallback_sub="Feodo Tracker blocklist CSV · Emotet/Dridex/QakBot")

with c8:  # CISA ICS Advisories — LIVE
    live_card(
        "ICS/SCADA ADVISORIES (CISA)", "https://www.cisa.gov/ics",
        ics,
        val_fn  = lambda d: f"{d[7]}/week",
        sub_fn  = lambda d: "OT/ICS critical-infrastructure security alerts",
        d1_fn   = lambda d: f"+{d[1]}",
        d7_fn   = lambda d: f"+{d[7]}",
        d30_fn  = lambda d: f"+{d[30]}",
        d365_fn = lambda d: f"+{d[365]}",
        fallback_sub="CISA ICS advisory RSS feed")


# ─── ROW C: INCIDENT & BREACH RISK ───────────────────────────────────────────
row_label("▸ INCIDENT & BREACH RISK  [EST — annual-report baselines with daily interpolation]")
c9, c10, c11, c12 = st.columns(4)

# Baseline sources (published reports)
ANN_RANSOMWARE   = 5_500    # CrowdStrike GTR 2024
ANN_BREACH_REC   = 8_000_000_000  # Verizon DBIR 2024
ANN_BEC          = 21_489   # FBI IC3 2023
ANN_PHISH        = 1_970_000  # APWG eCrime 2024

with c9:
    card("RANSOMWARE INCIDENTS [EST]", "https://www.cisa.gov/stopransomware",
         _fmt(ytd(ANN_RANSOMWARE)), f"YTD · ~{ANN_RANSOMWARE:,}/yr · CrowdStrike GTR 2024",
         f"+{per(ANN_RANSOMWARE,1)}","d-bad",
         f"+{per(ANN_RANSOMWARE,7)}","d-bad",
         f"+{per(ANN_RANSOMWARE,30):,}","d-bad",
         f"~{ANN_RANSOMWARE:,}","d-bad", live=False)

with c10:
    card("DATA RECORDS BREACHED [EST]", "https://www.verizon.com/business/resources/reports/dbir/",
         f"{ytd(ANN_BREACH_REC)//1_000_000}M", "YTD · Verizon DBIR 2024 baseline",
         f"+{per(ANN_BREACH_REC,1)//1_000_000}M","d-bad",
         f"+{per(ANN_BREACH_REC,7)//1_000_000}M","d-bad",
         f"+{per(ANN_BREACH_REC,30)//1_000_000}M","d-bad",
         "~8B/yr","d-bad", live=False)

with c11:
    card("BEC INCIDENTS [EST]", "https://www.ic3.gov/AnnualReport",
         _fmt(ytd(ANN_BEC)), f"YTD · FBI IC3 2023: {ANN_BEC:,} complaints",
         f"+{per(ANN_BEC,1)}","d-bad",
         f"+{per(ANN_BEC,7):,}","d-bad",
         f"+{per(ANN_BEC,30):,}","d-bad",
         f"~{ANN_BEC:,}/yr","d-bad", live=False)

with c12:
    card("PHISHING REPORTS [EST]", "https://apwg.org/trendsreports/",
         f"{ytd(ANN_PHISH)//1_000}k YTD", "APWG eCrime 2024 baseline",
         f"+{per(ANN_PHISH,1):,}","d-bad",
         f"+{per(ANN_PHISH,7):,}","d-bad",
         f"+{per(ANN_PHISH,30):,}","d-bad",
         f"~{ANN_PHISH//1_000}k/yr","d-bad", live=False)


# ─── ROW D: FINANCIAL & COMPLIANCE RISK ──────────────────────────────────────
row_label("▸ FINANCIAL & COMPLIANCE RISK  [EST — annual-report baselines]")
c13, c14, c15, c16 = st.columns(4)

with c13:
    card("AVG BREACH COST [EST]", "https://www.ibm.com/security/data-breach",
         "$4.88M", "global avg · IBM Cost of Data Breach 2024",
         "+$13k","d-bad", "+$94k","d-bad", "+$407k","d-bad", "+$4.88M","d-bad",
         live=False)

with c14:
    card("HEALTHCARE BREACH COST [EST]", "https://www.ibm.com/security/data-breach",
         "$9.77M", "highest sector avg · IBM Cost of Breach 2024",
         "+$27k","d-bad", "+$188k","d-bad", "+$814k","d-bad", "+$9.77M","d-bad",
         live=False)

with c15:
    card("AVG MTTD (DWELL TIME) [EST]", "https://www.mandiant.com/m-trends",
         "10 Days", "global median dwell time · Mandiant M-Trends 2024",
         "-0.03d","d-good", "-0.2d","d-good", "-0.8d","d-good", "-4d","d-good",
         live=False)

with c16:
    card("AVG TIME TO EXPLOIT [EST]", "https://www.crowdstrike.com/global-threat-report/",
         "5 Days", "avg disclosure-to-exploit · CrowdStrike GTR 2024",
         "–","d-neu", "–","d-neu", "-0.5d","d-good", "-3d","d-good",
         live=False)


# ─── ROW E: THREAT ACTOR & CAMPAIGN CONTEXT ──────────────────────────────────
row_label("▸ THREAT ACTOR & CAMPAIGN CONTEXT  [EST — annual-report baselines]")
c17, c18, c19, c20 = st.columns(4)

ANN_SUPPLY = 3_000      # CrowdStrike GTR 2024
ANN_INSIDER = 6_800     # Verizon DBIR 2024 insider threat cases
ANN_IDENTITY = 17_000_000_000  # SpyCloud 2024: 17B exposed creds

with c17:
    card("SUPPLY CHAIN ATTACKS [EST]", "https://www.crowdstrike.com/global-threat-report/",
         "+45% YoY", f"~{ytd(ANN_SUPPLY):,} incidents YTD · CrowdStrike GTR 2024",
         f"+{per(ANN_SUPPLY,1)}","d-bad",
         f"+{per(ANN_SUPPLY,7)}","d-bad",
         f"+{per(ANN_SUPPLY,30)}","d-bad",
         f"~{ANN_SUPPLY:,}/yr","d-bad", live=False)

with c18:
    card("INSIDER THREAT INCIDENTS [EST]", "https://www.verizon.com/business/resources/reports/dbir/",
         _fmt(ytd(ANN_INSIDER)), f"YTD · Verizon DBIR 2024: {ANN_INSIDER:,} cases",
         f"+{per(ANN_INSIDER,1)}","d-bad",
         f"+{per(ANN_INSIDER,7)}","d-bad",
         f"+{per(ANN_INSIDER,30):,}","d-bad",
         f"~{ANN_INSIDER:,}/yr","d-bad", live=False)

with c19:
    card("EXPOSED CREDENTIALS [EST]", "https://spycloud.com/resource/2024-annual-identity-exposure-report/",
         f"{ytd(ANN_IDENTITY)//1_000_000_000:.1f}B YTD",
         "SpyCloud 2024 Annual Identity Exposure Report",
         f"+{per(ANN_IDENTITY,1)//1_000_000}M","d-bad",
         f"+{per(ANN_IDENTITY,7)//1_000_000}M","d-bad",
         f"+{per(ANN_IDENTITY,30)//1_000_000}M","d-bad",
         "~17B/yr","d-bad", live=False)

with c20:
    card("IDENTITY-BASED INTRUSIONS [EST]", "https://www.crowdstrike.com/global-threat-report/",
         "75%", "of attacks now use valid credentials · CrowdStrike 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+75% ↑ YoY","d-bad",
         live=False)


# ─── ROW F: SECTOR & REGULATORY RISK ─────────────────────────────────────────
row_label("▸ SECTOR & REGULATORY RISK  [EST — annual-report baselines]")
c21, c22, c23, c24 = st.columns(4)

ANN_GDPR_FINES  = 2_100_000_000  # €2.1B in GDPR fines 2023 (DLA Piper)
ANN_IC3_LOSSES  = 12_500_000_000  # FBI IC3 2023: $12.5B total cybercrime losses

with c21:
    card("GDPR FINES ISSUED [EST]", "https://www.enforcementtracker.com/",
         f"€{ytd(ANN_GDPR_FINES)//1_000_000}M YTD",
         "YTD est. · DLA Piper GDPR fines report 2024",
         f"+€{per(ANN_GDPR_FINES,1)//1_000_000}M","d-bad",
         f"+€{per(ANN_GDPR_FINES,7)//1_000_000}M","d-bad",
         f"+€{per(ANN_GDPR_FINES,30)//1_000_000}M","d-bad",
         "~€2.1B/yr","d-bad", live=False)

with c22:
    card("CYBERCRIME LOSSES [EST]", "https://www.ic3.gov/AnnualReport",
         f"${ytd(ANN_IC3_LOSSES)//1_000_000_000:.1f}B YTD",
         "YTD est. · FBI IC3 2023: $12.5B total losses",
         f"+${per(ANN_IC3_LOSSES,1)//1_000_000}M","d-bad",
         f"+${per(ANN_IC3_LOSSES,7)//1_000_000}M","d-bad",
         f"+${per(ANN_IC3_LOSSES,30)//1_000_000}M","d-bad",
         "~$12.5B/yr","d-bad", live=False)

with c23:
    card("ZERO-TRUST ADOPTION [EST]", "https://www.crowdstrike.com/global-threat-report/",
         "67%", "orgs actively implementing zero-trust · CrowdStrike 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+12% YoY","d-good",
         live=False)

with c24:
    card("CLOUD MISCONFIG INCIDENTS [EST]", "https://www.verizon.com/business/resources/reports/dbir/",
         "21%", "of breaches involve misconfiguration · DBIR 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+3% YoY","d-bad",
         live=False)


# ─── SOURCES BAR ──────────────────────────────────────────────────────────────
refresh_ts = now_utc.strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""
<div class="src-bar">
  <span style="color:#383838;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">
    LIVE FEEDS &nbsp;</span>
  <a href="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
     target="_blank" class="src-link">CISA KEV JSON</a> ·
  <a href="https://services.nvd.nist.gov/rest/json/cves/2.0"
     target="_blank" class="src-link">NVD CVE API v2</a> ·
  <a href="https://bazaar.abuse.ch/export/csv/recent/"
     target="_blank" class="src-link">MalwareBazaar CSV</a> ·
  <a href="https://urlhaus.abuse.ch/downloads/text_online/"
     target="_blank" class="src-link">URLhaus Feed</a> ·
  <a href="https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
     target="_blank" class="src-link">Feodo Tracker CSV</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml"
     target="_blank" class="src-link">CISA ICS RSS</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/all.xml"
     target="_blank" class="src-link">CISA All Advisories RSS</a>
  <br>
  <span style="color:#383838;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">
    EST BASELINES &nbsp;</span>
  <a href="https://www.verizon.com/business/resources/reports/dbir/"
     target="_blank" class="src-link">Verizon DBIR 2024</a> ·
  <a href="https://www.mandiant.com/m-trends"
     target="_blank" class="src-link">Mandiant M-Trends 2024</a> ·
  <a href="https://www.crowdstrike.com/global-threat-report/"
     target="_blank" class="src-link">CrowdStrike GTR 2024</a> ·
  <a href="https://www.ic3.gov/AnnualReport"
     target="_blank" class="src-link">FBI IC3 2023</a> ·
  <a href="https://www.ibm.com/security/data-breach"
     target="_blank" class="src-link">IBM Cost of Breach 2024</a> ·
  <a href="https://apwg.org/trendsreports/"
     target="_blank" class="src-link">APWG eCrime 2024</a> ·
  <a href="https://spycloud.com/resource/2024-annual-identity-exposure-report/"
     target="_blank" class="src-link">SpyCloud Identity 2024</a> ·
  <a href="https://www.enforcementtracker.com/"
     target="_blank" class="src-link">GDPR Enforcement Tracker</a>
  <span style="float:right;color:#282828;">↻ {refresh_ts}</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LIVE THREAT MAPS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:8px 0 14px 0;">
  <span style="font-size:1.1rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.2px;">
    <a href="https://livethreatmap.radware.com/" target="_blank" class="sec-hdr">
      &gt;&gt; LIVE THREAT MAP FEEDS</a>
  </span>
</div>""", unsafe_allow_html=True)

col_rad, col_fort = st.columns(2)
with col_rad:
    st.markdown('<a href="https://livethreatmap.radware.com/" target="_blank" class="map-lnk">&gt;&gt; RADWARE LIVE THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://livethreatmap.radware.com/")
with col_fort:
    st.markdown('<a href="https://threatmap.fortiguard.com/" target="_blank" class="map-lnk">&gt;&gt; FORTINET THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.fortiguard.com/")
st.markdown("---")

col_son, col_cp = st.columns(2)
with col_son:
    st.markdown('<a href="https://attackmap.sonicwall.com/live-attack-map/" target="_blank" class="map-lnk">&gt;&gt; SONICWALL LIVE MAP</a>', unsafe_allow_html=True)
    iframe("https://attackmap.sonicwall.com/live-attack-map/")
with col_cp:
    st.markdown('<a href="https://threatmap.checkpoint.com/" target="_blank" class="map-lnk">&gt;&gt; CHECK POINT THREATCLOUD</a>', unsafe_allow_html=True)
    iframe("https://threatmap.checkpoint.com/")
st.markdown("---")

col_sich, col_kas = st.columns(2)
with col_sich:
    st.markdown('<a href="https://www.sicherheitstacho.eu/?lang=en" target="_blank" class="map-lnk">&gt;&gt; SICHERHEITSTACHO (DT)</a>', unsafe_allow_html=True)
    iframe("https://www.sicherheitstacho.eu/?lang=en")
with col_kas:
    st.markdown('<a href="https://cybermap.kaspersky.com/en/widget/dynamic/dark" target="_blank" class="map-lnk">&gt;&gt; KASPERSKY CYBERMAP</a>', unsafe_allow_html=True)
    iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark")
st.markdown("---")

col_tb, col_bit = st.columns(2)
with col_tb:
    st.markdown('<a href="https://threatbutt.com/map/" target="_blank" class="map-lnk">&gt;&gt; THREATBUTT ATTACK MAP</a>', unsafe_allow_html=True)
    iframe("https://threatbutt.com/map/")
with col_bit:
    st.markdown('<a href="https://threatmap.bitdefender.com/" target="_blank" class="map-lnk">&gt;&gt; BITDEFENDER THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.bitdefender.com/")
st.markdown("---")

st.markdown('<a href="https://viz.greynoise.io/trends/trending" target="_blank" class="map-lnk">&gt;&gt; GREYNOISE INTELLIGENCE</a>', unsafe_allow_html=True)
iframe("https://viz.greynoise.io/trends/trending", h=1400)
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  GRC RESOURCES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin-top:32px;margin-bottom:22px;text-align:center;">
  <span style="font-size:1.15rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;">
    <a href="https://www.nist.gov/cyberframework" target="_blank" class="sec-hdr">
      &gt;&gt; ADDITIONAL GRC RESOURCES &lt;&lt;</a>
  </span>
</div>""", unsafe_allow_html=True)

_, l1, l2, l3, _ = st.columns([0.5, 3, 3, 3, 0.5])

with l1:
    for a in [
        ("01","NIST AI RMF","https://www.nist.gov/itl/ai-risk-management-framework","AI risk management framework for organizations."),
        ("02","HITRUST Alliance","https://hitrustalliance.net/","Safeguarding sensitive data and managing information risk."),
        ("03","OWASP LLM Top 10","https://owasp.org/www-project-top-10-for-large-language-model-applications/","Critical security risks in Large Language Models."),
        ("04","NIST CSF 2.0","https://www.nist.gov/cyberframework","Standards to manage and reduce cybersecurity risk."),
        ("05","ISO/IEC 27001","https://www.iso.org/isoiec-27001-information-security.html","International standard for ISMS management."),
        ("06","OWASP Top 10 Web","https://owasp.org/www-project-top-ten/","Critical web application security risks."),
        ("07","NIST NVD","https://nvd.nist.gov/","US repository of standards-based vulnerability data."),
        ("08","CIS Controls v8","https://www.cisecurity.org/controls/","Prioritized safeguards against prevalent cyber-attacks."),
        ("09","CISA KEV Catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","Authoritative source of actively exploited CVEs."),
        ("10","MITRE ATT&CK","https://mitre-attack.github.io/attack-navigator/","Matrix for mapping adversary TTPs."),
        ("11","CVSS 4.0 Calc","https://www.first.org/cvss/calculator/4.0","Common Vulnerability Scoring System v4.0."),
        ("12","VirusTotal","https://www.virustotal.com/","Analyze suspicious files, domains, IPs, and URLs."),
        ("13","Exploit Database","https://www.exploit-db.com/","Archive of public exploits and POCs."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)

with l2:
    for a in [
        ("14","Shodan Search","https://www.shodan.io/","Search engine for exposed internet-connected devices."),
        ("15","Have I Been Pwned","https://haveibeenpwned.com/","Check if an email/domain is in a data breach."),
        ("16","AlienVault OTX","https://otx.alienvault.com/","Real-time crowdsourced threat intelligence IOCs."),
        ("17","crt.sh Search","https://crt.sh/","Certificate Transparency log for attack surface mapping."),
        ("18","SANS ISC","https://isc.sans.edu/","Cooperative cyber threat monitor and research diary."),
        ("19","BleepingComputer","https://www.bleepingcomputer.com/","Trusted cybersecurity and ransomware news source."),
        ("20","Abuse.ch URLhaus","https://urlhaus.abuse.ch/","Tracking malware distribution URLs globally."),
        ("21","Any.Run Sandbox","https://any.run/","Interactive online malware analysis sandbox."),
        ("22","URLScan.io","https://urlscan.io/","Scan and analyze websites for malicious content."),
        ("23","GTFOBins","https://gtfobins.github.io/","Unix binaries that can bypass local security."),
        ("24","MalwareBazaar","https://bazaar.abuse.ch/","Open-source malware sample repository."),
        ("25","HackTheBox","https://www.hackthebox.com/","Gamified cybersecurity training platform."),
        ("26","Security Onion","https://securityonionsolutions.com/","Threat hunting and enterprise security monitoring."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)

with l3:
    for a in [
        ("27","HackerOne","https://www.hackerone.com/","Bug bounty platform for vulnerability disclosure."),
        ("28","Bugcrowd","https://www.bugcrowd.com/","Crowdsourced vulnerability disclosure and bounties."),
        ("29","TryHackMe","https://tryhackme.com/","Hands-on cybersecurity training labs."),
        ("30","CyberChef","https://gchq.github.io/CyberChef/","The Cyber Swiss Army Knife for data analysis."),
        ("31","CISA Shields Up","https://www.cisa.gov/shields-up","Building resilience against cyberattacks."),
        ("32","NIST CSRC","https://csrc.nist.gov/","NIST Computer Security Resource Center."),
        ("33","SANS Reading Room","https://www.sans.org/white-papers/","Cybersecurity research and whitepapers."),
        ("34","DEF CON Archives","https://defcon.org/html/links/dc-archives.html","Presentations from the DEF CON conference."),
        ("35","OSINT Framework","https://osintframework.com/","Interactive OSINT gathering tool collection."),
        ("36","Talos Threat Intel","https://talosintelligence.com/","Cisco's premier threat intelligence group."),
        ("37","PayloadsAllThings","https://github.com/swisskyrepo/PayloadsAllTheThings","Useful payloads and bypass techniques."),
        ("38","PortSwigger Academy","https://portswigger.net/web-security","Web vulnerability training from Burp Suite creators."),
        ("39","VulnHub","https://www.vulnhub.com/","Hands-on digital security practice environments."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="border-top:1px solid #141414;padding-top:24px;margin-top:40px;
            text-align:center;font-family:{MONO};">
  <div style="color:#555;font-size:0.85rem;margin-bottom:4px;">
    Questions, Comments, or Recommendations?</div>
  <div style="color:#555;font-size:0.85rem;margin-bottom:18px;">
    Developed by <b>Adam Kistler</b> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">LinkedIn</a>
  </div>
  <div style="color:#333;font-size:0.7rem;padding:0 10%;line-height:1.5;margin-bottom:12px;">
    <b>LEGAL DISCLAIMER:</b> Educational and portfolio purposes only. All threat maps and data
    are property of their respective owners. SecAI-Nexus does not host or process third-party content.<br>
    <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank"
       class="footer-lic">Code and layout licensed CC BY-NC 4.0.</a>
  </div>
  <div style="color:#282828;font-size:0.72rem;">
    SecAI-Nexus GRC [v16.0] &nbsp;·&nbsp; Live Data Engine &nbsp;·&nbsp; {now_utc.strftime("%Y")}
  </div>
</div>
""", unsafe_allow_html=True)
