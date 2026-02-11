# SecAI-Nexus v2.0

**AI-Powered Cybersecurity Research and Analysis Platform**

SecAI-Nexus is a modular, multi-language cybersecurity toolkit designed to demonstrate practical skills in threat detection, digital forensics, low-level system analysis, and Governance, Risk, and Compliance (GRC) assessment. It integrates artificial intelligence, compiled native code, and interactive visualization into a single, user-friendly Streamlit dashboard.

This project serves as a portfolio showcase for roles such as **Security Researcher**, **Cybersecurity Analyst**, **Threat Intelligence Analyst**, or **GRC Specialist**, highlighting cross-language development, secure coding practices, and domain-specific cybersecurity techniques.

## Key Features

- **Interactive Dashboard** — Real-time metrics, threat distribution charts (Plotly), simulated threat feed, and scan history with exportable CSV reports.
- **AI Threat Analyzer** (Python + scikit-learn) — Random Forest classification of files based on engineered features: file size, Shannon entropy, and suspicious keyword density. Simulates static malware analysis.
- **C Low-Level Scanner** — High-performance file scanner (compiled binary) performing size checks, signature string detection, and simulated hash reporting. Demonstrates low-level file I/O and potential EDR/AV component design.
- **Java Log Forensics Analyzer** — Rule-based log parser (compiled Java class) detecting indicators of compromise such as failed logins, brute-force attempts, injection patterns, and ransomware signals. Mimics SIEM correlation rules.
- **GRC Risk Assessment Tool** — Interactive slider-based risk scoring with qualitative levels (Low/Medium/High/Critical) and policy recommendations.
- **Cross-Language Integration** — Python orchestrates subprocess calls to compiled C and Java binaries, showcasing heterogeneous system design.

## Architecture Overview

    A[Streamlit Dashboard<br>(Python Frontend)] --> B[AI/ML Engine<br>(scikit-learn RandomForest)]
    A --> C[C Low-Level Scanner<br>(gcc compiled binary)]
    A --> D[Java Log Forensics<br>(javac compiled class)]
    A --> E[GRC Risk Calculator<br>(Pure Python)]
    B --> F[Feature Extraction Utils<br>(Entropy, Keyword Scan)]
    C & D --> G[Subprocess Execution Layer]
    F --> H[Sample Datasets & Config]

Component,Technology,Purpose
Frontend / Orchestration,"Streamlit, Plotly, pandas","Interactive UI, visualizations, data handling"
AI / Machine Learning,"Python, scikit-learn, numpy",Threat classification via feature engineering
Low-Level Scanning,C (gcc),"Fast file I/O, signature detection"
Log Forensics,Java (javac + java runtime),Rule-based pattern matching
Build & Dependencies,"Makefile, packages.txt, Docker","Compilation, system package management"
Deployment,"Streamlit Community Cloud, Docker",Hosting and containerization

Quick Start (Local Development)
Prerequisites: Python 3.9+, gcc, javac (JDK), git
Bash# Clone the repository
git clone https://gitlab.com/your-username/SecAI-Nexus.git
cd SecAI-Nexus

pip install -r requirements.txt
make
streamlit run streamlit_app.py
Open http://localhost:8501 in your browser.
Docker alternative (includes gcc and JDK):
Bashdocker build -t secai-nexus .
docker run -p 8501:8501 secai-nexus
