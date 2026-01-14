"""
Email Processor Module - Claude API Integration + Gmail Send
Handles email categorization, draft generation, auto-replies, and notifications.
"""

import os
import json
import base64
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Claude API support (optional)
try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = bool(os.getenv('ANTHROPIC_API_KEY'))
except ImportError:
    CLAUDE_AVAILABLE = False

# Windows notification support
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
    toaster = ToastNotifier()
except ImportError:
    TOAST_AVAILABLE = False
    toaster = None


class EmailProcessor:
    """Processes emails using Claude API (optional) and Gmail API for sending."""

    def __init__(self, vault_path: str, gmail_service=None):
        self.vault_path = Path(vault_path)
        self.gmail_service = gmail_service
        self.handbook_path = self.vault_path / "Company_Handbook.md"
        self.dashboard_path = self.vault_path / "Dashboard.md"
        self.done_folder = self.vault_path / "Done"
        self.done_folder.mkdir(parents=True, exist_ok=True)

        # Initialize Claude client if available
        if CLAUDE_AVAILABLE:
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        else:
            self.client = None

        # Load tone guidelines if available
        self.tone_guidelines = self._load_handbook()

        # Auto-reply templates for LOW priority
        self.auto_reply_templates = {
            "newsletter": None,  # No reply for newsletters
            "notification": None,  # No reply for notifications
            "default": "Thank you for your email. I've received it and will review it shortly."
        }

    def _load_handbook(self) -> str:
        """Load Company_Handbook.md for tone guidelines."""
        if self.handbook_path.exists():
            return self.handbook_path.read_text(encoding='utf-8')
        return "Use a professional and friendly tone."

    def categorize_email(self, email_from: str, subject: str, content: str) -> dict:
        """
        Categorize email priority using Claude API or fallback rules.
        Returns: {"priority": "URGENT|HIGH|MEDIUM|LOW", "reason": str, "needs_response": bool, "suggested_action": str, "auto_reply": bool}
        """
        # Try Claude API first if available
        if self.client:
            try:
                return self._claude_categorize(email_from, subject, content)
            except Exception as e:
                print(f"Claude API error: {e}, using fallback")

        # Fallback to rule-based
        return self._fallback_categorize(email_from, subject, content)

    def _claude_categorize(self, email_from: str, subject: str, content: str) -> dict:
        """Use Claude API to categorize email priority."""
        prompt = f"""Analyze this email and return ONLY valid JSON (no markdown, no explanation):

{{
  "priority": "URGENT or HIGH or MEDIUM or LOW",
  "reason": "brief 5-10 word explanation",
  "needs_response": true or false,
  "suggested_action": "brief action recommendation",
  "auto_reply": true or false (true only for LOW priority that needs a simple acknowledgment)
}}

Priority Rules:
- URGENT: Contains "urgent", "ASAP", "deadline today", "immediate action", time-sensitive requests
- HIGH: From important contacts, meeting invites, project deliverables, client requests
- MEDIUM: General inquiries, personal contacts, follow-ups
- LOW: Newsletters, automated notifications, marketing, no-reply addresses

Auto-reply Rules:
- Set auto_reply=true ONLY for LOW priority emails that deserve a brief acknowledgment
- Set auto_reply=false for newsletters, no-reply addresses, and marketing emails
- Never auto_reply to URGENT/HIGH/MEDIUM emails

Email:
From: {email_from}
Subject: {subject}
Content: {content[:500]}
"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = response.content[0].text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        result_text = result_text.strip()

        return json.loads(result_text)

    def _fallback_categorize(self, email_from: str, subject: str, content: str) -> dict:
        """Fallback categorization when Claude API is unavailable."""
        text = f"{subject} {content}".lower()
        email_lower = email_from.lower()

        # Check for urgent keywords
        urgent_keywords = ['urgent', 'asap', 'deadline', 'immediate', 'today', 'emergency']
        if any(kw in text for kw in urgent_keywords):
            return {"priority": "URGENT", "reason": "Contains urgent keywords", "needs_response": True, "suggested_action": "Respond immediately", "auto_reply": False}

        # Check for high priority senders
        if 'muniya' in email_lower or 'm95251957' in email_lower:
            return {"priority": "HIGH", "reason": "Important sender", "needs_response": True, "suggested_action": "Respond within 4 hours", "auto_reply": False}

        # Check for no-reply/automated (no response needed)
        if 'no-reply' in email_lower or 'noreply' in email_lower or 'mailer-daemon' in email_lower:
            return {"priority": "LOW", "reason": "Automated/no-reply", "needs_response": False, "suggested_action": "Archive", "auto_reply": False}

        # Check for newsletters (no response needed)
        if 'newsletter' in text or 'unsubscribe' in text or 'marketing' in email_lower:
            return {"priority": "LOW", "reason": "Newsletter/marketing", "needs_response": False, "suggested_action": "Archive or unsubscribe", "auto_reply": False}

        # Medium priority - general emails that may need auto-reply
        if any(kw in text for kw in ['question', 'inquiry', 'help', 'support', 'information']):
            return {"priority": "MEDIUM", "reason": "General inquiry", "needs_response": True, "suggested_action": "Review and respond", "auto_reply": False}

        # Default LOW priority with potential auto-reply
        return {"priority": "LOW", "reason": "General email", "needs_response": True, "suggested_action": "Review when available", "auto_reply": True}

    def generate_draft(self, email_from: str, subject: str, content: str, priority: str) -> str:
        """Generate a draft response using Claude API or template."""
        if self.client:
            try:
                return self._claude_generate_draft(email_from, subject, content, priority)
            except Exception as e:
                print(f"Claude API error (draft): {e}")

        # Fallback template
        return "Thank you for your email. I'll review this and get back to you shortly."

    def _claude_generate_draft(self, email_from: str, subject: str, content: str, priority: str) -> str:
        """Use Claude API to generate a draft response."""
        prompt = f"""Write a brief, professional email response (2-4 sentences).

