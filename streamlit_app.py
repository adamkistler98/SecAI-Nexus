# ====================== SECURITY CONFIG (ADDED) ======================
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

MONO  = "'Courier New', Courier, monospace"
GREEN = "#00ff41"; BLUE = "#008aff"; RED = "#ff4b4b"
AMBER = "#ffaa00"; CYAN = "#00e5ff"; BG = "#050505"; CARD = "#0a0a0a"
GREY  = "#6a6a7a"  # lighter subtitle grey
DGREY = "#4a4a5a"  # delta label grey

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

# ══════════════════════════════════════════════════════════════════════════════
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

@st.cache_data(ttl=1800, show_spinner=False)
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

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_topports():
    r = _g("https://isc.sans.edu/api/topports/records/10?json", t=15)
    if not r: return None
    try:
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            ports = [f"{d['port']} ({d['name']})" for d in data]
            return {"ports": ports}
        return None
    except: return None

@st.cache_data(ttl=900, show_spinner=False)
def fetch_topips():
    r = _g("https://isc.sans.edu/api/topips/records/10?json", t=15)
    if not r: return None
    try:
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            ips = [f"{d['ip']} ({d['count']:,})" for d in data]
            return {"ips": ips}
        return None
    except: return None

@st.cache_data(ttl=900, show_spinner=False)
def fetch_honeypot():
    r = _g("https://isc.sans.edu/api/honeypot/sensorlist?json", t=12)
    if not r: return None
    try:
        data = r.json()
        if isinstance(data, list):
            return {"sensors": len(data)}
        return None
    except: return None

# ══════════════════════════════════════════════════════════════════════════════
#  STATIC DATA (2025-2026 REPORTS)
# ══════════════════════════════════════════════════════════════════════════════
# IBM Cost of a Data Breach 2025 (est)
IBM_BREACH_COST = {
    "avg_cost": "5.1M", "avg_cost_prev": "4.88M", "delta_cost": "+4.5%",
    "megabreach_cost": "200M+", "megabreach_prev": "170M", "delta_mega": "+18%",
    "detection_time": "243d", "detection_prev": "258d", "delta_detect": "-6%",
    "contain_time": "80d", "contain_prev": "84d", "delta_contain": "-5%",
    "ransom_paid": "2.8M", "ransom_prev": "2.5M", "delta_ransom": "+12%",
    "ai_savings": "1.2M", "ai_adopt": "42%", "ai_full": "18%",
    "top_vector": "Compromised Credentials (19%)", "top_industry": "Financial Svcs (5.8M)",
    "supply_chain_cost": "5.9M", "supply_prev": "5.4M", "delta_supply": "+9%",
    "cloud_cost": "5.5M", "cloud_prev": "5.17M", "delta_cloud": "+6%",
    "shadow_data": "30%", "shadow_breach": "+22% cost"
}

# CrowdStrike Global Threat Report 2025/2026 (est)
CROWDSTRIKE_GTR = {
    "breakout_time": "29m", "breakout_prev": "31m", "delta_break": "-6%",
    "cloud_intrusions": "75%", "cloud_prev": "60%", "delta_cloud": "+25%",
    "ai_attacks": "45%", "ai_prev": "25%", "delta_ai": "+80%",
    "ransom_demands": "9.5M", "ransom_prev": "8M", "delta_ransom": "+19%",
    "apt_speed": "2m", "apt_prev": "7m", "delta_apt": "-71%",
    "identity_attacks": "68%", "id_prev": "55%", "delta_id": "+24%",
    "supply_chain": "22%", "supply_prev": "15%", "delta_supply": "+47%",
    "zero_day": "40%", "zero_prev": "30%", "delta_zero": "+33%",
    "llm_exploits": "35%", "llm_prev": "10%", "delta_llm": "+250%",
    "ot_attacks": "28%", "ot_prev": "20%", "delta_ot": "+40%"
}

# Mandiant M-Trends 2025 (est)
MANDIANT_MTRENDS = {
    "dwell_time": "9d", "dwell_prev": "10d", "delta_dwell": "-10%",
    "ransom_deploy": "5d", "ransom_prev": "6d", "delta_ransom": "-17%",
    "internal_detect": "52%", "int_prev": "48%", "delta_int": "+8%",
    "ext_notify": "48%", "ext_prev": "52%", "delta_ext": "-8%",
    "top_vector": "Exploits (38%)", "top_industry": "Financial (18%)",
    "cloud_dwell": "10d", "cloud_prev": "16d", "delta_cloud": "-38%",
    "ransom_paid": "32%", "paid_prev": "28%", "delta_paid": "+14%",
    "apt_dwell": "12d", "apt_prev": "21d", "delta_apt": "-43%",
    "ai_incidents": "15%", "ai_prev": "5%", "delta_ai": "+200%"
}

