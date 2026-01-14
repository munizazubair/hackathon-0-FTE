# Dashboard Queries - Dataview Templates

This file contains Dataview query templates for creating dynamic, auto-updating dashboards in Obsidian.

**Load this file when**: Updating the dashboard, creating dynamic views, or building custom queries.

---

## Basic Folder Counts

### Count All Emails by Folder

```dataview
TABLE WITHOUT ID
  length(rows) as "Count"
WHERE type = "email"
GROUP BY choice(contains(string(file.folder), "Inbox"), "📬 Inbox",
  choice(contains(string(file.folder), "Needs_Action"), "⚠️ Needs Action",
    choice(contains(string(file.folder), "Done"), "✅ Done", "Other"))) as "Folder"
```

**Purpose**: Shows count of emails in each folder
**Use in**: Dashboard summary statistics section

---

### Count Inbox Items Only

```dataview
TABLE WITHOUT ID
  length(rows) as "Unread Emails"
FROM "Inbox"
WHERE type = "email" AND status = "pending"
```

**Purpose**: Quick count of unprocessed inbox items
**Use in**: Inbox Overview section

---

## Priority-Based Queries

### Emails Needing Review (by Priority)

```dataview
TABLE WITHOUT ID
  file.link as "📄 File",
  from as "👤 Sender",
  choice(contains(lower(from), "muniya") or contains(lower(from), "m95251957"), "🔴 HIGH",
    choice(contains(lower(from), "munizazubair"), "🟡 MEDIUM",
      choice(contains(lower(from), "google") or contains(lower(from), "no-reply"), "⚪ LOW", "🟡 MEDIUM"))) as "⚡ Priority",
  choice(deadline, deadline, "—") as "📅 Deadline",
  subject as "📧 Subject"
FROM "Inbox" OR "Needs_Action"
WHERE type = "email" AND status = "pending"
SORT choice(contains(lower(from), "muniya"), 1, choice(contains(lower(from), "m95251957"), 1, choice(contains(lower(subject), "urgent"), 2, 3))) ASC, received DESC
```

**Purpose**: Complete review table with auto-assigned priorities
**Use in**: "Needs My Review" section

---

### High Priority Items Only

```dataview
TABLE
  subject as "Subject",
  from as "From",
  received as "Received"
FROM "Inbox" OR "Needs_Action"
WHERE type = "email"
  AND (contains(lower(from), "muniya") OR contains(lower(from), "m95251957"))
  AND status = "pending"
SORT received DESC
```

**Purpose**: Filter for high-priority senders only
**Use in**: Priority Tasks section

---

### Urgent Items (by Keywords)

```dataview
TABLE
  file.link as "Email",
  from as "Sender",
  subject as "Subject",
  received as "Received"
FROM "Inbox" OR "Needs_Action"
WHERE type = "email"
  AND (contains(lower(subject), "urgent")
    OR contains(lower(subject), "asap")
    OR contains(lower(subject), "deadline")
    OR contains(lower(subject), "today"))
SORT received DESC
```

**Purpose**: Detect urgent emails by keyword matching
**Use in**: Active Alerts section

---

## Recent Activity Queries

### Recently Processed (Today)

```dataview
LIST "✓ **" + from + "**: " + subject
FROM "Done"
WHERE type = "email" AND date(received) = date(today)
SORT received DESC
```

**Purpose**: Show emails processed today
**Use in**: Recently Processed section

---

### Recent Inbox Items (Last 5)

```dataview
TABLE WITHOUT ID
  file.link as "Email",
  from as "Sender",
  subject as "Subject",
  received as "Time"
FROM "Inbox"
WHERE type = "email"
SORT received DESC
LIMIT 5
```

**Purpose**: Display most recent inbox arrivals
**Use in**: Recent Items list

---

### Today's Activity (All Folders)

```dataview
TABLE
  file.folder as "Location",
  subject as "Subject",
  status as "Status"
FROM "Inbox" OR "Needs_Action" OR "Done"
WHERE type = "email" AND date(received) = date(today)
SORT received DESC
```

**Purpose**: All email activity for current day
**Use in**: Daily summary section

---

## Status-Based Queries

### Pending Action Items

```dataview
TABLE
  subject as "Subject",
  from as "From",
  received as "Received",
  status as "Status"
FROM "Needs_Action"
WHERE type = "email" AND (status = "pending" OR status = "in_progress")
SORT received DESC
```

**Purpose**: Items awaiting user action
**Use in**: Needs Action section

---

### Waiting for Response

```dataview
TABLE
  subject as "Subject",
  from as "From",
  received as "Received"
FROM "Needs_Action"
WHERE type = "email" AND status = "waiting"
SORT received DESC
```

**Purpose**: Items blocked waiting for external response
**Use in**: Blocked Items section

---

### Completed Items (Last 7 Days)

```dataview
TABLE
  subject as "Subject",
  from as "From",
  received as "Received",
  status as "Status"
FROM "Done"
WHERE type = "email"
  AND (status = "completed" OR status = "archived")
  AND date(received) >= date(today) - dur(7 days)
SORT received DESC
```

**Purpose**: Recently completed work
**Use in**: Weekly summary

---

## Sender Analysis Queries

### Emails by Sender

```dataview
TABLE
  length(rows) as "Email Count",
  choice(contains(lower(rows[0].from), "muniya"), "🔴 HIGH",
    choice(contains(lower(rows[0].from), "munizazubair"), "🟡 MEDIUM", "⚪ LOW")) as "Priority"
WHERE type = "email"
GROUP BY from
SORT length(rows) DESC
```

