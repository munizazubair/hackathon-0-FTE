#!/usr/bin/env python3
"""
Email Categorization Script for AI Employee System

This script automatically categorizes emails based on Handbook priority rules:
- Analyzes sender email address
- Checks subject line for urgent keywords
- Assigns priority (URGENT, HIGH, MEDIUM, LOW)
- Updates email frontmatter with priority field

Usage:
    python categorize_email.py EMAIL_FILE.md
    python categorize_email.py --folder Inbox
    python categorize_email.py --batch --dry-run
"""

import os
import re
import yaml
import argparse
from pathlib import Path
from typing import Dict, Optional, List


class EmailCategorizer:
    """Categorize emails based on Handbook priority rules."""

    # Priority rules from Handbook
    HIGH_PRIORITY_PATTERNS = [
        'muniya',
        'm95251957@gmail.com'
    ]

    MEDIUM_PRIORITY_PATTERNS = [
        'munizazubair',
        'munizazubairkhan@gmail.com'
    ]

    LOW_PRIORITY_PATTERNS = [
        'google',
        'no-reply',
        'noreply'
    ]

    URGENT_KEYWORDS = [
        'urgent',
        'asap',
        'deadline',
        'today',
        'immediate',
        'critical',
        'emergency',
        'high priority'
    ]

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

    def read_email_file(self, file_path: Path) -> Optional[Dict]:
        """Read email file and extract frontmatter + content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
            if not match:
                print(f"WARNING: No valid frontmatter found in {file_path.name}")
                return None

            frontmatter_text = match.group(1)
            body = match.group(2)

            frontmatter = yaml.safe_load(frontmatter_text)

            # Convert datetime objects to strings
            if frontmatter and 'received' in frontmatter:
                received = frontmatter['received']
                if hasattr(received, 'isoformat'):
                    frontmatter['received'] = received.isoformat()

            return {
                'frontmatter': frontmatter,
                'body': body,
                'frontmatter_text': frontmatter_text,
                'full_content': content
            }
        except Exception as e:
            print(f"ERROR reading {file_path}: {e}")
            return None

    def categorize_by_sender(self, email_from: str) -> Optional[str]:
        """Categorize email priority based on sender."""
        email_lower = email_from.lower()

        # Check HIGH priority patterns
        for pattern in self.HIGH_PRIORITY_PATTERNS:
            if pattern in email_lower:
                return 'HIGH'

        # Check MEDIUM priority patterns
        for pattern in self.MEDIUM_PRIORITY_PATTERNS:
            if pattern in email_lower:
                return 'MEDIUM'

        # Check LOW priority patterns
        for pattern in self.LOW_PRIORITY_PATTERNS:
            if pattern in email_lower:
                return 'LOW'

        # Default: MEDIUM (unknown sender)
        return 'MEDIUM'

    def check_urgent_keywords(self, text: str) -> bool:
        """Check if text contains urgent keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.URGENT_KEYWORDS)

    def categorize_email(self, email_data: Dict) -> str:
        """
        Categorize email using complete Handbook rules.

        Priority hierarchy:
        1. URGENT: Contains urgent keywords (overrides sender-based)
        2. HIGH: From high-priority senders
        3. MEDIUM: From medium-priority senders or unknown
        4. LOW: From low-priority senders (newsletters, system emails)
        """
        frontmatter = email_data['frontmatter']
        email_from = frontmatter.get('from', '')
        subject = frontmatter.get('subject', '')
        body = email_data['body']

        # Check for URGENT keywords in subject or body
        if self.check_urgent_keywords(subject) or self.check_urgent_keywords(body):
            return 'URGENT'

        # Categorize based on sender
        return self.categorize_by_sender(email_from)

    def update_frontmatter(self, file_path: Path, priority: str, dry_run: bool = False) -> bool:
        """Update email file with priority field in frontmatter."""
        email_data = self.read_email_file(file_path)
        if not email_data:
            return False

        frontmatter = email_data['frontmatter']

        # Check if priority already exists
        existing_priority = frontmatter.get('priority')
        if existing_priority:
            print(f"  ℹ️ Priority already set: {existing_priority}")
            if existing_priority != priority:
                print(f"  🔄 Would update from {existing_priority} → {priority}")
            else:
                print(f"  OK Priority unchanged: {priority}")
                return True

        # Add priority field
        frontmatter['priority'] = priority

        # Reconstruct file content
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        new_content = f"---\n{new_frontmatter}---\n{email_data['body']}"

        if dry_run:
            print(f"  [DRY RUN] Would set priority: {priority}")
            return True

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  OK Updated priority: {priority}")
            return True
        except Exception as e:
            print(f"  ERROR Error writing file: {e}")
            return False

    def categorize_single_file(self, file_path: Path, dry_run: bool = False) -> Optional[str]:
        """Categorize a single email file."""
        print(f"\n[Email] Processing: {file_path.name}")

        email_data = self.read_email_file(file_path)
        if not email_data:
            return None

        frontmatter = email_data['frontmatter']
        print(f"  From: {frontmatter.get('from', 'Unknown')}")
        print(f"  Subject: {frontmatter.get('subject', 'No subject')}")

        # Categorize
        priority = self.categorize_email(email_data)
        print(f"  Assigned Priority: {priority}")

        # Update file
        self.update_frontmatter(file_path, priority, dry_run)

        return priority

    def categorize_folder(self, folder_name: str, dry_run: bool = False) -> Dict[str, int]:
        """Categorize all emails in a folder."""
        folder_path = self.vault_path / folder_name

        if not folder_path.exists():
            print(f"ERROR Folder not found: {folder_path}")
            return {}

        email_files = list(folder_path.glob("EMAIL_*.md"))
        print(f"\n[Folder] Processing folder: {folder_name}")
        print(f"   Found {len(email_files)} email files")

        priority_counts = {'URGENT': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

        for file_path in email_files:
            priority = self.categorize_single_file(file_path, dry_run)
            if priority:
                priority_counts[priority] += 1

        return priority_counts

    def print_summary(self, counts: Dict[str, int]):
        """Print categorization summary."""
        print("\n" + "="*50)
        print("[STATS] CATEGORIZATION SUMMARY")
        print("="*50)
        total = sum(counts.values())
        print(f"Total Emails: {total}")
        print(f"  [!] URGENT:  {counts['URGENT']}")
        print(f"  ! HIGH:    {counts['HIGH']}")
        print(f"  [~] MEDIUM:  {counts['MEDIUM']}")
        print(f"  [-] LOW:     {counts['LOW']}")
        print("="*50)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Categorize emails by priority based on Handbook rules'
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Specific email file to categorize'
    )
    parser.add_argument(
        '--vault-path',
        default=r'C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--folder',
        choices=['Inbox', 'Needs_Action', 'Done'],
        help='Process all emails in specified folder'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process all folders (Inbox, Needs_Action)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    # Initialize categorizer
    categorizer = EmailCategorizer(args.vault_path)

    try:
        if args.file:
            # Categorize single file
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"ERROR File not found: {file_path}")
                return 1
            categorizer.categorize_single_file(file_path, args.dry_run)

        elif args.folder:
            # Categorize specific folder
            counts = categorizer.categorize_folder(args.folder, args.dry_run)
            categorizer.print_summary(counts)

        elif args.batch:
            # Categorize all folders
            all_counts = {'URGENT': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}

            for folder in ['Inbox', 'Needs_Action']:
                counts = categorizer.categorize_folder(folder, args.dry_run)
                for priority, count in counts.items():
                    all_counts[priority] += count

            categorizer.print_summary(all_counts)

        else:
            print("ERROR Please specify a file, folder, or use --batch")
            print("   Examples:")
            print("     python categorize_email.py EMAIL_123.md")
            print("     python categorize_email.py --folder Inbox")
            print("     python categorize_email.py --batch --dry-run")
            return 1

    except Exception as e:
        print(f"ERROR Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
