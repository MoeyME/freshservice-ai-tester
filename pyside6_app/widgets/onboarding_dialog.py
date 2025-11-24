"""
First-run onboarding wizard dialog.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QStackedWidget, QWidget
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CaptionLabel, PushButton,
    PrimaryPushButton
)


class OnboardingDialog(QDialog):
    """
    First-run onboarding wizard.

    Guides users through initial setup with a multi-page wizard:
    1. Welcome page
    2. Microsoft 365 setup instructions
    3. Claude AI setup instructions
    4. Freshservice setup (optional)
    5. Ready to start summary
    """

    def __init__(self, parent=None):
        """
        Initialize onboarding dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Welcome to IT Ticket Email Generator")
        self.setFixedSize(600, 450)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Stacked pages
        self._pages = QStackedWidget()
        self._pages.addWidget(self._create_welcome_page())
        self._pages.addWidget(self._create_microsoft_page())
        self._pages.addWidget(self._create_claude_page())
        self._pages.addWidget(self._create_freshservice_page())
        self._pages.addWidget(self._create_ready_page())
        layout.addWidget(self._pages)

        # Navigation buttons
        nav_row = QHBoxLayout()

        self._back_button = PushButton("Back")
        self._back_button.clicked.connect(self._go_back)
        self._back_button.setVisible(False)
        nav_row.addWidget(self._back_button)

        nav_row.addStretch()

        self._skip_button = PushButton("Skip Setup")
        self._skip_button.setToolTip("Skip the wizard and configure manually")
        self._skip_button.clicked.connect(self.accept)
        nav_row.addWidget(self._skip_button)

        self._next_button = PrimaryPushButton("Next")
        self._next_button.clicked.connect(self._go_next)
        nav_row.addWidget(self._next_button)

        layout.addLayout(nav_row)

    def _create_welcome_page(self) -> QWidget:
        """Create the welcome page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Icon
        icon = SubtitleLabel("\U0001F4E7")  # Envelope emoji
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Title
        title = SubtitleLabel("Welcome!")
        title.setStyleSheet("font-size: 24px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = BodyLabel(
            "This tool helps you generate and send realistic IT support ticket\n"
            "test emails to validate your Freshservice categorization rules.\n\n"
            "Let's set up your connections."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        return page

    def _create_microsoft_page(self) -> QWidget:
        """Create the Microsoft 365 setup page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        # Title
        title = SubtitleLabel("1. Microsoft 365 Setup")
        layout.addWidget(title)

        # Icon
        icon = SubtitleLabel("\U0001F4BB")  # Computer emoji
        icon.setStyleSheet("font-size: 32px;")
        layout.addWidget(icon)

        # Description
        desc = BodyLabel(
            "You'll need an Azure AD app registration with Mail.Send permissions.\n\n"
            "Required information:\n"
            "\u2022 Client ID (from Azure Portal > App Registrations)\n"
            "\u2022 Tenant ID (from Azure Portal > Overview)\n"
            "\u2022 Sender email address (your work email)\n"
            "\u2022 Recipient email (Freshservice inbox)\n\n"
            "If you don't have these yet, ask your Azure administrator."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        return page

    def _create_claude_page(self) -> QWidget:
        """Create the Claude AI setup page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        # Title
        title = SubtitleLabel("2. Claude AI Setup")
        layout.addWidget(title)

        # Icon
        icon = SubtitleLabel("\U0001F916")  # Robot emoji
        icon.setStyleSheet("font-size: 32px;")
        layout.addWidget(icon)

        # Description
        desc = BodyLabel(
            "Claude AI generates realistic email content for your test tickets.\n\n"
            "To get your API key:\n"
            "1. Visit console.anthropic.com\n"
            "2. Sign up or log in\n"
            "3. Go to API Keys section\n"
            "4. Create a new key\n\n"
            "The key starts with 'sk-ant-'\n\n"
            "Cost: Approximately $0.001 per email generated."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        return page

    def _create_freshservice_page(self) -> QWidget:
        """Create the Freshservice setup page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        # Title
        title = SubtitleLabel("3. Freshservice Setup (Optional)")
        layout.addWidget(title)

        # Icon
        icon = SubtitleLabel("\U0001F3AB")  # Ticket emoji
        icon.setStyleSheet("font-size: 32px;")
        layout.addWidget(icon)

        # Description
        desc = BodyLabel(
            "Connect to Freshservice to verify that your test emails\n"
            "created properly categorized tickets.\n\n"
            "Required information:\n"
            "\u2022 Freshservice domain (yourcompany.freshservice.com)\n"
            "\u2022 API key (from Profile Settings > API)\n\n"
            "This step is optional - you can send test emails\n"
            "without verification enabled."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        return page

    def _create_ready_page(self) -> QWidget:
        """Create the ready to start page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # Icon
        icon = SubtitleLabel("\u2705")  # Checkmark emoji
        icon.setStyleSheet("font-size: 64px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Title
        title = SubtitleLabel("You're Ready!")
        title.setStyleSheet("font-size: 24px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Description
        desc = BodyLabel(
            "Fill in your credentials in the left panel, then:\n\n"
            "1. Click 'Authenticate' for Microsoft 365\n"
            "2. Set your email count and quality level\n"
            "3. Click 'Generate Draft' to create test emails\n"
            "4. Review drafts and 'Mark Ready' the ones you want\n"
            "5. Click 'Confirm & Send' to deliver them\n"
            "6. Optionally verify tickets in Freshservice"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        # Keyboard shortcuts hint
        shortcuts_hint = CaptionLabel(
            "Tip: Use Ctrl+G to generate, Ctrl+E to export"
        )
        shortcuts_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(shortcuts_hint)

        return page

    def _go_next(self):
        """Go to the next page."""
        current = self._pages.currentIndex()
        if current < self._pages.count() - 1:
            self._pages.setCurrentIndex(current + 1)
            self._back_button.setVisible(True)
            if current + 1 == self._pages.count() - 1:
                self._next_button.setText("Get Started")
                self._skip_button.setVisible(False)
        else:
            self.accept()

    def _go_back(self):
        """Go to the previous page."""
        current = self._pages.currentIndex()
        if current > 0:
            self._pages.setCurrentIndex(current - 1)
            self._next_button.setText("Next")
            self._skip_button.setVisible(True)
            if current - 1 == 0:
                self._back_button.setVisible(False)
