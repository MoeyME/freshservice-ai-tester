"""
Connection cards for Microsoft and Freshservice.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel
)
from qfluentwidgets import (
    ElevatedCardWidget, LineEdit, PasswordLineEdit,
    PushButton, PrimaryPushButton, TransparentToolButton,
    SubtitleLabel, CaptionLabel, InfoBadge, InfoLevel,
    FluentIcon, isDarkTheme
)

from ..state.store import StateStore
from ..utils.validators import EmailValidator, GUIDValidator, DomainValidator


class MicrosoftCard(ElevatedCardWidget):
    """
    Microsoft 365 connection card.

    Signals:
        authenticate_clicked: Emitted when authenticate button clicked
    """

    authenticate_clicked = Signal()

    def __init__(self, state_store: StateStore, parent: QWidget = None):
        """
        Initialize Microsoft card.

        Args:
            state_store: Application state store
            parent: Parent widget
        """
        super().__init__(parent)
        self.state_store = state_store

        self.setMinimumHeight(380)  # Minimum to show content, allows expansion

        # Create UI
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = SubtitleLabel("Microsoft 365 (Graph)")
        layout.addWidget(header)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setHorizontalSpacing(12)

        # Client ID
        client_id_row = QHBoxLayout()
        self.client_id_input = PasswordLineEdit()
        self.client_id_input.setPlaceholderText("Enter Client ID (GUID)")
        self.client_id_input.setToolTip("Azure AD Application (Client) ID - Found in Azure Portal > App Registrations")
        self.client_id_toggle = TransparentToolButton(FluentIcon.VIEW)
        self.client_id_toggle.setFixedSize(32, 32)
        self.client_id_toggle.setToolTip("Show/hide Client ID")
        client_id_row.addWidget(self.client_id_input)
        client_id_row.addWidget(self.client_id_toggle)
        form_layout.addRow(CaptionLabel("Client ID:"), client_id_row)

        # Tenant ID
        self.tenant_id_input = LineEdit()
        self.tenant_id_input.setPlaceholderText("Enter Tenant ID (GUID)")
        self.tenant_id_input.setToolTip("Azure AD Directory (Tenant) ID - Found in Azure Portal > Overview")
        form_layout.addRow(CaptionLabel("Tenant ID:"), self.tenant_id_input)

        # Sender Email
        self.sender_email_input = LineEdit()
        self.sender_email_input.setPlaceholderText("sender@example.com")
        self.sender_email_input.setToolTip("Email address to send test tickets from (must have Mail.Send permission)")
        form_layout.addRow(CaptionLabel("Sender:"), self.sender_email_input)

        # Recipient Email
        self.recipient_email_input = LineEdit()
        self.recipient_email_input.setPlaceholderText("recipient@example.com")
        self.recipient_email_input.setToolTip("Freshservice inbox email that creates tickets")
        form_layout.addRow(CaptionLabel("Recipient:"), self.recipient_email_input)

        # Claude API Key
        claude_key_row = QHBoxLayout()
        self.claude_key_input = PasswordLineEdit()
        self.claude_key_input.setPlaceholderText("sk-ant-...")
        self.claude_key_input.setToolTip("Anthropic API key starting with 'sk-ant-' - Get one at console.anthropic.com")
        self.claude_key_toggle = TransparentToolButton(FluentIcon.VIEW)
        self.claude_key_toggle.setFixedSize(32, 32)
        self.claude_key_toggle.setToolTip("Show/hide API key")
        claude_key_row.addWidget(self.claude_key_input)
        claude_key_row.addWidget(self.claude_key_toggle)
        form_layout.addRow(CaptionLabel("Claude Key:"), claude_key_row)

        layout.addLayout(form_layout)

        # Auth button and status
        auth_row = QHBoxLayout()
        self.auth_button = PrimaryPushButton("Authenticate")
        self.auth_button.setFixedHeight(36)
        self.auth_button.setToolTip("Open Microsoft OAuth flow in browser")
        auth_row.addWidget(self.auth_button)

        self.auth_status_badge = InfoBadge.error("Not Connected", self)
        self.auth_status_badge.setVisible(True)
        auth_row.addWidget(self.auth_status_badge)

        self.token_expiry_label = CaptionLabel("")
        self.token_expiry_label.setVisible(False)
        auth_row.addWidget(self.token_expiry_label)

        auth_row.addStretch()

        layout.addLayout(auth_row)

        # Load initial state
        self._load_from_state()

        # Connect signals
        self._init_connections()

    def _init_connections(self):
        """Initialize signal connections."""
        # Input changes -> update state
        self.client_id_input.textChanged.connect(self._on_client_id_changed)
        self.tenant_id_input.textChanged.connect(self._on_tenant_id_changed)
        self.sender_email_input.textChanged.connect(self._on_sender_email_changed)
        self.recipient_email_input.textChanged.connect(self._on_recipient_email_changed)
        self.claude_key_input.textChanged.connect(self._on_claude_key_changed)

        # Toggle visibility
        self.client_id_toggle.clicked.connect(self._toggle_client_id)
        self.claude_key_toggle.clicked.connect(self._toggle_claude_key)

        # Auth button
        self.auth_button.clicked.connect(self.authenticate_clicked.emit)

        # State changes
        self.state_store.connections_changed.connect(self._on_state_changed)

    def _load_from_state(self):
        """Load values from state."""
        ms = self.state_store.state.connections.microsoft

        self.client_id_input.setText(ms.client_id)
        self.tenant_id_input.setText(ms.tenant_id)
        self.sender_email_input.setText(str(ms.sender_email) if ms.sender_email else "")
        self.recipient_email_input.setText(str(ms.recipient_email) if ms.recipient_email else "")

        # Load Claude API key from secure storage
        claude_key = self.state_store.get_secret('claude_api_key')
        if claude_key:
            self.claude_key_input.setText(claude_key)

        # Update auth status
        self._update_auth_status()

    def _update_auth_status(self):
        """Update authentication status badge."""
        ms = self.state_store.state.connections.microsoft

        if ms.is_authenticated:
            self.auth_status_badge.setLevel(InfoLevel.SUCCESS)
            self.auth_status_badge.setText("Connected")
            self.auth_button.setText("Sign Out")

            if ms.token_expiry:
                self.token_expiry_label.setText(f"Expires: {ms.token_expiry.strftime('%H:%M')}")
                self.token_expiry_label.setVisible(True)
        else:
            self.auth_status_badge.setLevel(InfoLevel.ERROR)
            self.auth_status_badge.setText("Not Connected")
            self.auth_button.setText("Authenticate")
            self.token_expiry_label.setVisible(False)

    def _on_client_id_changed(self, text: str):
        """Handle client ID change."""
        # Validate
        is_valid, error = GUIDValidator.validate(text) if text else (True, "")

        if is_valid:
            self.state_store.update_connections(
                lambda s: setattr(s.connections.microsoft, 'client_id', text)
            )

    def _on_tenant_id_changed(self, text: str):
        """Handle tenant ID change."""
        is_valid, error = GUIDValidator.validate(text) if text else (True, "")

        if is_valid:
            self.state_store.update_connections(
                lambda s: setattr(s.connections.microsoft, 'tenant_id', text)
            )

    def _on_sender_email_changed(self, text: str):
        """Handle sender email change."""
        is_valid, error = EmailValidator.validate(text) if text else (True, "")

        if is_valid:
            self.state_store.update_connections(
                lambda s: setattr(s.connections.microsoft, 'sender_email', text)
            )

    def _on_recipient_email_changed(self, text: str):
        """Handle recipient email change."""
        is_valid, error = EmailValidator.validate(text) if text else (True, "")

        if is_valid:
            self.state_store.update_connections(
                lambda s: setattr(s.connections.microsoft, 'recipient_email', text)
            )

    def _on_claude_key_changed(self, text: str):
        """Handle Claude API key change."""
        # Store full key in secure memory
        if text:
            self.state_store.set_secret('claude_api_key', text)

        # Store only last 4 characters in state
        if len(text) >= 4:
            last_four = text[-4:]
            self.state_store.update_connections(
                lambda s: setattr(s.connections.claude, 'api_key_last_four', last_four)
            )
            self.state_store.update_connections(
                lambda s: setattr(s.connections.claude, 'is_configured', True)
            )

    def _toggle_client_id(self):
        """Toggle Client ID visibility."""
        if self.client_id_input.echoMode() == LineEdit.EchoMode.Password:
            self.client_id_input.setEchoMode(LineEdit.EchoMode.Normal)
            self.client_id_toggle.setIcon(FluentIcon.HIDE)
        else:
            self.client_id_input.setEchoMode(LineEdit.EchoMode.Password)
            self.client_id_toggle.setIcon(FluentIcon.VIEW)

    def _toggle_claude_key(self):
        """Toggle Claude Key visibility."""
        if self.claude_key_input.echoMode() == LineEdit.EchoMode.Password:
            self.claude_key_input.setEchoMode(LineEdit.EchoMode.Normal)
            self.claude_key_toggle.setIcon(FluentIcon.HIDE)
        else:
            self.claude_key_input.setEchoMode(LineEdit.EchoMode.Password)
            self.claude_key_toggle.setIcon(FluentIcon.VIEW)

    def _on_state_changed(self, connections):
        """Handle state changes."""
        self._update_auth_status()
        self._update_card_border()

    def _update_card_border(self):
        """Update card border based on connection state."""
        ms = self.state_store.state.connections.microsoft

        if ms.is_authenticated:
            color = "#27ae60" if not isDarkTheme() else "#58d68d"  # Green
        else:
            color = "transparent"

        self.setStyleSheet(f"""
            MicrosoftCard {{
                border-left: 3px solid {color};
            }}
        """)

    def set_accessibility_names(self):
        """Set accessibility names for screen readers."""
        self.client_id_input.setAccessibleName("Microsoft Client ID")
        self.client_id_input.setAccessibleDescription("Enter your Azure AD Application Client ID in GUID format")
        self.tenant_id_input.setAccessibleName("Microsoft Tenant ID")
        self.tenant_id_input.setAccessibleDescription("Enter your Azure AD Directory Tenant ID in GUID format")
        self.sender_email_input.setAccessibleName("Sender email address")
        self.sender_email_input.setAccessibleDescription("Email address to send test tickets from")
        self.recipient_email_input.setAccessibleName("Recipient email address")
        self.recipient_email_input.setAccessibleDescription("Freshservice inbox email that creates tickets")
        self.claude_key_input.setAccessibleName("Claude API key")
        self.claude_key_input.setAccessibleDescription("Anthropic API key for content generation")
        self.auth_button.setAccessibleName("Authenticate with Microsoft")
        self.auth_button.setAccessibleDescription("Opens browser for Microsoft OAuth login")


class FreshserviceCard(ElevatedCardWidget):
    """
    Freshservice connection card.

    Signals:
        test_connection_clicked: Emitted when test button clicked
    """

    test_connection_clicked = Signal()

    def __init__(self, state_store: StateStore, parent: QWidget = None):
        """
        Initialize Freshservice card.

        Args:
            state_store: Application state store
            parent: Parent widget
        """
        super().__init__(parent)
        self.state_store = state_store

        self.setMinimumHeight(220)  # Minimum to show content, allows expansion

        # Create UI
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = SubtitleLabel("Freshservice")
        layout.addWidget(header)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setHorizontalSpacing(12)

        # Domain
        self.domain_input = LineEdit()
        self.domain_input.setPlaceholderText("yourcompany.freshservice.com")
        self.domain_input.setToolTip("Your Freshservice subdomain (e.g., yourcompany.freshservice.com)")
        form_layout.addRow(CaptionLabel("Domain:"), self.domain_input)

        # API Key
        api_key_row = QHBoxLayout()
        self.api_key_input = PasswordLineEdit()
        self.api_key_input.setPlaceholderText("Enter API Key")
        self.api_key_input.setToolTip("Freshservice API key - Found in Profile Settings > API")
        self.api_key_toggle = TransparentToolButton(FluentIcon.VIEW)
        self.api_key_toggle.setFixedSize(32, 32)
        self.api_key_toggle.setToolTip("Show/hide API key")
        api_key_row.addWidget(self.api_key_input)
        api_key_row.addWidget(self.api_key_toggle)
        form_layout.addRow(CaptionLabel("API Key:"), api_key_row)

        layout.addLayout(form_layout)

        # Test button and status
        test_row = QHBoxLayout()
        self.test_button = PushButton("Test Connection")
        self.test_button.setFixedHeight(36)
        self.test_button.setToolTip("Verify Freshservice connection and permissions")
        test_row.addWidget(self.test_button)

        self.status_badge = InfoBadge.attension("Not Configured", self)
        self.status_badge.setVisible(True)
        test_row.addWidget(self.status_badge)

        test_row.addStretch()

        layout.addLayout(test_row)

        # Load initial state
        self._load_from_state()

        # Connect signals
        self._init_connections()

    def _init_connections(self):
        """Initialize signal connections."""
        # Input changes -> update state
        self.domain_input.textChanged.connect(self._on_domain_changed)
        self.api_key_input.textChanged.connect(self._on_api_key_changed)

        # Toggle visibility
        self.api_key_toggle.clicked.connect(self._toggle_api_key)

        # Test button
        self.test_button.clicked.connect(self.test_connection_clicked.emit)

        # State changes
        self.state_store.connections_changed.connect(self._on_state_changed)

    def _load_from_state(self):
        """Load values from state."""
        fs = self.state_store.state.connections.freshservice

        self.domain_input.setText(fs.domain)

        # Load Freshservice API key from secure storage
        fs_key = self.state_store.get_secret('freshservice_api_key')
        if fs_key:
            self.api_key_input.setText(fs_key)

        # Update status
        self._update_status()

    def _update_status(self):
        """Update connection status badge."""
        fs = self.state_store.state.connections.freshservice

        if fs.is_connected:
            self.status_badge.setLevel(InfoLevel.SUCCESS)
            self.status_badge.setText("Connected")
        elif fs.domain and fs.api_key_last_four:
            self.status_badge.setLevel(InfoLevel.ATTENTION)
            self.status_badge.setText("Not Tested")
        else:
            self.status_badge.setLevel(InfoLevel.INFOAMTION)  # Note: typo in qfluentwidgets library
            self.status_badge.setText("Not Configured")

    def _on_domain_changed(self, text: str):
        """Handle domain change."""
        is_valid, error = DomainValidator.validate_freshservice(text) if text else (True, "")

        if is_valid:
            self.state_store.update_connections(
                lambda s: setattr(s.connections.freshservice, 'domain', text)
            )

    def _on_api_key_changed(self, text: str):
        """Handle API key change."""
        # Store full key in secure memory
        if text:
            self.state_store.set_secret('freshservice_api_key', text)

        # Store only last 4 characters in state
        if len(text) >= 4:
            last_four = text[-4:]
            self.state_store.update_connections(
                lambda s: setattr(s.connections.freshservice, 'api_key_last_four', last_four)
            )

    def _toggle_api_key(self):
        """Toggle API Key visibility."""
        if self.api_key_input.echoMode() == LineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(LineEdit.EchoMode.Normal)
            self.api_key_toggle.setIcon(FluentIcon.HIDE)
        else:
            self.api_key_input.setEchoMode(LineEdit.EchoMode.Password)
            self.api_key_toggle.setIcon(FluentIcon.VIEW)

    def _on_state_changed(self, connections):
        """Handle state changes."""
        self._update_status()
        self._update_card_border()

    def _update_card_border(self):
        """Update card border based on connection state."""
        fs = self.state_store.state.connections.freshservice

        if fs.is_connected:
            color = "#27ae60" if not isDarkTheme() else "#58d68d"  # Green
        elif fs.domain and fs.api_key_last_four:
            color = "#f39c12" if not isDarkTheme() else "#f8c471"  # Orange - not tested
        else:
            color = "transparent"

        self.setStyleSheet(f"""
            FreshserviceCard {{
                border-left: 3px solid {color};
            }}
        """)

    def set_accessibility_names(self):
        """Set accessibility names for screen readers."""
        self.domain_input.setAccessibleName("Freshservice domain")
        self.domain_input.setAccessibleDescription("Your Freshservice subdomain in format yourcompany.freshservice.com")
        self.api_key_input.setAccessibleName("Freshservice API key")
        self.api_key_input.setAccessibleDescription("API key from Freshservice Profile Settings")
        self.test_button.setAccessibleName("Test Freshservice connection")
        self.test_button.setAccessibleDescription("Verify connection to Freshservice API")
