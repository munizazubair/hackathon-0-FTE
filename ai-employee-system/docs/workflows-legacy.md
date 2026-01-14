# Workflows and Processes

## Core Workflow: Email Processing

### Phase 1: Capture (Automated)
```
Unread Email in Gmail
    ↓
GmailWatcher detects (every 2 min)
    ↓
Extract: From, Subject, Snippet
    ↓
Create EMAIL_{id}.md in Inbox/
    ↓
Add to processed_ids set
    ↓
Log: "Captured new email: {subject}"
```

### Phase 2: Review (Manual/AI-Assisted)
```
User opens Obsidian
    ↓
Review Dashboard (shows Inbox count)
    ↓
Open emails in Inbox/
    ↓
Assess priority and required action
    ↓
Decide: Action needed or Archive?
```

### Phase 3: Action (Manual)
```
If action needed:
    Move to Needs_Action/
    ↓
    Update status: pending → in_progress
    ↓
    Complete action items
    ↓
    Update status: in_progress → completed
    ↓
    Move to Done/

If no action:
    Update status: pending → archived
    ↓
    Move to Done/
```

## File Lifecycle

```
Created → Inbox/EMAIL_{id}.md (status: pending)
    ↓
Reviewed → Needs_Action/EMAIL_{id}.md (status: in_progress)
    ↓
Completed → Done/EMAIL_{id}.md (status: completed/archived)
```

## Status Values

| Status | Meaning | Location |
|--------|---------|----------|
| `pending` | New, unreviewed | Inbox/ |
| `in_progress` | Currently working on | Needs_Action/ |
| `completed` | Action finished | Done/ |
| `archived` | No action needed | Done/ |
| `waiting` | Blocked/waiting for response | Needs_Action/ |

## Email Markdown Template

### Current Structure
```markdown
---
type: email
from: sender@example.com
subject: Project Update
received: 2026-01-11T00:20:00
status: pending
---

## Email Content
[Email snippet from Gmail API]

## Suggested Actions
- [ ] Reply to sender
- [ ] Archive after processing
```

### Proposed Enhanced Structure
```markdown
---
type: email
from: sender@example.com
subject: Project Update
received: 2026-01-11T00:20:00
status: pending
priority: medium
labels: [work, project-x]
thread_id: 19b75bbe585d25b1
---

## Email Content
[Email snippet from Gmail API]

## Context
- Related to: [[Project X Planning]]
- Previous emails: [[EMAIL_19b12345]]

## AI Analysis
**Summary**: Client requesting update on Project X timeline
**Sentiment**: Neutral, business inquiry
**Urgency**: Medium (no deadline mentioned)

## Suggested Actions
- [ ] Review Project X current status
- [ ] Draft timeline response
- [ ] CC project manager
- [ ] Set follow-up reminder

## Response Draft
[AI-generated draft response]

## Notes
[User's manual notes]
```

## Dashboard Queries (Planned)

### Obsidian Dataview Queries

**Inbox Count**
```dataview
TABLE WITHOUT ID
    length(rows) as "Unread Emails"
FROM "Inbox"
WHERE type = "email" AND status = "pending"
```

**Priority Tasks**
```dataview
TABLE
    subject as "Subject",
    from as "From",
    received as "Received"
FROM "Needs_Action"
WHERE type = "email" AND priority = "high"
SORT received DESC
```

**Today's Activity**
```dataview
TABLE
    subject as "Subject",
    status as "Status"
FROM "Inbox" OR "Needs_Action" OR "Done"
WHERE type = "email" AND date(received) = date(today)
SORT received DESC
```

## Automation Ideas (Future)

### Auto-Categorization Rules
```python
# Example: Priority based on sender
HIGH_PRIORITY_SENDERS = [
    "boss@company.com",
    "client@important.com"
]

# Example: Auto-archive newsletters
AUTO_ARCHIVE_KEYWORDS = [
    "unsubscribe",
    "newsletter",
    "marketing"
]
```

### Smart Actions
```python
# Example: Meeting invite detection
if "meeting" in subject.lower():
    add_action("Add to calendar")
    add_action("Prepare agenda")

# Example: Question detection
if "?" in content:
    add_action("Research answer")
    add_action("Draft response")
```

## Manual Workflows

### Daily Review Routine
1. Open Obsidian Dashboard
2. Check Inbox count
3. Process 5-10 emails at a time
4. Move to Needs_Action or Done
5. Update priorities
6. Review Needs_Action list
7. Complete top 3 priority items

### Weekly Cleanup
1. Review Done/ folder
2. Archive old completed items
3. Check for stale Needs_Action items
4. Update priorities based on changes
5. Review patterns in email types

### Emergency Workflow
For high-priority/urgent emails:
1. Create in Inbox/ as normal
2. Add `priority: high` in frontmatter
3. Tag with `#urgent`
4. Immediately move to Needs_Action/
5. Process before other items

## Integration Workflows (Planned)

### Gmail → Obsidian → Notion
```
Email captured
    ↓
AI analyzes content
    ↓
Extract action items
    ↓
Create Notion database entry
    ↓
Link back to Obsidian note
```

### Gmail → Obsidian → Calendar
```
Meeting invite detected
    ↓
Parse date/time
    ↓
Create calendar event
    ↓
Link to email note
    ↓
Set reminder
```

### Gmail → Obsidian → Slack
```
Urgent email received
    ↓
Send Slack notification
    ↓
Include summary + link
    ↓
Wait for user response
    ↓
Log interaction
```

## Best Practices

### File Management
- Keep Inbox/ clean (process daily)
- Archive Done/ items monthly
- Use tags for categorization
- Link related emails together

### Naming Conventions
- Email files: `EMAIL_{id}.md`
- Task files: `TASK_{yyyymmdd}_{description}.md`
- Meeting notes: `MEETING_{yyyymmdd}_{title}.md`

### Frontmatter Standards
Always include:
- `type`: Category (email, task, meeting)
- `status`: Current state
- `received`/`created`: Timestamp
- `tags`: Relevant labels

### Processing Speed
- Aim to process Inbox → empty daily
- Spend 15-20 minutes on email review
- Focus on high-priority items first
- Batch similar actions together
