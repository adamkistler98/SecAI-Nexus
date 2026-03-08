# Security Policy

## Supported Versions

Only the latest version on the `main` branch receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 30.x    | ✅ Active          |
| < 30    | ❌ Unsupported     |

## Architecture & Attack Surface

SecAI-Nexus is designed with a **minimal attack surface by default**:

| Vector | Risk | Mitigation |
|--------|------|------------|
| User input | **None** | Dashboard is read-only. No forms, text fields, file uploads, or user-submitted data. |
| Data storage | **None** | No database, no disk writes, no session persistence, no cookies. |
| Authentication | **None** | No credentials stored or transmitted. No API keys required. |
| API calls | **Low** | Read-only GET requests to 9 public endpoints. No write operations. |
| Iframe embedding | **Medium** | Third-party maps (Radware, FortiGuard) sandboxed with `allow-scripts allow-same-origin allow-forms allow-popups`. No `allow-top-navigation`. |
| `unsafe_allow_html` | **Medium** | Used for custom CSS/HTML styling. All HTML is developer-authored (no user input rendered). Streamlit sanitizes by default; our override is for layout only. |
| Dependencies | **Low** | Only 2 runtime dependencies (`streamlit`, `requests`). SAST scans on every commit. |
| Hosting | **Low** | Streamlit Community Cloud. No server-side code execution beyond Streamlit's sandbox. |

## DevSecOps Pipeline

The GitLab CI/CD pipeline runs on every commit:

- **SAST** — Static Application Security Testing via GitLab's built-in analyzers (Semgrep, Bandit)
- **Dependency Scanning** — Checks `requirements.txt` against known CVE databases
- **Secret Detection** — Scans for accidentally committed credentials or tokens

## Known Considerations

1. **Iframe Content**: Embedded threat maps load content from third-party domains (Radware, FortiGuard). While sandboxed, these domains control their own content. If a map provider were compromised, the sandbox restrictions limit impact to the iframe container only.

2. **`unsafe_allow_html=True`**: Streamlit requires this flag for custom HTML/CSS. All rendered HTML in SecAI-Nexus is hardcoded by the developer — no user input is ever interpolated into HTML output. This is a cosmetic override, not a security gap.

3. **Data Accuracy**: Live API data and estimated metrics are provided as-is for educational and situational awareness purposes. This is not a compliance tool — verify all data independently before making business decisions.

4. **Network Exposure**: The app makes outbound HTTPS GET requests to public APIs. In restricted network environments, these may be blocked by firewalls. Fallback data renders automatically when APIs are unreachable.

## Hardening Recommendations (For Self-Hosted Deployments)

If deploying SecAI-Nexus on your own infrastructure:

```toml
# .streamlit/config.toml
[server]
enableXsrfProtection = true
enableCORS = false

[browser]
gatherUsageStats = false
```

- Place behind a reverse proxy (nginx/Caddy) with TLS termination
- Set `Content-Security-Policy` headers to restrict iframe sources
- Use `X-Frame-Options: DENY` if not embedding the dashboard itself
- Restrict outbound network to only the 9 required API domains
- Run in a read-only container (Docker `--read-only`)

## Reporting a Vulnerability

**Do NOT disclose vulnerabilities publicly** on the issue tracker or social media.

Report directly and privately to **Adam Kistler** via [LinkedIn DM](https://www.linkedin.com/in/adam-kistler-441a31192/).

**Include in your report:**
- Clear description of the vulnerability and potential impact
- Steps to reproduce
- Suggested mitigation (if known)

All legitimate disclosures will be investigated and addressed promptly. Contributors who responsibly disclose vulnerabilities will be credited (with permission) in the changelog.

Thank you for helping keep the open-source community secure.
