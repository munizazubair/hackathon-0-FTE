---
name: email-processing
description: Processes Gmail via MCP, categorizes by priority in Obsidian, and manages the Draft-to-Send approval workflow.
tier: silver
version: 2.1.0
triggers:
  - /email
  - process email
  - draft response
  - send approved
  - weekly audit
  - monday briefing
---

# Email Processing Skill (Silver Tier)

Manages the complete email workflow: Gmail monitoring, Obsidian organization, priority categorization, and **automatic sending via checkbox trigger**.

---

## IMPORTANT: System Architecture

The email system runs on **TWO components**:

### 1. Gmail Watcher (Python Script) - Runs Continuously
**Location**: `C:\Users\SIBGHAT\OneDrive\Desktop\ai-employee-system\gmail_watcher.py`

**What it does automatically (every 2 minutes):**
- Monitors Gmail for new unread emails
- Categorizes priority (URGENT/HIGH/MEDIUM/LOW)
- Generates draft responses for HIGH/URGENT
- Sends auto-replies for LOW priority (newsletters excluded)
- **Detects checkbox triggers and sends emails automatically**
- Updates Dashboard.md
- Sends Windows notifications for important emails

**To start:** `python gmail_watcher.py` (keep running in terminal)

### 2. Claude (This Skill) - On-Demand
**Use Claude for:**
- Processing inbox manually
- Creating custom draft responses via MCP
- Weekly audit reports
- Dashboard updates
- Any task requiring AI judgment

---

## CRITICAL: Checkbox Auto-Send Feature

**The Gmail Watcher automatically sends emails when user checks the "Reply to sender" checkbox in Obsidian.**

### How It Works:

1. Email arrives → Watcher creates file in `Inbox/` or `Pending_Approval/`
2. File contains:
   ```markdown
   ## Actions
   - [ ] Reply to sender    ← User checks this box
   - [ ] Archive

   ## Draft Response
   > Thank you for your email...
   ```
3. User opens file in Obsidian, changes `[ ]` to `[x]`:
   ```markdown
   - [x] Reply to sender
   ```
4. User saves the file
5. **Watcher detects the checkbox (within 2 minutes)**
6. **Watcher sends the email automatically using the Draft Response**
7. **File moves to Done/ folder automatically**

### What Claude Should Know:

- **DO NOT manually send emails that have `- [x] Reply to sender`** - the watcher handles this
- If user asks "send this email", tell them to check the checkbox and the watcher will send it
- If watcher is not running, Claude can send via MCP tools as fallback

---

## Vault Configuration

**Base Path**: `C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault`

| Folder | Purpose | Status Values |
|--------|---------|---------------|
| `Inbox/` | New unprocessed emails (MEDIUM/LOW priority) | `pending` |
| `Pending_Approval/` | HIGH/URGENT emails with draft responses | `pending` |
| `Approved/` | Legacy folder (checkbox method preferred) | `approved` |
| `Done/` | Sent/archived items | `sent`, `archived` |
| `Briefings/` | Weekly audit reports | N/A |

**Control Files** (Vault Root):
- `Dashboard.md` - Real-time metrics and status
- `Company_Handbook.md` - Tone guidelines and business rules
- `PLAN.md` - Reasoning loop log (created during workflows)

---

## Email File Structure

### Current Format (v2.1):

```yaml
---
type: email
from: Sender Name <email@example.com>
subject: Email Subject Line
received: 2026-01-14T10:30:00
status: pending
priority: HIGH
priority_reason: Important sender
sent_at:                          # Added when sent
---

## Email Content
[Original email snippet]

## AI Analysis
- **Priority**: HIGH
- **Reason**: Important sender
- **Suggested Action**: Respond within 4 hours

## Actions
- [ ] Reply to sender              ← CHECK THIS TO AUTO-SEND
- [ ] Archive

## Draft Response
> Thank you for your email. I'll review this and get back to you shortly.

*Check "Reply to sender" above to send this draft automatically.*
```

### Status Flow:

| Status | Location | Meaning |
|--------|----------|---------|
| `pending` | Inbox/ or Pending_Approval/ | Awaiting action |
| `sent` | Done/ | Email sent (via checkbox or manual) |
| `archived` | Done/ | No response needed |

