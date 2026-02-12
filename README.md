🔒 SecAI-Nexus // GRC
Global Threat Visibility & Intelligence Dashboard
Status: OPERATIONAL | Encryption: AES-256 | Protocol: REAL-TIME

📡 Overview
SecAI-Nexus GRC is a unified situational awareness console designed for Security Operations Centers (SOC) and Governance, Risk, and Compliance (GRC) teams.

It aggregates real-time cyber threat telemetry from multiple Tier-1 intelligence sources into a single, high-contrast "stealth" interface. Unlike static dashboards, SecAI-Nexus pulls live data from global sensors, vulnerability databases, and threat intelligence feeds to provide an instant pulse on the global cyber battlefield.

👁️ Key Capabilities
1. Multi-Vector Threat Maps
A synchronized 4x2 grid visualizing live attack vectors across the globe.

Sources: Bitdefender, Deutsche Telekom (Sicherheitstacho), Check Point ThreatCloud, Radware, Fortinet, Kaspersky, SonicWall, and Threatbutt.

Utility: Instant visualization of DDoS campaigns, malware propagation, and botnet activity.

2. Internet Noise Intelligence (GreyNoise)
A dedicated, large-scale viewport for the GreyNoise Visualizer.

Function: A search engine and intelligence tool that analyzes "internet background noise." It identifies mass-scanners, bots, and benign crawlers (like Shodan or Googlebot).

Utility: Helps analysts distinguish between harmless automated scanning and actual targeted attacks. "Anti-Threat Intelligence"—it tells you what not to worry about.

3. Live CVE Vulnerability Feed (Real-Time)
Connects directly to the CIRCL.LU Open Data API to fetch the latest Common Vulnerabilities and Exposures (CVEs) as they are published.

Dual-Layer Failover System:

Primary: Fetches live JSON data from the official CVE database.

Failover: If the API is unreachable, the system instantly switches to a High-Fidelity Simulation Mode, generating realistic vulnerability data based on current 2025/2026 trends (e.g., OpenSSL buffers, Kubernetes privilege escalation) to ensure the dashboard never displays "Unknown" errors.

Export: One-click generation of .CSV Intelligence Reports.

4. Infrastructure Risk Landscape
A semi-static, curated intelligence board tracking active threat actor campaigns.

Categories: Ransomware (LockBit, BlackCat), Malware (Emotet, Cobalt Strike), Phishing, and Nation-State APTs (Volt Typhoon, Lazarus).

Dynamic Styling: Automatically color-codes risks (CRITICAL = Red, HIGH = Orange, MEDIUM = Green).

💻 Installation & Deployment
Prerequisites
Python 3.8 or higher

Internet connection (for fetching live map iframes and API data)

1. Clone the Uplink
Bash
git clone https://github.com/yourusername/secai-nexus.git
cd secai-nexus
2. Install Dependencies
Bash
pip install streamlit pandas requests plotly
3. Initialize the Dashboard
Bash
streamlit run app.py
The interface will automatically launch in your default browser at http://localhost:8501.

🛠️ Configuration
Stealth UI (CSS)
The application uses a custom injected CSS block to override Streamlit's default "Light Mode."

Background: Deep Black (#050505)

Accent Color: Cyber Green (#00ff41)

Alert Colors: Critical Red (#ff3333) & High-Vis Orange (#ffaa00)

Font: Monospace (Courier New) for that "terminal" aesthetic.

To modify the theme, edit the st.markdown section under --- ADVANCED GRC CSS --- in app.py.

📂 Project Structure
Plaintext
secai-nexus/
├── app.py              # Main dashboard logic and UI rendering
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
└── assets/             # (Optional) Static assets
⚠️ Disclaimer
This dashboard is intended for educational and situational awareness purposes.

The Maps are embedded iframes from third-party vendors (Bitdefender, Kaspersky, etc.) and rely on their respective service availability.

The CVE Feed pulls public data; do not use this as a sole source for critical patching decisions.

Failover Data: If the internet connection is severed, the CVE and Risk sections may switch to simulation mode to preserve UI integrity.

"Eternal vigilance is the price of security."

SecAI-Nexus // End of Transmission
