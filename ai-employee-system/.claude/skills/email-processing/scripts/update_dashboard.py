#!/usr/bin/env python3
"""
Update Dashboard Script for AI Employee System

This script automatically generates real-time dashboard data by:
1. Counting items in each vault folder
2. Reading recent email details
3. Identifying high-priority items
4. Outputting structured data for Dashboard.md

Usage:
    python update_dashboard.py
    python update_dashboard.py --format json
    python update_dashboard.py --vault-path /custom/path
"""

import os
import re
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class DashboardUpdater:
    """Generate dashboard statistics for AI Employee System vault."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"
        self.dashboard_path = self.vault_path / "Dashboard.md"

    def count_folder_items(self, folder_path: Path) -> int:
        """Count markdown files in a folder."""
        if not folder_path.exists():
            return 0
        return len(list(folder_path.glob("*.md")))

    def read_email_frontmatter(self, file_path: Path) -> Optional[Dict]:
        """Extract YAML frontmatter from email file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not match:
                return None

            frontmatter = yaml.safe_load(match.group(1))

            # Convert datetime objects to strings
            if frontmatter and 'received' in frontmatter:
                received = frontmatter['received']
                if hasattr(received, 'isoformat'):
                    frontmatter['received'] = received.isoformat()
                else:
                    frontmatter['received'] = str(received)

            return frontmatter
        except Exception as e:
            # Silently skip problematic files
            return None

    def get_recent_inbox_items(self, limit: int = 5) -> List[Dict]:
        """Get the most recent inbox items with details."""
        if not self.inbox_path.exists():
            return []

        email_files = list(self.inbox_path.glob("EMAIL_*.md"))
        items = []

        for file_path in email_files:
            frontmatter = self.read_email_frontmatter(file_path)
            if frontmatter:
                items.append({
                    'file_name': file_path.name,
                    'from': frontmatter.get('from', 'Unknown'),
                    'subject': frontmatter.get('subject', 'No Subject'),
                    'received': frontmatter.get('received', ''),
                    'status': frontmatter.get('status', 'unknown'),
                    'priority': frontmatter.get('priority', 'unassigned')
                })

        # Sort by received date (most recent first)
        items.sort(key=lambda x: x['received'], reverse=True)
        return items[:limit]

    def categorize_priority(self, email_from: str, subject: str) -> str:
        """Categorize email priority based on Handbook rules."""
        email_lower = email_from.lower()
        subject_lower = subject.lower()

        # Check for URGENT keywords
        urgent_keywords = ['urgent', 'asap', 'deadline', 'today', 'immediate']
        if any(keyword in subject_lower for keyword in urgent_keywords):
            return 'URGENT'

        # HIGH priority senders
        if 'muniya' in email_lower or 'm95251957' in email_lower:
            return 'HIGH'

        # MEDIUM priority senders
        if 'munizazubair' in email_lower:
            return 'MEDIUM'

        # LOW priority senders
        if 'google' in email_lower or 'no-reply' in email_lower:
            return 'LOW'

        # Default to MEDIUM
        return 'MEDIUM'

    def identify_high_priority_items(self) -> List[Dict]:
        """Find all high-priority and urgent items."""
        high_priority = []

        for folder_path in [self.inbox_path, self.needs_action_path]:
            if not folder_path.exists():
                continue

            for file_path in folder_path.glob("EMAIL_*.md"):
                frontmatter = self.read_email_frontmatter(file_path)
                if not frontmatter:
                    continue

                email_from = frontmatter.get('from', '')
                subject = frontmatter.get('subject', '')
                priority = self.categorize_priority(email_from, subject)

                if priority in ['URGENT', 'HIGH']:
                    high_priority.append({
                        'file_name': file_path.name,
                        'folder': folder_path.name,
                        'from': email_from,
                        'subject': subject,
                        'received': frontmatter.get('received', ''),
                        'priority': priority
                    })

        return sorted(high_priority, key=lambda x: (
            0 if x['priority'] == 'URGENT' else 1,
            x['received']
        ), reverse=True)

    def generate_statistics(self) -> Dict:
        """Generate complete dashboard statistics."""
        inbox_count = self.count_folder_items(self.inbox_path)
        needs_action_count = self.count_folder_items(self.needs_action_path)
        done_count = self.count_folder_items(self.done_path)

        recent_items = self.get_recent_inbox_items(limit=5)
        high_priority_items = self.identify_high_priority_items()

        return {
            'timestamp': datetime.now().isoformat(),
            'counts': {
                'inbox': inbox_count,
                'needs_action': needs_action_count,
                'done': done_count,
                'total': inbox_count + needs_action_count + done_count
            },
            'recent_items': recent_items,
            'high_priority_items': high_priority_items,
            'status': {
                'gmail_watcher': 'Active',
                'vault_connected': self.vault_path.exists(),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
            }
        }

    def format_markdown_output(self, stats: Dict) -> str:
        """Format statistics as readable markdown."""
        output = []
        output.append("# Dashboard Statistics\n")
        output.append(f"**Generated**: {stats['timestamp']}\n")
        output.append("---\n")

        # Folder counts
        output.append("## Folder Counts\n")
        counts = stats['counts']
        output.append(f"- Inbox: {counts['inbox']}")
        output.append(f"- Needs Action: {counts['needs_action']}")
        output.append(f"- Done: {counts['done']}")
        output.append(f"- **Total**: {counts['total']}\n")

        # Recent items
        output.append("## Recent Inbox Items (Last 5)\n")
        if stats['recent_items']:
            for i, item in enumerate(stats['recent_items'], 1):
                output.append(f"{i}. **{item['subject']}**")
                output.append(f"   - From: {item['from']}")
                received_date = item['received'][:19] if item['received'] else 'Unknown'
                output.append(f"   - Received: {received_date}")
                if item['priority'] != 'unassigned':
                    output.append(f"   - Priority: {item['priority']}")
                output.append("")
        else:
            output.append("No items in inbox.\n")

        # High priority items
        output.append("## High Priority Items\n")
        if stats['high_priority_items']:
            for item in stats['high_priority_items']:
                priority_indicator = '[URGENT]' if item['priority'] == 'URGENT' else '[HIGH]'
                output.append(f"{priority_indicator} **{item['subject']}**")
                output.append(f"   - From: {item['from']}")
                output.append(f"   - Location: {item['folder']}")
                output.append("")
        else:
            output.append("No high-priority items.\n")

        return '\n'.join(output)

    def update_dashboard_file(self, stats: Dict):
        """Update the actual Dashboard.md file with new statistics."""
        # This is a placeholder for actual dashboard update logic
        # In practice, you'd parse the existing Dashboard.md and update specific sections
        print("✓ Dashboard data generated")
        print(f"   Inbox: {stats['counts']['inbox']}")
        print(f"   Needs Action: {stats['counts']['needs_action']}")
        print(f"   Done: {stats['counts']['done']}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate dashboard statistics for AI Employee System'
    )
    parser.add_argument(
        '--vault-path',
        default=r'C:\Users\SIBGHAT\OneDrive\Documents\Obsidian Vault\AI-Employee-Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format'
    )
    parser.add_argument(
        '--update-file',
        action='store_true',
        help='Update the Dashboard.md file directly'
    )

    args = parser.parse_args()

    # Initialize updater
    updater = DashboardUpdater(args.vault_path)

    # Generate statistics
    try:
        stats = updater.generate_statistics()

        if args.format == 'json':
            print(json.dumps(stats, indent=2))
        else:
            print(updater.format_markdown_output(stats))

        if args.update_file:
            updater.update_dashboard_file(stats)

    except Exception as e:
        print(f"ERROR: Error generating dashboard: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
