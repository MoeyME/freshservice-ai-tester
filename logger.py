"""
Logging system for email test runs.
Creates detailed log files with ticket information and statistics.
"""

from datetime import datetime
from typing import Dict, List, Optional
import os


class TicketLogger:
    """Handles logging of email test runs to file."""

    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the logger.

        Args:
            log_dir: Directory to save log files (default: logs subdirectory)
        """
        self.log_dir = log_dir
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.log_file = None
        self.log_entries = []
        self.start_time = None

    def start_log(
        self,
        client_id: str,
        tenant_id: str,
        sender_email: str,
        recipient_email: str,
        claude_api_key: str,
        total_emails: int
    ) -> str:
        """
        Start a new log file.

        Args:
            client_id: Microsoft client ID
            tenant_id: Microsoft tenant ID
            sender_email: Email address of sender
            recipient_email: Email address of recipient
            claude_api_key: Claude API key (will be masked)
            total_emails: Number of emails to send

        Returns:
            Path to log file
        """
        self.start_time = datetime.now()
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"email_test_log_{timestamp}.txt"
        self.log_file = os.path.join(self.log_dir, filename)

        # Mask API key
        masked_key = self._mask_api_key(claude_api_key)

        # Write header
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("IT TICKET EMAIL TEST RUN LOG\n")
            f.write("="*80 + "\n\n")
            f.write(f"Test Run Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("CONFIGURATION\n")
            f.write("-" * 80 + "\n")
            f.write(f"Microsoft Client ID:    {client_id}\n")
            f.write(f"Microsoft Tenant ID:    {tenant_id}\n")
            f.write(f"Sender Email:           {sender_email}\n")
            f.write(f"Recipient Email:        {recipient_email}\n")
            f.write(f"Claude API Key:         {masked_key}\n")
            f.write(f"Total Emails Requested: {total_emails}\n")
            f.write("\n" + "="*80 + "\n\n")

        return self.log_file

    def log_email(
        self,
        email_number: int,
        category: str,
        ticket_type: str,
        priority: str,
        subject: str,
        description: str,
        success: bool,
        error: Optional[str] = None
    ):
        """
        Log an individual email entry.

        Args:
            email_number: Sequential email number
            category: IT category
            ticket_type: Incident or Service Request
            priority: Priority level
            subject: Email subject
            description: Email body
            success: Whether email sent successfully
            error: Error message if failed
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        entry = {
            "number": email_number,
            "category": category,
            "type": ticket_type,
            "priority": priority,
            "subject": subject,
            "description": description,
            "timestamp": timestamp,
            "success": success,
            "error": error
        }

        self.log_entries.append(entry)

        # Write to file immediately
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"EMAIL #{email_number}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Ticket Number:   {email_number}\n")
                f.write(f"Email Number:    {email_number}\n")
                f.write(f"Category:        {category}\n")
                f.write(f"Type:            {ticket_type}\n")
                f.write(f"Priority:        {priority}\n")
                f.write(f"Subject:         {subject}\n")
                f.write(f"Timestamp:       {timestamp}\n")
                f.write(f"Status:          {'SUCCESS' if success else 'FAILED'}\n")
                if error:
                    f.write(f"Error:           {error}\n")
                f.write("\nDescription:\n")
                f.write(description + "\n")
                f.write("\nTicket #: ___________\n")
                f.write("\n" + "="*80 + "\n\n")

    def finalize_log(
        self,
        total_sent: int,
        success_count: int,
        failure_count: int,
        distribution: Dict[str, int],
        type_distribution: Dict[str, int],
        estimated_cost: float,
        token_stats: Dict[str, int]
    ):
        """
        Write summary statistics to log file.

        Args:
            total_sent: Total emails attempted
            success_count: Number of successful sends
            failure_count: Number of failed sends
            distribution: Dictionary of priority -> count
            type_distribution: Dictionary of ticket_type -> count
            estimated_cost: Estimated DeepSeek API cost
            token_stats: Token usage statistics
        """
        if not self.log_file:
            return

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() if self.start_time else 0

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*80 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("="*80 + "\n\n")
            f.write(f"Test Run Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Duration:     {duration:.1f} seconds ({duration/60:.1f} minutes)\n\n")
            f.write(f"Total Emails:       {total_sent}\n")
            f.write(f"Successful:         {success_count}\n")
            f.write(f"Failed:             {failure_count}\n")
            f.write(f"Success Rate:       {(success_count/total_sent*100) if total_sent > 0 else 0:.1f}%\n\n")

            f.write("PRIORITY DISTRIBUTION\n")
            f.write("-" * 80 + "\n")
            for priority in sorted(distribution.keys()):
                f.write(f"{priority}: {distribution[priority]}\n")

            f.write("\nTYPE DISTRIBUTION\n")
            f.write("-" * 80 + "\n")
            for ticket_type in sorted(type_distribution.keys()):
                f.write(f"{ticket_type}: {type_distribution[ticket_type]}\n")

            f.write("\nCLAUDE API USAGE\n")
            f.write("-" * 80 + "\n")
            f.write(f"Input Tokens:       {token_stats.get('input_tokens', 0):,}\n")
            f.write(f"Output Tokens:      {token_stats.get('output_tokens', 0):,}\n")
            f.write(f"Total Tokens:       {token_stats.get('total_tokens', 0):,}\n")
            f.write(f"Estimated Cost:     ${estimated_cost:.4f}\n")

            f.write("\n" + "="*80 + "\n")
            f.write("END OF LOG\n")
            f.write("="*80 + "\n")

        print(f"\n✓ Log file saved: {self.log_file}")

    def _mask_api_key(self, api_key: str) -> str:
        """
        Mask API key for logging (show first and last few characters).

        Args:
            api_key: Full API key

        Returns:
            Masked version (e.g., "sk-ant-...xyz123")
        """
        if len(api_key) <= 10:
            return "sk-ant-***"

        return f"{api_key[:7]}...{api_key[-6:]}"

    def get_log_file_path(self) -> Optional[str]:
        """
        Get the current log file path.

        Returns:
            Path to log file or None
        """
        return self.log_file
