"""
Verification Results Dialog - Shows detailed ticket verification information.
"""

from typing import Dict, List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QDialog
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, PushButton, FluentIcon,
    TableWidget, isDarkTheme
)


class VerificationDialog(QDialog):
    """
    Dialog showing detailed verification results for each ticket.

    Shows:
    - Ticket number and Freshservice ID
    - Subject
    - Expected vs Actual comparison for:
        - Priority
        - Type
        - Category/Subcategory/Item
        - Assigned Team
        - Urgency/Impact
    - Notes (if any)
    - Overall pass/fail status
    """

    def __init__(self, verification_results: Dict, parent: QWidget = None):
        """
        Initialize verification dialog.

        Args:
            verification_results: Results from TicketVerifier.verify_batch()
            parent: Parent widget
        """
        super().__init__(parent)
        self.verification_results = verification_results

        self.setWindowTitle("Verification Results")
        self.resize(1200, 800)

        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title = SubtitleLabel("Ticket Verification Results")
        layout.addWidget(title)

        # Summary stats
        summary_widget = self._create_summary_widget()
        layout.addWidget(summary_widget)

        # Results table
        table_label = BodyLabel("Detailed Results:")
        layout.addWidget(table_label)

        self.results_table = self._create_results_table()
        layout.addWidget(self.results_table, 1)

        # Close button
        close_button = PushButton("Close")
        close_button.setIcon(FluentIcon.CLOSE)
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(100)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

    def _create_summary_widget(self) -> QWidget:
        """Create summary statistics widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(32)

        summary = self.verification_results['summary']

        # Total tickets
        total_label = BodyLabel(f"Total: {summary['total_tickets']}")
        layout.addWidget(total_label)

        # Found
        found_label = BodyLabel(f"Found: {summary['found']}")
        layout.addWidget(found_label)

        # Not found
        if summary['not_found'] > 0:
            not_found_label = BodyLabel(f"Not Found: {summary['not_found']}")
            if isDarkTheme():
                not_found_label.setStyleSheet("color: #ec7063;")
            else:
                not_found_label.setStyleSheet("color: #e74c3c;")
            layout.addWidget(not_found_label)

        # Pass/Fail
        passed_label = BodyLabel(f"Passed: {summary['passed']}")
        if isDarkTheme():
            passed_label.setStyleSheet("color: #58d68d;")
        else:
            passed_label.setStyleSheet("color: #27ae60;")
        layout.addWidget(passed_label)

        failed_label = BodyLabel(f"Failed: {summary['failed']}")
        if isDarkTheme():
            failed_label.setStyleSheet("color: #f8c471;")
        else:
            failed_label.setStyleSheet("color: #f39c12;")
        layout.addWidget(failed_label)

        # Pass rate
        pass_rate_label = BodyLabel(f"Pass Rate: {summary['pass_rate']:.1f}%")
        layout.addWidget(pass_rate_label)

        layout.addStretch()

        return widget

    def _create_results_table(self) -> TableWidget:
        """Create detailed results table."""
        table = TableWidget()

        # Define columns
        columns = [
            "Ticket #",
            "FS ID",
            "Subject",
            "Priority",
            "Type",
            "Category",
            "Subcategory",
            "Item",
            "Team",
            "Urgency",
            "Impact",
            "Status",
            "Notes"
        ]

        results = self.verification_results['results']

        table.setColumnCount(len(columns))
        table.setRowCount(len(results))
        table.setHorizontalHeaderLabels(columns)

        # Populate table
        for row_idx, result in enumerate(results):
            # Ticket number
            table.setItem(row_idx, 0, QTableWidgetItem(str(result['ticket_number'])))

            if result['status'] == 'NOT_FOUND':
                # Not found in Freshservice
                table.setItem(row_idx, 1, QTableWidgetItem("NOT FOUND"))
                table.setItem(row_idx, 2, QTableWidgetItem(result['subject']))
                for col in range(3, len(columns) - 2):
                    table.setItem(row_idx, col, QTableWidgetItem("-"))
                table.setItem(row_idx, 11, QTableWidgetItem("NOT FOUND"))
                table.setItem(row_idx, 12, QTableWidgetItem("-"))
            else:
                # Found - show details
                comparisons = result['comparisons']
                actual_ticket = result.get('actual', {})

                # Freshservice ID
                table.setItem(row_idx, 1, QTableWidgetItem(str(result['freshservice_id'])))

                # Subject
                table.setItem(row_idx, 2, QTableWidgetItem(result['subject']))

                # Priority (Expected → Actual)
                priority_comp = comparisons.get('priority', {})
                priority_text = self._format_comparison(priority_comp)
                table.setItem(row_idx, 3, QTableWidgetItem(priority_text))

                # Type (Expected → Actual)
                type_comp = comparisons.get('type', {})
                type_text = self._format_comparison(type_comp)
                table.setItem(row_idx, 4, QTableWidgetItem(type_text))

                # Category
                cat_comp = comparisons.get('category', {})
                cat_text = self._format_comparison(cat_comp)
                table.setItem(row_idx, 5, QTableWidgetItem(cat_text))

                # Subcategory
                subcat_comp = comparisons.get('sub_category', {})
                subcat_text = self._format_comparison(subcat_comp)
                table.setItem(row_idx, 6, QTableWidgetItem(subcat_text))

                # Item
                item_comp = comparisons.get('item', {})
                item_text = self._format_comparison(item_comp)
                table.setItem(row_idx, 7, QTableWidgetItem(item_text))

                # Team (Group)
                group_comp = comparisons.get('group', {})
                group_text = self._format_comparison(group_comp)
                table.setItem(row_idx, 8, QTableWidgetItem(group_text))

                # Urgency
                urgency_comp = comparisons.get('urgency', {})
                urgency_text = self._format_comparison(urgency_comp)
                table.setItem(row_idx, 9, QTableWidgetItem(urgency_text))

                # Impact
                impact_comp = comparisons.get('impact', {})
                impact_text = self._format_comparison(impact_comp)
                table.setItem(row_idx, 10, QTableWidgetItem(impact_text))

                # Overall Status
                overall = result['overall_result']
                if overall == 'PASS':
                    status_text = "✓ PASS"
                elif overall == 'FAIL':
                    match_count = result['match_count']
                    mismatch_count = result['mismatch_count']
                    status_text = f"✗ FAIL ({match_count} match, {mismatch_count} mismatch)"
                else:
                    status_text = overall
                table.setItem(row_idx, 11, QTableWidgetItem(status_text))

                # Notes (from Freshservice ticket)
                notes = self._get_ticket_notes(actual_ticket)
                table.setItem(row_idx, 12, QTableWidgetItem(notes))

        # Adjust column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Ticket #
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # FS ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Subject
        for col in range(3, 11):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(12, QHeaderView.ResizeMode.Stretch)           # Notes

        # Enable sorting
        table.setSortingEnabled(True)

        return table

    def _format_comparison(self, comparison: Dict) -> str:
        """
        Format expected vs actual comparison.

        Args:
            comparison: Comparison dict with 'expected', 'actual', 'match' keys

        Returns:
            Formatted string showing comparison
        """
        if not comparison:
            return "-"

        expected = comparison.get('expected', 'N/A')
        actual = comparison.get('actual', 'N/A')
        match = comparison.get('match')

        # If match is None, just show actual (discovery mode)
        if match is None:
            return str(actual)

        # Show expected → actual with indicator
        if match:
            return f"✓ {actual}"
        else:
            return f"✗ {expected} → {actual}"

    def _get_ticket_notes(self, actual_ticket: Dict) -> str:
        """
        Extract notes from Freshservice ticket.

        Args:
            actual_ticket: Actual Freshservice ticket data

        Returns:
            Notes text or "-" if no notes
        """
        # Check for common note fields in Freshservice API
        description = actual_ticket.get('description_text', '')
        notes = actual_ticket.get('notes', [])

        if notes and len(notes) > 0:
            # Return first note
            return notes[0].get('body_text', '-')
        elif description:
            # Return truncated description if no notes
            return description[:100] + "..." if len(description) > 100 else description
        else:
            return "-"
