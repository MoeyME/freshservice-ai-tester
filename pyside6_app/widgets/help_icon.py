"""
Help icon component with flyout tooltip.
"""

from PySide6.QtWidgets import QWidget
from qfluentwidgets import TransparentToolButton, FluentIcon, Flyout, FlyoutViewBase, InfoBarIcon


class HelpFlyoutView(FlyoutViewBase):
    """Custom flyout view for help content."""

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QVBoxLayout
        from qfluentwidgets import SubtitleLabel, BodyLabel

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title_label = SubtitleLabel(title)
        layout.addWidget(title_label)

        # Content
        content_label = BodyLabel(content)
        content_label.setWordWrap(True)
        content_label.setMaximumWidth(300)
        layout.addWidget(content_label)


class HelpIcon(TransparentToolButton):
    """
    Small help icon that shows a flyout with detailed help text on click.

    Usage:
        help_icon = HelpIcon(
            help_text="Detailed explanation of this field...",
            title="Field Name Help"
        )
    """

    def __init__(self, help_text: str, title: str = "Help", parent: QWidget = None):
        """
        Initialize help icon.

        Args:
            help_text: The detailed help text to show in the flyout
            title: The title of the flyout
            parent: Parent widget
        """
        super().__init__(FluentIcon.QUESTION, parent)
        self.setFixedSize(20, 20)
        self.help_text = help_text
        self.title = title
        self.clicked.connect(self._show_flyout)
        self.setToolTip("Click for more information")

    def _show_flyout(self):
        """Show the help flyout."""
        view = HelpFlyoutView(self.title, self.help_text)
        Flyout.make(view, self, self.window())
