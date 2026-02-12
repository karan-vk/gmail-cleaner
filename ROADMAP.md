# Gmail Cleaner Roadmap

> A free, privacy-focused tool to bulk unsubscribe from emails, delete emails by sender, and mark emails as read.

This roadmap outlines the planned development and direction of Gmail Cleaner. It's designed to help contributors understand where the project is heading and identify areas where help is needed.

---

## Vision

**Make email cleanup accessible, private, and efficient for everyone.**

Gmail Cleaner aims to be the go-to open-source solution for Gmail users who want to take control of their inbox without sacrificing privacy. We believe email management should be:

- **Private**: Your data never leaves your machine
- **Free**: No subscriptions, no hidden costs
- **Simple**: Clean UI, minimal setup friction
- **Powerful**: Bulk operations that would take hours manually

---

## Current Version: v1.x

**Focus**: Stability, performance, and core functionality

### Completed ✅

- [x] Bulk unsubscribe from newsletters
- [x] Delete emails by sender
- [x] Mark emails as read in bulk
- [x] Archive emails
- [x] Label management (create, delete, apply, remove)
- [x] Mark/unmark as important
- [x] Smart filters (date, size, category, sender, labels)
- [x] Docker support
- [x] Standalone desktop apps (Windows, macOS, Linux)
- [x] OAuth authentication with user's own credentials
- [x] Batch API requests for performance (100 emails/call)
- [x] Real-time progress tracking
- [x] CSV export for email metadata

### In Progress 🔄

- [ ] Integration tests suite
- [ ] Performance optimizations for large inboxes (100k+ emails)
- [ ] Better error handling and user feedback

---

## Upcoming: v1.1

**Focus**: User experience and reliability

### Planned Features

- [ ] **Undo actions** - Recover from accidental bulk operations
- [ ] **Operation history** - View past operations with details
- [ ] **Dry run mode** - Preview what would be deleted before executing
- [ ] **Keyboard shortcuts** - Power user efficiency
- [ ] **Dark mode** - Easy on the eyes
- [ ] **Export scan results** - Save sender lists for later

### Improvements

- [ ] Better progress indicators with time estimates
- [ ] Improved error messages with actionable guidance
- [ ] Faster scanning with parallel processing
- [ ] Reduced memory footprint

---

## Future: v1.2+

**Focus**: Advanced features and platform expansion

### Planned Features

- [ ] **Scheduled cleanup** - Automated regular cleaning
- [ ] **Smart rules** - Auto-delete/archive based on conditions
- [ ] **Sender grouping** - Group similar senders (e.g., all "noreply@*" addresses)
- [ ] **Whitelist management** - Never delete from trusted senders
- [ ] **Statistics dashboard** - Visualize email patterns over time
- [ ] **Multi-account support** - Switch between Gmail accounts easily

---

## Long-term Vision: v2.0

**Focus**: Platform expansion and ecosystem

### Potential Directions

> These are exploratory ideas. Community input will shape priorities.

#### Multi-Provider Support

- [ ] Outlook/Hotmail support via Microsoft Graph API
- [ ] Yahoo Mail support
- [ ] IMAP/SMTP for custom email providers
- [ ] Unified inbox management across providers

#### Enhanced Capabilities

- [ ] AI-powered email categorization (optional, local models)
- [ ] Smart unsubscribe validation (verify before clicking)
- [ ] Email deduplication
- [ ] Attachment management (find and delete large attachments)

#### Platform & Ecosystem

- [ ] Browser extension for quick actions
- [ ] Mobile companion app (iOS/Android)
- [ ] Plugin system for custom actions
- [ ] CLI version for automation/scripting

---

## Help Wanted 🙋

We need your help! Priority areas:

### High Priority

| Area | Skills Needed | Issue Labels |
|------|---------------|--------------|
| Integration Tests | Python, pytest | `help wanted`, `testing` |
| UI/UX Improvements | JavaScript, CSS | `help wanted`, `frontend` |
| Documentation | Writing, technical docs | `help wanted`, `documentation` |
| Error Handling | Python, FastAPI | `help wanted`, `backend` |

### Good First Issues

New to the project? Look for [`good first issue`](https://github.com/Gururagavendra/gmail-cleaner/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) labels.

### Feature Requests

Have an idea? [Open a feature request](https://github.com/Gururagavendra/gmail-cleaner/issues/new?template=feature_request.yml)!

We especially welcome:

- Ideas to improve the onboarding experience
- Ways to make setup easier for non-technical users
- Performance optimizations for large inboxes
- Accessibility improvements

---

## Release Cadence

| Release Type | Frequency | Description |
|--------------|-----------|-------------|
| Patch (x.x.**Z**) | As needed | Bug fixes, security updates |
| Minor (x.**Y**.0) | Monthly | New features, improvements |
| Major (**X**.0.0) | As needed | Breaking changes, major features |

---

## Contribution Milestones

We're building towards these community goals:

| Milestone | Target | Status |
|-----------|--------|--------|
| 100 contributors | v1.2 release | 🔜 Coming soon |
| 50 integrations tests | v1.1 release | 🔄 In progress |
| 90% code coverage | v1.2 release | 📈 Growing |
| Multi-provider support | v2.0 release | 🗓️ Planned |

---

## Feedback

This roadmap is a living document. Your input shapes its direction:

- **Feature requests**: [Open an issue](https://github.com/Gururagavendra/gmail-cleaner/issues/new)
- **Discussions**: [GitHub Discussions](https://github.com/Gururagavendra/gmail-cleaner/discussions)
- **Email**: guruvelu85@gmail.com

---

*Last updated: February 2026*