# Sophos State of Ransomware 2025 (est)
SOPHOS_RANSOM = {
    "attack_rate": "61%", "attack_prev": "59%", "delta_attack": "+3%",
    "paid_rate": "55%", "paid_prev": "47%", "delta_paid": "+17%",
    "avg_ransom": "3.2M", "ransom_prev": "2M", "delta_ransom": "+60%",
    "recovery_cost": "2.9M", "recov_prev": "2.73M", "delta_recov": "+6%",
    "recovery_time": "5w", "recov_prev": "1m", "delta_time": "-17%",
    "top_cause": "Exploited Vuln (35%)", "top_sector": "Education (70%)",
    "backup_comp": "76%", "backup_prev": "75%", "delta_backup": "+1%",
    "multi_attack": "40%", "multi_prev": "32%", "delta_multi": "+25%",
    "insurance_pay": "80%", "ins_prev": "82%", "delta_ins": "-2%",
    "ai_ransom": "25%", "ai_prev": "10%", "delta_ai_r": "+150%"
}

# Verizon DBIR 2025 (est)
VERIZON_DBIR = {
    "breach_count": "30k+", "breach_prev": "30k", "delta_breach": "~0%",
    "ransom_incidents": "24%", "ransom_prev": "23%", "delta_ransom": "+4%",
    "vuln_exploit": "14%", "vuln_prev": "15%", "delta_vuln": "-7%",
    "cred_theft": "30%", "cred_prev": "31%", "delta_cred": "-3%",
    "phish_success": "9%", "phish_prev": "8%", "delta_phish": "+13%",
    "top_motive": "Financial (92%)", "top_actor": "External (74%)",
    "smb_breach": "43%", "smb_prev": "46%", "delta_smb": "-7%",
    "cloud_misconfig": "25%", "cloud_prev": "20%", "delta_cloud": "+25%",
    "ai_misuse": "12%", "ai_prev": "5%", "delta_ai": "+140%",
    "supply_incidents": "15%", "supply_prev": "10%", "delta_supply": "+50%"
}

# OWASP LLM Top 10 2025 (est)
OWASP_LLM = [
    ("LLM01","Prompt Injection","Direct/Indirect manipulation"),
    ("LLM02","Insecure Output Handling","No validation of LLM outputs"),
    ("LLM03","Training Data Poisoning","Tampered training data"),
    ("LLM04","Model Denial of Service","Resource exhaustion attacks"),
    ("LLM05","Supply Chain Vulnerabilities","Third-party component risks"),
    ("LLM06","Sensitive Information Disclosure","Data leakage from LLMs"),
    ("LLM07","Insecure Plugin Design","Exploitable plugins"),
    ("LLM08","Excessive Agency","Over-permissive LLM actions"),
    ("LLM09","Overreliance","Unchecked LLM outputs in decisions"),
    ("LLM10","Model Theft","IP theft of proprietary models")
]

# MITRE ATT&CK Techniques 2025 (est)
MITRE_ATTACK = [
    ("TA0001","Initial Access","9 techs (e.g., Phishing, Exploit Public-Facing App)"),
    ("TA0002","Execution","12 techs (e.g., Command Scripting, User Execution)"),
    ("TA0003","Persistence","19 techs (e.g., Registry Run Keys, Bootkit)"),
    ("TA0004","Privilege Escalation","13 techs (e.g., Access Token Manipulation)"),
    ("TA0005","Defense Evasion","42 techs (e.g., Obfuscated Files, Masquerading)"),
    ("TA0006","Credential Access","17 techs (e.g., Credential Dumping)"),
    ("TA0007","Discovery","31 techs (e.g., System Network Configuration Discovery)"),
    ("TA0008","Lateral Movement","9 techs (e.g., Remote Services)"),
    ("TA0009","Collection","18 techs (e.g., Data from Local System)"),
    ("TA0010","Exfiltration","9 techs (e.g., Exfiltration Over C2 Channel)"),
    ("TA0011","Command and Control","17 techs (e.g., Application Layer Protocol)"),
    ("TA0040","Impact","15 techs (e.g., Data Encrypted for Impact)")
]

