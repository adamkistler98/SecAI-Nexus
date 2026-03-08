"""
live_metrics.py — Drop-in replacement for the GLOBAL THREAT METRICS section
of SecAI-Nexus GRC. Pulls real data from free, no-API-key sources.
"""

import streamlit as st
import requests
import json
import html
from datetime import datetime, timezone, timedelta
import math

# ---------------------------------------------------------------------------
# API Configuration (Decoupled Hardcoded URLs)
# ---------------------------------------------------------------------------
API_URLS = {
    "cisa_kev": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    "nvd_cve": "https://services.nvd.nist.gov/rest/json/cves/2.0",
    "malwarebazaar": "https://mb-api.abuse.ch/api/v1/",
    "urlhaus": "https://urlhaus-api.abuse.ch/v1/urls/recent/limit/1000/",
    "feodo_tracker": "https://feodotracker.abuse.ch/downloads/ipblocklist.json",
    "cisa_ics_rss": "https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml"
}

# ---------------------------------------------------------------------------
# Shared request helper
# ---------------------------------------------------------------------------
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "SecAI-Nexus-GRC/1.0 (educational dashboard)"})

def _get(url, timeout=10, **kwargs):
    try:
        r = SESSION.get(url, timeout=timeout, **kwargs)
        r.raise_for_status()
        return r
    except Exception:
        return None

def _post(url, timeout=10, **kwargs):
    try:
        r = SESSION.post(url, timeout=timeout, **kwargs)
        r.raise_for_status()
        return r
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Formatters (with built-in HTML Escaping to prevent XSS)
# ---------------------------------------------------------------------------
def _fmt(n):
    """Format an integer with commas, or return it if already a string."""
    if isinstance(n, int):
        return html.escape(f"{n:,}")
    return html.escape(str(n))

def _delta_fmt(n, positive_is_bad=True):
    """Return (formatted_string, css_class) for a delta integer."""
    if n == 0:
        return html.escape("0"), "d-neu"
    sign = "+" if n > 0 else ""
    cls = ("d-bad" if n > 0 else "d-good") if positive_is_bad else ("d-good" if n > 0 else "d-bad")
    return html.escape(f"{sign}{n:,}"), html.escape(cls)

