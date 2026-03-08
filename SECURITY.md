# Security Policy

## Supported Versions

Only the latest version on the `main` branch receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| 30.x    | ✅ Active          |
| < 30    | ❌ Unsupported     |

## Architecture & Attack Surface

SecAI-Nexus is designed with a **minimal attack surface by default**:

| Vector                        | Risk      | Mitigation                                                                                   |
|-------------------------------|-----------|----------------------------------------------------------------------------------------------|
| User input                    | **None**  | Dashboard is read-only. No forms, text fields, file uploads, or user-submitted data.         |
| Data storage                  | **None**  | No database, no disk writes, no session persistence, no cookies.                             |
| Authentication                | **None**  | No credentials stored or transmitted. No API keys required.                                  |
| API calls                     | **Low**   | Read-only GET requests to 9 public endpoints. No write operations. Strict size/type validation. |
| Iframe embedding              | **Medium**| Third-party maps sandboxed with `allow-scripts allow-same-origin allow-forms allow-popups`. No `allow-top-navigation`. |
| `unsafe_allow_html`           | **Medium**| Used only for developer-controlled CSS/HTML styling. No user input rendered.                 |
| Dependencies                  | **Low**   | Exact versions pinned in `requirements.txt`. GitLab Dependency Scanning on every commit.     |
| Hosting                       | **Low**   | Streamlit Community Cloud sandboxed runtime. HTTPS enforced.                                 |

## Hardened Security Controls (2026 updates)

- **Content-Security-Policy (CSP)**: Enforced via meta tag — restricts script/style sources to self, allows only trusted map domains for frames, and limits outbound connections.
- **X-Frame-Options**: Set to `DENY` — prevents clickjacking.
- **Referrer-Policy**: `strict-origin-when-cross-origin` — minimizes information leakage.
- **XSRF Protection & CORS**: Explicitly enabled/disabled via Streamlit config.
- **Request hardening**: Response size capped at 5 MB, content-type validation on JSON endpoints, enforced TLS verification, short timeouts.
- **Session-based rate limiting**: Prevents abuse of outbound API calls.
- **Docker runtime**: Non-root user, minimal base image, explicit permissions, read-only filesystem flags where applicable.

## DevSecOps Pipeline

The GitLab CI/CD pipeline runs on every commit:

- **SAST** — Static Application Security Testing via GitLab's built-in analyzers (Semgrep, Bandit)
- **Dependency Scanning** — Checks `requirements.txt` against known CVE databases
- **Secret Detection** — Scans for accidentally committed credentials or tokens

## Known Considerations

1. **Iframe Content**: Embedded threat maps load from Radware and FortiGuard. CSP and sandboxing limit impact if a provider is compromised.
2. **`unsafe_allow_html=True`**: Required for custom styling. All HTML/CSS is developer-authored — no dynamic user content is inserted.
3. **Data Accuracy**: Live API data and estimated metrics are provided as-is for educational purposes. Verify independently before any decision-making.
4. **Network Exposure**: Outbound HTTPS GET requests only to trusted public APIs. Fallback rendering occurs if endpoints are unreachable.

## Hardening Recommendations (Self-Hosted Deployments)

- Use a reverse proxy (nginx/Caddy) with TLS termination and strict outbound allow-listing.
- Set additional headers: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`.
- Run container with `--read-only` and `--security-opt no-new-privileges`.

## Reporting a Vulnerability

**Do NOT disclose vulnerabilities publicly** on the issue tracker or social media.

Report directly and privately to **Adam Kistler** via [LinkedIn DM](https://www.linkedin.com/in/adam-kistler-441a31192/).

**Include in your report:**
- Clear description of the vulnerability and potential impact
- Steps to reproduce
- Suggested mitigation (if known)

All legitimate disclosures will be investigated and addressed promptly. Contributors who responsibly disclose vulnerabilities will be credited (with permission) in the changelog.

Thank you for helping keep the open-source community secure.
