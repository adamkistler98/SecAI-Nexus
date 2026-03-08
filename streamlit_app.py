import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SecAI-Nexus GRC",
    layout="wide",
    page_icon="🔒",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
MONO = "'Courier New', Courier, monospace"
GREEN = "#00ff41"
BLUE  = "#008aff"
RED   = "#ff4b4b"
BG    = "#050505"
CARD  = "#0a0a0a"

st.markdown(f"""
<style>
  .stApp {{ background-color:{BG} !important; font-family:{MONO} !important; }}
  div[data-testid="stMarkdownContainer"] > p {{
      color:{GREEN}; font-size:1.1rem; line-height:1.6;
      font-family:{MONO}; font-weight:normal;
  }}
  h1,h2,h3,h4,h5,h6,label {{ color:{GREEN} !important; }}
  header,footer {{ visibility:hidden; }}
  .stDeployButton {{ display:none; }}

  /* ── METRIC CARD ── */
  .cm {{
      background:{CARD}; border:1px solid #222;
      border-left:4px solid {BLUE};
      padding:12px 14px; margin-bottom:14px;
      font-family:{MONO};
  }}
  .cm-title a {{
      color:{BLUE}; font-size:0.78rem; font-weight:bold;
      text-transform:uppercase; letter-spacing:0.6px;
      text-decoration:none; transition:0.25s;
  }}
  .cm-title a:hover {{ color:{GREEN}; text-shadow:0 0 6px {GREEN}; border-bottom:1px dashed {GREEN}; }}
  .cm-badge-live {{
      font-size:0.6rem; color:{GREEN}; border:1px solid {GREEN};
      padding:1px 4px; margin-left:5px; vertical-align:middle;
  }}
  .cm-badge-est {{
      font-size:0.6rem; color:#666; border:1px solid #444;
      padding:1px 4px; margin-left:5px; vertical-align:middle;
  }}
  .cm-badge-err {{
      font-size:0.6rem; color:{RED}; border:1px solid {RED};
      padding:1px 4px; margin-left:5px; vertical-align:middle;
  }}
  .cm-val  {{ color:{GREEN}; font-size:1.75rem; font-weight:bold; margin:6px 0; }}
  .cm-sub  {{ font-size:0.72rem; color:#555; margin-top:-4px; margin-bottom:6px; }}
  .cm-deltas {{ font-size:0.8rem; border-top:1px dashed #222; padding-top:6px; line-height:1.7; }}
  .d-bad  {{ color:{RED};   font-weight:bold; }}
  .d-good {{ color:{GREEN}; font-weight:bold; }}
  .d-neu  {{ color:{BLUE};  font-weight:bold; }}

  /* ── SECTION HEADER ── */
  .sec-hdr {{ color:{GREEN}; text-decoration:none; transition:0.25s; }}
  .sec-hdr:hover {{ color:{BLUE}; text-shadow:0 0 6px {BLUE}; }}

  /* ── SOURCE LINKS ── */
  .src-link {{
      color:{BLUE}; font-weight:bold; text-decoration:none;
      border-bottom:1px dashed #333; padding-bottom:1px; transition:0.25s;
  }}
  .src-link:hover {{ color:{GREEN}; border-bottom:1px dashed {GREEN}; text-shadow:0 0 5px {GREEN}; }}

  /* ── MAP TITLES ── */
  .map-lnk {{
      color:{BLUE}; font-size:1rem; font-weight:bold; text-transform:uppercase;
      text-decoration:none; transition:0.25s; display:inline-block; margin-bottom:8px;
  }}
  .map-lnk:hover {{ color:{GREEN}; text-shadow:0 0 6px {GREEN}; }}

  /* ── GRC RESOURCE LINKS ── */
  .res-link {{
      color:{BLUE}; font-weight:bold; font-size:1.0rem;
      text-decoration:none; border-bottom:1px dashed {BLUE};
  }}
  .res-link:hover {{ color:{GREEN}; border-bottom:1px dashed {GREEN}; }}

  /* ── FOOTER ── */
  .footer-lic {{ color:#444; text-decoration:none; border-bottom:1px dashed #444; transition:0.25s; }}
  .footer-lic:hover {{ color:{GREEN}; border-bottom:1px dashed {GREEN}; }}

  /* ── DIVIDERS ── */
  hr {{ border-color:#1a1a1a !important; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LIVE DATA FETCHERS  (all free, no API key required)
# ══════════════════════════════════════════════════════════════════════════════
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "SecAI-Nexus-GRC/2.0 (educational-dashboard)"})

def _get(url, **kw):
    try:
        r = SESSION.get(url, timeout=12, **kw)
        r.raise_for_status()
        return r
    except Exception:
        return None

# ── 1. CISA KEV ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_kev():
    """CISA KEV JSON — fully public, no key."""
    r = _get("https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json")
    if not r:
        return None
    try:
        vulns = r.json().get("vulnerabilities", [])
        now = datetime.now(timezone.utc)
        counts = {1: 0, 7: 0, 30: 0, 365: 0}
        ransomware = 0
        for v in vulns:
            try:
                age = (now - datetime.strptime(v["dateAdded"], "%Y-%m-%d").replace(tzinfo=timezone.utc)).days
                for d in counts:
                    if age <= d:
                        counts[d] += 1
            except Exception:
                pass
            if v.get("knownRansomwareCampaignUse", "").lower() == "known":
                ransomware += 1
        return {"total": len(vulns), "d1": counts[1], "d7": counts[7],
                "d30": counts[30], "d365": counts[365], "ransomware": ransomware}
    except Exception:
        return None

# ── 2. NVD CVE API v2 ──────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nvd():
    """NVD CVE API v2 — no key (5 req / 30 s), uses single efficient call."""
    now = datetime.now(timezone.utc)
    # One call for 365-day window; derive shorter windows from same dataset
    start = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S.000")
    end   = now.strftime("%Y-%m-%dT%H:%M:%S.000")
    params = {"pubStartDate": start, "pubEndDate": end, "resultsPerPage": 1}
    r = _get("https://services.nvd.nist.gov/rest/json/cves/2.0",
             params=params, timeout=20)
    if not r:
        return None
    try:
        total_year = r.json().get("totalResults", 0)
        # Estimate shorter windows proportionally (avoids extra API calls / rate limiting)
        return {
            "d365": total_year,
            "d30":  int(total_year / 12),
            "d7":   int(total_year / 52),
            "d1":   int(total_year / 365),
        }
    except Exception:
        return None

# ── 3. MalwareBazaar — public CSV export (no key needed) ──────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_bazaar():
    """
    MalwareBazaar recent.csv — generated every 5 min, contains last 48 h.
    Public URL, no auth key required for the CSV exports.
    """
    r = _get("https://bazaar.abuse.ch/export/csv/recent/", timeout=20)
    if not r:
        return None
    try:
        lines = [l for l in r.text.splitlines() if l and not l.startswith("#")]
        now = datetime.now(timezone.utc)
        d1 = d7 = 0
        for line in lines:
            parts = line.split('","')
            if not parts:
                continue
            ts_raw = parts[0].strip('"')
            try:
                dt = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                age = (now - dt).days
                if age <= 1:  d1 += 1
                if age <= 7:  d7 += 1
            except Exception:
                pass
        return {"d1": d1, "d7": d7, "total_in_feed": len(lines)}
    except Exception:
        return None

# ── 4. URLhaus plaintext feed (no key) ────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_urlhaus():
    """
    URLhaus text_online feed — active malicious URLs only.
    Updated every 5 min, completely public.
    """
    r = _get("https://urlhaus.abuse.ch/downloads/text_online/", timeout=15)
    if not r:
        return None
    lines = [l.strip() for l in r.text.splitlines()
             if l.strip() and not l.startswith("#")]
    return {"online": len(lines)}

# ── 5. Feodo Tracker CSV (no key) ─────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_feodo():
    """Feodo Tracker C2 IP blocklist CSV — public, no key."""
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

# ── 6. CISA ICS Advisories RSS (no key) ───────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ics_rss():
    """CISA ICS advisory RSS feed — public."""
    r = _get("https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml", timeout=15)
    if not r:
        return None
    try:
        root = ET.fromstring(r.content)
        now  = datetime.now(timezone.utc)
        items = root.findall(".//item")
        counts = {1: 0, 7: 0, 30: 0, 365: 0}
        for item in items:
            pub = item.findtext("pubDate", "")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt  = datetime.strptime(pub.strip(), fmt)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    for d in counts:
                        if age <= d:
                            counts[d] += 1
                    break
                except ValueError:
                    continue
        return counts
    except Exception:
        return None

# ── 7. CISA Advisories RSS (all, not just ICS) ────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cisa_all_rss():
    r = _get("https://www.cisa.gov/cybersecurity-advisories/all.xml", timeout=15)
    if not r:
        return None
    try:
        root  = ET.fromstring(r.content)
        now   = datetime.now(timezone.utc)
        items = root.findall(".//item")
        counts = {1: 0, 7: 0, 30: 0, 365: 0}
        for item in items:
            pub = item.findtext("pubDate", "")
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt = datetime.strptime(pub.strip(), fmt)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    age = (now - dt).days
                    for d in counts:
                        if age <= d:
                            counts[d] += 1
                    break
                except ValueError:
                    continue
        return counts
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _fmt(n):
    if isinstance(n, int):
        if   n >= 1_000_000: return f"{n/1_000_000:.1f}M"
        elif n >= 1_000:     return f"{n:,}"
        return str(n)
    return str(n)

def _delta(n, bad_if_positive=True):
    """Return (label, css_class)."""
    if n == 0:
        return "±0", "d-neu"
    sign = "+" if n > 0 else ""
    val  = f"{sign}{_fmt(n)}"
    if bad_if_positive:
        cls = "d-bad" if n > 0 else "d-good"
    else:
        cls = "d-good" if n > 0 else "d-bad"
    return val, cls

def metric_card(title, url, value, subtitle,
                d1, d1c, d7, d7c, d30, d30c, d365, d365c,
                badge="live"):
    b = {"live": f'<span class="cm-badge-live">LIVE</span>',
         "est":  f'<span class="cm-badge-est">EST</span>',
         "err":  f'<span class="cm-badge-err">⚠ OFFLINE</span>'}.get(badge, "")
    st.markdown(f"""
<div class="cm">
  <div class="cm-title"><a href="{url}" target="_blank">{title}</a>{b}</div>
  <div class="cm-val">{value}</div>
  <div class="cm-sub">{subtitle}</div>
  <div class="cm-deltas">
    <span style="color:#555;">1d:</span> <span class="{d1c}">{d1}</span> &nbsp;
    <span style="color:#555;">7d:</span> <span class="{d7c}">{d7}</span> &nbsp;
    <span style="color:#555;">30d:</span> <span class="{d30c}">{d30}</span> &nbsp;
    <span style="color:#555;">1yr:</span> <span class="{d365c}">{d365}</span>
  </div>
</div>""", unsafe_allow_html=True)

def est_card(title, url, value, subtitle,
             d1, d1c, d7, d7c, d30, d30c, d365, d365c):
    metric_card(title, url, value, subtitle, d1, d1c, d7, d7c,
                d30, d30c, d365, d365c, badge="est")

def err_card(title, url, value, subtitle,
             d1, d1c, d7, d7c, d30, d30c, d365, d365c):
    metric_card(title, url, value, subtitle, d1, d1c, d7, d7c,
                d30, d30c, d365, d365c, badge="err")

def iframe(url, h=1100):
    st.markdown(
        f'<iframe src="{url}" width="100%" height="{h}" style="border:none;" '
        f'sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>',
        unsafe_allow_html=True)

def grc_link(num, title, url, desc):
    return (
        f'<div style="margin-bottom:16px;">'
        f'<span style="color:{GREEN};font-weight:bold;">{num}.</span> '
        f'<a href="{url}" target="_blank" class="res-link">{title}</a>'
        f'<div style="color:{GREEN};font-size:0.82rem;margin-top:3px;padding-left:28px;line-height:1.4;">{desc}</div>'
        f'</div>'
    )


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
st.markdown(f"""
<div style="border-bottom:2px solid #1a1a1a;padding-bottom:10px;margin-bottom:18px;margin-top:-50px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;">
    <div>
      <span style="font-size:1.35rem;font-weight:bold;color:{GREEN};text-shadow:0 0 8px {GREEN};">🔒 SecAI-Nexus</span>
      <span style="font-size:0.9rem;color:{BLUE};margin-left:10px;font-weight:bold;">// CYBER THREAT OBSERVABILITY PLATFORM</span>
    </div>
    <div style="font-size:0.95rem;font-weight:bold;color:{BLUE};text-shadow:0 0 5px {BLUE};">
      SYS_TIME: {now_utc.strftime("%H:%M:%S")} UTC &nbsp;|&nbsp; {now_utc.strftime("%Y-%m-%d")}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FETCH ALL DATA UPFRONT
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("🔄 Pulling live threat intelligence feeds..."):
    kev    = fetch_kev()
    nvd    = fetch_nvd()
    baz    = fetch_bazaar()
    uhaus  = fetch_urlhaus()
    feodo  = fetch_feodo()
    ics    = fetch_ics_rss()
    cisa_a = fetch_cisa_all_rss()


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION: GLOBAL THREAT METRICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:10px 0 18px 0;line-height:1.3;">
  <span style="font-size:1.1rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.2px;">
    <a href="https://www.cisa.gov/" target="_blank" class="sec-hdr">&gt;&gt; GLOBAL THREAT METRICS</a>
  </span><br>
  <span style="font-size:0.78rem;color:#555;">
    <span style="color:{GREEN};">LIVE</span> = real-time API feed &nbsp;|&nbsp;
    <span style="color:#666;">EST</span> = annual-report baseline (DBIR · M-Trends · CrowdStrike GTR · FBI IC3)
    &nbsp;|&nbsp; Deltas: 1d · 7d · 30d · 1yr
  </span>
</div>
""", unsafe_allow_html=True)

# ─── ROW 1: Vulnerability Intelligence (most critical for GRC) ───────────────
r1c1, r1c2, r1c3, r1c4 = st.columns(4)

# M1 — CISA KEV Total (LIVE)
with r1c1:
    if kev:
        d1v,d1c = _delta(kev["d1"], True); d7v,d7c = _delta(kev["d7"], True)
        d30v,d30c = _delta(kev["d30"], True); d365v,d365c = _delta(kev["d365"], True)
        metric_card(
            "CISA KEV: EXPLOITED CVEs",
            "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            _fmt(kev["total"]), f"{kev['ransomware']} linked to ransomware campaigns",
            d1v,d1c, d7v,d7c, d30v,d30c, d365v,d365c)
    else:
        err_card("CISA KEV: EXPLOITED CVEs",
            "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            "~1,200+", "known active exploit confirmed",
            "+1","d-bad","+4","d-bad","+15","d-bad","+185","d-bad")

# M2 — KEV Added This Period (LIVE — separate view of same data)
with r1c2:
    if kev:
        metric_card(
            "KEV ADDITIONS (RECENT)",
            "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            f"+{kev['d7']}", "new known-exploited CVEs this week",
            f"+{kev['d1']}","d-bad", f"+{kev['d7']}","d-bad",
            f"+{kev['d30']}","d-bad", f"+{kev['d365']}","d-bad")
    else:
        err_card("KEV ADDITIONS (RECENT)",
            "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            "~3/week", "new known-exploited CVEs",
            "+1","d-bad","+3","d-bad","+15","d-bad","+185","d-bad")

# M3 — NVD CVEs Published (LIVE)
with r1c3:
    if nvd:
        d1v,d1c = _delta(nvd["d1"], True); d7v,d7c = _delta(nvd["d7"], True)
        d30v,d30c = _delta(nvd["d30"], True); d365v,d365c = _delta(nvd["d365"], True)
        metric_card(
            "NEW CVEs PUBLISHED (NVD)",
            "https://nvd.nist.gov/",
            _fmt(nvd["d1"]) + "/day", f"{_fmt(nvd['d365'])} CVEs in past 12 months",
            d1v,d1c, d7v,d7c, d30v,d30c, d365v,d365c)
    else:
        err_card("NEW CVEs PUBLISHED (NVD)", "https://nvd.nist.gov/",
            "~100/day","~36,000/year",
            "+100","d-bad","+700","d-bad","+3k","d-bad","+36k","d-bad")

# M4 — CISA All Advisories (LIVE)
with r1c4:
    if cisa_a:
        d1v,d1c = _delta(cisa_a[1], True); d7v,d7c = _delta(cisa_a[7], True)
        d30v,d30c = _delta(cisa_a[30], True); d365v,d365c = _delta(cisa_a[365], True)
        metric_card(
            "CISA ADVISORIES (ALL)",
            "https://www.cisa.gov/news-events/cybersecurity-advisories",
            f"{cisa_a[7]}/week", "AA · ICS · ICS-MA · Med. advisories",
            d1v,d1c, d7v,d7c, d30v,d30c, d365v,d365c)
    else:
        err_card("CISA ADVISORIES (ALL)",
            "https://www.cisa.gov/news-events/cybersecurity-advisories",
            "~10/week","all advisory types",
            "+2","d-bad","+10","d-bad","+40","d-bad","+500","d-bad")

# ─── ROW 2: Malware & Threat Actor Activity ───────────────────────────────────
r2c1, r2c2, r2c3, r2c4 = st.columns(4)

# M5 — MalwareBazaar 48h feed (LIVE)
with r2c1:
    if baz:
        d1v,d1c = _delta(baz["d1"], True); d7v,d7c = _delta(baz["d7"], True)
        metric_card(
            "MALWARE SAMPLES (BAZAAR)",
            "https://bazaar.abuse.ch/",
            _fmt(baz["d1"]) + "/day",
            f"{_fmt(baz['total_in_feed'])} samples in 48h export",
            d1v,d1c, d7v,d7c,
            f"+{_fmt(int(baz['d7']*(30/7)))}","d-bad",
            f"+{_fmt(int(baz['d7']*(365/7)))}","d-bad")
    else:
        err_card("MALWARE SAMPLES (BAZAAR)", "https://bazaar.abuse.ch/",
            "~1k/day","MalwareBazaar 48h feed",
            "+1k","d-bad","+7k","d-bad","+30k","d-bad","+365k","d-bad")

# M6 — URLhaus Online Malicious URLs (LIVE)
with r2c2:
    if uhaus:
        metric_card(
            "ACTIVE MALICIOUS URLs",
            "https://urlhaus.abuse.ch/",
            _fmt(uhaus["online"]), "currently serving malware (URLhaus feed)",
            "–","d-neu","–","d-neu","–","d-neu","3.6M+ total tracked","d-neu")
    else:
        err_card("ACTIVE MALICIOUS URLs", "https://urlhaus.abuse.ch/",
            "~1,500 online","URLhaus live feed",
            "–","d-neu","–","d-neu","–","d-neu","3.6M+ tracked","d-neu")

# M7 — Feodo Tracker C2 Servers (LIVE)
with r2c3:
    if feodo:
        online  = feodo["online"]
        total   = feodo["total"]
        o_str   = _fmt(online) if online > 0 else "0"
        note    = f"{total} tracked (incl. offline)" if total > 0 else "Post-Operation Endgame (2024)"
        badge   = "live" if total > 0 else "live"
        metric_card(
            "BOTNET C2 SERVERS (FEODO)",
            "https://feodotracker.abuse.ch/",
            o_str + " online", note,
            "–","d-neu","–","d-neu","–","d-neu",
            f"{_fmt(total)} total","d-neu")
    else:
        err_card("BOTNET C2 SERVERS (FEODO)", "https://feodotracker.abuse.ch/",
            "N/A","Feodo tracker feed",
            "–","d-neu","–","d-neu","–","d-neu","–","d-neu")

# M8 — ICS / SCADA Advisories (LIVE)
with r2c4:
    if ics:
        d1v,d1c = _delta(ics[1], True); d7v,d7c = _delta(ics[7], True)
        d30v,d30c = _delta(ics[30], True); d365v,d365c = _delta(ics[365], True)
        metric_card(
            "ICS/SCADA ADVISORIES (CISA)",
            "https://www.cisa.gov/ics",
            f"{ics[7]}/week", "OT/ICS critical-infrastructure alerts",
            d1v,d1c, d7v,d7c, d30v,d30c, d365v,d365c)
    else:
        err_card("ICS/SCADA ADVISORIES (CISA)", "https://www.cisa.gov/ics",
            "~5/week","OT/ICS alerts",
            "+1","d-bad","+5","d-bad","+20","d-bad","+250","d-bad")

# ─── ROW 3: Risk Posture (EST — no free real-time API exists) ─────────────────
st.markdown(f'<div style="font-size:0.72rem;color:#444;margin-bottom:6px;margin-top:4px;">↓ ROWS 3–4 use annual-report baselines (Verizon DBIR 2024 · Mandiant M-Trends 2024 · CrowdStrike GTR 2024 · FBI IC3 2023) with daily interpolation</div>', unsafe_allow_html=True)
r3c1, r3c2, r3c3, r3c4 = st.columns(4)

now_day  = (datetime.now(timezone.utc) - datetime(datetime.now().year, 1, 1, tzinfo=timezone.utc)).days + 1

# Helper: YTD count from annual
def ytd(annual): return int(annual * now_day / 365)

# M9 — Ransomware Incidents (EST — CrowdStrike GTR 2024: 75% increase, ~5,500 tracked incidents)
with r3c1:
    ann = 5_500
    est_card("RANSOMWARE INCIDENTS [EST]","https://www.cisa.gov/stopransomware",
        _fmt(ytd(ann)), f"YTD est. · ~{ann:,}/yr (CrowdStrike GTR 2024)",
        f"+{int(ann/365)}","d-bad",
        f"+{int(ann/52)}","d-bad",
        f"+{int(ann/12)}","d-bad",
        f"~{ann:,}","d-bad")

# M10 — Data Records Breached (EST — IBM Cost of Breach 2024: ~8B records/yr)
with r3c2:
    ann_r = 8_000_000_000
    est_card("DATA RECORDS BREACHED [EST]","https://www.verizon.com/business/resources/reports/dbir/",
        f"{ytd(ann_r)//1_000_000}M", f"YTD est. · Verizon DBIR 2024 baseline",
        f"+{int(ann_r/365)//1_000_000}M","d-bad",
        f"+{int(ann_r/52)//1_000_000}M","d-bad",
        f"+{int(ann_r/12)//1_000_000}M","d-bad",
        f"~{ann_r//1_000_000_000}B/yr","d-bad")

# M11 — Business Email Compromise (EST — FBI IC3 2023: 21,489 BEC complaints)
with r3c3:
    ann_b = 21_489
    est_card("BEC INCIDENTS [EST]","https://www.ic3.gov/",
        _fmt(ytd(ann_b)), f"YTD est. · FBI IC3 2023: {ann_b:,} complaints",
        f"+{int(ann_b/365)}","d-bad",
        f"+{int(ann_b/52)}","d-bad",
        f"+{int(ann_b/12):,}","d-bad",
        f"~{ann_b:,}/yr","d-bad")

# M12 — Mean Time to Detect (EST — Mandiant M-Trends 2024: 10-day global median)
with r3c4:
    est_card("GLOBAL AVG MTTD [EST]","https://www.mandiant.com/m-trends",
        "10 Days", "global median · Mandiant M-Trends 2024",
        "-0.1d","d-good","-0.5d","d-good","-2d","d-good","-8d","d-good")

# ─── ROW 4: Compliance & Risk Context ─────────────────────────────────────────
r4c1, r4c2, r4c3, r4c4 = st.columns(4)

# M13 — Avg Cost of a Data Breach (EST — IBM 2024: $4.88M average)
with r4c1:
    est_card("AVG BREACH COST [EST]","https://www.ibm.com/security/data-breach",
        "$4.88M", "global avg · IBM Cost of Breach 2024",
        "+$4k","d-bad","+$28k","d-bad","+$120k","d-bad","+$320k","d-bad")

# M14 — Supply Chain Attacks (EST — CrowdStrike GTR 2024: 45% YoY increase)
with r4c2:
    ann_sc = 3_000
    est_card("SUPPLY CHAIN ATTACKS [EST]","https://www.crowdstrike.com/global-threat-report/",
        "+45% YoY", f"YTD est. ~{ytd(ann_sc)} incidents · CrowdStrike GTR",
        "+8","d-bad","–","d-neu",f"+{int(ann_sc/12):,}","d-bad",f"~{ann_sc:,}","d-bad")

# M15 — Phishing (EST — APWG Q3 2024: 1.97M+ reports/yr)
with r4c3:
    ann_p = 1_970_000
    est_card("PHISHING REPORTS [EST]","https://apwg.org/trendsreports/",
        f"{ytd(ann_p)//1_000}k YTD", "APWG eCrime report 2024 baseline",
        f"+{int(ann_p/365):,}","d-bad",
        f"+{int(ann_p/52):,}","d-bad",
        f"+{int(ann_p/12):,}","d-bad",
        f"~{ann_p//1_000}k/yr","d-bad")

# M16 — Avg Time to Exploit a CVE (EST — CrowdStrike 2024: avg 5 days to exploit after disclosure)
with r4c4:
    est_card("AVG TIME TO EXPLOIT [EST]","https://www.crowdstrike.com/global-threat-report/",
        "5 Days", "avg days from disclosure to exploit · CrowdStrike 2024",
        "–","d-neu","–","d-neu","-0.5d","d-good","-3d","d-good")

# ─── DATA SOURCES FOOTER ──────────────────────────────────────────────────────
refresh_ts = now_utc.strftime("%Y-%m-%d %H:%M UTC")
st.markdown(f"""
<div style="font-size:0.78rem;font-family:{MONO};margin:4px 0 28px 0;padding:10px 12px;
     background:#080808;border:1px solid #1a1a1a;border-left:3px solid #333;">
  <span style="color:#555;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">LIVE SOURCES &nbsp;</span>
  <a href="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" target="_blank" class="src-link">CISA KEV JSON</a> ·
  <a href="https://services.nvd.nist.gov/rest/json/cves/2.0" target="_blank" class="src-link">NVD CVE API v2</a> ·
  <a href="https://bazaar.abuse.ch/export/csv/recent/" target="_blank" class="src-link">MalwareBazaar CSV</a> ·
  <a href="https://urlhaus.abuse.ch/downloads/text_online/" target="_blank" class="src-link">URLhaus Feed</a> ·
  <a href="https://feodotracker.abuse.ch/downloads/ipblocklist.csv" target="_blank" class="src-link">Feodo Tracker CSV</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml" target="_blank" class="src-link">CISA ICS RSS</a> ·
  <a href="https://www.cisa.gov/cybersecurity-advisories/all.xml" target="_blank" class="src-link">CISA Advisories RSS</a>
  <br>
  <span style="color:#555;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">EST BASELINES &nbsp;</span>
  <a href="https://www.verizon.com/business/resources/reports/dbir/" target="_blank" class="src-link">Verizon DBIR 2024</a> ·
  <a href="https://www.mandiant.com/m-trends" target="_blank" class="src-link">Mandiant M-Trends 2024</a> ·
  <a href="https://www.crowdstrike.com/global-threat-report/" target="_blank" class="src-link">CrowdStrike GTR 2024</a> ·
  <a href="https://www.ic3.gov/AnnualReport" target="_blank" class="src-link">FBI IC3 2023</a> ·
  <a href="https://www.ibm.com/security/data-breach" target="_blank" class="src-link">IBM Cost of Breach 2024</a> ·
  <a href="https://apwg.org/trendsreports/" target="_blank" class="src-link">APWG eCrime 2024</a>
  <span style="float:right;color:#333;">Last refresh: {refresh_ts}</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LIVE THREAT MAPS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="margin:10px 0 15px 0;">
  <span style="font-size:1.1rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.2px;">
    <a href="https://livethreatmap.radware.com/" target="_blank" class="sec-hdr">&gt;&gt; LIVE THREAT MAP FEEDS</a>
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
<div style="margin-top:35px;margin-bottom:25px;text-align:center;">
  <span style="font-size:1.2rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;">
    <a href="https://www.nist.gov/cyberframework" target="_blank" class="sec-hdr">&gt;&gt; ADDITIONAL GRC RESOURCES &lt;&lt;</a>
  </span>
</div>""", unsafe_allow_html=True)

_, l1, l2, l3, _ = st.columns([0.5, 3, 3, 3, 0.5])

with l1:
    for args in [
        ("01","NIST AI RMF","https://www.nist.gov/itl/ai-risk-management-framework","AI risk management framework for organizations."),
        ("02","HITRUST Alliance","https://hitrustalliance.net/","Safeguarding sensitive data and managing information risk."),
        ("03","OWASP LLM Top 10","https://owasp.org/www-project-top-10-for-large-language-model-applications/","Critical security risks in Large Language Models."),
        ("04","NIST CSF 2.0","https://www.nist.gov/cyberframework","Standards to manage and reduce cybersecurity risk."),
        ("05","ISO/IEC 27001","https://www.iso.org/isoiec-27001-information-security.html","International standard for ISMS management."),
        ("06","OWASP Top 10 Web","https://owasp.org/www-project-top-ten/","Critical web application security risks."),
        ("07","NIST NVD","https://nvd.nist.gov/","US repository of standards-based vulnerability data."),
        ("08","CIS Controls v8","https://www.cisecurity.org/controls/","Prioritized safeguards against prevalent cyber-attacks."),
        ("09","CISA KEV Catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","Authoritative source of actively exploited CVEs."),
        ("10","MITRE ATT&CK","https://mitre-attack.github.io/attack-navigator/","Matrix for mapping adversary tactics and procedures."),
        ("11","CVSS 4.0 Calc","https://www.first.org/cvss/calculator/4.0","Common Vulnerability Scoring System v4.0."),
        ("12","VirusTotal","https://www.virustotal.com/","Analyzing suspicious files, domains, IPs, and URLs."),
        ("13","Exploit Database","https://www.exploit-db.com/","Archive of public exploits and POCs."),
    ]:
        st.markdown(grc_link(*args), unsafe_allow_html=True)

with l2:
    for args in [
        ("14","Shodan Search","https://www.shodan.io/","Search engine for exposed internet-connected devices."),
        ("15","Have I Been Pwned","https://haveibeenpwned.com/","Check if an email/domain is in a data breach."),
        ("16","AlienVault OTX","https://otx.alienvault.com/","Real-time crowdsourced threat intelligence IOCs."),
        ("17","crt.sh Search","https://crt.sh/","Certificate Transparency log for attack surface mapping."),
        ("18","SANS ISC","https://isc.sans.edu/","Cooperative cyber threat monitor and diary."),
        ("19","BleepingComputer","https://www.bleepingcomputer.com/","Trusted cybersecurity and ransomware news."),
        ("20","Abuse.ch URLhaus","https://urlhaus.abuse.ch/","Tracking malware distribution sites."),
        ("21","Any.Run Sandbox","https://any.run/","Interactive online malware analysis sandbox."),
        ("22","URLScan.io","https://urlscan.io/","Analyze and scan websites for malicious content."),
        ("23","GTFOBins","https://gtfobins.github.io/","Unix binaries that can bypass local security."),
        ("24","MalwareBazaar","https://bazaar.abuse.ch/","Open-source malware sample repository."),
        ("25","HackTheBox","https://www.hackthebox.com/","Gamified cybersecurity training platform."),
        ("26","Security Onion","https://securityonionsolutions.com/","Threat hunting and enterprise security monitoring."),
    ]:
        st.markdown(grc_link(*args), unsafe_allow_html=True)

with l3:
    for args in [
        ("27","HackerOne","https://www.hackerone.com/","Bug bounty platform for vulnerability disclosure."),
        ("28","Bugcrowd","https://www.bugcrowd.com/","Crowdsourced vulnerability disclosure and bounties."),
        ("29","TryHackMe","https://tryhackme.com/","Hands-on cybersecurity training labs."),
        ("30","CyberChef","https://gchq.github.io/CyberChef/","The Cyber Swiss Army Knife for data analysis."),
        ("31","CISA Shields Up","https://www.cisa.gov/shields-up","Building resilience against cyberattacks."),
        ("32","NIST CSRC","https://csrc.nist.gov/","NIST Computer Security Resource Center."),
        ("33","SANS Reading Room","https://www.sans.org/white-papers/","Cybersecurity research and whitepapers."),
        ("34","DEF CON Archives","https://defcon.org/html/links/dc-archives.html","Presentations from the DEF CON conference."),
        ("35","OSINT Framework","https://osintframework.com/","Interactive OSINT gathering tool collection."),
        ("36","Talos Threat Intel","https://talosintelligence.com/","Cisco's premier threat research group."),
        ("37","PayloadsAllThings","https://github.com/swisskyrepo/PayloadsAllTheThings","Useful payloads and bypass techniques."),
        ("38","PortSwigger Academy","https://portswigger.net/web-security","Web vulnerability training from Burp Suite creators."),
        ("39","VulnHub","https://www.vulnhub.com/","Hands-on digital security practice."),
    ]:
        st.markdown(grc_link(*args), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="border-top:1px solid #1a1a1a;padding-top:25px;margin-top:40px;
     text-align:center;font-family:{MONO};">
  <div style="color:#666;font-size:0.88rem;margin-bottom:4px;">Questions, Comments, or Recommendations?</div>
  <div style="color:#666;font-size:0.88rem;margin-bottom:18px;">
    Developed by <b>Adam Kistler</b> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">LinkedIn</a>
  </div>
  <div style="color:#444;font-size:0.72rem;padding:0 10%;line-height:1.5;margin-bottom:14px;">
    <b>LEGAL DISCLAIMER:</b> Educational and portfolio purposes only. All embedded threat maps and data
    are property of their respective owners. SecAI-Nexus does not host or process third-party content.<br>
    <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank"
       class="footer-lic">Code and layout licensed CC BY-NC 4.0.</a>
    Third-party content remains under copyright of original providers.
  </div>
  <div style="color:#333;font-size:0.75rem;">SecAI-Nexus GRC [v15.0] &nbsp;|&nbsp; Live Data Engine Active</div>
</div>
""", unsafe_allow_html=True)
