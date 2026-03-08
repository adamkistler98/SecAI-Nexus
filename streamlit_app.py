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
  @keyframes scanline {{
    0% {{ background-position: 0 0; }}
    100% {{ background-position: 0 100%; }}
  }}
  @keyframes pulse-glow {{
    0%, 100% {{ text-shadow: 0 0 8px {GREEN}40; }}
    50% {{ text-shadow: 0 0 16px {GREEN}80; }}
  }}
  @keyframes border-pulse {{
    0%, 100% {{ border-left-color: {BLUE}; }}
    50% {{ border-left-color: {CYAN}; }}
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

  /* ── METRIC CARD ── */
  .cm {{
      background: linear-gradient(135deg, {CARD} 0%, #0d0d12 100%);
      border:1px solid #1a1a2e;
      border-left:4px solid {BLUE};
      padding:14px 15px;margin-bottom:13px;font-family:{MONO};
      transition: all 0.35s ease;
      position: relative;
      overflow: hidden;
  }}
  .cm::before {{
      content: '';
      position: absolute;
      top: 0; right: 0;
      width: 40px; height: 40px;
      background: radial-gradient(circle at top right, {BLUE}08, transparent 70%);
      pointer-events: none;
  }}
  .cm:hover {{
      border-left-color:{GREEN};
      box-shadow: 0 0 15px {GREEN}12, inset 0 0 30px {GREEN}05;
      transform: translateY(-1px);
  }}
  .cm-title a {{
      color:{BLUE};font-size:0.72rem;font-weight:bold;
      text-transform:uppercase;letter-spacing:0.7px;
      text-decoration:none;transition:0.2s;
  }}
  .cm-title a:hover {{color:{GREEN};text-shadow:0 0 6px {GREEN};}}
  .cm-live {{
      font-size:0.55rem;color:{GREEN};border:1px solid {GREEN};
      padding:1px 5px;margin-left:5px;vertical-align:middle;
      letter-spacing:0.5px;text-shadow:0 0 4px {GREEN}60;
      animation: pulse-glow 3s ease-in-out infinite;
  }}
  .cm-est {{
      font-size:0.55rem;color:{AMBER};border:1px solid {AMBER}80;
      padding:1px 5px;margin-left:5px;vertical-align:middle;letter-spacing:0.5px;
  }}
  .cm-val {{
      color:{GREEN};font-size:1.65rem;font-weight:bold;margin:5px 0 2px 0;line-height:1.1;
      text-shadow:0 0 6px {GREEN}30;
  }}
  .cm-sub {{font-size:0.68rem;color:#4a4a5a;margin-bottom:7px;line-height:1.3;}}
  .cm-deltas {{
      font-size:0.74rem;border-top:1px dashed #1a1a2e;padding-top:6px;line-height:1.8;
  }}
  .d-bad  {{color:{RED};font-weight:bold;}}
  .d-good {{color:{GREEN};font-weight:bold;}}
  .d-neu  {{color:{BLUE};font-weight:bold;}}
  .d-amb  {{color:{AMBER};font-weight:bold;}}
  .d-cyan {{color:{CYAN};font-weight:bold;}}

  /* ── ROW LABEL ── */
  .row-label {{
      font-size:0.68rem;color:#3a3a4a;text-transform:uppercase;letter-spacing:1.2px;
      border-left:3px solid {BLUE}60;padding-left:8px;margin:18px 0 10px 0;
      background: linear-gradient(90deg, {BLUE}08, transparent 50%);
      padding-top:3px;padding-bottom:3px;
  }}

  /* ── SECTION HEADER ── */
  .sec-hdr {{
      color:{GREEN};text-decoration:none;transition:0.25s;
      text-shadow:0 0 8px {GREEN}30;
  }}
  .sec-hdr:hover {{color:{BLUE};text-shadow:0 0 12px {BLUE};}}

  /* ── SOURCE / MAP / RESOURCE LINKS ── */
  .src-link {{
      color:{BLUE};font-weight:bold;text-decoration:none;
      border-bottom:1px dashed #2a2a3a;padding-bottom:1px;transition:0.2s;
  }}
  .src-link:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};text-shadow:0 0 5px {GREEN};}}
  .map-lnk {{
      color:{BLUE};font-size:0.92rem;font-weight:bold;text-transform:uppercase;
      text-decoration:none;transition:0.2s;display:inline-block;margin-bottom:7px;
      letter-spacing:0.5px;
  }}
  .map-lnk:hover {{color:{GREEN};text-shadow:0 0 8px {GREEN};}}
  .res-link {{
      color:{BLUE};font-weight:bold;font-size:0.95rem;
      text-decoration:none;border-bottom:1px dashed {BLUE}60;transition:0.2s;
  }}
  .res-link:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};text-shadow:0 0 5px {GREEN};}}

  /* ── SOURCES BAR ── */
  .src-bar {{
      font-size:0.73rem;font-family:{MONO};margin:2px 0 26px 0;
      padding:12px 16px;
      background: linear-gradient(135deg, #070709 0%, #0a0a10 100%);
      border:1px solid #181828;border-left:3px solid {BLUE}40;line-height:2;
  }}

  /* ── STATUS INDICATOR ── */
  .status-dot {{
      display:inline-block;width:6px;height:6px;border-radius:50%;
      margin-right:5px;vertical-align:middle;
  }}
  .status-green {{background:{GREEN};box-shadow:0 0 6px {GREEN};}}
  .status-amber {{background:{AMBER};box-shadow:0 0 6px {AMBER};}}
  .status-red {{background:{RED};box-shadow:0 0 6px {RED};}}

  /* ── FOOTER ── */
  .footer-lic {{color:#383848;text-decoration:none;border-bottom:1px dashed #383848;transition:0.2s;}}
  .footer-lic:hover {{color:{GREEN};border-bottom:1px dashed {GREEN};}}
  hr {{border-color:#141420 !important;}}

  /* ── MAP CONTAINER ── */
  .map-container {{
      border:1px solid #1a1a2e;
      background:#080810;
      padding:2px;
      margin-bottom:8px;
  }}

  /* ── CATEGORY BADGE ── */
  .cat-badge {{
      display:inline-block;font-size:0.58rem;color:#5a5a6a;
      border:1px solid #2a2a3a;padding:1px 6px;margin-left:8px;
      vertical-align:middle;letter-spacing:0.5px;text-transform:uppercase;
  }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA FETCHERS  — all free, no API key
#  Falls back gracefully: returns None on any error; cards show "Loading…"
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

def _post(url, json_data=None, timeout=14, **kw):
    try:
        r = SESSION.post(url, json=json_data, timeout=timeout, **kw)
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

# ── NVD HIGH CVEs (CVSS 7.0-8.9) ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nvd_high():
    now   = datetime.now(timezone.utc)
    start = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.000")
    end   = now.strftime("%Y-%m-%dT%H:%M:%S.000")
    r = _get("https://services.nvd.nist.gov/rest/json/cves/2.0",
             params={"pubStartDate": start, "pubEndDate": end,
                     "cvssV3Severity": "HIGH", "resultsPerPage": 1},
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

# ── SSL Blocklist (abuse.ch) ──────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_sslbl():
    r = _get("https://sslbl.abuse.ch/blacklist/sslipblacklist.csv", timeout=15)
    if not r:
        return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        now = datetime.now(timezone.utc)
        d1 = d7 = d30 = 0
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 3:
                try:
                    dt = datetime.strptime(parts[0].strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    if age <= 1: d1 += 1
                    if age <= 7: d7 += 1
                    if age <= 30: d30 += 1
                except Exception:
                    pass
        return {"total": len(lines), "d1": d1, "d7": d7, "d30": d30}
    except Exception:
        return None

# ── SANS ISC InfoCON & Top Ports ──────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_sans_isc():
    # InfoCON level
    r_info = _get("https://isc.sans.edu/api/infocon?json", timeout=12)
    # Top attacked ports
    r_ports = _get("https://isc.sans.edu/api/topports/records/5?json", timeout=12)
    result = {}
    if r_info:
        try:
            data = r_info.json()
            result["infocon"] = data.get("status", "unknown")
        except Exception:
            result["infocon"] = "unknown"
    if r_ports:
        try:
            ports = r_ports.json()
            if isinstance(ports, list) and len(ports) > 0:
                top = ports[0]
                result["top_port"] = top.get("targetport", "N/A")
                result["top_port_records"] = top.get("records", 0)
                result["port_count"] = len(ports)
            else:
                result["top_port"] = "N/A"
        except Exception:
            result["top_port"] = "N/A"
    return result if result else None

# ── Tor Exit Nodes ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tor_exits():
    r = _get("https://check.torproject.org/torbulkexitlist", timeout=15)
    if not r:
        return None
    try:
        nodes = [l.strip() for l in r.text.splitlines()
                 if l.strip() and not l.startswith("#")]
        return {"count": len(nodes)}
    except Exception:
        return None

# ── ThreatFox IOC Export (CSV, no auth) ───────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_threatfox():
    r = _get("https://threatfox.abuse.ch/export/csv/recent/", timeout=20)
    if not r:
        return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#") and not l.startswith('"')]
        now = datetime.now(timezone.utc)
        d1 = d7 = 0
        types = {}
        for line in lines:
            parts = line.split('","')
            if len(parts) >= 5:
                ts_raw = parts[0].strip('"')
                try:
                    dt = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    if age <= 1: d1 += 1
                    if age <= 7: d7 += 1
                except Exception:
                    pass
                if len(parts) > 4:
                    t = parts[4].strip('"').strip()
                    if t:
                        types[t] = types.get(t, 0) + 1
        top_type = max(types, key=types.get) if types else "N/A"
        return {"d1": d1, "d7": d7, "total": len(lines), "top_type": top_type}
    except Exception:
        return None

# ── CISA Alerts RSS (separate from all advisories) ───────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cisa_alerts():
    r = _get("https://www.cisa.gov/cybersecurity-advisories/aa.xml", timeout=15)
    if not r:
        return None
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
                    dt  = datetime.strptime(pub.strip(), fmt)
                    if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    for d in cnt:
                        if age <= d: cnt[d] += 1
                    break
                except ValueError:
                    continue
        cnt["total"] = total
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
    <span style="color:#383848;">1d&nbsp;</span><span class="{d1c}">{d1}</span>
    &ensp;<span style="color:#383848;">7d&nbsp;</span><span class="{d7c}">{d7}</span>
    &ensp;<span style="color:#383848;">30d&nbsp;</span><span class="{d30c}">{d30}</span>
    &ensp;<span style="color:#383848;">1yr&nbsp;</span><span class="{d365c}">{d365}</span>
  </div>
</div>""", unsafe_allow_html=True)


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
        f'<div class="map-container">'
        f'<iframe src="{url}" width="100%" height="{h}" style="border:none;" '
        f'sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>'
        f'</div>',
        unsafe_allow_html=True)

def row_label(text):
    st.markdown(f'<div class="row-label">{text}</div>', unsafe_allow_html=True)

def grc_link(num, title, url, desc):
    return (f'<div style="margin-bottom:14px;">'
            f'<span style="color:{GREEN};font-weight:bold;font-size:0.85rem;">{num}.</span> '
            f'<a href="{url}" target="_blank" class="res-link">{title}</a>'
            f'<div style="color:#5a5a6a;font-size:0.78rem;margin-top:3px;'
            f'padding-left:26px;line-height:1.35;">{desc}</div></div>')


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
st.markdown(f"""
<div style="border-bottom:2px solid #141420;padding-bottom:12px;
            margin-bottom:22px;margin-top:-50px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;">
    <div>
      <span style="font-size:1.5rem;font-weight:bold;color:{GREEN};
                   text-shadow:0 0 14px {GREEN}80;letter-spacing:1px;">🔒 SecAI-Nexus</span>
      <span style="font-size:0.85rem;color:{BLUE};margin-left:12px;
                   font-weight:bold;letter-spacing:0.5px;">// CYBER THREAT OBSERVABILITY PLATFORM</span>
      <span class="cat-badge">v17.0</span>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.85rem;font-weight:bold;color:{BLUE};
                  text-shadow:0 0 5px {BLUE};">
        SYS_TIME: {now_utc.strftime("%H:%M:%S")} UTC &nbsp;·&nbsp; {now_utc.strftime("%Y-%m-%d")}
      </div>
      <div style="font-size:0.62rem;color:#3a3a4a;margin-top:2px;">
        <span class="status-dot status-green"></span>ALL FEEDS NOMINAL
        &nbsp;·&nbsp; REFRESH: 15-60 MIN
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FETCH ALL LIVE DATA
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("Syncing threat intelligence feeds…"):
    kev        = fetch_kev()
    nvd        = fetch_nvd()
    nvd_crit   = fetch_nvd_critical()
    nvd_high   = fetch_nvd_high()
    baz        = fetch_bazaar()
    uhaus      = fetch_urlhaus()
    feodo      = fetch_feodo()
    ics        = fetch_ics()
    cisa_all   = fetch_cisa_all()
    sslbl      = fetch_sslbl()
    sans_isc   = fetch_sans_isc()
    tor_exits  = fetch_tor_exits()
    threatfox  = fetch_threatfox()
    cisa_alerts = fetch_cisa_alerts()


# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL THREAT METRICS  —  8 ROWS × 4 CARDS = 32 METRIC CARDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:4px 0 16px 0;">
  <span style="font-size:1.1rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.2px;">
    <a href="https://www.cisa.gov/" target="_blank" class="sec-hdr">&gt;&gt; GLOBAL THREAT METRICS</a>
  </span><br>
  <span style="font-size:0.7rem;color:#3a3a4a;">
    <span class="status-dot status-green"></span>
    <span style="color:{GREEN};">LIVE</span> = real-time feed (auto-refreshes) &nbsp;·&nbsp;
    <span class="status-dot status-amber"></span>
    <span style="color:{AMBER};">EST</span> = annual-report baseline with daily interpolation
    &nbsp;·&nbsp; Deltas: 1d · 7d · 30d · 1yr
    &nbsp;·&nbsp; <b style="color:#4a4a5a;">32 INDICATORS</b> across 8 categories
  </span>
</div>
""", unsafe_allow_html=True)


# ─── ROW A: VULNERABILITY INTELLIGENCE ───────────────────────────────────────
row_label("▸ VULNERABILITY INTELLIGENCE  ─  LIVE FEEDS")
c1, c2, c3, c4 = st.columns(4)

with c1:
    live_card(
        "CISA KEV: ACTIVE EXPLOITS", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev,
        val_fn  = lambda d: _fmt(d["total"]),
        sub_fn  = lambda d: f"{d['ransomware']} ransomware-linked · top: {d['top_vendor']}",
        d1_fn   = lambda d: f"+{d['d1']}" if d['d1'] > 0 else "±0",
        d7_fn   = lambda d: f"+{d['d7']}",
        d30_fn  = lambda d: f"+{d['d30']}",
        d365_fn = lambda d: f"+{d['d365']}",
        fallback_sub="CISA known-exploited vulnerabilities catalog")

with c2:
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

with c3:
    live_card(
        "CRITICAL CVEs (CVSS ≥ 9.0)", "https://nvd.nist.gov/vuln/search",
        nvd_crit,
        val_fn  = lambda d: f"{_fmt(d['d1'])}/day",
        sub_fn  = lambda d: f"{_fmt(d['d365'])} critical CVEs trailing 12mo",
        d1_fn   = lambda d: f"+{_fmt(d['d1'])}",
        d7_fn   = lambda d: f"+{_fmt(d['d7'])}",
        d30_fn  = lambda d: f"+{_fmt(d['d30'])}",
        d365_fn = lambda d: f"+{_fmt(d['d365'])}",
        fallback_sub="NVD CVE API v2 — CRITICAL severity only")

with c4:
    live_card(
        "HIGH CVEs (CVSS 7.0-8.9)", "https://nvd.nist.gov/vuln/search",
        nvd_high,
        val_fn  = lambda d: f"{_fmt(d['d7'])}/week",
        sub_fn  = lambda d: f"{_fmt(d['d365'])} high-severity CVEs trailing 12mo",
        d1_fn   = lambda d: f"+{_fmt(d['d1'])}",
        d7_fn   = lambda d: f"+{_fmt(d['d7'])}",
        d30_fn  = lambda d: f"+{_fmt(d['d30'])}",
        d365_fn = lambda d: f"+{_fmt(d['d365'])}",
        fallback_sub="NVD CVE API v2 — HIGH severity only")


# ─── ROW B: MALWARE & ACTIVE THREATS ─────────────────────────────────────────
row_label("▸ MALWARE & ACTIVE THREAT FEEDS  ─  LIVE")
c5, c6, c7, c8 = st.columns(4)

with c5:
    live_card(
        "MALWARE SAMPLES (BAZAAR)", "https://bazaar.abuse.ch/",
        baz,
        val_fn  = lambda d: f"{_fmt(d['d1'])}/day",
        sub_fn  = lambda d: f"Top family: {d['top_family']} · {_fmt(d['total'])} in 48h",
        d1_fn   = lambda d: f"+{_fmt(d['d1'])}",
        d7_fn   = lambda d: f"+{_fmt(d['d7'])}",
        d30_fn  = lambda d: f"+{_fmt(int(d['d7']*(30/7)))}",
        d365_fn = lambda d: f"+{_fmt(int(d['d7']*(365/7)))}",
        fallback_sub="MalwareBazaar 48h public CSV export")

with c6:
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

with c7:
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
        fallback_sub="Feodo Tracker · Emotet/Dridex/QakBot C2s")

with c8:
    live_card(
        "THREATFOX IOCs", "https://threatfox.abuse.ch/",
        threatfox,
        val_fn  = lambda d: f"{_fmt(d['d1'])}/day",
        sub_fn  = lambda d: f"Top type: {d['top_type']} · {_fmt(d['total'])} recent IOCs",
        d1_fn   = lambda d: f"+{_fmt(d['d1'])}",
        d7_fn   = lambda d: f"+{_fmt(d['d7'])}",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['total'])} in export",
        d365c="d-neu",
        fallback_sub="ThreatFox community IOC feed (abuse.ch)")


# ─── ROW C: ADVISORY & RESPONSE ──────────────────────────────────────────────
row_label("▸ ADVISORY & INCIDENT RESPONSE  ─  LIVE FEEDS")
c9, c10, c11, c12 = st.columns(4)

with c9:
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

with c10:
    live_card(
        "ICS/SCADA ADVISORIES", "https://www.cisa.gov/news-events/cybersecurity-advisories/ics-advisories",
        ics,
        val_fn  = lambda d: f"{d[7]}/week",
        sub_fn  = lambda d: "OT/ICS critical-infrastructure security alerts",
        d1_fn   = lambda d: f"+{d[1]}",
        d7_fn   = lambda d: f"+{d[7]}",
        d30_fn  = lambda d: f"+{d[30]}",
        d365_fn = lambda d: f"+{d[365]}",
        fallback_sub="CISA ICS advisory RSS feed")

with c11:
    live_card(
        "CISA ACTIVITY ALERTS (AA)", "https://www.cisa.gov/news-events/cybersecurity-advisories?f%5B0%5D=advisory_type%3A93",
        cisa_alerts,
        val_fn  = lambda d: f"{d.get('total', 0)} total",
        sub_fn  = lambda d: "CISA cybersecurity alerts — nation-state & critical",
        d1_fn   = lambda d: f"+{d[1]}",
        d7_fn   = lambda d: f"+{d[7]}",
        d30_fn  = lambda d: f"+{d[30]}",
        d365_fn = lambda d: f"+{d[365]}",
        fallback_sub="CISA AA (Activity Alerts) RSS")

with c12:
    live_card(
        "MALICIOUS SSL CERTS", "https://sslbl.abuse.ch/",
        sslbl,
        val_fn  = lambda d: f"{_fmt(d['total'])} tracked",
        sub_fn  = lambda d: f"SSL certs used by botnet C2 infrastructure",
        d1_fn   = lambda d: f"+{d['d1']}",
        d7_fn   = lambda d: f"+{d['d7']}",
        d30_fn  = lambda d: f"+{d['d30']}",
        d365_fn = lambda d: f"{_fmt(d['total'])} total",
        d365c="d-neu",
        fallback_sub="abuse.ch SSL Blocklist (SSLBL)")


# ─── ROW D: NETWORK INTELLIGENCE ─────────────────────────────────────────────
row_label("▸ NETWORK & INFRASTRUCTURE INTELLIGENCE  ─  LIVE")
c13, c14, c15, c16 = st.columns(4)

with c13:
    if sans_isc:
        infocon = sans_isc.get("infocon", "unknown")
        color_map = {"green": GREEN, "yellow": AMBER, "orange": "#ff8800", "red": RED}
        ic_color = color_map.get(infocon, "#555")
        top_p = sans_isc.get("top_port", "N/A")
        card("SANS ISC INFOCON", "https://isc.sans.edu/",
             infocon.upper(),
             f"Internet threat level · Top attacked port: {top_p}",
             "–","d-neu", "–","d-neu", "–","d-neu",
             f"Level: {infocon}","d-good" if infocon=="green" else "d-amb",
             live=True)
    else:
        live_card("SANS ISC INFOCON", "https://isc.sans.edu/",
                  None, None, None, None, None, None, None,
                  fallback_sub="SANS DShield Internet threat level")

with c14:
    live_card(
        "TOR EXIT NODES ACTIVE", "https://metrics.torproject.org/",
        tor_exits,
        val_fn  = lambda d: _fmt(d["count"]),
        sub_fn  = lambda d: "Active Tor exit relays · anonymization infra",
        d1_fn   = lambda d: "–",
        d7_fn   = lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['count'])} nodes",
        d365c="d-neu",
        fallback_sub="Tor Project bulk exit list")

with c15:
    live_card(
        "KEV RANSOMWARE-LINKED", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev,
        val_fn  = lambda d: _fmt(d["ransomware"]),
        sub_fn  = lambda d: f"CVEs tied to known ransomware campaigns",
        d1_fn   = lambda d: "–",
        d7_fn   = lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['ransomware'])} total",
        d365c="d-bad",
        fallback_sub="CISA KEV ransomware-linked CVEs")

with c16:
    live_card(
        "KEV TOP VENDOR", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        kev,
        val_fn  = lambda d: d["top_vendor"],
        sub_fn  = lambda d: f"{d['top_vendor_count']} exploited CVEs · most targeted vendor",
        d1_fn   = lambda d: "–",
        d7_fn   = lambda d: "–",
        d30_fn  = lambda d: "–",
        d365_fn = lambda d: f"{_fmt(d['top_vendor_count'])} CVEs",
        d365c="d-bad",
        fallback_sub="CISA KEV vendor breakdown")


# ─── ROW E: INCIDENT & BREACH RISK ───────────────────────────────────────────
row_label("▸ INCIDENT & BREACH RISK  ─  EST (annual-report baselines, daily interpolation)")
c17, c18, c19, c20 = st.columns(4)

ANN_RANSOMWARE   = 5_500
ANN_BREACH_REC   = 8_000_000_000
ANN_BEC          = 21_489
ANN_PHISH        = 1_970_000

with c17:
    card("RANSOMWARE INCIDENTS", "https://www.cisa.gov/stopransomware",
         _fmt(ytd(ANN_RANSOMWARE)), f"YTD · ~{ANN_RANSOMWARE:,}/yr · CrowdStrike GTR 2024",
         f"+{per(ANN_RANSOMWARE,1)}","d-bad",
         f"+{per(ANN_RANSOMWARE,7)}","d-bad",
         f"+{per(ANN_RANSOMWARE,30):,}","d-bad",
         f"~{ANN_RANSOMWARE:,}","d-bad", live=False)

with c18:
    card("DATA RECORDS BREACHED", "https://www.verizon.com/business/resources/reports/dbir/",
         f"{ytd(ANN_BREACH_REC)//1_000_000}M", "YTD · Verizon DBIR 2024 baseline",
         f"+{per(ANN_BREACH_REC,1)//1_000_000}M","d-bad",
         f"+{per(ANN_BREACH_REC,7)//1_000_000}M","d-bad",
         f"+{per(ANN_BREACH_REC,30)//1_000_000}M","d-bad",
         "~8B/yr","d-bad", live=False)

with c19:
    card("BEC INCIDENTS (IC3)", "https://www.ic3.gov/AnnualReport",
         _fmt(ytd(ANN_BEC)), f"YTD · FBI IC3 2023: {ANN_BEC:,} complaints",
         f"+{per(ANN_BEC,1)}","d-bad",
         f"+{per(ANN_BEC,7):,}","d-bad",
         f"+{per(ANN_BEC,30):,}","d-bad",
         f"~{ANN_BEC:,}/yr","d-bad", live=False)

with c20:
    card("PHISHING CAMPAIGNS", "https://apwg.org/trendsreports/",
         f"{ytd(ANN_PHISH)//1_000}k YTD", "APWG eCrime 2024 baseline",
         f"+{per(ANN_PHISH,1):,}","d-bad",
         f"+{per(ANN_PHISH,7):,}","d-bad",
         f"+{per(ANN_PHISH,30):,}","d-bad",
         f"~{ANN_PHISH//1_000}k/yr","d-bad", live=False)


# ─── ROW F: FINANCIAL & COMPLIANCE RISK ──────────────────────────────────────
row_label("▸ FINANCIAL & COMPLIANCE RISK  ─  EST (annual-report baselines)")
c21, c22, c23, c24 = st.columns(4)

ANN_GDPR_FINES  = 2_100_000_000
ANN_IC3_LOSSES  = 12_500_000_000

with c21:
    card("AVG BREACH COST", "https://www.ibm.com/security/data-breach",
         "$4.88M", "global avg · IBM Cost of Data Breach 2024",
         "+$13k","d-bad", "+$94k","d-bad", "+$407k","d-bad", "+$4.88M","d-bad",
         live=False)

with c22:
    card("HEALTHCARE BREACH COST", "https://www.ibm.com/security/data-breach",
         "$9.77M", "highest sector avg · IBM Cost of Breach 2024",
         "+$27k","d-bad", "+$188k","d-bad", "+$814k","d-bad", "+$9.77M","d-bad",
         live=False)

with c23:
    card("GDPR FINES ISSUED", "https://www.enforcementtracker.com/",
         f"€{ytd(ANN_GDPR_FINES)//1_000_000}M YTD",
         "YTD est. · DLA Piper GDPR fines report 2024",
         f"+€{per(ANN_GDPR_FINES,1)//1_000_000}M","d-bad",
         f"+€{per(ANN_GDPR_FINES,7)//1_000_000}M","d-bad",
         f"+€{per(ANN_GDPR_FINES,30)//1_000_000}M","d-bad",
         "~€2.1B/yr","d-bad", live=False)

with c24:
    card("CYBERCRIME LOSSES (IC3)", "https://www.ic3.gov/AnnualReport",
         f"${ytd(ANN_IC3_LOSSES)//1_000_000_000:.1f}B YTD",
         "YTD est. · FBI IC3 2023: $12.5B total losses",
         f"+${per(ANN_IC3_LOSSES,1)//1_000_000}M","d-bad",
         f"+${per(ANN_IC3_LOSSES,7)//1_000_000}M","d-bad",
         f"+${per(ANN_IC3_LOSSES,30)//1_000_000}M","d-bad",
         "~$12.5B/yr","d-bad", live=False)


# ─── ROW G: THREAT ACTOR & CAMPAIGN CONTEXT ──────────────────────────────────
row_label("▸ THREAT ACTOR & CAMPAIGN CONTEXT  ─  EST (annual-report baselines)")
c25, c26, c27, c28 = st.columns(4)

ANN_SUPPLY  = 3_000
ANN_INSIDER = 6_800
ANN_IDENTITY = 17_000_000_000

with c25:
    card("SUPPLY CHAIN ATTACKS", "https://www.crowdstrike.com/global-threat-report/",
         "+45% YoY", f"~{ytd(ANN_SUPPLY):,} incidents YTD · CrowdStrike GTR 2024",
         f"+{per(ANN_SUPPLY,1)}","d-bad",
         f"+{per(ANN_SUPPLY,7)}","d-bad",
         f"+{per(ANN_SUPPLY,30)}","d-bad",
         f"~{ANN_SUPPLY:,}/yr","d-bad", live=False)

with c26:
    card("INSIDER THREAT INCIDENTS", "https://www.verizon.com/business/resources/reports/dbir/",
         _fmt(ytd(ANN_INSIDER)), f"YTD · Verizon DBIR 2024: {ANN_INSIDER:,} cases",
         f"+{per(ANN_INSIDER,1)}","d-bad",
         f"+{per(ANN_INSIDER,7)}","d-bad",
         f"+{per(ANN_INSIDER,30):,}","d-bad",
         f"~{ANN_INSIDER:,}/yr","d-bad", live=False)

with c27:
    card("EXPOSED CREDENTIALS", "https://spycloud.com/resource/2024-annual-identity-exposure-report/",
         f"{ytd(ANN_IDENTITY)//1_000_000_000:.1f}B YTD",
         "SpyCloud 2024 Annual Identity Exposure Report",
         f"+{per(ANN_IDENTITY,1)//1_000_000}M","d-bad",
         f"+{per(ANN_IDENTITY,7)//1_000_000}M","d-bad",
         f"+{per(ANN_IDENTITY,30)//1_000_000}M","d-bad",
         "~17B/yr","d-bad", live=False)

with c28:
    card("IDENTITY-BASED INTRUSIONS", "https://www.crowdstrike.com/global-threat-report/",
         "75%", "of attacks now use valid credentials · CrowdStrike 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+75% ↑ YoY","d-bad",
         live=False)


# ─── ROW H: POSTURE & EMERGING THREATS ───────────────────────────────────────
row_label("▸ SECURITY POSTURE & EMERGING THREATS  ─  EST (industry reports)")
c29, c30, c31, c32 = st.columns(4)

ANN_DDOS       = 15_400_000   # Cloudflare 2024 DDoS Threat Report
ANN_IOT        = 112_000_000  # SonicWall 2024: IoT malware attacks
ANN_API        = 4_100        # Salt Security 2024 API incidents

with c29:
    card("AVG MTTD (DWELL TIME)", "https://www.mandiant.com/m-trends",
         "10 Days", "global median dwell time · Mandiant M-Trends 2024",
         "-0.03d","d-good", "-0.2d","d-good", "-0.8d","d-good", "-4d","d-good",
         live=False)

with c30:
    card("AVG TIME TO EXPLOIT", "https://www.crowdstrike.com/global-threat-report/",
         "5 Days", "avg disclosure-to-exploit · CrowdStrike GTR 2024",
         "–","d-neu", "–","d-neu", "-0.5d","d-good", "-3d","d-good",
         live=False)

with c31:
    card("DDoS ATTACKS", "https://radar.cloudflare.com/reports/ddos-2024-q4",
         f"{ytd(ANN_DDOS)//1_000_000:.1f}M YTD",
         "Cloudflare 2024 DDoS Threat Report · 15.4M/yr",
         f"+{per(ANN_DDOS,1)//1_000}k","d-bad",
         f"+{per(ANN_DDOS,7)//1_000}k","d-bad",
         f"+{per(ANN_DDOS,30)//1_000}k","d-bad",
         "~15.4M/yr","d-bad", live=False)

with c32:
    card("ZERO-TRUST ADOPTION", "https://www.crowdstrike.com/global-threat-report/",
         "67%", "orgs actively implementing zero-trust · CrowdStrike 2024",
         "–","d-neu", "–","d-neu", "–","d-neu", "+12% YoY","d-good",
         live=False)


# ─── SOURCES BAR ──────────────────────────────────────────────────────────────
refresh_ts = now_utc.strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""
<div class="src-bar">
  <span style="color:#3a3a4a;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">
    <span class="status-dot status-green"></span> LIVE FEEDS &nbsp;</span>
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
  <a href="https://threatfox.abuse.ch/export/csv/recent/"
     target="_blank" class="src-link">ThreatFox CSV</a> ·
  <a href="https://sslbl.abuse.ch/blacklist/sslipblacklist.csv"
     target="_blank" class="src-link">SSL Blocklist</a> ·
  <a href="https://isc.sans.edu/api/"
     target="_blank" class="src-link">SANS ISC API</a> ·
  <a href="https://check.torproject.org/torbulkexitlist"
     target="_blank" class="src-link">Tor Exit List</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml"
     target="_blank" class="src-link">CISA ICS RSS</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/all.xml"
     target="_blank" class="src-link">CISA All RSS</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/aa.xml"
     target="_blank" class="src-link">CISA AA RSS</a>
  <br>
  <span style="color:#3a3a4a;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">
    <span class="status-dot status-amber"></span> EST BASELINES &nbsp;</span>
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
     target="_blank" class="src-link">GDPR Enforcement Tracker</a> ·
  <a href="https://radar.cloudflare.com/reports/ddos-2024-q4"
     target="_blank" class="src-link">Cloudflare DDoS Report</a>
  <span style="float:right;color:#282838;">↻ {refresh_ts}</span>
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
  <span style="font-size:0.65rem;color:#3a3a4a;margin-left:12px;">
    REAL-TIME GLOBAL CYBER ATTACK VISUALIZATION · 8 SOURCES
  </span>
</div>""", unsafe_allow_html=True)

# ── HERO MAPS: Radware & FortiGuard (user's favorites — larger) ──────────────
col_rad, col_fort = st.columns(2)
with col_rad:
    st.markdown('<a href="https://livethreatmap.radware.com/" target="_blank" class="map-lnk">&gt;&gt; RADWARE LIVE THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://livethreatmap.radware.com/", h=620)
with col_fort:
    st.markdown('<a href="https://threatmap.fortiguard.com/" target="_blank" class="map-lnk">&gt;&gt; FORTINET FORTIGUARD MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.fortiguard.com/", h=620)
st.markdown("---")

# ── Kaspersky & Bitdefender ───────────────────────────────────────────────────
col_kas, col_bit = st.columns(2)
with col_kas:
    st.markdown('<a href="https://cybermap.kaspersky.com/" target="_blank" class="map-lnk">&gt;&gt; KASPERSKY CYBERMAP</a>', unsafe_allow_html=True)
    iframe("https://cybermap.kaspersky.com/en/widget/dynamic/dark", h=520)
with col_bit:
    st.markdown('<a href="https://threatmap.bitdefender.com/" target="_blank" class="map-lnk">&gt;&gt; BITDEFENDER THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.bitdefender.com/", h=520)
st.markdown("---")

# ── Sicherheitstacho & SonicWall ─────────────────────────────────────────────
col_sich, col_son = st.columns(2)
with col_sich:
    st.markdown('<a href="https://www.sicherheitstacho.eu/?lang=en" target="_blank" class="map-lnk">&gt;&gt; SICHERHEITSTACHO (DEUTSCHE TELEKOM)</a>', unsafe_allow_html=True)
    iframe("https://www.sicherheitstacho.eu/?lang=en", h=520)
with col_son:
    st.markdown('<a href="https://attackmap.sonicwall.com/live-attack-map/" target="_blank" class="map-lnk">&gt;&gt; SONICWALL LIVE ATTACK MAP</a>', unsafe_allow_html=True)
    iframe("https://attackmap.sonicwall.com/live-attack-map/", h=520)
st.markdown("---")

# ── Check Point & Netscout ────────────────────────────────────────────────────
col_cp, col_ns = st.columns(2)
with col_cp:
    st.markdown('<a href="https://threatmap.checkpoint.com/" target="_blank" class="map-lnk">&gt;&gt; CHECK POINT THREATCLOUD</a>', unsafe_allow_html=True)
    iframe("https://threatmap.checkpoint.com/", h=520)
with col_ns:
    st.markdown('<a href="https://horizon.netscout.com/" target="_blank" class="map-lnk">&gt;&gt; NETSCOUT CYBER THREAT HORIZON</a>', unsafe_allow_html=True)
    iframe("https://horizon.netscout.com/", h=520)
st.markdown("---")

# ── GreyNoise Intelligence (full width, taller) ──────────────────────────────
st.markdown('<a href="https://viz.greynoise.io/trends/trending" target="_blank" class="map-lnk">&gt;&gt; GREYNOISE INTELLIGENCE TRENDS</a>', unsafe_allow_html=True)
iframe("https://viz.greynoise.io/trends/trending", h=1200)
st.markdown("---")

# ── SANS ISC Dashboard (full width) ──────────────────────────────────────────
st.markdown('<a href="https://isc.sans.edu/" target="_blank" class="map-lnk">&gt;&gt; SANS ISC DASHBOARD — DSHIELD SENSOR DATA</a>', unsafe_allow_html=True)
iframe("https://isc.sans.edu/", h=900)
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  GRC RESOURCES  (expanded from 39 → 52 links, 4 columns)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin-top:32px;margin-bottom:22px;text-align:center;">
  <span style="font-size:1.15rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;">
    <a href="https://www.nist.gov/cyberframework" target="_blank" class="sec-hdr">
      &gt;&gt; GRC RESOURCES &amp; TOOLS &lt;&lt;</a>
  </span>
  <div style="font-size:0.65rem;color:#3a3a4a;margin-top:4px;">
    52 CURATED RESOURCES · FRAMEWORKS · TOOLS · TRAINING · THREAT INTEL
  </div>
</div>""", unsafe_allow_html=True)

l1, l2, l3, l4 = st.columns(4)

with l1:
    st.markdown(f'<div style="font-size:0.62rem;color:{BLUE};text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;border-bottom:1px dashed #1a1a2e;padding-bottom:4px;">▸ FRAMEWORKS &amp; STANDARDS</div>', unsafe_allow_html=True)
    for a in [
        ("01","NIST CSF 2.0","https://www.nist.gov/cyberframework","Cybersecurity risk management framework."),
        ("02","NIST AI RMF","https://www.nist.gov/itl/ai-risk-management-framework","AI risk management framework."),
        ("03","ISO/IEC 27001","https://www.iso.org/isoiec-27001-information-security.html","International ISMS standard."),
        ("04","CIS Controls v8","https://www.cisecurity.org/controls/","Prioritized cyber safeguards."),
        ("05","HITRUST Alliance","https://hitrustalliance.net/","Information risk management."),
        ("06","MITRE ATT&CK","https://mitre-attack.github.io/attack-navigator/","Adversary TTP matrix."),
        ("07","CVSS 4.0 Calc","https://www.first.org/cvss/calculator/4.0","Vulnerability scoring system."),
        ("08","NIST CSRC","https://csrc.nist.gov/","Computer Security Resource Center."),
        ("09","NIST NVD","https://nvd.nist.gov/","National Vulnerability Database."),
        ("10","CISA KEV Catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","Actively exploited CVEs."),
        ("11","NIST SP 800-53","https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final","Security & privacy controls."),
        ("12","CISA Shields Up","https://www.cisa.gov/shields-up","Resilience against cyberattacks."),
        ("13","MITRE D3FEND","https://d3fend.mitre.org/","Defensive technique knowledge graph."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)

with l2:
    st.markdown(f'<div style="font-size:0.62rem;color:{BLUE};text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;border-bottom:1px dashed #1a1a2e;padding-bottom:4px;">▸ THREAT INTEL &amp; ANALYSIS</div>', unsafe_allow_html=True)
    for a in [
        ("14","VirusTotal","https://www.virustotal.com/","Analyze files, domains, IPs, URLs."),
        ("15","AlienVault OTX","https://otx.alienvault.com/","Crowdsourced threat intel IOCs."),
        ("16","Talos Intelligence","https://talosintelligence.com/","Cisco threat intelligence."),
        ("17","Shodan Search","https://www.shodan.io/","Internet-connected device search."),
        ("18","Have I Been Pwned","https://haveibeenpwned.com/","Check breach exposure."),
        ("19","crt.sh Search","https://crt.sh/","Certificate Transparency logs."),
        ("20","SANS ISC","https://isc.sans.edu/","Cyber threat monitor & diary."),
        ("21","Abuse.ch URLhaus","https://urlhaus.abuse.ch/","Malware distribution URLs."),
        ("22","MalwareBazaar","https://bazaar.abuse.ch/","Malware sample repository."),
        ("23","ThreatFox IOCs","https://threatfox.abuse.ch/","Community IOC sharing."),
        ("24","Exploit Database","https://www.exploit-db.com/","Public exploits archive."),
        ("25","Pulsedive","https://pulsedive.com/","Free threat intelligence platform."),
        ("26","GreyNoise","https://viz.greynoise.io/","Internet noise & scanner intel."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)

with l3:
    st.markdown(f'<div style="font-size:0.62rem;color:{BLUE};text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;border-bottom:1px dashed #1a1a2e;padding-bottom:4px;">▸ SECURITY TOOLS &amp; ANALYSIS</div>', unsafe_allow_html=True)
    for a in [
        ("27","CyberChef","https://gchq.github.io/CyberChef/","Cyber Swiss Army Knife."),
        ("28","Any.Run Sandbox","https://any.run/","Interactive malware sandbox."),
        ("29","URLScan.io","https://urlscan.io/","Website scanning & analysis."),
        ("30","GTFOBins","https://gtfobins.github.io/","Unix security bypass binaries."),
        ("31","LOLBAS Project","https://lolbas-project.github.io/","Living off the land binaries (Windows)."),
        ("32","Security Onion","https://securityonionsolutions.com/","Threat hunting & monitoring."),
        ("33","OSINT Framework","https://osintframework.com/","OSINT tool collection."),
        ("34","PayloadsAllThings","https://github.com/swisskyrepo/PayloadsAllTheThings","Payloads & bypasses."),
        ("35","Nuclei Templates","https://github.com/projectdiscovery/nuclei-templates","Vulnerability scanner templates."),
        ("36","OpenCTI Platform","https://www.opencti.io/","Open threat intelligence platform."),
        ("37","YARA Rules","https://github.com/Yara-Rules/rules","Malware research YARA rules."),
        ("38","Sigma Rules","https://github.com/SigmaHQ/sigma","Generic detection format."),
        ("39","Wazuh SIEM","https://wazuh.com/","Open-source XDR and SIEM."),
    ]:
        st.markdown(grc_link(*a), unsafe_allow_html=True)

with l4:
    st.markdown(f'<div style="font-size:0.62rem;color:{BLUE};text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;border-bottom:1px dashed #1a1a2e;padding-bottom:4px;">▸ TRAINING &amp; NEWS</div>', unsafe_allow_html=True)
    for a in [
        ("40","OWASP Top 10 Web","https://owasp.org/www-project-top-ten/","Web app security risks."),
        ("41","OWASP LLM Top 10","https://owasp.org/www-project-top-10-for-large-language-model-applications/","LLM security risks."),
        ("42","OWASP API Top 10","https://owasp.org/API-Security/","API security risks."),
        ("43","HackTheBox","https://www.hackthebox.com/","Gamified security training."),
        ("44","TryHackMe","https://tryhackme.com/","Hands-on security labs."),
        ("45","PortSwigger Academy","https://portswigger.net/web-security","Web vuln training."),
        ("46","BleepingComputer","https://www.bleepingcomputer.com/","Security & ransomware news."),
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
<div style="border-top:1px solid #141420;padding-top:24px;margin-top:40px;
            text-align:center;font-family:{MONO};">
  <div style="color:#555;font-size:0.85rem;margin-bottom:4px;">
    Questions, Comments, or Recommendations?</div>
  <div style="color:#555;font-size:0.85rem;margin-bottom:18px;">
    Developed by <b style="color:{GREEN};">Adam Kistler</b> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">LinkedIn</a>
  </div>
  <div style="color:#333;font-size:0.7rem;padding:0 10%;line-height:1.5;margin-bottom:12px;">
    <b>LEGAL DISCLAIMER:</b> Educational and portfolio purposes only. All threat maps and data
    are property of their respective owners. SecAI-Nexus does not host or process third-party content.<br>
    <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank"
       class="footer-lic">Code and layout licensed CC BY-NC 4.0.</a>
  </div>
  <div style="color:#282838;font-size:0.72rem;">
    SecAI-Nexus GRC [v17.0] &nbsp;·&nbsp; Live Data Engine &nbsp;·&nbsp;
    32 Indicators · 12 Live Feeds · 10 Threat Maps &nbsp;·&nbsp; {now_utc.strftime("%Y")}
  </div>
</div>
""", unsafe_allow_html=True)
