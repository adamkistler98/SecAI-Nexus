# 🤖 SecAI-Nexus GRC

**Real-Time Cyber Threat Intelligence & Governance, Risk & Compliance (GRC) Observability Platform**

**SecAI-Nexus** is a **free, open-source** cybersecurity GRC observability platform that consolidates real-time cyber threat intelligence from public sources into one centralized, always-available dashboard.

**100% free. No API keys. No login. No tracking. No data collection.**

🔗 **[Live Dashboard →](https://secai-nexus.streamlit.app)**  
Works seamlessly on desktop and mobile.

---

## 👤 Created by Adam Kistler — The Original Creator

This project was conceived, designed, developed, and is actively maintained by **Adam Kistler** (LinkedIn: [adam-kistler-441a31192](https://www.linkedin.com/in/adam-kistler-441a31192/)).

**The reason I built it:**  
What began as a personal tool has evolved into a centralized dashboard designed to sharpen awareness for both experienced cybersecurity/GRC professionals and those just entering the field.

---

## 💡 The Vision

SecAI-Nexus was created to democratize high-quality threat intelligence and GRC visibility. It brings together live metrics, AI-specific risk tracking, and contextual intelligence in a clean, high-density interface — all without subscriptions, complexity, or hidden costs.

### What It Includes

- **112 near-real-time risk metrics** across 14 thematic sections  
- **Dedicated AI & LLM threat intelligence reference**, tracking the emerging AI attack landscape  
- **Contextual, evidence-based intelligence** — each metric includes 5 supporting data points from trusted sources (IBM, CrowdStrike, Mandiant, Sophos, Verizon DBIR, CISA)  
- **80 curated cybersecurity resources** — tools, frameworks, training resources, and references  
- **Live global threat visualization** — embedded real-time attack maps from Radware and FortiGuard  
- **Full transparency** — all third-party sources credited with direct hyperlinks  

---

## ⚡ Optimized Architecture

- 12-hour TTL caching cycle using Streamlit decorators for reliable, always-available metrics while respecting upstream API rate limits and reducing compute overhead  
- Python + Streamlit with intelligent caching, efficient request handling, and custom UI optimized for high-density information display and fast performance  
- Automated CI/CD pipeline via GitHub for consistent deployments, rapid iteration, and version-controlled releases  

---

## 🛡️ Security by Design

- Strictly read-only, zero-input architecture (no authentication, no persistent storage, no user tracking)  
- Hardened browser runtime with Content-Security-Policy (CSP), X-Frame-Options: DENY, and XSRF protection  
- Pinned dependencies with automated scanning (CodeQL, secret detection, and CVE checks) via GitHub Actions  
- Strict request validation including response size limits (5 MB cap) and content-type enforcement  
- Session-based rate limiting to prevent API abuse and excessive upstream load  
- All outbound traffic restricted to trusted threat intelligence endpoints only  

---

## 🛠️ Data Sources

**Live Public Feeds (no keys required)**  
- CISA Known Exploited Vulnerabilities (KEV)  
- MalwareBazaar, URLhaus, Feodo Tracker (abuse.ch)  
- SANS Internet Storm Center (Infocon, top ports, top IPs, honeypots)  
- Tor Project exit nodes  

**Estimated metrics** (clearly labeled `EST`) are drawn from the latest published industry reports.

---

## 🚀 Quick Start

### Local Development
```bash
git clone https://github.com/adamkistler98/SecAI-Nexus.git
cd SecAI-Nexus
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
One-Click Deploy (Free)
Visit share.streamlit.io, connect your repo, and deploy streamlit_app.py.

📄 License
Dual licensing (chosen by the original creator):

Source code — MIT License
Design, layout & visual architecture — CC BY-NC 4.0 (non-commercial use with attribution)


📬 Community & Feedback
Community Resource — Feedback Welcome!

Shoutout to Streamlit and GitHub for their incredible open-source platforms that power this build!

Full source code → https://github.com/adamkistler98/SecAI-Nexus
This tool is provided for educational purposes only — use at your own risk!
#cybersecurity #GRC #threatintelligence #infosec #CISO #AI #LLM #OWASP #SecAINexus #opensource #streamlit #observability #Python #OSINT #APIs #CyberSecurityTools
