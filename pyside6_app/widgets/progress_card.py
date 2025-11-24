"""
Progress card with percentage, ETA, and cancel button.
"""

import time
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    SimpleCardWidget, SubtitleLabel, CaptionLabel,
    ProgressBar, PushButton, FluentIcon, isDarkTheme
)


class ProgressCard(SimpleCardWidget):
    """
    Rich progress display with percentage, ETA, and cancel button.

    Features:
    - Title label (customizable)
    - Progress bar with percentage
    - Status text (e.g., "15 of 50")
    - ETA calculation and display
    - Cancel button
    """

    cancel_clicked = Signal()

    def __init__(self, parent: QWidget = None):
        """
        Initialize progress card.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._start_time = None
        self._total = 0
        self._current = 0

        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        self._title_label = SubtitleLabel("Processing...")
        layout.addWidget(self._title_label)

        # Progress bar
        self._progress_bar = ProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)

        # Status row
        status_row = QHBoxLayout()

        self._status_label = CaptionLabel("Preparing...")
        status_row.addWidget(self._status_label)

        status_row.addStretch()

        self._eta_label = CaptionLabel("")
        status_row.addWidget(self._eta_label)

        layout.addLayout(status_row)

        # Cancel button
        self._cancel_button = PushButton("Cancel")
        self._cancel_button.setIcon(FluentIcon.CANCEL)
        self._cancel_button.setToolTip("Cancel the current operation")
        self._cancel_button.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(self._cancel_button)

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self._cancel_button.setEnabled(False)
        self._cancel_button.setText("Cancelling...")
        self.cancel_clicked.emit()

    def start_progress(self, title: str, total: int):
        """
        Start progress tracking with known total.

        Args:
            title: Title to display (e.g., "Generating Emails")
            total: Total number of items to process
        """
        self._title_label.setText(title)
        self._total = total
        self._current = 0
        self._start_time = time.time()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._status_label.setText(f"0 of {total}")
        self._eta_label.setText("Calculating...")
        self._cancel_button.setEnabled(True)
        self._cancel_button.setText("Cancel")
        self.setVisible(True)

    def update_progress(self, current: int, status_text: str = None):
        """
        Update progress display.

        Args:
            current: Current progress count
            status_text: Optional custom status text
        """
        if self._total <= 0:
            return

        self._current = current
        percentage = int((current / self._total) * 100)
        self._progress_bar.setValue(percentage)

        if status_text:
            self._status_label.setText(status_text)
        else:
            self._status_label.setText(f"{current} of {self._total}")

        # Calculate ETA
        if current > 0 and self._start_time:
            elapsed = time.time() - self._start_time
            rate = current / elapsed
            remaining = (self._total - current) / rate if rate > 0 else 0
            self._eta_label.setText(f"~{self._format_time(remaining)} remaining")

    def show_indeterminate(self, message: str):
        """
        Show indeterminate progress (spinner).

        Args:
            message: Message to display
        """
        self._title_label.setText(message)
        self._progress_bar.setRange(0, 0)  # Indeterminate mode
        self._status_label.setText("Please wait...")
        self._eta_label.setText("")
        self._cancel_button.setEnabled(True)
        self._cancel_button.setText("Cancel")
        self.setVisible(True)

    def complete(self, message: str = "Complete!"):
        """
        Mark progress as complete.

        Args:
            message: Completion message to display
        """
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(100)
        self._status_label.setText(message)
        self._eta_label.setText("")
        self._cancel_button.setEnabled(False)
        self._cancel_button.setText("Done")

    def hide_progress(self):
        """Hide the progress card and reset state."""
        self.setVisible(False)
        self._cancel_button.setEnabled(True)
        self._cancel_button.setText("Cancel")
        self._progress_bar.setValue(0)
        self._start_time = None

    def _format_time(self, seconds: float) -> str:
        """
        Format seconds as human-readable time.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            mins = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m"

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since progress started.

        Returns:
            Elapsed time in seconds, or 0 if not started
        """
        if self._start_time:
            return time.time() - self._start_time
        return 0

    def get_progress_percentage(self) -> int:
        """
        Get current progress percentage.

        Returns:
            Progress percentage (0-100)
        """
        if self._total <= 0:
            return 0
        return int((self._current / self._total) * 100)
