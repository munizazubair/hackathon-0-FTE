# Email Processing Utility Scripts

These Python scripts provide automated functionality for the email-processing skill.

## Prerequisites

```bash
pip install pyyaml
```

---

## 1. update_dashboard.py

Automatically generates real-time dashboard statistics from your vault.

### Usage

**Basic usage** (markdown output):
```bash
python update_dashboard.py
```

**JSON output**:
```bash
python update_dashboard.py --format json
```

**Custom vault path**:
```bash
python update_dashboard.py --vault-path "/path/to/vault"
```

**Update Dashboard.md file directly**:
```bash
python update_dashboard.py --update-file
```

### What It Does

1. Counts items in Inbox, Needs_Action, Done folders
2. Reads the 5 most recent inbox emails
3. Identifies high-priority and urgent items
4. Generates formatted statistics output

### Example Output

```
# Dashboard Statistics

**Generated**: 2026-01-11T23:30:00

---

## Folder Counts

- 📬 Inbox: 8
- ⚠️ Needs Action: 0
- ✅ Done: 0
- **Total**: 8

## Recent Inbox Items (Last 5)

1. **Project Alpha**
   - From: Muniza Zubair <munizazubairkhan@gmail.com>
   - Received: 2026-01-11 23:05:26
   - Priority: MEDIUM

[...]
```

---

## 2. categorize_email.py

Automatically categorizes emails based on Handbook priority rules.

### Usage

**Categorize single email**:
```bash
python categorize_email.py EMAIL_19bad427787ef9ad.md
```

**Categorize all emails in Inbox**:
```bash
python categorize_email.py --folder Inbox
```

**Batch process all folders**:
```bash
python categorize_email.py --batch
```

**Dry run (preview without changes)**:
```bash
python categorize_email.py --batch --dry-run
```

**Custom vault path**:
```bash
python categorize_email.py --vault-path "/path/to/vault" --batch
```

### What It Does

1. Reads email frontmatter (from, subject)
2. Applies Handbook priority rules:
   - HIGH: Muniya (m95251957@gmail.com)
   - MEDIUM: Muniza Zubair (munizazubairkhan@gmail.com)
   - LOW: Google, system emails
   - URGENT: Keywords like "urgent", "ASAP", "deadline"
3. Updates frontmatter with `priority` field
4. Reports categorization results

### Example Output

```
📂 Processing folder: Inbox
   Found 8 email files

📧 Processing: EMAIL_19bad427787ef9ad.md
  From: Muniza Zubair <munizazubairkhan@gmail.com>
  Subject: Project Alpha
  Assigned Priority: MEDIUM
  ✅ Updated priority: MEDIUM

[...]

==================================================
📊 CATEGORIZATION SUMMARY
==================================================
Total Emails: 8
  🔴 URGENT:  0
  ⚠️ HIGH:    0
  🟡 MEDIUM:  1
  ⚪ LOW:     7
==================================================
```

---

## Priority Rules

Both scripts use these priority rules from the Handbook:

### By Sender

- **HIGH**: Muniya (m95251957@gmail.com)
  - Response time: 4 hours
  - Type: Professional client/colleague

- **MEDIUM**: Muniza Zubair (munizazubairkhan@gmail.com)
  - Response time: 24 hours
  - Type: Personal contact

- **LOW**: Google (no-reply@accounts.google.com)
  - Response time: 48+ hours or archive
  - Type: System emails, newsletters

### By Keywords (Overrides Sender)

- **URGENT**: Contains "urgent", "ASAP", "deadline", "today", "immediate", "critical", "emergency"
  - Response time: 1 hour
  - Highest priority regardless of sender

---

## Integration with Claude

These scripts are designed to work seamlessly with the email-processing skill.

### Option 1: Manual Execution

Run scripts manually when needed:
```bash
python scripts/categorize_email.py --batch
python scripts/update_dashboard.py
```

### Option 2: Called by Claude

Claude can execute these scripts when processing requests:

**User**: "Categorize my inbox emails"

**Claude**:
```bash
python scripts/categorize_email.py --folder Inbox
```

**User**: "Update my dashboard"

**Claude**:
```bash
python scripts/update_dashboard.py
```

### Option 3: Automated (Scheduled)

Add to system cron or scheduled tasks:
```bash
# Categorize new emails every 10 minutes
*/10 * * * * cd /path/to/ai-employee-system && python .claude/skills/email-processing/scripts/categorize_email.py --folder Inbox

# Update dashboard every hour
0 * * * * cd /path/to/ai-employee-system && python .claude/skills/email-processing/scripts/update_dashboard.py --update-file
```

---

## Troubleshooting

### "No module named 'yaml'"
```bash
pip install pyyaml
```

### "Folder not found"
Check the vault path is correct:
```bash
python categorize_email.py --vault-path "C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault" --folder Inbox
```

### "No valid frontmatter found"
Ensure email files have proper YAML frontmatter:
```yaml
---
type: email
from: sender@example.com
subject: Email Subject
received: 2026-01-11T23:05:27
status: pending
---
```

### Script runs but no output
Use `--dry-run` flag to see what would happen:
```bash
python categorize_email.py --batch --dry-run
```

---

## Development Notes

### Adding New Priority Rules

Edit the categorization logic in `categorize_email.py`:

```python
HIGH_PRIORITY_PATTERNS = [
    'muniya',
    'm95251957@gmail.com',
    'newclient@example.com'  # Add new high-priority sender
]

URGENT_KEYWORDS = [
    'urgent',
    'asap',
    'critical-issue'  # Add new urgent keyword
]
```

### Extending update_dashboard.py

Add custom statistics:

```python
def generate_statistics(self) -> Dict:
    stats = {
        # ... existing stats ...
        'custom_metric': self.calculate_custom_metric()
    }
    return stats
```

---

## Script Output Formats

### update_dashboard.py

**Markdown format** (default):
- Human-readable
- Copy-paste into Dashboard.md
- Includes emoji indicators

**JSON format** (`--format json`):
- Machine-readable
- API integration
- Programmatic processing

### categorize_email.py

**Console output**:
- Progress indicators
- Per-file results
- Summary statistics
- Error messages

---

## Best Practices

1. **Always test with --dry-run first** before making changes
2. **Backup vault** before batch operations
3. **Review automated categorizations** to ensure accuracy
4. **Update priority rules** as your email patterns change
5. **Check script output** for errors or warnings

---

*These scripts are part of the email-processing skill for the AI Employee System.*
