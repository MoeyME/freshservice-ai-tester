"""
Activity Log widget for tracking operations in real-time.
"""

from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PySide6.QtGui import QTextCursor
from qfluentwidgets import (
    ElevatedCardWidget, SubtitleLabel, TextEdit, CaptionLabel,
    PushButton, FluentIcon, isDarkTheme
)


class ActivityLogWidget(ElevatedCardWidget):
    """
    Activity log widget for displaying operation progress and status.

    Signals:
        clear_log_clicked: Emitted when clear log button clicked
    """

    clear_log_clicked = Signal()

    def __init__(self, parent: QWidget = None):
        """
        Initialize activity log widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.setMinimumHeight(300)  # Minimum to show content, allows expansion

        # Create UI
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header with clear button
        header_row = QVBoxLayout()
        header_label = SubtitleLabel("Activity Log")
        header_row.addWidget(header_label)

        self.status_label = CaptionLabel("Ready")
        self._update_status_style("#27ae60")
        header_row.addWidget(self.status_label)

        layout.addLayout(header_row)

        # Log text area (read-only)
        self.log_text = TextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Activity will appear here...")
        self.log_text.setStyleSheet("""
            TextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                background-color: palette(base);
                border: 1px solid palette(mid);
            }
        """)
        layout.addWidget(self.log_text, 1)

        # Clear button
        self.clear_button = PushButton("Clear Log")
        self.clear_button.setIcon(FluentIcon.DELETE)
        self.clear_button.setFixedHeight(28)
        self.clear_button.clicked.connect(self.clear_log)
        layout.addWidget(self.clear_button)

    def add_log(self, message: str, level: str = "info"):
        """
        Add a log entry.

        Args:
            message: Log message
            level: Log level (info, success, warning, error)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color code by level - use brighter colors for dark mode
        if isDarkTheme():
            colors = {
                "info": "#5dade2",      # Lighter blue
                "success": "#58d68d",   # Lighter green
                "warning": "#f8c471",   # Lighter orange
                "error": "#ec7063"      # Lighter red
            }
        else:
            colors = {
                "info": "#3498db",
                "success": "#27ae60",
                "warning": "#f39c12",
                "error": "#e74c3c"
            }
        color = colors.get(level, colors["info"])

        # Format entry
        entry = f'<span style="color: {color};">[{timestamp}]</span> {message}<br>'

        # Append to log
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
        self.log_text.insertHtml(entry)
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)

    def add_info(self, message: str):
        """Add info log entry."""
        self.add_log(message, "info")

    def add_success(self, message: str):
        """Add success log entry."""
        self.add_log(message, "success")

    def add_warning(self, message: str):
        """Add warning log entry."""
        self.add_log(message, "warning")

    def add_error(self, message: str):
        """Add error log entry."""
        self.add_log(message, "error")

    def set_status(self, status: str, level: str = "info"):
        """
        Update status label.

        Args:
            status: Status text
            level: Status level (info, success, warning, error, busy)
        """
        self.status_label.setText(status)

        if isDarkTheme():
            colors = {
                "info": "#5dade2",
                "success": "#58d68d",
                "warning": "#f8c471",
                "error": "#ec7063",
                "busy": "#bb8fce"
            }
        else:
            colors = {
                "info": "#3498db",
                "success": "#27ae60",
                "warning": "#f39c12",
                "error": "#e74c3c",
                "busy": "#9b59b6"
            }
        color = colors.get(level, colors["info"])
        self._update_status_style(color)

    def _update_status_style(self, color: str):
        """Update status label style with given color."""
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def clear_log(self):
        """Clear all log entries."""
        self.log_text.clear()
        self.add_info("Log cleared")
        self.set_status("Ready", "info")

    def refresh_theme(self):
        """Refresh colors after theme change."""
        # Re-apply current status color
        current_text = self.status_label.text()
        # Extract level from current style (default to info if can't determine)
        self.set_status(current_text, "info")
