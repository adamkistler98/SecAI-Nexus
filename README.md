# 🤖 SecAI-Nexus GRC

**Real-Time Cyber Threat Intelligence & Governance, Risk & Compliance (GRC) Observability Platform**

**Version 1.4 (v73) — July 2026**

**SecAI-Nexus** is a **free, open-source** cybersecurity GRC observability platform that consolidates real-time threat intelligence, AI/LLM risk tracking, multi-framework comparison, and interactive gap analysis into one high-density dashboard.

**100% free. No API keys. No login. No tracking. No data collection.**

🔗 **[Live Dashboard →](https://secai-nexus.streamlit.app)**  
Works seamlessly on desktop and mobile (fully responsive).

---

## 👤 Created & Maintained by Adam Kistler

This project was conceived, designed, developed, and is actively maintained by **Adam Kistler** (Data Governance Platform Administrator at Hertz | CISSP candidate).

**LinkedIn:** [adam-kistler-441a31192](https://www.linkedin.com/in/adam-kistler-441a31192/)  
**GitHub:** [adamkistler98/SecAI-Nexus](https://github.com/adamkistler98/SecAI-Nexus)

**Why I built it:**  
What started as a personal tool has evolved into a centralized, high-density GRC platform designed to give cybersecurity professionals, CISOs, and teams clear visibility into live threats **and** the rapidly evolving AI/regulatory risk landscape of 2026.

---

## 🚀 What's New in v73 (July 2026)

- **Major "Why AI Security Matters" Executive Brief** — 8 prioritized, monetized AI risk cards with specific 2026 statistics and regulatory impact:
  - EU AI Act 7% global revenue fines (first enforcement actions Q2 2026)
  - Shadow AI driving **22% of breaches** (+$680k average cost adder)
  - Record GDPR enforcement (€1.2B single fine)
  - Deepfake CEO fraud ($28M+ documented loss)
  - AI Agent visibility crisis (48.9% of orgs blind to agent traffic)
  - GitHub Advisory surge + agentic AI espionage cases
  - And more — all mapped to real regulatory penalties and board concerns

- **Interactive Framework Gap Matrix (BETA)** — New one-click crosswalk tool. Select any 2+ frameworks (or use presets) to instantly see:
  - Consolidated control coverage %
  - Identified gaps in **AI/LLM governance**, **Vendor/Third-Party Risk**, and **Business Continuity**
  - Dynamic, prioritized recommendations tied directly to high-penalty regulations (EU AI Act, NIS2/DORA, GDPR, SEC AI disclosure, CMMC)

- **12-Framework Comparison Matrix + Visual Analytics** — Now includes SOC 2 Type II, FedRAMP, and NIST AI RMF 1.0 with:
  - Adoption rates, control density, hybrid combination analysis
  - Radar coverage chart, bar charts, pie chart, and new SOC 2 vs NIST CSF coverage heatmap
  - CSV export button for reports and audits

- **Control Lineage Sankey Diagrams** — Two interactive visualizations:
  - Full 12-framework → 34 critical controls lineage
  - Focused SOC 2 + NIST AI RMF → AI governance controls (Prompt Injection, Model Governance, Excessive Agency, etc.)

- **CSV Export Buttons** — Download full framework comparison and crosswalk results for GRC tooling, board packs, and audit evidence.

- **UI/UX & Performance Upgrades** — Sleek cyan-themed refresh button, improved mobile responsiveness, tighter spacing, stronger visual hierarchy for executive briefings, and enhanced security headers (CSP, X-Frame-Options, Referrer-Policy).

- **Updated Metrics** — Now tracking **118 metrics**, 14 data rows, 10 intel tables, and 80+ curated resources.

---

## 💡 Core Features

- **118 near-real-time risk metrics** from live public feeds (CISA KEV, abuse.ch, SANS ISC, Tor Project, etc.) with 30-day and 1-year trend indicators
- **Executive AI Risk Brief** — 8 high-impact, regulation-mapped AI threats with direct source links (IBM 2026, Salt Security, CrowdStrike, etc.)
- **Framework Intelligence Suite** — Side-by-side comparison of 12 major frameworks + interactive Gap Matrix for control rationalization and regulatory alignment
- **Control Lineage Visualization** — Sankey diagrams showing framework overlap and AI-specific governance coverage
- **Live Global Threat Maps** — Embedded real-time attack visualizations from Radware and Fortinet FortiGuard
- **80+ Curated GRC Resources** — Frameworks, threat intel platforms, free tools, training sites, and community resources (categorized and ranked)
- **Clean Cyber-Themed UI** — Monospace font, high-density cards, glowing accents, fully responsive, dark-optimized

---

## 📊 Current Stats (v73)

**118 Metrics** · **14 Data Rows** · **10 Intel Tables** · **80+ Resources**  
**12 Frameworks** in comparison matrix + Gap Matrix  
**2 Interactive Sankey Lineage Diagrams**  
Multiple CSV export options for GRC workflows

---

## 🛡️ Security by Design

- Strictly read-only, zero-input architecture (no authentication, no persistent storage, no user tracking)
- Hardened browser runtime with Content-Security-Policy (CSP), X-Frame-Options: DENY, Referrer-Policy, and XSRF protection
- Pinned dependencies with automated scanning (CodeQL, secret detection, CVE checks) via GitHub Actions
- Strict request validation and session-based rate limiting
- All outbound traffic restricted to trusted public threat intelligence endpoints only

---

## 🛠️ Data Sources

**Live Public Feeds (no keys required)**  
- CISA Known Exploited Vulnerabilities (KEV)  
- MalwareBazaar, URLhaus, Feodo Tracker (abuse.ch)  
- SANS Internet Storm Center (Infocon, top ports, top IPs, honeypots)  
- Tor Project bulk exit list  

**Estimated metrics** (clearly labeled `EST`) are drawn from the latest published industry reports (IBM, CrowdStrike, Salt Security, Verizon DBIR, etc.).

---

## 🚀 Local Deployment

```bash
git clone https://github.com/adamkistler98/SecAI-Nexus.git
cd SecAI-Nexus
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

**One-Click Deploy (Free)**  
Visit [share.streamlit.io](https://share.streamlit.io), connect your repo, and deploy `streamlit_app.py`.

---

## 📄 License

**Dual License** (chosen by the original creator):

- **Source code** — [MIT License](https://opensource.org/licenses/MIT)
- **Design, layout & visual architecture** — [CC BY-NC 4.0](http://creativecommons.org/licenses/by-nc/4.0/) (non-commercial use with attribution)

Full terms: [LICENSE](https://github.com/adamkistler98/SecAI-Nexus/blob/main/LICENSE)

---

## ⚠️ Legal Disclaimer

This project is provided **for educational, informational, portfolio demonstration, and personal use purposes only**. It is **not intended** for use in production environments, as a compliance tool, as professional security advice, or as a basis for business, legal, financial, or regulatory decisions.

All threat intelligence, metrics, statistics, estimates, and data presented are sourced from publicly available third-party reports and APIs. The author makes no representations or warranties, express or implied, regarding accuracy, completeness, timeliness, reliability, or fitness for any particular purpose.

The author shall not be liable for any direct, indirect, incidental, special, exemplary, or consequential damages arising in any way out of the use of this software or reliance on its output, even if advised of the possibility of such damages.

Estimated metrics (labeled "EST") are derived from annually published industry reports and may not reflect current conditions. Live metrics depend on the availability and accuracy of upstream API providers.

This software does not collect, store, process, or transmit any user data. No authentication, cookies, tracking, telemetry, or analytics are implemented.

The author is not affiliated with, endorsed by, or sponsored by any third-party data provider or cybersecurity company referenced within this project.

**Use at your own risk.**

---

## 📬 Community & Feedback

This is a community resource — feedback, suggestions, and contributions are welcome!

- **GitHub Repository**: https://github.com/adamkistler98/SecAI-Nexus  
- **Live App**: https://secai-nexus.streamlit.app  
- **LinkedIn**: https://www.linkedin.com/in/adam-kistler-441a31192/

Shoutout to Streamlit and GitHub for their incredible open-source platforms that power this build!

---

**SecAI-Nexus GRC [v73] | Live Data Engine | 12 hr Cache | 118 Metrics | 10 Intel Tables | 2 Maps | 80+ Resources | 2026**

#cybersecurity #GRC #threatintelligence #AI #LLM #EUAIAct #NIS2 #SOC2 #NIST #frameworks #GapAnalysis #opensource #streamlit #observability #Python #OSINT
