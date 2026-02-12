# Security Policy

## Reporting a Vulnerability

We take the security of Gmail Cleaner seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **Email**: Send details to [guruvelu85@gmail.com](mailto:guruvelu85@gmail.com)
2. **GitHub Security Advisories**: Use [GitHub's private vulnerability reporting](https://github.com/Gururagavendra/gmail-cleaner/security/advisories/new)

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Affected versions (if known)
- Potential impact
- Any possible mitigations (optional)

### Response Timeline

| Stage | Expected Timeframe |
|-------|-------------------|
| Initial response | Within 48 hours |
| Triage & assessment | Within 5 business days |
| Fix development | Depends on severity |
| Security advisory | After fix is released |

### What to Expect

1. **Acknowledgment**: We'll confirm receipt of your report within 48 hours
2. **Assessment**: We'll investigate and determine the severity
3. **Updates**: We'll keep you informed about our progress
4. **Disclosure**: We'll coordinate with you on responsible disclosure

## Security Best Practices for Users

When using Gmail Cleaner:

### Credentials Protection

- **Never commit** `credentials.json` or `token.json` to version control
- **Use your own** Google Cloud Project (not someone else's credentials)
- **Rotate credentials** if you suspect they've been compromised
- **Limit OAuth scopes** to only what's necessary

### Running Safely

- **Review the code** before running (it's open source!)
- **Use Docker** for additional isolation (optional)
- **Audit permissions** in your Google Account after use
- **Revoke access** if you stop using the tool: [Google Account Permissions](https://myaccount.google.com/permissions)

### Data Privacy

- All email processing happens **locally on your machine**
- **No data** is sent to external servers
- **No telemetry** or usage tracking
- **No analytics** collected

## Supported Versions

| Version | Supported | Notes |
| ------- | --------- | ----- |
| Latest | ✅ | Active development |
| Previous minor | ✅ | Security fixes only |
| Older versions | ❌ | Please upgrade |

We recommend always using the latest release for the most up-to-date security fixes.

## Security Features

Gmail Cleaner is designed with privacy and security as core principles:

| Feature | Description |
|---------|-------------|
| **Local Processing** | All data stays on your machine |
| **Your OAuth App** | Each user creates their own Google Cloud credentials |
| **Minimal Scopes** | Only requests `gmail.readonly` and `gmail.modify` |
| **No External Services** | No telemetry, analytics, or tracking |
| **Open Source** | Full code auditability |
| **Gitignored Secrets** | Credentials and tokens are never committed |

## Known Security Considerations

### OAuth Credentials

- Your `credentials.json` contains a client secret - treat it like a password
- If compromised, regenerate credentials in Google Cloud Console immediately
- Rotate credentials periodically for best security

### Token Storage

- `token.json` contains your access and refresh tokens
- Stored locally in your platform's data directory
- Protected by your operating system's file permissions

### Docker Considerations

- Docker containers run as root by default
- Files in `./data/` (like `token.json`) may have root ownership
- Fix with: `sudo chown -R $USER:$USER ./data/`

## Security Updates

Security updates are released as patch versions and announced via:

- [GitHub Releases](https://github.com/Gururagavendra/gmail-cleaner/releases)
- [GitHub Security Advisories](https://github.com/Gururagavendra/gmail-cleaner/security/advisories)

## Responsible Disclosure

We believe in responsible disclosure. Security researchers who follow these guidelines:

- Report vulnerabilities privately first
- Allow reasonable time for a fix before disclosure
- Do not access or modify user data without permission

We will:

- Credit you in the security advisory (if desired)
- Respond promptly to your report
- Work with you on the disclosure timeline

---

Thank you for helping keep Gmail Cleaner and its users safe!
