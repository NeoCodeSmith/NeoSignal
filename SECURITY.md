# Security Policy

NeoSignal is a scraper pipeline with no user-facing services, no authentication, and no stored credentials.

## Supported Versions

| Version | Supported |
|---|---|
| 2.x | Yes |
| 1.x | No — use 2.x |

## Reporting a Vulnerability

If you find a security issue (e.g. a dependency with a CVE, a workflow that leaks secrets, or unsafe handling of scraped content):

1. **Do not open a public issue.**
2. Use GitHub's [private security advisory](https://github.com/NeoCodeSmith/NeoSignal/security/advisories/new) feature.
3. Include: the affected file/component, reproduction steps, and impact assessment.

Response within 48 hours. Fix within 7 days for confirmed issues.

## Security Posture

- No secrets in code — all config via environment variables
- `GITHUB_TOKEN` scoped to `contents: write` only
- No external API keys required
- Scraped content is never executed — text only
- All dependencies pinned to minimum versions in `requirements.txt`
