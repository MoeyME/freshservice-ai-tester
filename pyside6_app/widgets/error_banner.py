"""
Persistent error banner with retry and dismiss actions.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import (
    BodyLabel, PushButton, TransparentToolButton,
    FluentIcon, isDarkTheme
)


class ErrorBanner(QWidget):
    """
    Persistent error banner with retry and dismiss actions.

    Displayed at the top of a section to indicate an error occurred.
    Includes an optional retry button for recoverable errors.

    Signals:
        retry_clicked: Emitted when retry button is clicked
        dismiss_clicked: Emitted when dismiss button is clicked
    """

    retry_clicked = Signal()
    dismiss_clicked = Signal()

    def __init__(self, parent: QWidget = None):
        """
        Initialize error banner.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._update_style()
        self.setVisible(False)

    def _setup_ui(self):
        """Set up the UI components."""
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # Error icon
        self._icon_label = BodyLabel("\u26a0")  # Warning triangle
        self._icon_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self._icon_label)

        # Message
        self._message_label = BodyLabel("")
        self._message_label.setWordWrap(True)
        layout.addWidget(self._message_label, 1)

        # Retry button
        self._retry_button = PushButton("Retry")
        self._retry_button.setIcon(FluentIcon.SYNC)
        self._retry_button.setToolTip("Retry the failed operation")
        self._retry_button.clicked.connect(self._on_retry)
        layout.addWidget(self._retry_button)

        # Dismiss button
        self._dismiss_button = TransparentToolButton(FluentIcon.CLOSE)
        self._dismiss_button.setFixedSize(32, 32)
        self._dismiss_button.setToolTip("Dismiss this error")
        self._dismiss_button.clicked.connect(self._on_dismiss)
        layout.addWidget(self._dismiss_button)

    def _update_style(self):
        """Update styling based on current theme."""
        if isDarkTheme():
            bg = "#4a1c1c"
            border = "#8b3a3a"
            text = "#f5b7b1"
        else:
            bg = "#fdeaea"
            border = "#e74c3c"
            text = "#922b21"

        self.setStyleSheet(f"""
            ErrorBanner {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 4px;
            }}
        """)
        self._message_label.setStyleSheet(f"color: {text};")

    def show_error(self, message: str, retryable: bool = True):
        """
        Show error banner with message.

        Args:
            message: Error message to display
            retryable: Whether to show retry button
        """
        self._message_label.setText(message)
        self._retry_button.setVisible(retryable)
        self._retry_button.setEnabled(True)
        self._update_style()
        self.setVisible(True)

    def show_warning(self, message: str, retryable: bool = False):
        """
        Show warning banner with message.

        Args:
            message: Warning message to display
            retryable: Whether to show retry button
        """
        if isDarkTheme():
            bg = "#4a3c1c"
            border = "#8b7a3a"
            text = "#f5e7b1"
        else:
            bg = "#fef9e7"
            border = "#f39c12"
            text = "#9a7d0a"

        self.setStyleSheet(f"""
            ErrorBanner {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 4px;
            }}
        """)
        self._message_label.setStyleSheet(f"color: {text};")
        self._icon_label.setText("\u26a0")  # Warning triangle

        self._message_label.setText(message)
        self._retry_button.setVisible(retryable)
        self._retry_button.setEnabled(True)
        self.setVisible(True)

    def hide_banner(self):
        """Hide the error banner."""
        self.setVisible(False)

    def _on_retry(self):
        """Handle retry button click."""
        self._retry_button.setEnabled(False)
        self._retry_button.setText("Retrying...")
        self.setVisible(False)
        self.retry_clicked.emit()
        # Reset button state for next time
        self._retry_button.setEnabled(True)
        self._retry_button.setText("Retry")

    def _on_dismiss(self):
        """Handle dismiss button click."""
        self.setVisible(False)
        self.dismiss_clicked.emit()

    def refresh_theme(self):
        """Refresh styling when theme changes."""
        if self.isVisible():
            self._update_style()
