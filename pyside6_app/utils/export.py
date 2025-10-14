"""
CSV export functionality for drafts.
"""

import csv
from pathlib import Path
from typing import List
from datetime import datetime

from ..state.models import DraftEmail


class CSVExporter:
    """Export draft emails to CSV format."""

    @staticmethod
    def export_drafts(drafts: List[DraftEmail], file_path: Path) -> bool:
        """
        Export drafts to CSV file.

        Args:
            drafts: List of DraftEmail objects
            file_path: Output file path

        Returns:
            True if export successful

        Raises:
            Exception: If export fails
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    'ID',
                    'Type',
                    'Priority',
                    'Category',
                    'Sub-Category',
                    'Item',
                    'Subject',
                    'Body',
                    'Recipient',
                    'Status',
                    'Error Message',
                    'Sent Timestamp'
                ])

                # Write drafts
                for draft in drafts:
                    writer.writerow([
                        draft.id,
                        draft.type.value,
                        draft.priority,
                        draft.category,
                        draft.subcategory,
                        draft.item,
                        draft.subject,
                        draft.body,
                        str(draft.recipient),
                        draft.status.value,
                        draft.error_message or '',
                        draft.sent_timestamp.isoformat() if draft.sent_timestamp else ''
                    ])

            return True

        except Exception as e:
            raise Exception(f"Failed to export to CSV: {str(e)}")

    @staticmethod
    def get_default_filename() -> str:
        """
        Get default export filename.

        Returns:
            Default filename with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"ticket_drafts_{timestamp}.csv"