**Purpose**: Volume analysis by sender
**Use in**: Sender Activity section

---

### High Priority Senders Activity

```dataview
TABLE
  file.link as "Email",
  subject as "Subject",
  received as "Received"
FROM "Inbox" OR "Needs_Action"
WHERE type = "email"
  AND contains(lower(from), "muniya")
SORT received DESC
LIMIT 10
```

**Purpose**: Track all activity from VIP senders
**Use in**: VIP Communications section

---

## Time-Based Queries

### This Week's Emails

```dataview
TABLE
  file.link as "Email",
  from as "Sender",
  subject as "Subject"
FROM "Inbox" OR "Needs_Action" OR "Done"
WHERE type = "email"
  AND date(received) >= date(today) - dur(7 days)
SORT received DESC
```

**Purpose**: Weekly email volume
**Use in**: Weekly reports

---

### Overdue Items (No Deadline Set)

```dataview
TABLE
  file.link as "Email",
  from as "Sender",
  received as "Received",
  date(today) - date(received) as "Age (days)"
FROM "Inbox" OR "Needs_Action"
WHERE type = "email"
  AND status = "pending"
  AND date(received) < date(today) - dur(2 days)
SORT received ASC
```

**Purpose**: Identify stale items needing attention
**Use in**: Overdue section

---

## Combined Statistics

### Priority Breakdown (Current)

```dataview
TABLE WITHOUT ID
  choice(contains(lower(from), "muniya") or contains(lower(from), "m95251957"), "🔴 HIGH",
    choice(contains(lower(from), "munizazubair"), "🟡 MEDIUM",
      choice(contains(lower(from), "google"), "⚪ LOW", "⚫ UNKNOWN"))) as "Priority",
  length(rows) as "Count"
FROM "Inbox" OR "Needs_Action"
WHERE type = "email" AND status = "pending"
GROUP BY choice(contains(lower(from), "muniya") or contains(lower(from), "m95251957"), "🔴 HIGH",
    choice(contains(lower(from), "munizazubair"), "🟡 MEDIUM",
      choice(contains(lower(from), "google"), "⚪ LOW", "⚫ UNKNOWN")))
SORT choice(contains(string(rows[0]), "HIGH"), 1, choice(contains(string(rows[0]), "MEDIUM"), 2, 3)) ASC
```

**Purpose**: Current priority distribution
**Use in**: System Statistics section

---

## Custom Query Templates

### Template: Filter by Specific Sender

```dataview
TABLE
  subject as "Subject",
  received as "Received",
  status as "Status"
FROM "Inbox" OR "Needs_Action" OR "Done"
WHERE type = "email" AND contains(lower(from), "SENDER_EMAIL_HERE")
SORT received DESC
```

**Usage**: Replace `SENDER_EMAIL_HERE` with actual email address

---

### Template: Filter by Subject Keyword

```dataview
TABLE
  file.link as "Email",
  from as "Sender",
  received as "Received"
FROM "Inbox" OR "Needs_Action" OR "Done"
WHERE type = "email" AND contains(lower(subject), "KEYWORD_HERE")
SORT received DESC
```

**Usage**: Replace `KEYWORD_HERE` with search term

---

### Template: Date Range Query

```dataview
TABLE
  file.link as "Email",
  from as "Sender",
  subject as "Subject"
FROM "Inbox" OR "Needs_Action" OR "Done"
WHERE type = "email"
  AND date(received) >= date(START_DATE)
  AND date(received) <= date(END_DATE)
SORT received DESC
```

**Usage**: Replace `START_DATE` and `END_DATE` with YYYY-MM-DD format

---

## Query Usage Tips

### Best Practices

1. **Test queries in a scratch note first** before adding to Dashboard
2. **Use LIMIT** on large datasets to avoid performance issues
3. **Sort consistently** (DESC for recent first, ASC for oldest first)
4. **Include type = "email"** to exclude non-email files
5. **Use choice() for dynamic categorization** instead of hardcoded values

### Performance Optimization

- Limit queries to specific folders when possible
- Use `LIMIT` clause for preview sections
- Cache complex queries results if Obsidian supports it
- Avoid deeply nested `choice()` statements

### Debugging Queries

If a query doesn't work:
1. Check folder paths (case-sensitive on some systems)
2. Verify frontmatter field names (from, subject, received, status)
3. Test with simpler WHERE clauses first
4. Use `TABLE` instead of `LIST` to see all fields
5. Check Dataview plugin is installed and enabled

---

## Example: Complete Dashboard Query Set

Here's a minimal dashboard using core queries:

````markdown
# AI Agent Dashboard

## 📬 Inbox Overview

```dataview
TABLE WITHOUT ID length(rows) as "Count"
FROM "Inbox"
WHERE type = "email"
```

## 🔴 High Priority Items

```dataview
TABLE file.link as "Email", from as "Sender", subject as "Subject"
FROM "Inbox" OR "Needs_Action"
WHERE type = "email" AND contains(lower(from), "muniya")
SORT received DESC
```

## ✅ Today's Completed

```dataview
LIST "✓ " + from + ": " + subject
FROM "Done"
WHERE type = "email" AND date(received) = date(today)
```
````

---

*These queries use standard Obsidian Dataview syntax. Requires Dataview plugin installed in Obsidian.*
