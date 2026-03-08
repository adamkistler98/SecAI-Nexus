# 🤖 SecAI-Nexus GRC

**Real-Time Cyber Threat Intelligence & GRC Observability Platform**

A cyberpunk-themed Streamlit dashboard delivering live visibility into the global threat landscape — purpose-built for GRC professionals, security analysts, SOC teams, and CISOs who need a consolidated command center without enterprise licensing costs.

**100% free. No API keys. No authentication. No data collection.**

🔗 **[Live Dashboard →](https://secai-nexus.streamlit.app)** · Works on desktop and mobile

---

## 🎯 What It Does

SecAI-Nexus consolidates threat intelligence from 9 free public APIs and 15+ authoritative research reports into a single real-time dashboard with **112 metric cards**, **8 reference tables**, **2 live attack maps**, and **80 curated resource links**.

Every metric includes 5 contextual intel points sourced from the latest published data (IBM 2025, CrowdStrike GTR 2025/2026, Mandiant M-Trends, Sophos, OWASP, DBIR).

### Dashboard Sections

| Section | Cards | Focus |
|---------|-------|-------|
| 🤖 AI & LLM Threat Intelligence | 6 | Deepfake vishing, prompt injection, AI malware, model poisoning |
| 🔐 Cloud, Identity & AI Governance | 6 | Shadow AI, malware-free attacks, breakout time, cloud intrusions |
| 📊 Compliance & Third-Party Risk | 6 | SOC 2 readiness, vendor breaches, regulatory fines, cyber insurance |
| ⚡ Sector Risk & Adversary Intel | 6 | Healthcare/financial targeting, DPRK/Lazarus, eCrime index |
| ⚡ Ransomware Landscape | 6 | LockBit, ALPHV, Cl0p, double extortion, ransom economics |
| ⚡ Attack Surface & Exposure | 6 | Exposed SMB/RDP/databases, top target/source countries |
| ⚡ SANS DShield Sensor Network | 6 | Top attacked ports (live from DShield) |
| ⚡ Attack Sources & Honeypots | 6 | Top IPs, honeypot hits, SSH brute force, IoT scanning |
| ▸ AI Governance & Privacy | 9 | Shadow AI, DSAR volume, encryption, AI incident rate |
| ▸ Breach, Incident & Cost | 9 | Breach cost ($4.44M global), records breached, BEC, phishing |
| ▸ IR & SOC Operations | 9 | MTTD, MTTC, SOC alert volume, dwell time, recovery time |
| ▸ Security Posture & Workforce | 9 | Zero trust, MFA adoption, patch lag, workforce gap (4.0M) |
| ▸ Financial & Regulatory | 9 | GDPR fines, IC3 losses, crypto theft, supply chain |
| ▸ Vulnerability & Exploit Intel | 9 | CISA KEV (live), CVE volume, time-to-exploit, SANS Infocon |
| ▸ Malware, C2 & Advisories | 9 | MalwareBazaar (live), URLhaus, Feodo C2s, Tor exit nodes |

### Reference Tables (4×2 Grid)
- ⚔ MITRE ATT&CK Top Techniques
- 💀 Top Ransomware Groups
- 🌐 Nation-State APT Groups
- 📊 Attack Vector Breakdown (IBM 2025)
- 🔥 Top Exploited CVEs 2024
- 💰 Breach Cost by Industry (IBM 2025)
- 🛡 OWASP LLM Top 10 (2025)
- 🤖 AI-Powered Cybercrime & Threats

### Additional
- **CISA KEV Table** — 15 most recently added exploited vulnerabilities (live)
- **23 Compliance Frameworks** — NIST CSF 2.0, ISO 27001, SOC 2, PCI DSS, HIPAA, GDPR, CMMC, DORA, NIS2, China MLPS, OWASP LLM/API, and more
- **2 Live Threat Maps** — Radware and FortiGuard real-time attack visualization
- **80 Curated Resources** — Frameworks, tools, threat intel, training, maps

---

## 🛡️ Data Sources

### Live APIs (No Keys Required)
| Source | Data | Refresh |
|--------|------|---------|
| [CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | Exploited vulnerabilities catalog | 12 hr |
| [MalwareBazaar](https://bazaar.abuse.ch/) | Recent malware samples | 12 hr |
| [URLhaus](https://urlhaus.abuse.ch/) | Live malicious URLs | 12 hr |
| [Feodo Tracker](https://feodotracker.abuse.ch/) | Botnet C2 infrastructure | 12 hr |
| [SANS ISC Infocon](https://isc.sans.edu/) | Internet threat level | 12 hr |
| [SANS DShield TopPorts](https://isc.sans.edu/) | Most attacked ports | 12 hr |
| [SANS DShield TopIPs](https://isc.sans.edu/) | Top attacking IPs | 12 hr |
| [SANS Honeypot](https://isc.sans.edu/) | Web honeypot telemetry | 12 hr |
| [Tor Project](https://metrics.torproject.org/) | Active exit node count | 12 hr |

### Estimated Metrics (Labeled `EST`)
Sourced from the latest published reports, clearly labeled with "last verified 03/26":

IBM Cost of a Data Breach 2025 · CrowdStrike Global Threat Report 2025/2026 · Mandiant M-Trends 2025 · Verizon DBIR 2025 · Sophos State of Ransomware 2025 · FBI IC3 Annual Report · APWG eCrime Report · ISC2 Workforce Study · Chainalysis Crypto Crime Report · Qualys TruRisk Research · SpyCloud Identity Exposure Report · OWASP LLM Top 10 (2025)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | [Streamlit](https://streamlit.io/) (Python) |
| Language | Python 3.9+ |
| HTTP | `requests` (read-only GET to public APIs) |
| Caching | `@st.cache_data` with configurable TTL |
| Hosting | [Streamlit Community Cloud](https://streamlit.io/cloud) (free) |
| Styling | Custom CSS (cyberpunk terminal theme) |
| Security | Sandboxed iframes, no user data processing |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Internet connection (for live feeds and threat maps)

### Local Development
```bash
git clone https://github.com/adamkistler98/SecAI-Nexus.git
cd secai-nexus-grc

python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

### Deploy to Streamlit Cloud (Free)
1. Push to GitLab/GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Set main file to `app.py`
4. Deploy — no environment variables or secrets needed

---

## 📋 Requirements

```
streamlit>=1.30.0
requests>=2.28.0
```

That's it. No pandas, no numpy, no database drivers. Two dependencies.

---

## 🔒 Security

SecAI-Nexus is designed with a minimal attack surface:

- **No user input processing** — Dashboard is read-only, no forms or text fields
- **No data storage** — Nothing persisted to disk, database, or session
- **No authentication** — No credentials, tokens, or API keys used or stored
- **No outbound writes** — All API calls are read-only GET requests to public endpoints
- **Sandboxed iframes** — Embedded maps use `sandbox="allow-scripts allow-same-origin allow-forms allow-popups"` to restrict third-party content
- **No cookies or tracking** — No analytics, telemetry, or user fingerprinting
- **Fallback data** — If APIs are unreachable, static baseline data renders (no errors or empty states)
- **DevSecOps** — GitLab CI/CD pipeline runs SAST (Semgrep/Bandit) on every commit

For vulnerability reports, see [SECURITY.md](SECURITY.md).

---

## 📄 License

This project uses a **dual-license** structure:

- **Source Code** (`app.py`, configs) — [MIT License](https://opensource.org/licenses/MIT) — free to use, modify, and distribute with attribution
- **Dashboard Design & Layout** (CSS theme, card structure, section architecture, color scheme) — [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — non-commercial use with attribution


All embedded threat maps and external data feeds remain the property of their respective owners (Radware, Fortinet, CISA, abuse.ch, SANS ISC, Tor Project). SecAI-Nexus does not host, cache, or redistribute third-party content.

---

## 🎯 Roadmap

- [ ] Additional live API integrations (NVD, CISA RSS, ThreatFox)
- [ ] Exportable PDF/CSV threat reports
- [ ] Historical trend tracking with persistent storage
- [ ] Custom alert thresholds and notifications
- [ ] Dark/light theme toggle
- [ ] Containerized Docker deployment

---

## 🤝 Contributing

Contributions welcome. Please open an issue first to discuss proposed changes. All PRs must pass the SAST pipeline.

---

## 📬 Contact

**Adam Kistler** — [LinkedIn](https://www.linkedin.com/in/adam-kistler-441a31192/)

Questions, feedback, or collaboration inquiries welcome via LinkedIn DM.

---

<p align="center">
<b>SecAI-Nexus GRC [v30.0]</b><br>
112 Metrics · 8 Intel Tables · 2 Live Maps · 23 Frameworks · 80 Resources<br>
<i>Because visibility is the first step in defense.</i>
</p>