---

## Workflow 1: Process Inbox

**Triggers**: "process inbox", "categorize emails", "review inbox"

**Note**: The watcher already categorizes emails automatically. Use this workflow only if you need to re-categorize or review manually.

### Steps:
1. Count items in each folder
2. List emails by priority
3. Summarize for user
4. Ask if they want to:
   - Check "Reply to sender" for any email (watcher will send)
   - Move to Done/ (archive)
   - Need custom response (create draft)

---

## Workflow 2: Create Custom Draft

**Triggers**: "draft response", "create draft for [email]", "write reply to [sender]"

**Use when**: User wants a custom response (not the auto-generated draft)

### Steps:
1. Read the email file
2. Load tone guidelines from Company_Handbook.md
3. Generate custom draft response
4. **Update the Draft Response section in the file**
5. Tell user: "Draft updated. Check '- [x] Reply to sender' in Obsidian to send."

### Tone Guidelines:

**Professional Contacts** (Muniya, clients):
- Tone: Warm but professional
- Opening: "Thanks for reaching out!"
- Closing: "Let me know if you need anything else"

**Personal Contacts** (Muniza, friends):
- Tone: Casual and friendly
- Opening: "Hey!"
- Closing: "Talk soon!"

---

## Workflow 3: Send via MCP (Fallback)

**Triggers**: "send approved", "send email now", "force send"

**Use ONLY when**: Gmail watcher is not running or checkbox method isn't working.

### MCP Tools:
```
mcp__google-workspace__gmail_send:
  to: "[email]"
  subject: "Re: [subject]"
  body: "[response]"
```

After sending:
1. Update file: `status: sent`, `sent_at: [timestamp]`
2. Move file to Done/
3. Update Dashboard.md

---

## Workflow 4: Update Dashboard

**Triggers**: "update dashboard", "refresh dashboard", "show status"

### Steps:
1. Count files in each folder
2. Update Dashboard.md with:
   - Folder counts
   - Recent items
   - System status
   - Last updated timestamp

---

## Workflow 5: Weekly Audit (Monday Briefing)

**Triggers**: "weekly audit", "monday briefing", "generate briefing"

### Steps:
1. Scan Done/ for emails from past 7 days
2. Calculate processing time (received → sent)
3. Identify bottlenecks (>24 hours)
4. Generate `Briefings/Monday_Briefing_[date].md`
5. Update Dashboard with audit summary

---

## Quick Reference

| User Says | Action |
|-----------|--------|
| "Process inbox" | List and summarize emails by priority |
| "Send this email" | Tell user to check the checkbox in Obsidian |
| "Draft response to X" | Create custom draft, update file |
| "Update dashboard" | Refresh Dashboard.md with counts |
| "Weekly audit" | Generate Monday Briefing report |
| "Is watcher running?" | Check if gmail_watcher.py is active |

---

## Priority Auto-Actions (By Watcher)

| Priority | Auto-Reply | Notification | Draft | Folder |
|----------|------------|--------------|-------|--------|
| URGENT | No | Yes | Yes | Pending_Approval/ |
| HIGH | No | Yes | Yes | Pending_Approval/ |
| MEDIUM | No | No | No | Inbox/ |
| LOW | Yes (if appropriate) | No | No | Done/ |

---

## System Commands

### Start Watcher:
```bash
cd C:\Users\SIBGHAT\OneDrive\Desktop\ai-employee-system
python gmail_watcher.py
```

### Check Watcher Status:
Look at Dashboard.md - if "Last Updated" is recent, watcher is running.

---

## Vault Paths Reference

```
C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault\
├── Inbox/                 # MEDIUM/LOW priority emails
├── Pending_Approval/      # HIGH/URGENT with drafts
├── Approved/              # Legacy (use checkbox instead)
├── Done/                  # Sent and archived
├── Briefings/             # Weekly audit reports
├── Dashboard.md           # Real-time status
└── Company_Handbook.md    # Tone and rules
```

---

*Email Processing Skill v2.1 - Silver Tier*
*Features: Checkbox Auto-Send, Priority Categorization, Weekly Audit*
*Gmail Watcher handles automatic sending - Claude handles custom tasks*
