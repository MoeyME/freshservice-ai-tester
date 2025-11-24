"""
Validated input widgets with inline validation feedback.
"""

from typing import Callable, Tuple, Optional
from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    LineEdit, PasswordLineEdit, CaptionLabel, TransparentToolButton,
    FluentIcon, isDarkTheme
)


class ValidatedLineEdit(QWidget):
    """
    LineEdit with inline validation feedback.

    Shows visual feedback:
    - Neutral (default): No styling
    - Valid: Green border + checkmark
    - Invalid: Red border + error message below

    Validation is debounced by 300ms to avoid rapid updates.
    """

    textChanged = Signal(str)
    validationChanged = Signal(bool, str)  # is_valid, error_message

    def __init__(
        self,
        validator: Callable[[str], Tuple[bool, str]],
        placeholder: str = "",
        tooltip: str = "",
        parent: QWidget = None
    ):
        """
        Initialize validated line edit.

        Args:
            validator: Function that takes text and returns (is_valid, error_message)
            placeholder: Placeholder text
            tooltip: Tooltip text
            parent: Parent widget
        """
        super().__init__(parent)
        self._validator = validator
        self._is_valid = True
        self._has_been_edited = False
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._do_validate)

        self._setup_ui(placeholder, tooltip)

    def _setup_ui(self, placeholder: str, tooltip: str):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(4)

        self._input = LineEdit()
        self._input.setPlaceholderText(placeholder)
        if tooltip:
            self._input.setToolTip(tooltip)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.editingFinished.connect(self._on_editing_finished)
        input_row.addWidget(self._input)

        self._status_icon = CaptionLabel("")
        self._status_icon.setFixedWidth(20)
        input_row.addWidget(self._status_icon)

        layout.addLayout(input_row)

        # Error label
        self._error_label = CaptionLabel("")
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        self._update_error_style()
        layout.addWidget(self._error_label)

    def _update_error_style(self):
        """Update error label style based on theme."""
        if isDarkTheme():
            self._error_label.setStyleSheet("color: #ec7063; font-size: 11px;")
        else:
            self._error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")

    def text(self) -> str:
        """Get current text."""
        return self._input.text()

    def setText(self, text: str):
        """Set text value."""
        self._input.setText(text)

    def setPlaceholderText(self, text: str):
        """Set placeholder text."""
        self._input.setPlaceholderText(text)

    def setToolTip(self, text: str):
        """Set tooltip."""
        self._input.setToolTip(text)

    def clear(self):
        """Clear the input."""
        self._input.clear()
        self._set_state("neutral")

    def setEnabled(self, enabled: bool):
        """Enable or disable the input."""
        self._input.setEnabled(enabled)

    def setFocus(self):
        """Set focus to the input."""
        self._input.setFocus()

    def _on_text_changed(self, text: str):
        """Handle text change."""
        self.textChanged.emit(text)
        # Debounce validation to avoid rapid updates
        self._debounce_timer.start(300)

    def _on_editing_finished(self):
        """Handle editing finished (focus lost or Enter pressed)."""
        self._has_been_edited = True
        self._do_validate()

    def _do_validate(self):
        """Perform validation."""
        text = self._input.text()

        if not text:
            # Empty - neutral state
            self._set_state("neutral")
            self._is_valid = True
            return

        is_valid, error = self._validator(text)
        self._is_valid = is_valid

        if is_valid:
            self._set_state("valid")
        elif self._has_been_edited:
            self._set_state("invalid", error)

        self.validationChanged.emit(is_valid, error)

    def _set_state(self, state: str, error: str = ""):
        """
        Set visual state.

        Args:
            state: One of "valid", "invalid", or "neutral"
            error: Error message to display (for invalid state)
        """
        if isDarkTheme():
            valid_color = "#58d68d"
            invalid_color = "#ec7063"
        else:
            valid_color = "#27ae60"
            invalid_color = "#e74c3c"

        if state == "valid":
            self._input.setStyleSheet(f"LineEdit {{ border: 1px solid {valid_color}; }}")
            self._status_icon.setText("\u2713")  # Checkmark
            self._status_icon.setStyleSheet(f"color: {valid_color};")
            self._error_label.setVisible(False)
        elif state == "invalid":
            self._input.setStyleSheet(f"LineEdit {{ border: 1px solid {invalid_color}; }}")
            self._status_icon.setText("\u2717")  # X mark
            self._status_icon.setStyleSheet(f"color: {invalid_color};")
            self._error_label.setText(error)
            self._update_error_style()
            self._error_label.setVisible(True)
        else:  # neutral
            self._input.setStyleSheet("")
            self._status_icon.setText("")
            self._error_label.setVisible(False)

    def is_valid(self) -> bool:
        """Check if current input is valid."""
        return self._is_valid

    def force_validate(self) -> bool:
        """Force validation and return result."""
        self._has_been_edited = True
        self._do_validate()
        return self._is_valid