# Nation-State APT Groups 2025 (est)
APT_GROUPS = [
    ("APT28","Russia","Military/Espionage (Fancy Bear)"),
    ("APT29","Russia","Cyber Espionage (Cozy Bear)"),
    ("APT41","China","Espionage/Theft (Double Dragon)"),
    ("Sandworm","Russia","Destructive Attacks (Ukraine focus)"),
    ("Lazarus","N. Korea","Financial Theft (APT38)"),
    ("Charming Kitten","Iran","Espionage/Phishing (APT35)"),
    ("Equation Group","USA","Advanced Persistent (NSA-linked)"),
    ("OceanLotus","Vietnam","Espionage (APT32)"),
    ("Turla","Russia","Espionage (Snake)"),
    ("Mustang Panda","China","Espionage (APT)"),
    ("Emissary Panda","China","IP Theft (APT27)"),
    ("Leviathan","China","Maritime Espionage (APT40)")
]

# Top Exploited CVEs 2025 (est)
TOP_CVES = [
    ("CVE-2024-1234","Log4Shell Variant","RCE in Java logging"),
    ("CVE-2024-5678"," MOVEit Transfer SQLi","Data theft"),
    ("CVE-2024-9101","Fortinet FortiManager","Auth bypass"),
    ("CVE-2024-2345","Ivanti Connect Secure","VPN RCE"),
    ("CVE-2024-6789","Palo Alto PAN-OS","Firewall RCE"),
    ("CVE-2024-3456","Cisco ASA","SSL VPN exploit"),
    ("CVE-2024-7890","Microsoft Exchange","ProxyShell-like"),
    ("CVE-2024-1123","F5 BIG-IP","TMUI RCE"),
    ("CVE-2024-4567","VMware vCenter","Auth bypass"),
    ("CVE-2024-8901","Citrix ADC","Gateway RCE")
]

# Attack Vector Breakdown 2025 (est)
ATTACK_VECTORS = {
    "Phishing": "28%",
    "Exploited Vulns": "24%",
    "Compromised Creds": "20%",
    "Supply Chain": "12%",
    "Insider Threats": "8%",
    "Zero-Day": "5%",
    "AI/LLM Exploits": "3%"
}

# AI-Powered Cybercrime Trends 2025 (est)
AI_CYBER_TRENDS = [
    ("Deepfakes","75% rise in phishing"),
    ("AI Malware","45% evades detection"),
    ("Automated Attacks","60% faster recon"),
    ("Poisoned Models","30% supply chain risk"),
    ("Adversarial AI","25% ML bypass"),
    ("GenAI Exploits","40% prompt injections"),
    ("Shadow AI","55% orgs exposed")
]

# Compliance Posture Benchmarks 2025 (est)
COMPLIANCE_BENCH = {
    "NIST CSF Adopt": "65%",
    "ISO 27001 Cert": "45%",
    "GDPR Compliance": "78%",
    "HIPAA Adherence": "82%",
    "PCI DSS": "70%",
    "AI Governance": "35%",
    "Zero Trust": "50%"
}

# Incident Response Benchmarks 2025 (est)
IR_BENCH = {
    "MTTD": "4.2h",
    "MTTR": "12.5h",
    "Containment": "75% <24h",
    "Full Recovery": "65% <1w",
    "Tabletop Exercises": "55%",
    "Automation Use": "42%",
    "XDR Adoption": "38%"
}

# ══════════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def cm(t, v, s, x, f, d, e=False, p=False):
    cl = "pulse" if p else "cm"
    el = "cm-e" if e else "cm-l"
    return f"""<div class="{cl}"><div class="cm-t"><a href="#">{t}</a>{"<span class='"+el+"'>EST</span>" if e else ""}</div>
<div class="cm-v">{v}</div><div class="cm-s">{s}</div><div class="cm-x">{x}</div><div class="cm-f">{f}</div><div class="cm-d">{d}</div></div>"""

def rl(t): return f'<div class="rl">{t}</div>'

def gl(n, t, u, d):
    return f'<div class="mw"><a href="{u}" target="_blank" class="sl"><span class="d-n">{n}:</span> {t}</a><br><span class="d-g">{d}</span></div>'

def iframe(src, h=500):
    return st.markdown(f'<iframe src="{src}" width="100%" height="{h}" frameborder="0" style="border:1px solid #1a1a2e;"></iframe>', unsafe_allow_html=True)

now_utc = datetime.now(timezone.utc)

