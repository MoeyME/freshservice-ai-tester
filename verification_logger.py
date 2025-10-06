"""
Verification Report Logger
Creates detailed comparison reports for Freshservice ticket verification.
"""

from datetime import datetime
from typing import Dict, List
import os


class VerificationLogger:
    """Handles logging of verification results to file."""

    def __init__(self, log_dir: str = "."):
        """
        Initialize the verification logger.

        Args:
            log_dir: Directory to save log files (default: current directory)
        """
        self.log_dir = log_dir
        self.log_file = None

    def create_verification_report(
        self,
        verification_data: Dict,
        recipient_email: str,
        freshservice_domain: str
    ) -> str:
        """
        Create a detailed verification report.

        Args:
            verification_data: Verification results from TicketVerifier
            recipient_email: Email address that received tickets
            freshservice_domain: Freshservice domain

        Returns:
            Path to the created log file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"verification_report_{timestamp}.txt"
            self.log_file = os.path.join(self.log_dir, filename)

            with open(self.log_file, 'w', encoding='utf-8') as f:
                # Header
                f.write("=" * 80 + "\n")
                f.write("FRESHSERVICE TICKET VERIFICATION REPORT\n")
                f.write("=" * 80 + "\n\n")

                # Batch Information
                f.write("BATCH INFORMATION\n")
                f.write("-" * 80 + "\n")
                f.write(f"Generated:              {verification_data['batch_start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Verification Run:       {verification_data['verification_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                wait_time = (verification_data['verification_time'] - verification_data['batch_start_time']).total_seconds() / 60
                f.write(f"Wait Time:              {wait_time:.1f} minutes\n")
                f.write(f"Recipient Email:        {recipient_email}\n")
                f.write(f"Freshservice Domain:    {freshservice_domain}\n\n")

                # Summary Statistics
                summary = verification_data['summary']
                f.write("SUMMARY STATISTICS\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Emails Sent:      {verification_data['total_sent']}\n")
                f.write(f"Tickets Found:          {verification_data['total_found']}\n")
                f.write(f"Tickets Not Found:      {verification_data['total_not_found']}\n")
                f.write(f"Total Matches (PASS):   {summary['passed']}\n")
                f.write(f"Total Mismatches (FAIL):{summary['failed']}\n")
                f.write(f"Success Rate:           {summary['pass_rate']:.1f}%\n\n")

                # Field Accuracy
                f.write("FIELD ACCURACY\n")
                f.write("-" * 80 + "\n")
                field_stats = summary['field_stats']
                for field_name, stats in field_stats.items():
                    if field_name == 'group_assignments':
                        continue  # Handle separately
                    # Make sure stats is a dict with the expected keys
                    if isinstance(stats, dict) and 'total' in stats and 'correct' in stats and 'percentage' in stats:
                        field_label = field_name.replace('_', ' ').title()
                        if stats['total'] > 0:
                            f.write(f"{field_label:<20} {stats['correct']}/{stats['total']} ({stats['percentage']:.1f}%)\n")

                # Group Assignment Distribution
                if 'group_distribution' in field_stats:
                    group_data = field_stats['group_distribution']
                    if isinstance(group_data, dict) and group_data:
                        f.write("\nGROUP ASSIGNMENT DISTRIBUTION\n")
                        f.write("-" * 80 + "\n")
                        f.write("Valid Groups: Service Desk Team, Infrastructure Team, Application Team,\n")
                        f.write("              Enterprise Technology, Lightbulbs, People & Safety Systems\n\n")
                        try:
                            for group_name, count in sorted(group_data.items()):
                                f.write(f"{group_name:<40} {count} tickets\n")
                        except Exception as e:
                            f.write(f"Error displaying group distribution: {str(e)}\n")
                f.write("\n")

                # Detailed Ticket Verification
                f.write("=" * 80 + "\n")
                f.write("DETAILED TICKET VERIFICATION\n")
                f.write("=" * 80 + "\n\n")

                for result in verification_data['results']:
                    self._write_ticket_result(f, result)

                # Footer
                f.write("=" * 80 + "\n")
                f.write("END OF VERIFICATION REPORT\n")
                f.write("=" * 80 + "\n")

            return self.log_file

        except Exception as e:
            import traceback
            print(f"Error creating verification report: {str(e)}")
            print(traceback.format_exc())
            raise

    def _write_ticket_result(self, f, result: Dict):
        """Write individual ticket verification result."""
        ticket_num = result['ticket_number']
        status = result['status']
        overall = result['overall_result']

        # Status indicator
        if status == 'NOT_FOUND':
            status_icon = "⚠"
            status_text = "NOT FOUND"
        elif overall == 'PASS':
            status_icon = "✓"
            status_text = "PASS"
        else:
            status_icon = "✗"
            status_text = f"FAIL ({result['mismatch_count']} mismatches)"

        # Header
        f.write(f"TICKET #{ticket_num} - {status_icon} {status_text}\n")
        f.write("-" * 80 + "\n")
        f.write(f"Email Number:           {ticket_num}\n")

        if status == 'FOUND':
            f.write(f"Freshservice ID:        {result['freshservice_id']}\n")

        # Subject (truncate if too long)
        subject = result['subject']
        if len(subject) > 70:
            subject = subject[:67] + "..."
        f.write(f"Subject:                {subject}\n")
        f.write(f"Status:                 {status_icon} {status}\n\n")

        if status == 'FOUND':
            # Comparison table
            f.write("Expected vs Actual Comparison:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Field':<20} {'Expected':<25} {'Actual':<25} {'Status':<10}\n")
            f.write("-" * 80 + "\n")

            comparisons = result['comparisons']
            for field_name, comparison in comparisons.items():
                field_label = field_name.replace('_', ' ').title()
                expected = str(comparison['expected'])[:24]
                actual = str(comparison['actual'])[:24]

                # All fields are now validated (including group)
                if comparison['match'] is None:
                    match_icon = "ℹ INFO"
                elif comparison['match']:
                    match_icon = "✓ MATCH"
                else:
                    match_icon = "✗ MISMATCH"

                f.write(f"{field_label:<20} {expected:<25} {actual:<25} {match_icon:<10}\n")

            f.write("\n")

            # Overall result
            if overall == 'PASS':
                f.write("Overall Result: ✓ ALL FIELDS CORRECT\n")
            else:
                f.write(f"Overall Result: ✗ {result['mismatch_count']} FIELDS INCORRECT\n")

                # Possible reasons for mismatches
                f.write("\nPossible Reasons:\n")
                f.write("- Email content may not have triggered correct categorization rules\n")
                f.write("- Freshservice automation/workflow rules may override email-based assignment\n")
                f.write("- Priority Matrix in Freshservice may have different configuration\n")
                f.write("- Agent assignment rules may require specific keywords or patterns\n")

        else:  # NOT_FOUND
            f.write("Possible Reasons:\n")
            f.write("- Ticket still being processed (may take longer than expected)\n")
            f.write("- Email was rejected, filtered, or bounced by mail server\n")
            f.write("- Email not received by Freshservice inbox\n")
            f.write("- Check Freshservice email inbox and spam folder\n")
            f.write("- Verify email routing and forwarding rules\n")

        f.write("\n" + "=" * 80 + "\n\n")

    def append_to_main_log(self, main_log_path: str, verification_summary: str):
        """
        Append verification summary to the main email generation log.

        Args:
            main_log_path: Path to main log file
            verification_summary: Summary text to append
        """
        try:
            with open(main_log_path, 'a', encoding='utf-8') as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write("FRESHSERVICE VERIFICATION RESULTS\n")
                f.write("=" * 80 + "\n\n")
                f.write(verification_summary)
                f.write("\n" + "=" * 80 + "\n")
        except Exception as e:
            print(f"Error appending to main log: {str(e)}")

    def create_summary_text(self, verification_data: Dict) -> str:
        """
        Create a summary text for quick reference.

        Args:
            verification_data: Verification results

        Returns:
            Summary text
        """
        summary = verification_data['summary']
        text = f"Verification completed at {verification_data['verification_time'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        text += f"Results:\n"
        text += f"  Total Sent:     {verification_data['total_sent']}\n"
        text += f"  Found:          {verification_data['total_found']}\n"
        text += f"  Not Found:      {verification_data['total_not_found']}\n"
        text += f"  Passed:         {summary['passed']}\n"
        text += f"  Failed:         {summary['failed']}\n"
        text += f"  Success Rate:   {summary['pass_rate']:.1f}%\n\n"

        text += "Field Accuracy:\n"
        for field_name, stats in summary['field_stats'].items():
            # Skip the distribution dict
            if field_name == 'group_distribution':
                continue
            if isinstance(stats, dict) and 'total' in stats and stats['total'] > 0:
                field_label = field_name.replace('_', ' ').title()
                text += f"  {field_label:<20} {stats['correct']}/{stats['total']} ({stats['percentage']:.1f}%)\n"

        return text
