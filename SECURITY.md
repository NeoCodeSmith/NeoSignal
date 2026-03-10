# Security Policy

## Credentials

**Never commit credentials to this repository.**

- Email credentials are stored as GitHub Actions repository secrets (`EMAIL_USERNAME`, `EMAIL_PASSWORD`, `EMAIL_TO`)
- The pipeline uses `GITHUB_TOKEN` (auto-provisioned by Actions) for all git operations — no personal access tokens are needed or stored

If you discover credentials committed to this repo, report it immediately.

## Reporting Inaccuracies

If the authenticity scoring algorithm is producing verifiably incorrect results — for example, scoring a known false story as VERIFIED — please open an issue with:

1. The article title and URL
2. The sources it appeared in
3. Why the score is incorrect
4. Suggested scoring adjustment

## Supported Versions

| Version | Supported |
|---|---|
| 3.x (current) | ✅ |
| 2.x | ❌ |
| 1.x | ❌ |
