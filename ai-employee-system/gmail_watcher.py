"""
Gmail Watcher - Enhanced with Auto-Send on Checkbox
Monitors Gmail, auto-categorizes, and sends when you check "Reply to sender".
"""

import os
import re
import sys
import shutil
import logging
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"gmail_watcher_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('GmailWatcher')

# Import email processor (Claude API integration)
try:
    from email_processor import EmailProcessor
    PROCESSOR_AVAILABLE = True
except ImportError:
    PROCESSOR_AVAILABLE = False
    logger.warning("email_processor not available. Running in basic mode.")

# SCOPES define what the AI can do.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'  # To mark as read
]


class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, token_path: str):
        super().__init__(vault_path, check_interval=120)
        self.token_path = token_path
        self.creds = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.processed_ids = set()

        # Folders to scan for checkbox triggers
        self.scan_folders = [
            self.vault_path / "Inbox",
            self.vault_path / "Pending_Approval"
        ]
        self.done_folder = self.vault_path / "Done"
        self.done_folder.mkdir(parents=True, exist_ok=True)

        # Initialize email processor (works with or without Claude API)
        if PROCESSOR_AVAILABLE:
            self.processor = EmailProcessor(vault_path, gmail_service=self.service)
            if os.getenv('ANTHROPIC_API_KEY'):
                logger.info("Mode: AI-Powered (Claude API + Gmail Send)")
            else:
                logger.info("Mode: Rule-Based (Gmail Send enabled, no Claude API)")
        else:
            self.processor = None
            logger.warning("email_processor not available. Running in basic mode.")

    def _get_credentials(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def check_for_updates(self) -> list:
        results = self.service.users().messages().list(
            userId='me', q='is:unread'
        ).execute()
        messages = results.get('messages', [])
        return [m for m in messages if m['id'] not in self.processed_ids]

    def mark_as_read(self, message_id: str):
        """Mark an email as read in Gmail."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.info(f"  [GMAIL] Marked as read: {message_id[:10]}...")
            return True
        except Exception as e:
            logger.error(f"  [ERROR] Could not mark as read: {e}")
            return False

    def scan_for_checkbox_triggers(self):
        """Scan folders for emails with checked 'Reply to sender' checkbox."""
        for folder in self.scan_folders:
            if not folder.exists():
                continue

            for email_file in folder.glob("EMAIL_*.md"):
                try:
                    content = email_file.read_text(encoding='utf-8')

                    # Check if "Reply to sender" is checked
                    if '- [x] Reply to sender' in content or '- [X] Reply to sender' in content:
                        self._process_checked_email(email_file, content)
                except Exception as e:
                    logger.error(f"Error scanning {email_file.name}: {e}")

    def _process_checked_email(self, email_file: Path, content: str):
        """Process an email that has 'Reply to sender' checked."""
        logger.info(f"[CHECKBOX] Processing: {email_file.name}")

        # Extract email details from frontmatter
        from_match = re.search(r'^from:\s*(.+)$', content, re.MULTILINE)
        subject_match = re.search(r'^subject:\s*(.+)$', content, re.MULTILINE)

        if not from_match:
            logger.error(f"  Error: Could not find 'from' in {email_file.name}")
            return

        email_from = from_match.group(1).strip()
        subject = subject_match.group(1).strip() if subject_match else "No Subject"

        # Extract email address
        if '<' in email_from and '>' in email_from:
            reply_to = email_from.split('<')[1].split('>')[0]
        else:
            reply_to = email_from

        # Extract draft response if available
        draft_match = re.search(r'## Draft Response\s*\n((?:>.*\n?)+)', content)
        if draft_match:
            # Remove '> ' prefix from each line
            draft_lines = draft_match.group(1).strip().split('\n')
            reply_body = '\n'.join(line.lstrip('> ') for line in draft_lines)
        else:
            # Generate simple reply
            reply_body = "Thank you for your email. I've received it and will follow up shortly."

        reply_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject

        # Send the email
        if self.processor and self.processor.send_email(reply_to, reply_subject, reply_body):
            logger.info(f"  [SENT] Reply sent to: {reply_to}")

            # Extract message ID from filename (EMAIL_xxxxx.md)
            gmail_message_id = email_file.stem.replace('EMAIL_', '')

            # Mark original email as read in Gmail
            self.mark_as_read(gmail_message_id)

            # Update the file content - mark as sent
            updated_content = content.replace('status: pending', 'status: sent')
            updated_content = updated_content.replace('- [x] Reply to sender', '- [x] Reply to sender (SENT)')
            updated_content = updated_content.replace('- [X] Reply to sender', '- [x] Reply to sender (SENT)')

            # Add sent timestamp
            sent_timestamp = datetime.now().isoformat()
            updated_content = updated_content.replace(
                '---\n\n## Email Content',
                f'sent_at: {sent_timestamp}\n---\n\n## Email Content'
            )

            # Move to Done folder
            done_path = self.done_folder / email_file.name
            done_path.write_text(updated_content, encoding='utf-8')
            email_file.unlink()  # Delete original

            logger.info(f"  [MOVED] {email_file.name} → Done/")

            # Update dashboard
            if self.processor:
                self.processor.update_dashboard()
        else:
            logger.error(f"  [FAILED] Could not send reply to: {reply_to}")

    def run(self):
        """Override run to include checkbox scanning."""
        logger.info(f"Watcher started. Checking every {self.check_interval} seconds...")
        logger.info("Checkbox trigger: Check '- [x] Reply to sender' to auto-send")
        logger.info("-" * 50)

        try:
            while True:
                # 1. Check for new emails
                updates = self.check_for_updates()
                for update in updates:
                    self.create_action_file(update)

                # 2. Scan for checkbox triggers
                self.scan_for_checkbox_triggers()

                import time
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Watcher stopped.")

    def create_action_file(self, message) -> Path:
        msg = self.service.users().messages().get(
            userId='me', id=message['id']
        ).execute()

        headers = {h['name']: h['value'] for h in msg['payload']['headers']}

        email_from = headers.get('From', 'Unknown')
        subject = headers.get('Subject', 'No Subject')
        snippet = msg.get('snippet', '')
        message_id = message['id']

        # Process with email processor if available
        if self.processor:
            processed = self.processor.process_email(
                email_from=email_from,
                subject=subject,
                content=snippet,
                message_id=message_id
            )
            priority = processed.get('priority', 'MEDIUM')
            reason = processed.get('reason', '')
            suggested_action = processed.get('suggested_action', '')
            draft = processed.get('draft', '')
        else:
            priority = 'MEDIUM'
            reason = 'Auto-assigned (no AI)'
            suggested_action = 'Review manually'
            draft = ''

        # Build the markdown content
        content = f'''---
type: email
from: {email_from}
subject: {subject}
received: {datetime.now().isoformat()}
status: pending
priority: {priority}
priority_reason: {reason}
---

## Email Content
{snippet}

## AI Analysis
- **Priority**: {priority}
- **Reason**: {reason}
- **Suggested Action**: {suggested_action}

## Actions
- [ ] Reply to sender
- [ ] Archive
'''

        # Add draft section if generated
        if draft:
            content += f'''
## Draft Response
> {draft.replace(chr(10), chr(10) + '> ')}

*Check "Reply to sender" above to send this draft automatically.*
'''

        # Determine folder based on priority and auto-reply status
        auto_replied = processed.get('auto_replied', False) if self.processor else False

        if auto_replied:
            target_folder = self.vault_path / "Done"
            target_folder.mkdir(parents=True, exist_ok=True)
            filepath = target_folder / f'EMAIL_{message_id}.md'
        elif priority in ['URGENT', 'HIGH'] and draft:
            target_folder = self.vault_path / "Pending_Approval"
            target_folder.mkdir(parents=True, exist_ok=True)
            filepath = target_folder / f'EMAIL_{message_id}.md'
        else:
            filepath = self.needs_action / f'EMAIL_{message_id}.md'

        filepath.write_text(content, encoding='utf-8')
        self.processed_ids.add(message_id)

        # Console output
        priority_icons = {'URGENT': '[!!!]', 'HIGH': '[!!]', 'MEDIUM': '[!]', 'LOW': '[.]'}
        icon = priority_icons.get(priority, '[?]')
        auto_tag = " [AUTO-REPLIED]" if auto_replied else ""
        logger.info(f"{icon} {priority} - {subject[:50]}{'...' if len(subject) > 50 else ''}{auto_tag}")

        # Update dashboard
        if self.processor:
            self.processor.update_dashboard()

        return filepath


if __name__ == "__main__":
    VAULT_PATH = r"C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault"
    TOKEN_PATH = "token.json"

    logger.info("=" * 50)
    logger.info("AI Employee System - Gmail Watcher")
    logger.info("=" * 50)
    logger.info(f"Vault: {VAULT_PATH}")
    logger.info(f"Check Interval: 120 seconds")
    logger.info(f"Log File: {LOG_FILE}")
    logger.info("=" * 50)

    watcher = GmailWatcher(VAULT_PATH, TOKEN_PATH)
    watcher.run()
