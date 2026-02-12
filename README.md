# 🔒 SecAI-Nexus GRC

**Global Real-Time Cyber Threat Intelligence Dashboard**

A sleek, terminal-style Streamlit application delivering live visibility into worldwide cyber threats, vulnerabilities, and attack activity.

Built for Security Operations, Threat Intelligence, and GRC teams who want an always-on, immersive "war room" view.

---

## ✨ Features

- **Live Cyber Threat Maps** — 8+ embedded real-time attack maps (Bitdefender, Check Point, Fortinet, Kaspersky, GreyNoise, SonicWall, etc.)
- **Large GreyNoise Visualization** — Full-height advanced threat intelligence map
- **Real-Time CVE Feed** — Pulls latest CVEs from the circl.lu API with intelligent fallback to high-fidelity simulated data
- **Infrastructure Risk Landscape** — Dynamic panels for:
  - Ransomware groups (LockBit, BlackCat, Akira, etc.)
  - Malware families (Emotet, Qakbot, Cobalt Strike, etc.)
  - Phishing tactics and targets
  - Nation-state APT actors (APT29, Volt Typhoon, Lazarus, etc.)
- **Terminal-Style UI** — Dark cyberpunk theme with matrix-green accents, color-coded risk levels (Critical/High/Medium), and authentic hacker aesthetic
- **Export & Refresh** — One-click RE-SYNC and CSV download of vulnerability reports
- **Stealth Mode** — Collapsed sidebar, hidden Streamlit elements, system-clock header

---

## 🛠️ Tech Stack

- **Framework**: Streamlit
- **Data**: pandas, requests
- **Styling**: Custom CSS (terminal tables, glow effects, dark theme)
- **Data Sources**:
  - Real: [circl.lu CVE API](https://cve.circl.lu/api/last/30)
  - Maps: Public threat intelligence providers
  - Simulation: Realistic synthetic data when API is unavailable

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9 or higher

### 2. Installation

```bash
# Clone or download the project
git clone <your-repo-url>
cd sec-ai-nexus-grc

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Install dependencies
pip install streamlit pandas requests
3. Run the Dashboard
Bashstreamlit run sec_ai_nexus.py
Open http://localhost:8501 in your browser.

📋 Requirements (requirements.txt)
txtstreamlit>=1.30.0
pandas
requests
Install with:
Bashpip install -r requirements.txt

📖 How It Works

CVE Section: Attempts a real API call to https://cve.circl.lu/api/last/30. If it fails (network issues, rate limits, etc.), it seamlessly switches to generate_high_fidelity_sim() which creates realistic, up-to-date-looking CVE entries.
Threat Maps: Embedded via st.components.v1.iframe for zero-maintenance live feeds.
Risk Landscape Panels: Procedurally generated tables using real threat actor/group names for training and demonstration realism.
Styling: Heavy custom CSS injected via st.markdown(..., unsafe_allow_html=True) to create the distinctive terminal/cyberpunk look.
State Management: Uses st.session_state to persist CVE data between refreshes.


⚠️ Important Notes

Internet connection is required for live threat maps and real CVE data.
Some map providers may occasionally block iframes or experience slow loading due to their own protections.
All simulated data is for demonstration and training purposes only and uses publicly known threat actor names.
The dashboard is intentionally styled to look "stealth" and operator-focused.


🎯 Customization Ideas

Add more threat intelligence sources (AlienVault OTX, MITRE ATT&CK, etc.)
Integrate real APIs for ransomware or malware tracking
Add filtering, search, and pagination
Deploy to Streamlit Community Cloud, Hugging Face Spaces, or Docker
Extend the simulation engine with more realistic logic


📄 License
This project is open-source and free for educational, defensive security, and personal use.
Made with 🔥 for the cyber defense community.

SecAI-Nexus GRC — Because visibility is the first step in defense.
