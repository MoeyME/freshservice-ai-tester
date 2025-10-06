"""
Ticket Verification System
Compares sent emails with created Freshservice tickets to verify correct categorization.
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime
import re
from freshservice_client import FreshserviceClient


class TicketVerifier:
    """Verifies that Freshservice tickets match expected classifications."""

    # Freshservice priority mapping (API values)
    FS_PRIORITY_MAP = {
        1: 'Low',
        2: 'Medium',
        3: 'High',
        4: 'Urgent'
    }

    # Freshservice urgency/impact mapping
    FS_URGENCY_MAP = {
        1: 'Low',
        2: 'Medium',
        3: 'High'
    }

    FS_IMPACT_MAP = {
        1: 'Low',
        2: 'Medium',
        3: 'High'
    }

    # Priority to expected Urgency/Impact mapping based on ITIL matrix
    PRIORITY_TO_URGENCY_IMPACT = {
        'Priority 1': {'urgency': 3, 'impact': 3},  # High/High
        'Priority 2': [
            {'urgency': 3, 'impact': 2},  # High/Medium
            {'urgency': 2, 'impact': 3}   # Medium/High
        ],
        'Priority 3': [
            {'urgency': 3, 'impact': 1},  # High/Low
            {'urgency': 2, 'impact': 2},  # Medium/Medium
            {'urgency': 1, 'impact': 3}   # Low/High
        ],
        'Priority 4': {'urgency': 1, 'impact': 1}   # Low/Low
    }

    def __init__(self, fs_client: FreshserviceClient):
        """
        Initialize verifier.

        Args:
            fs_client: Freshservice API client
        """
        self.fs_client = fs_client

    def verify_batch(
        self,
        sent_emails: List[Dict],
        recipient_email: str,
        batch_start_time: datetime,
        expected_group: Optional[str] = None,
        sender_email: Optional[str] = None
    ) -> Dict:
        """
        Verify a batch of sent emails against Freshservice tickets.

        Args:
            sent_emails: List of sent email dictionaries with expected values
            recipient_email: Email address that received the tickets (for logging only)
            batch_start_time: When the batch started
            expected_group: Expected assignment group name
            sender_email: Email address that sent the emails (becomes the Freshservice requester)

        Returns:
            Dictionary with verification results
        """
        # Format timestamp for Freshservice API
        timestamp_str = self.fs_client.format_timestamp(batch_start_time)

        # IMPORTANT: Freshservice's 'email' parameter filters by REQUESTER email (the sender),
        # NOT the recipient email. When we know the sender's email, we can use it for filtering.

        if sender_email:
            print(f"Fetching tickets for requester {sender_email} since {timestamp_str}...")
            # Method 1: Get tickets by sender email + timestamp
            fs_tickets = self.fs_client.get_tickets_by_email(sender_email, timestamp_str)
            print(f"Found {len(fs_tickets)} tickets by email + timestamp filter")
        else:
            print(f"Fetching tickets since {timestamp_str}...")
            # Method 1: Get all tickets by timestamp (no email filter)
            fs_tickets = self.fs_client.get_tickets_by_email(None, timestamp_str)
            print(f"Found {len(fs_tickets)} tickets by timestamp filter")

        # Method 2: If no tickets found, broaden the search (last 24 hours)
        if not fs_tickets and sent_emails:
            print("No tickets found with batch timestamp, trying last 24 hours...")
            from datetime import timedelta
            yesterday = self.fs_client.format_timestamp(batch_start_time - timedelta(hours=24))
            fs_tickets = self.fs_client.get_tickets_by_email(sender_email, yesterday)
            print(f"Found {len(fs_tickets)} tickets in last 24 hours")

        # Method 3: If still nothing, get ALL recent tickets for this sender
        if not fs_tickets:
            print("No tickets found with timestamp filter, getting all recent tickets...")
            fs_tickets = self.fs_client.get_tickets_by_email(sender_email, None)
            print(f"Found {len(fs_tickets)} total recent tickets")

        # Debug: Show subjects of found tickets
        if fs_tickets:
            print(f"\nFreshservice ticket subjects found:")
            for ticket in fs_tickets[:10]:  # Show first 10
                print(f"  - ID {ticket.get('id')}: {ticket.get('subject', 'NO SUBJECT')}")
        else:
            print("⚠️ WARNING: No Freshservice tickets found at all!")

        # Debug: Show what we're searching for
        print(f"\nSearching for email subjects:")
        for sent_email in sent_emails[:10]:  # Show first 10
            prefix = f"[TEST-TKT-{sent_email['number']}]"
            print(f"  - {prefix}")

        # Match tickets to sent emails
        verification_results = []
        matched_fs_tickets = set()

        for sent_email in sent_emails:
            ticket_num = sent_email['number']
            expected_subject = sent_email['subject']

            # Find matching Freshservice ticket by subject prefix
            prefix = f"[TEST-TKT-{ticket_num}]"
            matching_ticket = None

            for fs_ticket in fs_tickets:
                fs_subject = fs_ticket.get('subject', '')
                if prefix in fs_subject and fs_ticket['id'] not in matched_fs_tickets:
                    matching_ticket = fs_ticket
                    matched_fs_tickets.add(fs_ticket['id'])
                    break

            if matching_ticket:
                # Compare ticket fields
                comparison = self._compare_ticket(
                    sent_email,
                    matching_ticket,
                    expected_group
                )
                verification_results.append(comparison)
            else:
                # Ticket not found
                verification_results.append({
                    'ticket_number': ticket_num,
                    'status': 'NOT_FOUND',
                    'freshservice_id': None,
                    'subject': expected_subject,
                    'comparisons': {},
                    'overall_result': 'NOT_FOUND',
                    'match_count': 0,
                    'mismatch_count': 0,
                    'expected': sent_email
                })

        # Generate summary statistics
        summary = self._generate_summary(verification_results)

        return {
            'results': verification_results,
            'summary': summary,
            'batch_start_time': batch_start_time,
            'verification_time': datetime.now(),
            'total_sent': len(sent_emails),
            'total_found': len([r for r in verification_results if r['status'] == 'FOUND']),
            'total_not_found': len([r for r in verification_results if r['status'] == 'NOT_FOUND'])
        }

    def _compare_ticket(
        self,
        sent_email: Dict,
        fs_ticket: Dict,
        expected_group: Optional[str]
    ) -> Dict:
        """
        Compare expected vs actual ticket fields.

        Args:
            sent_email: Expected email data
            fs_ticket: Actual Freshservice ticket
            expected_group: Expected assignment group

        Returns:
            Comparison result dictionary
        """
        comparisons = {}
        match_count = 0
        mismatch_count = 0

        # Check if this is discovery mode (manually selected tickets without full data)
        discovery_mode = 'priority' not in sent_email or 'type' not in sent_email or 'category' not in sent_email

        # Extract expected values (if available)
        if discovery_mode:
            # Discovery mode: Just report what's in Freshservice without comparison
            expected_priority = None
            expected_type = None
            expected_category = None
            expected_cat = None
            expected_subcat = None
            expected_item = None
        else:
            expected_priority = sent_email['priority']  # e.g., "Priority 2"
            expected_type = sent_email['type']          # e.g., "Incident" or "Service Request"
            expected_category = sent_email['category']  # e.g., "Application Support > Frameworks > Support"

            # Parse category hierarchy
            category_parts = [part.strip() for part in expected_category.split('>')]
            expected_cat = category_parts[0] if len(category_parts) > 0 else None
            expected_subcat = category_parts[1] if len(category_parts) > 1 else None
            expected_item = category_parts[2] if len(category_parts) > 2 else None

        # Get actual Freshservice values
        fs_priority = fs_ticket.get('priority')      # 1, 2, 3, or 4
        fs_urgency = fs_ticket.get('urgency')        # 1, 2, or 3
        fs_impact = fs_ticket.get('impact')          # 1, 2, or 3

        # Handle None/null values - Freshservice sometimes doesn't set these for email-created tickets
        # According to Freshservice docs, default should be Low (1) if not set
        if fs_urgency is None:
            fs_urgency = 1  # Default to Low
        if fs_impact is None:
            fs_impact = 1   # Default to Low

        fs_category = fs_ticket.get('category')
        fs_sub_category = fs_ticket.get('sub_category')
        fs_item = fs_ticket.get('item')
        fs_group_id = fs_ticket.get('group_id')
        fs_ticket_type = 'Incident' if fs_ticket.get('type') == 'Incident' else 'Service Request'

        # In discovery mode, just report actual values without comparison
        if discovery_mode:
            # Priority (report only)
            comparisons['priority'] = {
                'expected': 'Discovery Mode',
                'actual': self.FS_PRIORITY_MAP.get(fs_priority, f'Unknown ({fs_priority})'),
                'match': None  # No comparison in discovery mode
            }

            # Urgency (report only)
            comparisons['urgency'] = {
                'expected': 'Discovery Mode',
                'actual': self.FS_URGENCY_MAP.get(fs_urgency, f'Unknown ({fs_urgency})'),
                'match': None
            }

            # Impact (report only)
            comparisons['impact'] = {
                'expected': 'Discovery Mode',
                'actual': self.FS_IMPACT_MAP.get(fs_impact, f'Unknown ({fs_impact})'),
                'match': None
            }

            # Type (report only)
            comparisons['type'] = {
                'expected': 'Discovery Mode',
                'actual': fs_ticket_type,
                'match': None
            }

            # Category (report only)
            comparisons['category'] = {
                'expected': 'Discovery Mode',
                'actual': fs_category or 'Not Set',
                'match': None
            }

            # Sub-category (report only)
            comparisons['sub_category'] = {
                'expected': 'Discovery Mode',
                'actual': fs_sub_category or 'Not Set',
                'match': None
            }

            # Item (report only)
            comparisons['item'] = {
                'expected': 'Discovery Mode',
                'actual': fs_item or 'Not Set',
                'match': None
            }
        else:
            # Normal mode: Compare expected vs actual
            # Compare Priority
            expected_priority_num = self._priority_name_to_number(expected_priority)
            priority_match = (fs_priority == expected_priority_num)
            comparisons['priority'] = {
                'expected': expected_priority,
                'actual': self.FS_PRIORITY_MAP.get(fs_priority, f'Unknown ({fs_priority})'),
                'match': priority_match
            }
            if priority_match:
                match_count += 1
            else:
                mismatch_count += 1

            # Compare Urgency (based on priority matrix)
            expected_urgency = self._get_expected_urgency_from_priority(expected_priority)
            urgency_match = self._check_urgency_match(expected_urgency, fs_urgency)
            comparisons['urgency'] = {
                'expected': expected_urgency,
                'actual': self.FS_URGENCY_MAP.get(fs_urgency, f'Unknown ({fs_urgency})'),
                'match': urgency_match
            }
            if urgency_match:
                match_count += 1
            else:
                mismatch_count += 1

            # Compare Impact
            expected_impact = self._get_expected_impact_from_priority(expected_priority)
            impact_match = self._check_impact_match(expected_impact, fs_impact)
            comparisons['impact'] = {
                'expected': expected_impact,
                'actual': self.FS_IMPACT_MAP.get(fs_impact, f'Unknown ({fs_impact})'),
                'match': impact_match
            }
            if impact_match:
                match_count += 1
            else:
                mismatch_count += 1

            # Compare Type
            type_match = (fs_ticket_type == expected_type)
            comparisons['type'] = {
                'expected': expected_type,
                'actual': fs_ticket_type,
                'match': type_match
            }
            if type_match:
                match_count += 1
            else:
                mismatch_count += 1

            # Compare Category
            category_match = (fs_category == expected_cat)
            comparisons['category'] = {
                'expected': expected_cat or 'N/A',
                'actual': fs_category or 'Not Set',
                'match': category_match
            }
            if category_match:
                match_count += 1
            else:
                mismatch_count += 1

            # Compare Sub-category
            subcat_match = (fs_sub_category == expected_subcat)
            comparisons['sub_category'] = {
                'expected': expected_subcat or 'N/A',
                'actual': fs_sub_category or 'Not Set',
                'match': subcat_match
            }
            if subcat_match:
                match_count += 1
            else:
                mismatch_count += 1

            # Compare Item
            item_match = (fs_item == expected_item)
            comparisons['item'] = {
                'expected': expected_item or 'N/A',
                'actual': fs_item or 'Not Set',
                'match': item_match
            }
            if item_match:
                match_count += 1
            else:
                mismatch_count += 1

        # Validate Group Assignment - must be one of the valid groups
        # Valid groups: Service Desk Team, Infrastructure Team, Application Team,
        # Enterprise Technology, Lightbulbs, People & Safety Systems
        VALID_GROUP_IDS = {76000128925, 76000128926, 76000128927, 76000138755, 76000165188, 76000209739}

        if discovery_mode:
            # In discovery mode, just report the group without validation
            if fs_group_id is not None:
                group_name = self._get_group_name(fs_group_id)
                comparisons['group'] = {
                    'expected': 'Discovery Mode',
                    'actual': group_name,
                    'match': None
                }
            else:
                comparisons['group'] = {
                    'expected': 'Discovery Mode',
                    'actual': 'Unassigned',
                    'match': None
                }
        else:
            # Normal mode: Validate group
            if fs_group_id is not None:
                group_name = self._get_group_name(fs_group_id)
                # Check if group is one of the valid groups
                is_valid_group = fs_group_id in VALID_GROUP_IDS

                comparisons['group'] = {
                    'expected': 'One of 6 valid groups',
                    'actual': group_name,
                    'match': is_valid_group
                }
                if is_valid_group:
                    match_count += 1
                else:
                    mismatch_count += 1
            else:
                # No group assigned - this is a failure
                comparisons['group'] = {
                    'expected': 'One of 6 valid groups',
                    'actual': 'Unassigned',
                    'match': False
                }
                mismatch_count += 1

        # Overall result
        if discovery_mode:
            overall_result = 'DISCOVERY'  # Special status for discovery mode
        else:
            overall_result = 'PASS' if mismatch_count == 0 else 'FAIL'

        return {
            'ticket_number': sent_email['number'],
            'status': 'FOUND',
            'freshservice_id': fs_ticket['id'],
            'subject': sent_email['subject'],
            'comparisons': comparisons,
            'overall_result': overall_result,
            'match_count': match_count,
            'mismatch_count': mismatch_count,
            'expected': sent_email,
            'actual': fs_ticket
        }

    def _priority_name_to_number(self, priority_name: str) -> int:
        """Convert priority name to Freshservice number."""
        mapping = {
            'Priority 1': 4,  # Urgent
            'Priority 2': 3,  # High
            'Priority 3': 2,  # Medium
            'Priority 4': 1   # Low
        }
        return mapping.get(priority_name, 2)

    def _get_expected_urgency_from_priority(self, priority: str) -> str:
        """Get expected urgency value(s) from priority."""
        mapping = self.PRIORITY_TO_URGENCY_IMPACT.get(priority)
        if isinstance(mapping, list):
            # Multiple valid combinations, return as string
            urgencies = [self.FS_URGENCY_MAP[m['urgency']] for m in mapping]
            return ' or '.join(set(urgencies))
        elif isinstance(mapping, dict):
            return self.FS_URGENCY_MAP[mapping['urgency']]
        return 'Unknown'

    def _get_expected_impact_from_priority(self, priority: str) -> str:
        """Get expected impact value(s) from priority."""
        mapping = self.PRIORITY_TO_URGENCY_IMPACT.get(priority)
        if isinstance(mapping, list):
            # Multiple valid combinations
            impacts = [self.FS_IMPACT_MAP[m['impact']] for m in mapping]
            return ' or '.join(set(impacts))
        elif isinstance(mapping, dict):
            return self.FS_IMPACT_MAP[mapping['impact']]
        return 'Unknown'

    def _check_urgency_match(self, expected: str, actual: int) -> bool:
        """Check if urgency matches (handling 'or' cases)."""
        if ' or ' in expected:
            valid_values = expected.split(' or ')
            actual_str = self.FS_URGENCY_MAP.get(actual, '')
            return actual_str in valid_values
        else:
            return expected == self.FS_URGENCY_MAP.get(actual, '')

    def _check_impact_match(self, expected: str, actual: int) -> bool:
        """Check if impact matches (handling 'or' cases)."""
        if ' or ' in expected:
            valid_values = expected.split(' or ')
            actual_str = self.FS_IMPACT_MAP.get(actual, '')
            return actual_str in valid_values
        else:
            return expected == self.FS_IMPACT_MAP.get(actual, '')

    def _get_group_name(self, group_id: int) -> str:
        """
        Get group name from ID.

        Args:
            group_id: Freshservice group ID

        Returns:
            Group name or 'Unknown Group'
        """
        # Known group mappings - these are the ONLY valid groups
        group_map = {
            76000128925: 'Service Desk Team',
            76000128926: 'Infrastructure Team',
            76000128927: 'Application Team',  # Fixed typo: was "Applications Team"
            76000138755: 'Enterprise Technology',
            76000165188: 'Lightbulbs',
            76000209739: 'People & Safety Systems'
        }
        return group_map.get(group_id, f'Unknown Group (ID: {group_id})')

    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from verification results."""
        total = len(results)
        found = len([r for r in results if r['status'] == 'FOUND'])
        not_found = len([r for r in results if r['status'] == 'NOT_FOUND'])
        passed = len([r for r in results if r['overall_result'] == 'PASS'])
        failed = len([r for r in results if r['overall_result'] == 'FAIL'])

        # Field-level accuracy (now includes group validation)
        field_stats = {}
        fields = ['priority', 'urgency', 'impact', 'type', 'category', 'sub_category', 'item', 'group']

        for field in fields:
            correct = 0
            total_checked = 0
            for result in results:
                if result['status'] == 'FOUND' and field in result['comparisons']:
                    comp = result['comparisons'][field]
                    # All fields now count toward pass/fail (including group)
                    if comp.get('match') is not None:
                        total_checked += 1
                        if comp['match']:
                            correct += 1

            field_stats[field] = {
                'correct': correct,
                'total': total_checked,
                'percentage': (correct / total_checked * 100) if total_checked > 0 else 0
            }

        # Group assignment distribution (for reporting which groups were used)
        group_distribution = {}
        for result in results:
            if result['status'] == 'FOUND' and 'group' in result['comparisons']:
                group_actual = result['comparisons']['group']['actual']
                if group_actual not in group_distribution:
                    group_distribution[group_actual] = 0
                group_distribution[group_actual] += 1

        field_stats['group_distribution'] = group_distribution

        return {
            'total_tickets': total,
            'found': found,
            'not_found': not_found,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / found * 100) if found > 0 else 0,
            'field_stats': field_stats
        }
