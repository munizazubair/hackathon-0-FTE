# AI Employee System - Quick Reference

## 🎯 Project Purpose
An intelligent automation system that monitors Gmail (and future services) and creates actionable tasks in an Obsidian vault, acting as a personal AI assistant for information management.

## 📂 Project Structure

```
ai-employee-system/                    # Python watchers
├── .claude/                           # Claude context & documentation
│   ├── project-context.md            # System architecture & overview
│   ├── config.md                     # Setup & configuration guide
│   └── workflows.md                  # Email processing workflows
├── base_watcher.py                   # Abstract watcher base class
├── gmail_watcher.py                  # Gmail integration (main)
├── credentials.json                  # Google OAuth credentials
├── token.json                        # OAuth access token (auto-generated)
├── .env                              # Environment variables
└── requirements.txt                  # Python dependencies

AI-Employee-Vault/                     # Obsidian vault
├── Inbox/                            # New emails (113 currently)
├── Needs_Action/                     # Tasks requiring action
├── Done/                             # Completed/archived items
├── Dashboard.md.md                   # Main dashboard (TBD)
└── Handbook.md.md                    # System handbook (TBD)
```

## 🔧 Key Components

### Python System
- **Location**: `C:\Users\SIBGHAT\OneDrive\Desktop\ai-employee-system`
- **Main Script**: `gmail_watcher.py`
- **Run**: `python gmail_watcher.py`
- **Polling Interval**: 120 seconds (2 minutes)

### Obsidian Vault
- **Location**: `C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault`
- **Purpose**: Store and organize captured emails as markdown files
- **Current State**: 113 emails in Inbox, folders ready for workflow

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Install dependencies
cd ai-employee-system
pip install -r requirements.txt

# 2. Run watcher (triggers OAuth flow)
python gmail_watcher.py

# 3. Authorize in browser
# → token.json will be created automatically
```

### Daily Usage
```bash
# Start watcher
python gmail_watcher.py

# Check Obsidian vault for new emails in Inbox/
# Review and move to Needs_Action/ or Done/
```

## 📊 Current Status

### ✅ Working
- Gmail monitoring (unread emails)
- OAuth2 authentication
- Markdown file creation in Obsidian
- Duplicate detection
- Continuous polling

### 🚧 Next Steps
1. Build Dashboard.md.md interface
2. Implement auto-categorization
3. Add AI-powered summaries
4. Create additional watchers (Slack, Calendar)

## 🔑 Environment Variables

```env
GMAIL_CLIENT_ID="206397860430-ujebp3hidamqa2k6q7kke6klm0986sl6.apps.googleusercontent.com"
```

## 📖 Documentation

For detailed information, see:
- **`docs/architecture.md`** - Full system architecture, design principles, roadmap
- **`docs/configuration.md`** - Configuration, paths, installation, troubleshooting
- **`docs/workflows-legacy.md`** - Legacy workflow documentation (see skill below)
- **`.claude/skills/email-processing/`** - Active email processing Agent Skill

## 🔒 Security

- **Gmail Scope**: `gmail.readonly` (read-only, safe)
- **Credentials**: Stored locally, not in git
- **OAuth Tokens**: Auto-refreshing, managed by Google libraries

## 💡 Key Features

1. **Privacy-First**: All data stored locally in readable markdown
2. **Extensible**: Easy to add new watchers (BaseWatcher class)
3. **Transparent**: Full visibility into captured data
4. **Interruptible**: Safe to stop/restart anytime
5. **Idempotent**: Won't create duplicates

## 🎨 Email File Format

```markdown
---
type: email
from: sender@example.com
subject: Email Subject
received: 2026-01-11T00:20:00
status: pending
---

## Email Content
[Email snippet]

## Suggested Actions
- [ ] Reply to sender
- [ ] Archive after processing
```

## 🛠️ Common Commands

```bash
# Run Gmail watcher
python gmail_watcher.py

# Stop watcher
Ctrl+C

# Check system status
ls Inbox/ | wc -l          # Count inbox items (Unix)
dir Inbox\ /b | find /c    # Count inbox items (Windows)
```

## 📞 Integration Points

### Current
- Gmail API (read-only)
- Obsidian vault (file-based)

### Planned
- Claude API (summarization)
- Slack API (notifications)
- Google Calendar API (events)
- GitHub API (issues/PRs)

## 🧠 AI Enhancement Ideas

1. **Email Summarization**: Use Claude to summarize long emails
2. **Priority Detection**: Auto-assign priority based on content
3. **Action Extraction**: Parse emails for TODO items
4. **Response Drafting**: Generate suggested replies
5. **Context Gathering**: Link related emails and documents

---

**Last Updated**: 2026-01-11
**Status**: Active Development
**Maintainer**: SIBGHAT
