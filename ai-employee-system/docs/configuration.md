# Configuration Guide

## Environment Setup

### Required Files

#### 1. `.env`
Environment variables for API credentials.

```env
GMAIL_CLIENT_ID="your-client-id.apps.googleusercontent.com"
```

#### 2. `credentials.json`
OAuth2 credentials downloaded from Google Cloud Console.
- Create project at: https://console.cloud.google.com/
- Enable Gmail API
- Create OAuth 2.0 Client ID (Desktop app)
- Download credentials

#### 3. `token.json`
Auto-generated after first OAuth2 flow completion.
- Contains access token and refresh token
- Automatically refreshed when expired
- Should NOT be committed to git

### Path Configuration

#### System Paths
```python
# AI Employee System (Python watchers)
SYSTEM_PATH = r"C:\Users\SIBGHAT\OneDrive\Desktop\ai-employee-system"

# Obsidian Vault
VAULT_PATH = r"C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault"
```

#### Vault Structure
```
AI-Employee-Vault/
├── Inbox/          # New items from watchers
├── Needs_Action/   # Tasks requiring action
├── Done/           # Completed tasks
├── Dashboard.md.md # Main interface
└── Handbook.md.md  # Documentation
```

## Watcher Configuration

### GmailWatcher Settings

```python
# Check interval (seconds)
CHECK_INTERVAL = 120  # 2 minutes

# Gmail API Scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Search query
QUERY = 'is:unread'  # Only unread emails
```

### Available Gmail Queries
```
is:unread              # Unread emails
is:important           # Important emails
from:example@email.com # From specific sender
subject:urgent         # Subject contains "urgent"
newer_than:1d          # Last 24 hours
label:work             # Specific label
```

## File Naming Convention

### Email Files
```
EMAIL_{message_id}.md
```

Example: `EMAIL_19b75bbe585d25b1.md`

### Frontmatter Schema

```yaml
---
type: email
from: sender@example.com
subject: Email Subject Line
received: 2026-01-11T00:20:00
status: pending
---
```

## Installation Steps

### 1. Install Python Dependencies
```bash
cd C:\Users\SIBGHAT\OneDrive\Desktop\ai-employee-system
pip install -r requirements.txt
```

### 2. Set Up Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create new project: "AI Employee System"
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download as `credentials.json`

### 3. Configure Environment
1. Create `.env` file
2. Add `GMAIL_CLIENT_ID` from credentials
3. Ensure paths are correct in `gmail_watcher.py`

### 4. First Run (OAuth Flow)
```bash
python gmail_watcher.py
```
- Browser will open for Google authorization
- Select your Gmail account
- Grant read-only permissions
- `token.json` will be created automatically

### 5. Running the Watcher
```bash
# Foreground (with logs)
python gmail_watcher.py

# Background (Windows)
pythonw gmail_watcher.py

# Stop: Ctrl+C (foreground) or Task Manager (background)
```

## Git Configuration

### .gitignore
```gitignore
# Secrets
.env
credentials.json
token.json

# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# OS
.DS_Store
Thumbs.db
```

## Troubleshooting

### Common Issues

**Problem**: `token.json not found`
- Solution: Run `python gmail_watcher.py` and complete OAuth flow

**Problem**: `Invalid credentials`
- Solution: Delete `token.json` and re-authenticate

**Problem**: `API quota exceeded`
- Solution: Increase CHECK_INTERVAL or reduce polling frequency

**Problem**: `Permission denied on vault path`
- Solution: Check folder permissions and path accuracy

**Problem**: Duplicate emails created
- Solution: System tracks `processed_ids` - shouldn't happen unless watcher restarted

## Performance Tuning

### Check Interval Recommendations
- **Aggressive**: 60 seconds (high API usage)
- **Balanced**: 120 seconds (current default)
- **Conservative**: 300 seconds (5 minutes)

### API Quota Limits (Gmail)
- Free tier: 250 quota units/second/user
- 1 list request = 5 quota units
- 1 get request = 5 quota units
- At 120s interval: ~43 requests/hour (~215 quota units/hour)

## Security Best Practices

1. **Never commit secrets**: Keep `.env`, `credentials.json`, `token.json` out of git
2. **Use read-only scopes**: Current implementation is safe (no write access)
3. **Review permissions**: Check what OAuth scope grants before accepting
4. **Rotate credentials**: Periodically regenerate OAuth credentials
5. **Monitor access**: Check Google account "Security" page for active sessions