class ValidatedPasswordEdit(QWidget):
    """
    PasswordLineEdit with validation and visibility toggle.

    Same features as ValidatedLineEdit but with password masking
    and a toggle button to show/hide the password.
    """

    textChanged = Signal(str)
    validationChanged = Signal(bool, str)  # is_valid, error_message

    def __init__(
        self,
        validator: Callable[[str], Tuple[bool, str]],
        placeholder: str = "",
        tooltip: str = "",
        parent: QWidget = None
    ):
        """
        Initialize validated password edit.

        Args:
            validator: Function that takes text and returns (is_valid, error_message)
            placeholder: Placeholder text
            tooltip: Tooltip text
            parent: Parent widget
        """
        super().__init__(parent)
        self._validator = validator
        self._is_valid = True
        self._has_been_edited = False
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._do_validate)

        self._setup_ui(placeholder, tooltip)

    def _setup_ui(self, placeholder: str, tooltip: str):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(4)

        self._input = PasswordLineEdit()
        self._input.setPlaceholderText(placeholder)
        if tooltip:
            self._input.setToolTip(tooltip)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.editingFinished.connect(self._on_editing_finished)
        input_row.addWidget(self._input)

        # Visibility toggle
        self._toggle_button = TransparentToolButton(FluentIcon.VIEW)
        self._toggle_button.setFixedSize(32, 32)
        self._toggle_button.setToolTip("Show/hide value")
        self._toggle_button.clicked.connect(self._toggle_visibility)
        input_row.addWidget(self._toggle_button)

        self._status_icon = CaptionLabel("")
        self._status_icon.setFixedWidth(20)
        input_row.addWidget(self._status_icon)

        layout.addLayout(input_row)

        # Error label
        self._error_label = CaptionLabel("")
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)
        self._update_error_style()
        layout.addWidget(self._error_label)

    def _update_error_style(self):
        """Update error label style based on theme."""
        if isDarkTheme():
            self._error_label.setStyleSheet("color: #ec7063; font-size: 11px;")
        else:
            self._error_label.setStyleSheet("color: #e74c3c; font-size: 11px;")

    def _toggle_visibility(self):
        """Toggle password visibility."""
        if self._input.echoMode() == LineEdit.EchoMode.Password:
            self._input.setEchoMode(LineEdit.EchoMode.Normal)
            self._toggle_button.setIcon(FluentIcon.HIDE)
            self._toggle_button.setToolTip("Hide value")
        else:
            self._input.setEchoMode(LineEdit.EchoMode.Password)
            self._toggle_button.setIcon(FluentIcon.VIEW)
            self._toggle_button.setToolTip("Show value")

    def text(self) -> str:
        """Get current text."""
        return self._input.text()

    def setText(self, text: str):
        """Set text value."""
        self._input.setText(text)

    def setPlaceholderText(self, text: str):
        """Set placeholder text."""
        self._input.setPlaceholderText(text)

    def setToolTip(self, text: str):
        """Set tooltip."""
        self._input.setToolTip(text)

    def clear(self):
        """Clear the input."""
        self._input.clear()
        self._set_state("neutral")

    def setEnabled(self, enabled: bool):
        """Enable or disable the input."""
        self._input.setEnabled(enabled)
        self._toggle_button.setEnabled(enabled)

    def setFocus(self):
        """Set focus to the input."""
        self._input.setFocus()

    def _on_text_changed(self, text: str):
        """Handle text change."""
        self.textChanged.emit(text)
        # Debounce validation to avoid rapid updates
        self._debounce_timer.start(300)

    def _on_editing_finished(self):
        """Handle editing finished (focus lost or Enter pressed)."""
        self._has_been_edited = True
        self._do_validate()

    def _do_validate(self):
        """Perform validation."""
        text = self._input.text()

        if not text:
            # Empty - neutral state
            self._set_state("neutral")
            self._is_valid = True
            return

        is_valid, error = self._validator(text)
        self._is_valid = is_valid

        if is_valid:
            self._set_state("valid")
        elif self._has_been_edited:
            self._set_state("invalid", error)

        self.validationChanged.emit(is_valid, error)

    def _set_state(self, state: str, error: str = ""):
        """
        Set visual state.

        Args:
            state: One of "valid", "invalid", or "neutral"
            error: Error message to display (for invalid state)
        """
        if isDarkTheme():
            valid_color = "#58d68d"
            invalid_color = "#ec7063"
        else:
            valid_color = "#27ae60"
            invalid_color = "#e74c3c"

        if state == "valid":
            self._input.setStyleSheet(f"PasswordLineEdit {{ border: 1px solid {valid_color}; }}")
            self._status_icon.setText("\u2713")  # Checkmark
            self._status_icon.setStyleSheet(f"color: {valid_color};")
            self._error_label.setVisible(False)
        elif state == "invalid":
            self._input.setStyleSheet(f"PasswordLineEdit {{ border: 1px solid {invalid_color}; }}")
            self._status_icon.setText("\u2717")  # X mark
            self._status_icon.setStyleSheet(f"color: {invalid_color};")
            self._error_label.setText(error)
            self._update_error_style()
            self._error_label.setVisible(True)
        else:  # neutral
            self._input.setStyleSheet("")
            self._status_icon.setText("")
            self._error_label.setVisible(False)

    def is_valid(self) -> bool:
        """Check if current input is valid."""
        return self._is_valid

    def force_validate(self) -> bool:
        """Force validation and return result."""
        self._has_been_edited = True
        self._do_validate()
        return self._is_valid
