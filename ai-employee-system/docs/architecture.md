# AI Employee System - Project Context

## Overview
The AI Employee System is an intelligent automation framework that monitors external services (starting with Gmail) and creates actionable tasks in an Obsidian vault. The system acts as a personal AI assistant that captures, organizes, and helps manage incoming information streams.

## System Architecture

### Components

#### 1. **Python Watchers** (`ai-employee-system/`)
Located at: `C:\Users\SIBGHAT\OneDrive\Desktop\ai-employee-system`

- **base_watcher.py**: Abstract base class for all watchers
  - Provides common polling logic (default: 120 seconds)
  - Handles folder creation and management
  - Implements the main run loop with error handling

- **gmail_watcher.py**: Gmail integration watcher
  - Monitors Gmail inbox for unread emails
  - Uses Google Gmail API (read-only scope)
  - Creates markdown files in Obsidian vault for each email
  - Tracks processed message IDs to avoid duplicates
  - Runs continuously with 2-minute check intervals

#### 2. **Obsidian Vault** (`AI-Employee-Vault/`)
Located at: `C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault`

```
AI-Employee-Vault/
├── Dashboard.md.md       # Main control panel (to be developed)
├── Handbook.md.md        # System documentation (to be developed)
├── Inbox/                # New emails land here
├── Needs_Action/         # Tasks requiring immediate action
└── Done/                 # Completed tasks archive
```

### Data Flow

```
Gmail Inbox (Unread)
    ↓
[GmailWatcher polls every 2min]
    ↓
Create EMAIL_{id}.md in Vault/Inbox/
    ↓
[User/AI reviews in Obsidian]
    ↓
Move to Needs_Action/ or Done/
```

## Current Implementation Status

### ✅ Completed
- Base watcher infrastructure
- Gmail API integration with OAuth2
- Automatic email capture to Obsidian
- Markdown file generation with frontmatter
- Duplicate detection system

### 🚧 In Development
- Dashboard interface in Obsidian
- Automated email categorization
- AI-powered action suggestions
- Multi-source watcher support

### 📋 Planned Features
- Slack integration watcher
- Calendar event monitoring
- Automated task prioritization
- Smart notifications
- Email response drafting
- Context-aware summarization

## Technology Stack

### Backend (Python)
- **google-api-python-client**: Gmail API integration
- **google-auth-oauthlib**: OAuth2 authentication
- **google-auth-httplib2**: HTTP library for Google APIs
- **python-dotenv**: Environment variable management

### Frontend (Obsidian)
- Markdown files with YAML frontmatter
- Community plugins (TBD)
- Dataview queries (TBD)

## Design Principles

1. **Privacy First**: Read-only access by default, user control over all actions
2. **Extensible**: Easy to add new watchers for different services
3. **Transparent**: All data stored as readable markdown files
4. **Interruptible**: Can be stopped/started without data loss
5. **Idempotent**: Safe to run multiple times, won't create duplicates

## Security Considerations

- Gmail uses read-only scope (`gmail.readonly`)
- Credentials stored locally in `token.json`
- No data sent to external servers (except Google APIs)
- All sensitive configs in `.env` file (gitignored)
- OAuth2 tokens auto-refresh when expired

## Future Expansion Ideas

- **Tier System**:
  - Bronze: Read-only monitoring (current)
  - Silver: Basic automation (mark as read, archive)
  - Gold: AI-powered responses and actions

- **Additional Watchers**:
  - Slack messages
  - Discord notifications
  - Calendar events
  - GitHub issues/PRs
  - Twitter mentions

- **AI Integration**:
  - Claude API for email summarization
  - Automatic priority assignment
  - Smart action suggestions
  - Context gathering from previous interactions
