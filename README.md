# Gmail Bulk Unsubscribe & Cleanup Tool

A **free**, privacy-focused tool to bulk unsubscribe from emails, delete emails by sender, and mark emails as read. No subscriptions, no data collection - runs 100% on your machine.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)
![Gmail API](https://img.shields.io/badge/Gmail-API-EA4335?style=flat-square&logo=gmail)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/Gururagavendra/gmail-cleaner?style=flat-square&logo=github)

> **No Subscription Required - Free Forever**

## Features

| Feature | Description |
|---------|-------------|
| **Bulk Unsubscribe** | Find newsletters and unsubscribe with one click |
| **Delete by Sender** | See who sends you the most emails, delete in bulk |
| **Mark as Read** | Bulk mark thousands of unread emails as read |
| **Smart Filters** | Filter by days, size of email, and category (Promotions, Social, Updates) |
| **Privacy First** | Runs locally - your data never leaves your machine |
| **Super Fast** | Gmail API with batch requests (100 emails per API call) |
| **Gmail-style UI** | Clean, familiar interface |

## Demo

![Gmail Cleaner Demo](demo.gif)

**[Watch Setup Video on YouTube](https://youtu.be/CmOWn8Tm5ZE)** - Step-by-step guide to create OAuth credentials


## Setup

> **Important**: You must create your **OWN** Google Cloud credentials.  
> This app doesn't include pre-configured OAuth - that's what makes it privacy-focused!  
> Each user runs their own instance with their own credentials.

### 1. Get Google OAuth Credentials

> **Video Tutorial**: [Watch on YouTube](https://youtu.be/CmOWn8Tm5ZE) for a visual walkthrough

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Search for **"Gmail API"** and **Enable** it
4. Go to **Google Auth Platform**  → Click **"Get started"**
5. Fill in the wizard:
   - **App Information**: Enter app name (e.g., "Gmail Cleanup"), select your email
   - **Audience**: Select **External**
   - **Contact Information**: Add your email address
   - Click **Create**
6. Go to **Audience** (left sidebar) → Scroll to **Test users**
   - Click **Add Users** → Add your Gmail address → **Save**
7. Go to **Clients** (left sidebar) → **Create Client**
   - Application type: **Desktop app**
   - Name: "Gmail Cleanup" (or anything)
   - Click **Create**
   - Click **Download** (downloads JSON file)
   - Rename the downloaded file to `credentials.json`

### 2. Clone the Repository

```bash
git clone https://github.com/Gururagavendra/gmail-cleaner.git
cd gmail-cleaner
```

Put your `credentials.json` file in the project folder.

## Usage

### Option A: Docker (Recommended)

**Step 1:** Start the container
```bash
docker compose up -d
```

**Step 2:** Open the app in your browser
```
http://localhost:8766
```

**Step 3:** Click **"Sign In"** button in the web UI

**Step 4:** Check logs for the OAuth URL (only after clicking Sign In!)
```bash
docker logs $(docker ps -q --filter ancestor=ghcr.io/gururagavendra/gmail-cleaner)
```
Or if you built locally:
```bash
docker logs $(docker ps -q --filter name=gmail-cleaner)
```

**Step 5:** Copy the Google OAuth URL from logs, open in browser, and authorize

> You'll see "Google hasn't verified this app" - this is normal! Click **Advanced** → **Go to Gmail Cleanup (unsafe)** to continue.

### Option B: Python (with uv)

```bash
uv sync
uv run python main.py
```

The app opens at http://localhost:8766

## Security & Privacy

- **100% Local** - No external servers, no data collection
- **Open Source** - Inspect all the code yourself
- **Minimal Permissions** - Only requests read + modify (for mark as read)
- **Your Credentials** - You control your own Google OAuth app
- **Gitignored Secrets** - `credentials.json` and `token.json` never get committed

## FAQ

**Q: Why do I need to create my own Google Cloud project?**
> Because this app accesses your Gmail. By using your own OAuth credentials, you have full control and don't need to trust a third party.

**Q: Is this safe?**
> Yes! The code is open source - you can inspect it. Your emails are processed locally on your machine.

**Q: Can I use this for multiple Gmail accounts?**
> Yes! Click "Sign Out" and sign in with a different account. Each account needs to be added as a test user in your Google Cloud project.

**Q: Emails went to Trash, can I recover them?**
> Yes! The delete feature moves emails to Trash. Go to Gmail → Trash to recover within 30 days.

## Troubleshooting

### "Access blocked: Gmail Cleanup has not completed the Google verification process"

This error means you're missing a step in the OAuth setup:

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → Your Project
2. Go to **APIs & Services** → **OAuth consent screen**
3. Scroll down to **Test users**
4. Click **Add Users** and add your Gmail address
5. Try signing in again

> **Why?** Since your app is in "Testing" mode, only emails listed as test users can sign in. This is normal and expected!

### "Error 403: access_denied"

- Make sure you created your **own** Google Cloud project and credentials
- Make sure your email is added as a **Test user**
- Make sure you downloaded `credentials.json` and placed it in the project folder

### Docker: "Where do I find the OAuth URL?"

Check the container logs:
```bash
docker logs $(docker ps -q --filter name=gmail-cleaner)
```
Look for a URL starting with `https://accounts.google.com/o/oauth2/...`

### Docker: OAuth CSRF Error / State Mismatch

If you see `OAuth error: (mismatching_state) CSRF Warning`:

1. **Stop and clean up:**
   ```bash
   docker compose down
   rm -f token.json
   ```

2. **Clear browser cookies** for `accounts.google.com` (or use incognito/private window)

3. **Start fresh:**
   ```bash
   docker compose up
   ```

4. Copy the OAuth URL from logs and paste in browser

**Windows Docker users:** If OAuth keeps failing, try running without Docker:
```bash
pip install uv && uv sync
uv run python main.py
```

### "Google hasn't verified this app" warning

This is normal for personal OAuth apps! Click:
1. **Advanced** (small link at bottom)
2. **Go to Gmail Cleanup (unsafe)**

This warning appears because your app isn't published to Google - which is exactly what we want for privacy!

## Contributing

PRs welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

- Report bugs
- Suggest features
- Improve the UI
- Add new functionality

## License

MIT License - Use it however you want!

---

<p align="center">
  Made to help you escape email hell
</p>
