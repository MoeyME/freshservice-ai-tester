"""
Empty state placeholder component.
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import SubtitleLabel, CaptionLabel, PushButton, isDarkTheme


class EmptyState(QWidget):
    """
    Empty state placeholder with icon, title, description, and optional action button.

    Used to show helpful guidance when a section has no content.

    Signals:
        action_clicked: Emitted when the action button is clicked
    """

    action_clicked = Signal()

    # Common icons (emoji-based for simplicity)
    ICON_MAIL = "\U0001F4E7"       # Envelope
    ICON_DOCUMENT = "\U0001F4C4"   # Document
    ICON_SEARCH = "\U0001F50D"     # Magnifying glass
    ICON_SETTINGS = "\u2699"       # Gear
    ICON_CHECK = "\u2705"          # Checkmark
    ICON_EMPTY = "\U0001F4ED"      # Empty mailbox

    def __init__(
        self,
        icon: str = ICON_EMPTY,
        title: str = "No Items",
        description: str = "There are no items to display.",
        action_text: str = None,
        parent: QWidget = None
    ):
        """
        Initialize empty state.

        Args:
            icon: Icon to display (emoji character)
            title: Title text
            description: Description text
            action_text: Optional action button text
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui(icon, title, description, action_text)

    def _setup_ui(self, icon: str, title: str, description: str, action_text: str):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Icon
        self._icon_label = SubtitleLabel(icon)
        self._icon_label.setStyleSheet("font-size: 48px;")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._icon_label)

        # Title
        self._title_label = SubtitleLabel(title)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title_label)

        # Description
        self._description_label = CaptionLabel(description)
        self._description_label.setWordWrap(True)
        self._description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description_label.setMaximumWidth(300)
        layout.addWidget(self._description_label)

        # Action button (optional)
        if action_text:
            self._action_button = PushButton(action_text)
            self._action_button.clicked.connect(self.action_clicked.emit)
            layout.addWidget(self._action_button, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            self._action_button = None

    def set_icon(self, icon: str):
        """
        Set the icon.

        Args:
            icon: Icon character to display
        """
        self._icon_label.setText(icon)

    def set_title(self, title: str):
        """
        Set the title.

        Args:
            title: Title text
        """
        self._title_label.setText(title)

    def set_description(self, description: str):
        """
        Set the description.

        Args:
            description: Description text
        """
        self._description_label.setText(description)

    def set_action_text(self, text: str):
        """
        Set or update action button text.

        Args:
            text: Button text (or None to hide button)
        """
        if text and self._action_button:
            self._action_button.setText(text)
            self._action_button.setVisible(True)
        elif text and not self._action_button:
            self._action_button = PushButton(text)
            self._action_button.clicked.connect(self.action_clicked.emit)
            self.layout().addWidget(
                self._action_button,
                alignment=Qt.AlignmentFlag.AlignCenter
            )
        elif not text and self._action_button:
            self._action_button.setVisible(False)

    def set_action_enabled(self, enabled: bool):
        """
        Enable or disable the action button.

        Args:
            enabled: Whether the button should be enabled
        """
        if self._action_button:
            self._action_button.setEnabled(enabled)