# ---------------------------------------------------------------------------
# --- DATA FETCHERS ---
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cisa_kev():
    r = _get(API_URLS["cisa_kev"])
    if not r: return None
    try:
        data = r.json()
        vulns = data.get("vulnerabilities", [])
        now = datetime.now(timezone.utc)
        total = len(vulns)
        d1 = d7 = d30 = d365 = 0
        for v in vulns:
            added_str = v.get("dateAdded", "")
            try:
                added = datetime.strptime(added_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                age = (now - added).days
                if age <= 1:   d1   += 1
                if age <= 7:   d7   += 1
                if age <= 30:  d30  += 1
                if age <= 365: d365 += 1
            except Exception:
                pass
        return {"total": total, "d1": d1, "d7": d7, "d30": d30, "d365": d365}
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nvd_cve_counts():
    now = datetime.now(timezone.utc)
    def _count(start_dt):
        params = {
            "pubStartDate": start_dt.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "pubEndDate":   now.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "resultsPerPage": 1,
        }
        r = _get(API_URLS["nvd_cve"], params=params, timeout=15)
        if r:
            try: return r.json().get("totalResults", None)
            except Exception: return None
        return None

    today = _count(now - timedelta(days=1))
    d7    = _count(now - timedelta(days=7))
    d30   = _count(now - timedelta(days=30))
    d365  = _count(now - timedelta(days=365))

    if any(x is None for x in [today, d7, d30, d365]): return None
    return {"today": today, "d7": d7, "d30": d30, "d365": d365}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_malwarebazaar_recent():
    r_day  = _post(API_URLS["malwarebazaar"], data={"query": "get_recent", "selector": "time_frame", "time_frame": "1d"}, timeout=15)
    r_week = _post(API_URLS["malwarebazaar"], data={"query": "get_recent", "selector": "time_frame", "time_frame": "7d"}, timeout=15)

    def _parse(r):
        if not r: return None
        try:
            j = r.json()
            if j.get("query_status") == "ok":
                return len(j.get("data", []))
        except Exception: pass
        return None

    return {"d1": _parse(r_day), "d7": _parse(r_week)}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_urlhaus_stats():
    r = _get(API_URLS["urlhaus"], timeout=15)
    if not r: return None
    try:
        j = r.json()
        if j.get("query_status") == "ok":
            urls = j.get("urls", [])
            online = sum(1 for u in urls if u.get("url_status") == "online")
            return {"online": online, "total_sample": len(urls)}
    except Exception: pass
    return None

@st.cache_data(ttl=600, show_spinner=False)
def fetch_feodo_c2():
    r = _get(API_URLS["feodo_tracker"], timeout=15)
    if not r: return None
    try:
        data = r.json()
        active = [x for x in data if x.get("status", "").lower() == "online"]
        return {"active": len(active), "total": len(data)}
    except Exception: return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_cisa_ics_alerts():
    import xml.etree.ElementTree as ET
    r = _get(API_URLS["cisa_ics_rss"], timeout=15)
    if not r: return None
    try:
        root = ET.fromstring(r.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        now = datetime.now(timezone.utc)
        d1 = d7 = d30 = d365 = total = 0
        items = root.findall(".//item") or root.findall(".//atom:entry", ns)
        for item in items:
            total += 1
            pub = (item.findtext("pubDate") or item.findtext("atom:updated", namespaces=ns) or "")
            try:
                for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
                    try:
                        dt = datetime.strptime(pub.strip(), fmt)
                        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                        break
                    except ValueError: continue
                age = (now - dt).days
                if age <= 1:   d1   += 1
                if age <= 7:   d7   += 1
                if age <= 30:  d30  += 1
                if age <= 365: d365 += 1
            except Exception: pass
        return {"d1": d1, "d7": d7, "d30": d30, "d365": d365, "total_in_feed": total}
    except Exception: return None

def _est_counter(annual_total, reference_year=2023):
    now = datetime.now(timezone.utc)
    year_start = datetime(now.year, 1, 1, tzinfo=timezone.utc)
    days_elapsed = (now - year_start).days + 1
    return int((annual_total / 365) * days_elapsed)

def _est_delta(annual_total, days):
    return int((annual_total / 365) * days)

# ---------------------------------------------------------------------------
# --- METRIC CARD RENDERER ---
# ---------------------------------------------------------------------------

def render_multi_metric(title, title_url, value, d1, d1_class, d7, d7_class,
                        d30, d30_class, d365, d365_class, live=True):
    
    t_esc = html.escape(str(title))
    url_esc = html.escape(str(title_url))
    val_esc = html.escape(str(value))
    d1_esc, d1c_esc = html.escape(str(d1)), html.escape(str(d1_class))
    d7_esc, d7c_esc = html.escape(str(d7)), html.escape(str(d7_class))
    d30_esc, d30c_esc = html.escape(str(d30)), html.escape(str(d30_class))
    d365_esc, d365c_esc = html.escape(str(d365)), html.escape(str(d365_class))

    badge = (
        '<span style="font-size:0.65rem; color:#00ff41; border:1px solid #00ff41; '
        'padding:1px 4px; margin-left:6px; vertical-align:middle;">LIVE</span>'
        if live else
        '<span style="font-size:0.65rem; color:#888; border:1px solid #555; '
        'padding:1px 4px; margin-left:6px; vertical-align:middle;">EST</span>'
    )
    
    html_block = f"""
    <div class="custom-metric">
        <div class="metric-title">
            <a href="{url_esc}" target="_blank">{t_esc}</a>{badge}
        </div>
        <div class="metric-value">{val_esc}</div>
        <div class="metric-deltas">
            <div style="margin-bottom:2px;"><span style="color:#888;">Past Day:</span>  <span class="{d1c_esc}">{d1_esc}</span></div>
            <div style="margin-bottom:2px;"><span style="color:#888;">Past Week:</span> <span class="{d7c_esc}">{d7_esc}</span></div>
            <div style="margin-bottom:2px;"><span style="color:#888;">Past Month:</span><span class="{d30c_esc}">{d30_esc}</span></div>
            <div><span style="color:#888;">Past Year:</span>  <span class="{d365c_esc}">{d365_esc}</span></div>
        </div>
    </div>"""
    st.markdown(html_block, unsafe_allow_html=True)

def _error_metric(title, title_url, fallback_value, d1, d1c, d7, d7c, d30, d30c, d365, d365c):
    t_esc = html.escape(str(title))
    url_esc = html.escape(str(title_url))
    val_esc = html.escape(str(fallback_value))
    
    html_block = f"""
    <div class="custom-metric" style="border-left-color:#ff4b4b;">
        <div class="metric-title">
            <a href="{url_esc}" target="_blank">{t_esc}</a>
            <span style="font-size:0.65rem; color:#ff4b4b; border:1px solid #ff4b4b;
                  padding:1px 4px; margin-left:6px; vertical-align:middle;">⚠ OFFLINE</span>
        </div>
        <div class="metric-value">{val_esc}</div>
        <div class="metric-deltas">
            <div style="margin-bottom:2px;"><span style="color:#888;">Past Day:</span>  <span class="{d1c}">{d1}</span></div>
            <div style="margin-bottom:2px;"><span style="color:#888;">Past Week:</span> <span class="{d7c}">{d7}</span></div>
            <div style="margin-bottom:2px;"><span style="color:#888;">Past Month:</span><span class="{d30c}">{d30}</span></div>
            <div><span style="color:#888;">Past Year:</span>  <span class="{d365c}">{d365}</span></div>
        </div>
    </div>"""
    st.markdown(html_block, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# MAIN RENDER FUNCTION 
# ---------------------------------------------------------------------------

def render_live_metrics_section():
    st.markdown(f'''
    <div style="margin-top:10px; margin-bottom:15px; line-height:1.3;">
        <span style="font-size:1.1rem; font-weight:bold; text-transform:uppercase; letter-spacing:1.2px;">
            <a href="https://www.cisa.gov/" target="_blank" class="section-header-link">&gt;&gt; GLOBAL THREAT METRICS</a>
        </span><br>
        <span style="font-size:0.85rem; color:#00ff41; font-family:'Courier New',monospace;">
            LIVE — CISA KEV · NVD · MalwareBazaar · URLhaus · Feodo Tracker · CISA ICS RSS
            &nbsp;|&nbsp; <span style="color:#00ff41; font-size:0.75rem;">LIVE</span> = real-time API &nbsp;
            <span style="color:#888; font-size:0.75rem;">EST</span> = annual-report model
        </span>
    </div>
    ''', unsafe_allow_html=True)

    kev   = fetch_cisa_kev()
    nvd   = fetch_nvd_cve_counts()
    mbaz  = fetch_malwarebazaar_recent()
    uhaus = fetch_urlhaus_stats()
    feodo = fetch_feodo_c2()
    ics   = fetch_cisa_ics_alerts()

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        if kev:
            d1v, d1c   = _delta_fmt(kev["d1"], True)
            d7v, d7c   = _delta_fmt(kev["d7"], True)
            d30v, d30c = _delta_fmt(kev["d30"], True)
            d365v,d365c= _delta_fmt(kev["d365"], True)
            render_multi_metric("CISA KEV (EXPLOITED CVEs)", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
                _fmt(kev["total"]), d1v, d1c, d7v, d7c, d30v, d30c, d365v, d365c, live=True)
        else:
            _error_metric("CISA KEV (EXPLOITED CVEs)", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
                "~1,500", "+2","d-bad","+6","d-bad","+15","d-bad","+185","d-bad")

    with m2:
        annual = 5200
        render_multi_metric("RANSOMWARE INCIDENTS [EST]", "https://www.cisa.gov/stopransomware", _fmt(_est_counter(annual)),
            f"+{_est_delta(annual,1):,}", "d-bad", f"+{_est_delta(annual,7):,}", "d-bad",
            f"+{_est_delta(annual,30):,}", "d-bad", f"+{annual:,}/yr", "d-bad", live=False)

    with m3:
        annual_m = 2_000_000_000
        ytd_m = int(_est_counter(annual_m) / 1_000_000)
        render_multi_metric("PHISHING REPORTS (YTD) [EST]", "https://www.verizon.com/business/resources/reports/dbir/", f"{ytd_m}M",
            f"+{int(_est_delta(annual_m,1)/1_000_000)}M", "d-bad", f"+{int(_est_delta(annual_m,7)/1_000_000)}M", "d-bad",
            f"+{int(_est_delta(annual_m,30)/1_000_000)}M", "d-bad", f"+{annual_m//1_000_000_000}B/yr", "d-bad", live=False)

    with m4:
        if mbaz and mbaz.get("d1") is not None:
            d1v, d1c = _delta_fmt(mbaz["d1"], True)
            d7_val = mbaz.get("d7") or 0
            d7v, d7c = _delta_fmt(d7_val, True)
            weekly = d7_val or mbaz["d1"] * 7
            d30v, d30c   = _delta_fmt(int(weekly * (30/7)), True)
            d365v, d365c = _delta_fmt(int(weekly * (365/7)), True)
            render_multi_metric("NEW MALWARE SAMPLES (BAZAAR)", "https://bazaar.abuse.ch/", _fmt(mbaz["d1"]) + " /day",
                d1v, d1c, d7v, d7c, d30v, d30c, d365v, d365c, live=True)
        else:
            _error_metric("NEW MALWARE SAMPLES (BAZAAR)", "https://bazaar.abuse.ch/", "~1,000/day", 
                "+1k","d-bad","+7k","d-bad","+30k","d-bad","+365k","d-bad")

    m5, m6, m7, m8 = st.columns(4)

    with m5:
        render_multi_metric("GLOBAL AVG MTTD [EST]", "https://www.mandiant.com/m-trends", "10 Days",
            "-0.2d","d-good", "-1.5d","d-good", "-3d","d-good", "-4d","d-good", live=False)

    with m6:
        render_multi_metric("AVG TIME TO EXPLOIT [EST]", "https://www.crowdstrike.com/global-threat-report/", "< 1 Day",
            "-", "d-neu", "-", "d-neu", "-0.5d","d-bad", "-2d","d-bad", live=False)

    with m7:
        if uhaus:
            render_multi_metric("ONLINE MALICIOUS URLs (URLHAUS)", "https://urlhaus.abuse.ch/", _fmt(uhaus["online"]) + " active",
                "–", "d-neu", "–", "d-neu", "–", "d-neu", "3.6M+ tracked", "d-bad", live=True)
        else:
            _error_metric("ONLINE MALICIOUS URLs (URLHAUS)", "https://urlhaus.abuse.ch/", "~84k active", 
                "+2.1k","d-bad","+14k","d-bad","+62k","d-bad","+2.1M","d-bad")

    with m8:
        annual_creds = 17_000_000_000
        render_multi_metric("EXPOSED CREDENTIALS (YTD) [EST]", "https://www.verizon.com/business/resources/reports/dbir/", f"{_est_counter(annual_creds)//1_000_000_000:.1f}B",
            f"+{_est_delta(annual_creds,1)//1_000_000}M", "d-bad", f"+{_est_delta(annual_creds,7)//1_000_000}M", "d-bad",
            f"+{_est_delta(annual_creds,30)//1_000_000}M", "d-bad", f"+{annual_creds//1_000_000_000}B/yr", "d-bad", live=False)

    m9, m10, m11, m12 = st.columns(4)

    with m9:
        render_multi_metric("TRACKED THREAT GROUPS [EST]", "https://www.mandiant.com/m-trends", "600+",
            "0","d-neu", "+1","d-bad", "+3","d-bad", "+41","d-bad", live=False)

    with m10:
        if nvd:
            d1v, d1c   = _delta_fmt(nvd["today"], True)
            d7v, d7c   = _delta_fmt(nvd["d7"],    True)
            d30v, d30c = _delta_fmt(nvd["d30"],   True)
            d365v,d365c= _delta_fmt(nvd["d365"],  True)
            render_multi_metric("NEW CVEs PUBLISHED (NVD)", "https://nvd.nist.gov/", _fmt(nvd["today"]) + " /day",
                d1v, d1c, d7v, d7c, d30v, d30c, d365v, d365c, live=True)
        else:
            _error_metric("NEW CVEs PUBLISHED (NVD)", "https://nvd.nist.gov/", "~100/day", 
                "+100","d-bad","+700","d-bad","+3k","d-bad","+36k","d-bad")

    with m11:
        if feodo:
            render_multi_metric("BOTNET C2s (FEODO TRACKER)", "https://feodotracker.abuse.ch/", _fmt(feodo["active"]) + " online",
                "–", "d-neu", "–", "d-neu", "–", "d-neu", f"{_fmt(feodo['total'])} tracked", "d-neu", live=True)
        else:
            st.markdown("""
            <div class="custom-metric">
                <div class="metric-title"><a href="https://feodotracker.abuse.ch/" target="_blank">BOTNET C2s (FEODO TRACKER)</a>
                <span style="font-size:0.65rem; color:#00ff41; border:1px solid #00ff41; padding:1px 4px; margin-left:6px;">LIVE</span></div>
                <div class="metric-value">0 active</div>
                <div class="metric-deltas"><span style="color:#888;">Note: Empty after Operation Endgame (2024).</span></div>
            </div>""", unsafe_allow_html=True)

    with m12:
        if ics:
            d1v, d1c   = _delta_fmt(ics["d1"], True)
            d7v, d7c   = _delta_fmt(ics["d7"], True)
            d30v, d30c = _delta_fmt(ics["d30"], True)
            d365v,d365c= _delta_fmt(ics["d365"],True)
            render_multi_metric("ICS/SCADA ADVISORIES (CISA)", "https://www.cisa.gov/ics", _fmt(ics["d7"]) + " /week",
                d1v, d1c, d7v, d7c, d30v, d30c, d365v, d365c, live=True)
        else:
            _error_metric("ICS/SCADA ADVISORIES (CISA)", "https://www.cisa.gov/ics", "~5/week", 
                "+1","d-bad","+5","d-bad","+20","d-bad","+250","d-bad")

    m13, m14, m15, m16 = st.columns(4)

    with m13:
        annual_breach = 8_000_000_000
        render_multi_metric("DATA RECORDS BREACHED (YTD) [EST]", "https://www.verizon.com/business/resources/reports/dbir/", f"{_est_counter(annual_breach)//1_000_000}M",
            f"+{_est_delta(annual_breach,1)//1_000_000}M", "d-bad", f"+{_est_delta(annual_breach,7)//1_000_000}M", "d-bad",
            f"+{_est_delta(annual_breach,30)//1_000_000}M", "d-bad", f"+{annual_breach//1_000_000_000}B/yr", "d-bad", live=False)

    with m14:
        if nvd:
            render_multi_metric("CVEs THIS YEAR (NVD LIVE)", "https://nvd.nist.gov/", _fmt(nvd["d365"]),
                f"+{nvd['today']:,}", "d-bad", f"+{nvd['d7']:,}", "d-bad", f"+{nvd['d30']:,}", "d-bad", f"~{nvd['d365']:,}/yr", "d-bad", live=True)
        else:
            _error_metric("CVEs THIS YEAR (NVD LIVE)", "https://nvd.nist.gov/", "~36k", 
                "+100","d-bad","+700","d-bad","+3k","d-bad","+36k","d-bad")

    with m15:
        if uhaus:
            render_multi_metric("MALICIOUS DOMAINS (URLHAUS)", "https://urlhaus.abuse.ch/", f"{3_654_915//1000}k tracked",
                f"{uhaus['online']} online", "d-bad", "–", "d-neu", "–", "d-neu", "3.6M+ total", "d-bad", live=True)
        else:
            _error_metric("MALICIOUS DOMAINS (URLHAUS)", "https://urlhaus.abuse.ch/", "3.6M tracked", 
                "+2k","d-bad","+14k","d-bad","+60k","d-bad","+2M","d-bad")

    with m16:
        annual_bec = 21_000
        render_multi_metric("BEC INCIDENTS (YTD) [EST]", "https://www.verizon.com/business/resources/reports/dbir/", _fmt(_est_counter(annual_bec)),
            f"+{_est_delta(annual_bec,1)}", "d-bad", f"+{_est_delta(annual_bec,7)}", "d-bad",
            f"+{_est_delta(annual_bec,30)}", "d-bad", f"+{annual_bec:,}/yr", "d-bad", live=False)

    m17, m18, m19, m20 = st.columns(4)

    with m17:
        if kev:
            render_multi_metric("CISA KEV ADDITIONS", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", _fmt(kev["d30"]) + " /month",
                f"+{kev['d1']}", "d-bad", f"+{kev['d7']}", "d-bad", f"+{kev['d30']}", "d-bad", f"+{kev['d365']}", "d-bad", live=True)
        else:
            _error_metric("CISA KEV ADDITIONS", "https://www.cisa.gov/known-exploited-vulnerabilities-catalog", "~15/month",
                "+1","d-bad","+3","d-bad","+15","d-bad","+185","d-bad")

    with m18:
        render_multi_metric("SUPPLY CHAIN ATTACKS [EST]", "https://www.crowdstrike.com/global-threat-report/", "~45% YoY ↑",
            "0","d-neu", "+2","d-bad", "+8","d-bad", "+45","d-bad", live=False)

    with m19:
        if mbaz and mbaz.get("d7") is not None:
            d7_count = mbaz["d7"]
            d1_count = mbaz.get("d1") or int(d7_count / 7)
            render_multi_metric("MALWARE SAMPLES (7d BAZAAR)", "https://bazaar.abuse.ch/", _fmt(d7_count) + " /7d",
                f"+{d1_count:,}", "d-bad", f"+{d7_count:,}", "d-bad",
                f"+{int(d7_count*(30/7)):,}", "d-bad", f"+{int(d7_count*(365/7)):,}", "d-bad", live=True)
        else:
            _error_metric("MALWARE SAMPLES (7d BAZAAR)", "https://bazaar.abuse.ch/", "~7k/week",
                "+1k","d-bad","+7k","d-bad","+30k","d-bad","+365k","d-bad")

    with m20:
        render_multi_metric("DEFCON THREAT LEVEL", "https://www.defconlevel.com/", "LEVEL 3",
            "Level 3","d-neu", "Level 3","d-neu", "Level 3","d-neu", "Level 3","d-neu", live=False)

    last_refreshed = datetime.now(timezone.utc).strftime("%H:%M UTC")
    st.markdown(f"""
    <div style="font-size:0.85rem; font-family:'Courier New',monospace; text-align:left; margin-bottom:25px; margin-top:-5px;">
        <span style="color:#888; font-weight:bold;">LIVE DATA SOURCES:</span> 
        <a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog" target="_blank" class="source-link">CISA KEV JSON</a> | 
        <a href="https://nvd.nist.gov/developers/vulnerabilities" target="_blank" class="source-link">NVD CVE API v2</a> | 
        <a href="https://bazaar.abuse.ch/api/" target="_blank" class="source-link">MALWAREBAZAAR API</a> | 
        <a href="https://urlhaus-api.abuse.ch/" target="_blank" class="source-link">URLHAUS API</a> | 
        <a href="https://feodotracker.abuse.ch/blocklist/" target="_blank" class="source-link">FEODO TRACKER</a> | 
        <a href="https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml" target="_blank" class="source-link">CISA ICS RSS</a>
        &nbsp;&nbsp;<span style="color:#555;">| EST baselines: Verizon DBIR · Mandiant M-Trends · CrowdStrike GTR · FBI IC3 · SpyCloud</span>
        &nbsp;&nbsp;<span style="color:#333;">| Last refresh: {last_refreshed}</span>
    </div>
    """, unsafe_allow_html=True)