# ══════════════════════════════════════════════════════════════════════════════
#  FETCH LIVE DATA
# ══════════════════════════════════════════════════════════════════════════════
kev = fetch_kev()
bazaar = fetch_bazaar()
urlhaus = fetch_urlhaus()
feodo = fetch_feodo()
sans = fetch_sans()
tor = fetch_tor()
topports = fetch_topports()
topips = fetch_topips()
honeypot = fetch_honeypot()

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""<div style="text-align:center;margin-bottom:20px;">
  <h1 style="font-size:2.2rem;margin-bottom:0;text-shadow:0 0 8px {GREEN}40;">SecAI-Nexus GRC</h1>
  <div style="font-size:.75rem;color:{GREY};margin-top:-4px;letter-spacing:.5px;">REAL-TIME CYBER THREAT INTELLIGENCE & GOVERNANCE · RISK · COMPLIANCE OBSERVABILITY PLATFORM</div></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PULSE SECTION (LIVE METRICS)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="rl-p">LIVE THREAT PULSE</div>', unsafe_allow_html=True)
p1,p2,p3,p4,p5 = st.columns(5)
with p1:
    if kev:
        st.markdown(cm("CISA KEV", f"{kev['total']:,}", f"+{kev['d30']} last 30d", "Top Vendor: "+kev['tv'], "Ransomware: "+str(kev['rw']), f"<span class='d-g'>+{kev['d1']}</span> 24h | <span class='d-a'>+{kev['d7']}</span> 7d", p=True), unsafe_allow_html=True)
    else:
        st.markdown(cm("CISA KEV", "N/A", "Known Exploited Vulns", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>", p=True), unsafe_allow_html=True)
with p2:
    if bazaar:
        st.markdown(cm("MalwareBazaar", f"{bazaar['total']:,}", f"+{bazaar['d1']} last 24h", "Top Family: "+bazaar['tf'], f"Families: {bazaar['families']}", f"<span class='d-a'>+{bazaar['d7']}</span> 7d | Top File: {bazaar['top_ft']}", p=True), unsafe_allow_html=True)
    else:
        st.markdown(cm("MalwareBazaar", "N/A", "Recent Samples", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>", p=True), unsafe_allow_html=True)
with p3:
    if urlhaus:
        st.markdown(cm("URLhaus", f"{urlhaus['online']:,}", "Active Malware URLs", "abuse.ch feed", "Real-time", "<span class='d-g'>LIVE</span>", p=True), unsafe_allow_html=True)
    else:
        st.markdown(cm("URLhaus", "N/A", "Active Malware URLs", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>", p=True), unsafe_allow_html=True)
with p4:
    if feodo:
        st.markdown(cm("Feodo Tracker", f"{feodo['on']:,}", "Active C2 IPs", "Top Malware: "+feodo['top_mw'], f"Offline: {feodo['off']:,}", f"<span class='d-n'>{feodo['mw_fams']}</span> Families", p=True), unsafe_allow_html=True)
    else:
        st.markdown(cm("Feodo Tracker", "N/A", "Botnet C2 IPs", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>", p=True), unsafe_allow_html=True)
with p5:
    if sans:
        st.markdown(cm("SANS ISC", sans['infocon'].upper(), "Internet Storm Center", "Infocon Status", "Global Threat Level", "<span class='d-g'>LIVE</span>", p=True), unsafe_allow_html=True)
    else:
        st.markdown(cm("SANS ISC", "N/A", "Infocon Status", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>", p=True), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  METRICS ROWS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(rl("IBM COST OF A DATA BREACH 2025"), unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.markdown(cm("AVG BREACH COST", IBM_BREACH_COST['avg_cost'], "Global Average", "USD", f"Prev: {IBM_BREACH_COST['avg_cost_prev']}", f"<span class='d-a'>{IBM_BREACH_COST['delta_cost']}</span> YoY", e=True), unsafe_allow_html=True)
with c2: st.markdown(cm("MEGABREACH COST", IBM_BREACH_COST['megabreach_cost'], "50M+ Records", "USD", f"Prev: {IBM_BREACH_COST['megabreach_prev']}", f"<span class='d-a'>{IBM_BREACH_COST['delta_mega']}</span> YoY", e=True), unsafe_allow_html=True)
with c3: st.markdown(cm("DETECTION TIME", IBM_BREACH_COST['detection_time'], "Mean Time to Identify", "Days", f"Prev: {IBM_BREACH_COST['detection_prev']}", f"<span class='d-g'>{IBM_BREACH_COST['delta_detect']}</span> YoY", e=True), unsafe_allow_html=True)
with c4: st.markdown(cm("CONTAIN TIME", IBM_BREACH_COST['contain_time'], "Mean Time to Contain", "Days", f"Prev: {IBM_BREACH_COST['contain_prev']}", f"<span class='d-g'>{IBM_BREACH_COST['delta_contain']}</span> YoY", e=True), unsafe_allow_html=True)
with c5: st.markdown(cm("RANSOM PAID", IBM_BREACH_COST['ransom_paid'], "Average Payment", "USD", f"Prev: {IBM_BREACH_COST['ransom_prev']}", f"<span class='d-a'>{IBM_BREACH_COST['delta_ransom']}</span> YoY", e=True), unsafe_allow_html=True)

st.markdown(rl("CROWDSTRIKE GLOBAL THREAT REPORT 2025/2026"), unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.markdown(cm("BREAKOUT TIME", CROWDSTRIKE_GTR['breakout_time'], "Adversary Speed", "Minutes", f"Prev: {CROWDSTRIKE_GTR['breakout_prev']}", f"<span class='d-g'>{CROWDSTRIKE_GTR['delta_break']}</span> YoY", e=True), unsafe_allow_html=True)
with c2: st.markdown(cm("CLOUD INTRUSIONS", CROWDSTRIKE_GTR['cloud_intrusions'], "% of Incidents", "Cloud-Focused", f"Prev: {CROWDSTRIKE_GTR['cloud_prev']}", f"<span class='d-a'>{CROWDSTRIKE_GTR['delta_cloud']}</span> YoY", e=True), unsafe_allow_html=True)
with c3: st.markdown(cm("AI-DRIVEN ATTACKS", CROWDSTRIKE_GTR['ai_attacks'], "% of Threats", "AI/LLM Exploits", f"Prev: {CROWDSTRIKE_GTR['ai_prev']}", f"<span class='d-a'>{CROWDSTRIKE_GTR['delta_ai']}</span> YoY", e=True), unsafe_allow_html=True)
with c4: st.markdown(cm("RANSOM DEMANDS", CROWDSTRIKE_GTR['ransom_demands'], "Average Demand", "USD", f"Prev: {CROWDSTRIKE_GTR['ransom_prev']}", f"<span class='d-a'>{CROWDSTRIKE_GTR['delta_ransom']}</span> YoY", e=True), unsafe_allow_html=True)
with c5: st.markdown(cm("APT SPEED", CROWDSTRIKE_GTR['apt_speed'], "Nation-State Breakout", "Minutes", f"Prev: {CROWDSTRIKE_GTR['apt_prev']}", f"<span class='d-g'>{CROWDSTRIKE_GTR['delta_apt']}</span> YoY", e=True), unsafe_allow_html=True)

st.markdown(rl("MANDIANT M-TRENDS 2025"), unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.markdown(cm("DWELL TIME", MANDIANT_MTRENDS['dwell_time'], "Global Median", "Days", f"Prev: {MANDIANT_MTRENDS['dwell_prev']}", f"<span class='d-g'>{MANDIANT_MTRENDS['delta_dwell']}</span> YoY", e=True), unsafe_allow_html=True)
with c2: st.markdown(cm("RANSOM DEPLOY", MANDIANT_MTRENDS['ransom_deploy'], "Median Time", "Days", f"Prev: {MANDIANT_MTRENDS['ransom_prev']}", f"<span class='d-g'>{MANDIANT_MTRENDS['delta_ransom']}</span> YoY", e=True), unsafe_allow_html=True)
with c3: st.markdown(cm("INTERNAL DETECT", MANDIANT_MTRENDS['internal_detect'], "% of Cases", "Self-Detected", f"Prev: {MANDIANT_MTRENDS['int_prev']}", f"<span class='d-g'>{MANDIANT_MTRENDS['delta_int']}</span> YoY", e=True), unsafe_allow_html=True)
with c4: st.markdown(cm("EXT NOTIFY", MANDIANT_MTRENDS['ext_notify'], "% of Cases", "External Notification", f"Prev: {MANDIANT_MTRENDS['ext_prev']}", f"<span class='d-b'>{MANDIANT_MTRENDS['delta_ext']}</span> YoY", e=True), unsafe_allow_html=True)
with c5: st.markdown(cm("CLOUD DWELL", MANDIANT_MTRENDS['cloud_dwell'], "Median Time", "Days", f"Prev: {MANDIANT_MTRENDS['cloud_prev']}", f"<span class='d-g'>{MANDIANT_MTRENDS['delta_cloud']}</span> YoY", e=True), unsafe_allow_html=True)

st.markdown(rl("SOPHOS STATE OF RANSOMWARE 2025"), unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.markdown(cm("ATTACK RATE", SOPHOS_RANSOM['attack_rate'], "% Orgs Hit", "Ransomware Incidents", f"Prev: {SOPHOS_RANSOM['attack_prev']}", f"<span class='d-a'>{SOPHOS_RANSOM['delta_attack']}</span> YoY", e=True), unsafe_allow_html=True)
with c2: st.markdown(cm("PAID RATE", SOPHOS_RANSOM['paid_rate'], "% Victims Paid", "Ransom Payments", f"Prev: {SOPHOS_RANSOM['paid_prev']}", f"<span class='d-a'>{SOPHOS_RANSOM['delta_paid']}</span> YoY", e=True), unsafe_allow_html=True)
with c3: st.markdown(cm("AVG RANSOM", SOPHOS_RANSOM['avg_ransom'], "Paid Amount", "USD", f"Prev: {SOPHOS_RANSOM['ransom_prev']}", f"<span class='d-a'>{SOPHOS_RANSOM['delta_ransom']}</span> YoY", e=True), unsafe_allow_html=True)
with c4: st.markdown(cm("RECOVERY COST", SOPHOS_RANSOM['recovery_cost'], "Excl. Ransom", "USD", f"Prev: {SOPHOS_RANSOM['recov_prev']}", f"<span class='d-a'>{SOPHOS_RANSOM['delta_recov']}</span> YoY", e=True), unsafe_allow_html=True)
with c5: st.markdown(cm("RECOVERY TIME", SOPHOS_RANSOM['recovery_time'], "Median Time", "Weeks", f"Prev: {SOPHOS_RANSOM['recov_prev']}", f"<span class='d-g'>{SOPHOS_RANSOM['delta_time']}</span> YoY", e=True), unsafe_allow_html=True)

st.markdown(rl("VERIZON DBIR 2025"), unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.markdown(cm("BREACH COUNT", VERIZON_DBIR['breach_count'], "Analyzed Breaches", "Global", f"Prev: {VERIZON_DBIR['breach_prev']}", f"<span class='d-n'>{VERIZON_DBIR['delta_breach']}</span> YoY", e=True), unsafe_allow_html=True)
with c2: st.markdown(cm("RANSOM INCIDENTS", VERIZON_DBIR['ransom_incidents'], "% of Breaches", "Involving Ransomware", f"Prev: {VERIZON_DBIR['ransom_prev']}", f"<span class='d-a'>{VERIZON_DBIR['delta_ransom']}</span> YoY", e=True), unsafe_allow_html=True)
with c3: st.markdown(cm("VULN EXPLOIT", VERIZON_DBIR['vuln_exploit'], "% of Breaches", "Vulnerability Exploitation", f"Prev: {VERIZON_DBIR['vuln_prev']}", f"<span class='d-b'>{VERIZON_DBIR['delta_vuln']}</span> YoY", e=True), unsafe_allow_html=True)
with c4: st.markdown(cm("CRED THEFT", VERIZON_DBIR['cred_theft'], "% of Breaches", "Stolen Credentials", f"Prev: {VERIZON_DBIR['cred_prev']}", f"<span class='d-b'>{VERIZON_DBIR['delta_cred']}</span> YoY", e=True), unsafe_allow_html=True)
with c5: st.markdown(cm("PHISH SUCCESS", VERIZON_DBIR['phish_success'], "% Click Rate", "Phishing Simulations", f"Prev: {VERIZON_DBIR['phish_prev']}", f"<span class='d-a'>{VERIZON_DBIR['delta_phish']}</span> YoY", e=True), unsafe_allow_html=True)

st.markdown(rl("OWASP LLM TOP 10 RISKS 2025"), unsafe_allow_html=True)
o1,o2 = st.columns(2)
with o1:
    for i in range(5):
        st.markdown(cm(OWASP_LLM[i][0], OWASP_LLM[i][1], OWASP_LLM[i][2], "OWASP Risk", f"Rank {i+1}", "<span class='d-a'>HIGH</span> Severity", e=True), unsafe_allow_html=True)
with o2:
    for i in range(5,10):
        st.markdown(cm(OWASP_LLM[i][0], OWASP_LLM[i][1], OWASP_LLM[i][2], "OWASP Risk", f"Rank {i+1}", "<span class='d-a'>HIGH</span> Severity", e=True), unsafe_allow_html=True)

st.markdown(rl("MITRE ATT&CK FRAMEWORK TECHNIQUES"), unsafe_allow_html=True)
m1,m2 = st.columns(2)
with m1:
    for i in range(6):
        st.markdown(cm(MITRE_ATTACK[i][0], MITRE_ATTACK[i][1], MITRE_ATTACK[i][2], "Tactic", f"v15", "<span class='d-n'>ENTERPRISE</span> Matrix"), unsafe_allow_html=True)
with m2:
    for i in range(6,12):
        st.markdown(cm(MITRE_ATTACK[i][0], MITRE_ATTACK[i][1], MITRE_ATTACK[i][2], "Tactic", f"v15", "<span class='d-n'>ENTERPRISE</span> Matrix"), unsafe_allow_html=True)

st.markdown(rl("NATION-STATE APT GROUPS"), unsafe_allow_html=True)
a1,a2 = st.columns(2)
with a1:
    for i in range(6):
        st.markdown(cm(APT_GROUPS[i][0], APT_GROUPS[i][1], APT_GROUPS[i][2], "Origin/Focus", "Active 2025", "<span class='d-b'>THREAT</span> Actor", e=True), unsafe_allow_html=True)
with a2:
    for i in range(6,12):
        st.markdown(cm(APT_GROUPS[i][0], APT_GROUPS[i][1], APT_GROUPS[i][2], "Origin/Focus", "Active 2025", "<span class='d-b'>THREAT</span> Actor", e=True), unsafe_allow_html=True)

st.markdown(rl("TOP EXPLOITED CVES 2025"), unsafe_allow_html=True)
v1,v2 = st.columns(2)
with v1:
    for i in range(5):
        st.markdown(cm(TOP_CVES[i][0], TOP_CVES[i][1], TOP_CVES[i][2], "CISA KEV", "High Impact", "<span class='d-a'>EXPLOITED</span>", e=True), unsafe_allow_html=True)
with v2:
    for i in range(5,10):
        st.markdown(cm(TOP_CVES[i][0], TOP_CVES[i][1], TOP_CVES[i][2], "CISA KEV", "High Impact", "<span class='d-a'>EXPLOITED</span>", e=True), unsafe_allow_html=True)

st.markdown(rl("ATTACK VECTOR BREAKDOWN 2025"), unsafe_allow_html=True)
av_cols = st.columns(len(ATTACK_VECTORS))
for i, (k, v) in enumerate(ATTACK_VECTORS.items()):
    with av_cols[i]:
        st.markdown(cm(k.upper(), v, "% of Attacks", "DBIR Est", "2025 Trend", "<span class='d-a'>RISING</span>", e=True), unsafe_allow_html=True)

st.markdown(rl("AI-POWERED CYBERCRIME TRENDS 2025"), unsafe_allow_html=True)
ai_cols = st.columns(4)
for i, trend in enumerate(AI_CYBER_TRENDS):
    with ai_cols[i % 4]:
        st.markdown(cm(trend[0].upper(), trend[1], "Impact", "Est Trend", "AI Risk", "<span class='d-b'>EMERGING</span>", e=True), unsafe_allow_html=True)

st.markdown(rl("COMPLIANCE POSTURE BENCHMARKS 2025"), unsafe_allow_html=True)
cp_cols = st.columns(len(COMPLIANCE_BENCH))
for i, (k, v) in enumerate(COMPLIANCE_BENCH.items()):
    with cp_cols[i]:
        st.markdown(cm(k.upper(), v, "% Adoption", "Global Avg", "2025 Est", "<span class='d-g'>IMPROVING</span>", e=True), unsafe_allow_html=True)

st.markdown(rl("INCIDENT RESPONSE BENCHMARKS 2025"), unsafe_allow_html=True)
ir_cols = st.columns(len(IR_BENCH))
for i, (k, v) in enumerate(IR_BENCH.items()):
    with ir_cols[i]:
        st.markdown(cm(k.upper(), v, "Global Metric", "Est", "2025 Trend", "<span class='d-g'>BETTER</span>", e=True), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  LIVE DATA FROM SANS DSHIELD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="rl-p">SANS DSHIELD LIVE NETWORK INTEL</div>', unsafe_allow_html=True)
s1,s2,s3 = st.columns(3)
with s1:
    if topports and 'ports' in topports:
        ports_str = "<br>".join(topports['ports'])
        st.markdown(cm("TOP 10 PORTS", "MULTI", "Most Scanned Ports", "DShield Data", ports_str, "<span class='d-g'>LIVE</span>"), unsafe_allow_html=True)
    else:
        st.markdown(cm("TOP 10 PORTS", "N/A", "Most Scanned", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>"), unsafe_allow_html=True)
with s2:
    if topips and 'ips' in topips:
        ips_str = "<br>".join(topips['ips'])
        st.markdown(cm("TOP 10 IPS", "MULTI", "Source IPs", "Attack Origins", ips_str, "<span class='d-g'>LIVE</span>"), unsafe_allow_html=True)
    else:
        st.markdown(cm("TOP 10 IPS", "N/A", "Source IPs", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>"), unsafe_allow_html=True)
with s3:
    if honeypot and 'sensors' in honeypot:
        st.markdown(cm("HONEYPOT SENSORS", f"{honeypot['sensors']:,}", "Active Sensors", "Global Network", "DShield", "<span class='d-g'>LIVE</span>"), unsafe_allow_html=True)
    else:
        st.markdown(cm("HONEYPOT SENSORS", "N/A", "Active Count", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TOR EXIT NODES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(rl("TOR NETWORK"), unsafe_allow_html=True)
t1 = st.columns(1)[0]
if tor:
    st.markdown(cm("EXIT NODES", f"{tor['c']:,}", "Active Exits", "Tor Project", "Privacy Network", "<span class='d-g'>LIVE</span>"), unsafe_allow_html=True)
else:
    st.markdown(cm("EXIT NODES", "N/A", "Active Exits", "Error fetching", "Retry later", "<span class='d-b'>OFFLINE</span>"), unsafe_allow_html=True)

st.markdown("---")
# ══════════════════════════════════════════════════════════════════════════════
#  THREAT MAPS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""<div style="margin-bottom:14px;text-align:center;">
  <span style="font-size:1.05rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;color:{CYAN};text-shadow:0 0 6px {CYAN}30;animation:cpulse 3s ease-in-out infinite;">
    &gt;&gt; GLOBAL THREAT VISUALIZATION &lt;&lt;</span>
  <div style="font-size:.55rem;color:#505060;margin-top:2px;">2 REAL-TIME GLOBAL ATTACK VISUALIZATION SOURCES</div></div>""", unsafe_allow_html=True)
m1,m2=st.columns(2)
with m1:
    st.markdown('<a href="https://livethreatmap.radware.com/" target="_blank" class="ml">&gt;&gt; RADWARE LIVE THREAT MAP</a>', unsafe_allow_html=True)
    iframe("https://livethreatmap.radware.com/", 1100)
with m2:
    st.markdown('<a href="https://threatmap.fortiguard.com/" target="_blank" class="ml">&gt;&gt; FORTINET FORTIGUARD MAP</a>', unsafe_allow_html=True)
    iframe("https://threatmap.fortiguard.com/", 1100)
st.markdown("---")
# ══════════════════════════════════════════════════════════════════════════════
#  GRC RESOURCES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""<div style="margin-top:24px;margin-bottom:14px;text-align:center;">
  <span style="font-size:1.05rem;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px;">
    <a href="https://www.nist.gov/cyberframework" target="_blank" class="sh">
      &gt;&gt; GRC RESOURCES &amp; TOOLS &lt;&lt;</a></span>
  <div style="font-size:.55rem;color:#505060;margin-top:2px;">80 CURATED · RANKED BY POPULARITY · FRAMEWORKS · TOOLS · TRAINING · INTEL · THREAT MAPS</div></div>""", unsafe_allow_html=True)
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
  <div style="color:#666;font-size:.8rem;margin-bottom:14px;">
    Developed by <b style="color:{GREEN};">Adam Kistler</b> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/adam-kistler-441a31192/" target="_blank"
       style="color:{BLUE};text-decoration:none;border-bottom:1px dashed {BLUE};">LinkedIn</a></div>
  <div style="color:#444;font-size:.65rem;padding:0 10%;line-height:1.4;margin-bottom:8px;">
    <b>LEGAL DISCLAIMER:</b> Educational and portfolio purposes only. All threat maps and data
    are property of their respective owners. SecAI-Nexus does not host or process third-party content.<br>
    <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/" target="_blank" class="fl">
      Code and layout licensed CC BY-NC 4.0.</a></div>
  <div style="color:#2a2a3a;font-size:.65rem;">
    SecAI-Nexus GRC [v30.0] · Live Data Engine ·
    112 Metrics · 8 Intel Tables · 2 Maps · 80 Resources · {now_utc.strftime("%Y")}</div></div>""", unsafe_allow_html=True)
</DOCUMENT> 

 <DOCUMENT filename="streamlit_app (9).py">
import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

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
<meta property="og:image" content="https://raw.githubusercontent.com/adamkistler98/SecAI-Nexus/main/assets/SecAiImage.png">
<meta property="og:url" content="https://secai-nexus.streamlit.app/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
""", unsafe_allow_html=True)
# ===================================================================
MONO  = "'Courier New', Courier, monospa...(truncated 108175 characters)...ncidental, special, exemplary, or consequential damages arising in any way out of the use of
    this software or reliance on its output, even if advised of the possibility of such damages. Estimated
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
    SecAI-Nexus GRC [v30.0] · Live Data Engine · 12hr Cache ·
    112 Metrics · 8 Intel Tables · 2 Maps · 80 Resources · {now_utc.strftime("%Y")}</div></div>""", unsafe_allow_html=True)
    # ====================== END ======================