Tone Guidelines:
{self.tone_guidelines[:1000]}

Rules:
- Be concise and actionable
- Include specific next steps if needed
- Match formality to sender (casual for personal, professional for business)
- Do NOT include subject line, just the body
- Do NOT include signature (user will add their own)

Original Email:
From: {email_from}
Subject: {subject}
Content: {content[:500]}

Priority: {priority}

Write the response body only:"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    def generate_auto_reply(self, email_from: str, subject: str, content: str) -> str:
        """Generate a simple auto-reply for LOW priority emails."""
        if self.client:
            try:
                prompt = f"""Write a very brief (1-2 sentences) acknowledgment email.
Keep it simple and professional. Just acknowledge receipt.
Do NOT include subject line or signature.

Original Email:
From: {email_from}
Subject: {subject}

Write the brief acknowledgment:"""

                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            except Exception as e:
                print(f"Claude API error (auto-reply): {e}")

        return self.auto_reply_templates["default"]

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email using Gmail API."""
        if not self.gmail_service:
            print("Gmail service not available for sending")
            return False

        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send
            self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            print(f"[SENT] Auto-reply to: {to}")
            return True

        except Exception as e:
            print(f"Send email error: {e}")
            return False

    def send_notification(self, title: str, message: str, priority: str = "MEDIUM"):
        """Send Windows desktop notification for important emails."""
        if not TOAST_AVAILABLE:
            print(f"[NOTIFICATION] {title}: {message}")
            return

        try:
            toaster.show_toast(
                title=title,
                msg=message[:200],
                duration=10 if priority in ["URGENT", "HIGH"] else 5,
                threaded=True
            )
        except Exception as e:
            print(f"Notification error: {e}")
            print(f"[NOTIFICATION] {title}: {message}")

    def update_dashboard(self):
        """Update Dashboard.md with current counts."""
        folders = {
            "Inbox": self.vault_path / "Inbox",
            "Pending_Approval": self.vault_path / "Pending_Approval",
            "Approved": self.vault_path / "Approved",
            "Done": self.vault_path / "Done"
        }

        counts = {}
        for name, path in folders.items():
            if path.exists():
                counts[name] = len(list(path.glob("*.md")))
            else:
                counts[name] = 0

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dashboard_content = f"""# AI Employee Dashboard

**Last Updated**: {timestamp}
**Status**: Active
**Mode**: {"AI-Powered" if CLAUDE_AVAILABLE else "Rule-Based"}

---

## Folder Counts

| Folder | Count |
|--------|-------|
| Inbox | {counts.get('Inbox', 0)} |
| Pending Approval | {counts.get('Pending_Approval', 0)} |
| Approved | {counts.get('Approved', 0)} |
| Done | {counts.get('Done', 0)} |

---

## System Status

- Watcher: Running
- Last Check: {timestamp}
- Claude API: {"Connected" if CLAUDE_AVAILABLE else "Not configured"}
- Gmail Send: {"Enabled" if self.gmail_service else "Disabled"}

---

*Auto-generated by AI Employee System*
"""

        try:
            self.dashboard_path.write_text(dashboard_content, encoding='utf-8')
        except Exception as e:
            print(f"Dashboard update error: {e}")

    def process_email(self, email_from: str, subject: str, content: str, message_id: str) -> dict:
        """
        Full email processing pipeline:
        1. Categorize priority
        2. Generate draft if HIGH/URGENT
        3. Auto-reply if LOW and auto_reply=True
        4. Send notification if HIGH/URGENT
        5. Return processed data
        """
        # Step 1: Categorize
        category = self.categorize_email(email_from, subject, content)
        priority = category.get("priority", "MEDIUM")
        auto_reply = category.get("auto_reply", False)

        result = {
            "message_id": message_id,
            "priority": priority,
            "reason": category.get("reason", ""),
            "needs_response": category.get("needs_response", True),
            "suggested_action": category.get("suggested_action", ""),
            "draft": None,
            "auto_replied": False
        }

        # Step 2: Generate draft for HIGH/URGENT
        if priority in ["URGENT", "HIGH"] and category.get("needs_response", True):
            result["draft"] = self.generate_draft(email_from, subject, content, priority)

        # Step 3: Auto-reply for LOW priority (if enabled)
        if priority == "LOW" and auto_reply and self.gmail_service:
            # Extract email address from "Name <email@example.com>" format
            if '<' in email_from and '>' in email_from:
                reply_to = email_from.split('<')[1].split('>')[0]
            else:
                reply_to = email_from

            # Generate and send auto-reply
            reply_body = self.generate_auto_reply(email_from, subject, content)
            reply_subject = f"Re: {subject}"

            if self.send_email(reply_to, reply_subject, reply_body):
                result["auto_replied"] = True
                result["suggested_action"] = "Auto-replied and archived"

        # Step 4: Send notification for HIGH/URGENT
        if priority in ["URGENT", "HIGH"]:
            icon = "URGENT" if priority == "URGENT" else "HIGH"
            self.send_notification(
                title=f"{icon} Email from {email_from.split('<')[0].strip()}",
                message=f"{subject[:50]}... - {category.get('suggested_action', 'Review needed')}",
                priority=priority
            )

        return result


# Standalone test
if __name__ == "__main__":
    vault = r"C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault"
    processor = EmailProcessor(vault)

    test_result = processor.categorize_email(
        "test@example.com",
        "Test Subject",
        "This is a test email content."
    )
    print(f"Test result: {test_result}")
