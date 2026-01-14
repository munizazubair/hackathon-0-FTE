# Implementation Plan: Full Email Automation

**Created**: 2026-01-14
**Goal**: Fully automated email processing with Claude API + Desktop Notifications

---

## User Selections

- **AI Method**: Claude API (direct calls when emails arrive)
- **Auto Actions**: Categorize + Draft (Full) - auto-priority AND auto-draft for HIGH/URGENT
- **Alerts**: Windows Desktop Notifications for URGENT/HIGH

---

## Architecture Overview

```
Gmail Inbox
     │
     ▼ (every 2 min)
┌─────────────────────────────────────┐
│  gmail_watcher.py (Enhanced)        │
│  ┌─────────────────────────────┐    │
│  │ 1. Fetch unread emails      │    │
│  │ 2. Call Claude API          │────┼──► Claude API
│  │    - Categorize priority    │    │    (anthropic SDK)
│  │    - Generate draft if HIGH │    │
│  │ 3. Create markdown file     │    │
│  │ 4. Desktop notification     │────┼──► Windows Toast
│  │ 5. Update Dashboard.md      │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
     │
     ▼
Obsidian Vault (Inbox/, Pending_Approval/, etc.)
```

---

## Implementation Steps

### Phase 1: Dependencies & Setup

- [ ] Install `anthropic` Python SDK
- [ ] Install `win10toast` for Windows notifications
- [ ] Add `ANTHROPIC_API_KEY` to .env
- [ ] Update requirements.txt

### Phase 2: Create Email Processor Module

- [ ] Create `email_processor.py` with:
  - `categorize_email(email_content)` - Claude API call for priority
  - `generate_draft(email_content, tone_guidelines)` - Claude API for draft
  - `send_notification(title, message)` - Windows toast

### Phase 3: Enhance Gmail Watcher

- [ ] Modify `gmail_watcher.py` to:
  - Import email_processor module
  - Call Claude API after fetching each email
  - Auto-create draft for HIGH/URGENT emails
  - Trigger desktop notification for HIGH/URGENT
  - Update Dashboard.md after processing

### Phase 4: Auto-Start Configuration

- [ ] Create `start_watcher.bat` for easy launch
- [ ] Set up Windows Task Scheduler for startup
- [ ] Test end-to-end automation

---

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `requirements.txt` | Edit | Add anthropic, win10toast |
| `.env` | Edit | Add ANTHROPIC_API_KEY |
| `email_processor.py` | Create | Claude API + notification logic |
| `gmail_watcher.py` | Edit | Integrate email_processor |
| `start_watcher.bat` | Create | One-click launcher |

---

## Claude API Prompts

### Categorization Prompt
```
Analyze this email and return JSON:
{
  "priority": "URGENT|HIGH|MEDIUM|LOW",
  "reason": "brief explanation",
  "needs_response": true|false,
  "suggested_action": "brief action"
}

Email:
From: {from}
Subject: {subject}
Content: {snippet}
```

### Draft Generation Prompt
```
Write a professional response to this email.
Tone: {from Company_Handbook.md}
Keep it concise (2-3 sentences).
Include specific next steps if needed.

Email:
From: {from}
Subject: {subject}
Content: {snippet}
```

---

## Cost Estimate

- Claude API: ~$0.01-0.03 per email (categorization + draft)
- 50 emails/day = ~$0.50-1.50/day
- Monthly estimate: $15-45

---

## Notifications

Desktop toast will show:
```
┌─────────────────────────────┐
│ 🔴 URGENT Email             │
│ From: Muniya                │
│ Subject: Project Deadline   │
│ Action: Response needed     │
└─────────────────────────────┘
```

---

## Success Criteria

1. New email arrives in Gmail
2. Within 2 minutes: appears in Obsidian Inbox/ with priority
3. If HIGH/URGENT: draft auto-created, notification shown
4. Dashboard.md auto-updated with counts
5. System runs unattended after startup

---

**Ready for implementation approval**
