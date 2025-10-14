"""
Main application window with frameless design and 12-column grid layout - Phase 2.
Complete with generation and review cards integrated.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QScrollArea, QSpacerItem, QSizePolicy, QFileDialog, QMenuBar, QMenu
)
from qfluentwidgets import (
    PushButton, CaptionLabel, FluentIcon, MessageBox, InfoBar, InfoBarPosition,
    setTheme, Theme, isDarkTheme
)

from ..state.store import StateStore
from ..utils.theme import ThemeManager
from ..state.models import EmailStatus, ThemeMode
from ..services.generator import GeneratorService
from ..utils.export import CSVExporter
from .connection_cards import MicrosoftCard, FreshserviceCard
from .generation_card import GenerationCard
from .review_card import ReviewCard
from .review_sheet import ReviewDetailSheet
from .activity_log import ActivityLogWidget


class MainWindow(QMainWindow):
    """
    Main application window with modern Fluent Design - Phase 2.

    Features:
    - Frameless window with acrylic background
    - 12-column responsive grid layout
    - Generation & review functionality
    - Theme toggle (light/dark)
    - Settings and help access
    """

    def __init__(self, state_store: StateStore, theme_manager: ThemeManager):
        """
        Initialize main window.

        Args:
            state_store: Application state store
            theme_manager: Theme manager
        """
        super().__init__()

        self.state_store = state_store
        self.theme_manager = theme_manager

        # Initialize generator service
        self.generator_service = GeneratorService(self)

        # Set window properties
        self.setWindowTitle("IT Ticket Email Generator")
        self.setMinimumSize(1280, 720)

        # Restore window geometry from state
        geometry = state_store.state.ui.window_geometry
        self.resize(geometry.width, geometry.height)
        self.move(geometry.x, geometry.y)

        # Initialize UI
        self._init_ui()
        self._init_connections()

        # Apply initial theme
        theme_manager.set_theme(state_store.state.ui.theme)

    def _init_ui(self):
        """Initialize the user interface."""
        # Create central widget with grid layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main grid layout (12 columns)
        main_layout = QGridLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Configure column stretches for 3-6-3 layout
        for i in range(12):
            if 0 <= i <= 2:
                main_layout.setColumnStretch(i, 1)
            elif 3 <= i <= 8:
                main_layout.setColumnStretch(i, 2)
            elif 9 <= i <= 11:
                main_layout.setColumnStretch(i, 1)

        # Row stretches
        main_layout.setRowStretch(0, 0)  # Header
        main_layout.setRowStretch(1, 1)  # Content
        main_layout.setRowStretch(2, 0)  # Footer

        # Create UI sections
        self._create_title_bar()
        self._create_left_dock(main_layout)
        self._create_center_workspace(main_layout)
        self._create_right_rail(main_layout)
        self._create_sticky_footer(main_layout)

        # Create review detail sheet (overlay)
        self.review_sheet = ReviewDetailSheet(self.state_store, self)
        self.review_sheet.setParent(central_widget)
        self.review_sheet.raise_()

    def _create_title_bar(self):
        """Create menu bar with theme toggle and settings."""
        menubar = self.menuBar()

        # View menu
        view_menu = menubar.addMenu("&View")
        theme_action = view_menu.addAction("Toggle Theme")
        theme_action.triggered.connect(self._on_theme_toggle)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        settings_action = tools_menu.addAction("Settings...")
        settings_action.triggered.connect(self._on_settings_clicked)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_action = help_menu.addAction("Documentation")
        help_action.triggered.connect(self._on_help_clicked)

    def _create_left_dock(self, layout: QGridLayout):
        """Create left dock with connection cards."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(16)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Microsoft card
        self.microsoft_card = MicrosoftCard(self.state_store, self)
        container_layout.addWidget(self.microsoft_card)

        # Freshservice card
        self.freshservice_card = FreshserviceCard(self.state_store, self)
        container_layout.addWidget(self.freshservice_card)

        # Spacer
        container_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area, 1, 0, 1, 3)

    def _create_center_workspace(self, layout: QGridLayout):
        """Create center workspace with generation and review cards."""
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(16)
        center_layout.setContentsMargins(0, 0, 0, 0)

        # Generation card
        self.generation_card = GenerationCard(self.state_store, self)
        center_layout.addWidget(self.generation_card)

        # Review card
        self.review_card = ReviewCard(self.state_store, self)
        center_layout.addWidget(self.review_card)

        layout.addWidget(center_widget, 1, 3, 1, 6)

    def _create_right_rail(self, layout: QGridLayout):
        """Create right rail with activity log."""
        # Activity log widget
        self.activity_log = ActivityLogWidget(self)
        self.activity_log.add_info("Application started")
        self.activity_log.set_status("Ready", "success")

        layout.addWidget(self.activity_log, 1, 9, 1, 3)

    def _create_sticky_footer(self, layout: QGridLayout):
        """Create sticky footer with status and primary CTA."""
        footer = QWidget()
        footer.setFixedHeight(56)
        footer.setStyleSheet("""
            QWidget {
                background-color: palette(base);
                border-top: 1px solid palette(mid);
            }
        """)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 0, 16, 0)

        # Status labels
        self.status_label = CaptionLabel("Ready")
        footer_layout.addWidget(self.status_label)

        self.drafts_count_label = CaptionLabel("Drafts: 0")
        footer_layout.addWidget(self.drafts_count_label)

        self.last_action_label = CaptionLabel("Last: None")
        footer_layout.addWidget(self.last_action_label)

        # Spacer
        footer_layout.addItem(
            QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        # Confirm & Send button (disabled by default)
        self.confirm_send_button = PushButton("Confirm & Send")
        self.confirm_send_button.setEnabled(False)
        self.confirm_send_button.setFixedWidth(140)
        footer_layout.addWidget(self.confirm_send_button)

        # Verify Tickets button (disabled by default)
        self.verify_button = PushButton("Verify Tickets")
        self.verify_button.setIcon(FluentIcon.SEARCH)
        self.verify_button.setEnabled(False)
        self.verify_button.setFixedWidth(140)
        footer_layout.addWidget(self.verify_button)

        layout.addWidget(footer, 2, 0, 1, 12)

    def _init_connections(self):
        """Initialize signal connections."""
        # State changes
        self.state_store.drafts_changed.connect(self._on_drafts_changed)
        self.state_store.connections_changed.connect(self._on_connections_changed)
        self.state_store.preflight_changed.connect(self._on_preflight_changed)

        # Theme changes
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

        # Connection card signals
        self.microsoft_card.authenticate_clicked.connect(self._on_authenticate_clicked)
        self.freshservice_card.test_connection_clicked.connect(self._on_test_connection_clicked)

        # Generation card signals
        self.generation_card.preview_clicked.connect(self._on_preview_clicked)
        self.generation_card.generate_clicked.connect(self._on_generate_clicked)
        self.generation_card.clear_clicked.connect(self._on_clear_clicked)

        # Review card signals
        self.review_card.row_clicked.connect(self._on_review_row_clicked)
        self.review_card.view_all_clicked.connect(self._on_view_all_details)
        self.review_card.export_csv_clicked.connect(self._on_export_csv)
        self.review_card.select_all_clicked.connect(self.review_card.select_all_rows)
        self.review_card.select_none_clicked.connect(self.review_card.clear_selection)
        self.review_card.mark_ready_clicked.connect(self._on_mark_ready)

        # Generator service signals
        self.generator_service.draft_generated.connect(self._on_draft_generated)
        self.generator_service.progress_updated.connect(self._on_progress_updated)
        self.generator_service.generation_complete.connect(self._on_generation_complete)
        self.generator_service.error_occurred.connect(self._on_generation_error)

        # Review sheet signals
        self.review_sheet.mark_ready_clicked.connect(self._on_mark_draft_ready)

        # Confirm send button
        self.confirm_send_button.clicked.connect(self._on_confirm_send)

        # Verify tickets button
        self.verify_button.clicked.connect(self._on_verify_tickets)

    # Event handlers
    def _on_theme_toggle(self):
        """Handle theme toggle."""
        self.theme_manager.toggle_theme()

    def _on_settings_clicked(self):
        """Handle settings button."""
        print("[INFO] Settings clicked (Phase 4)")

    def _on_help_clicked(self):
        """Handle help button."""
        print("[INFO] Help clicked (Phase 4)")

    def _on_authenticate_clicked(self):
        """Handle Microsoft authentication button click."""
        from ..services.auth import MicrosoftAuthService

        # Get credentials from state
        ms = self.state_store.state.connections.microsoft

        if not ms.client_id or not ms.tenant_id:
            self._show_error("Please enter Client ID and Tenant ID first.")
            self.activity_log.add_error("Authentication failed: Missing credentials")
            return

        # Check if already authenticated
        if ms.is_authenticated:
            # Sign out
            result = MessageBox(
                "Sign Out",
                "Are you sure you want to sign out?",
                self
            ).exec()

            if result:
                self.state_store.update_connections(
                    lambda s: setattr(s.connections.microsoft, 'is_authenticated', False)
                )
                self.state_store.update_connections(
                    lambda s: setattr(s.connections.microsoft, 'token_expiry', None)
                )

                self.activity_log.add_success("Signed out from Microsoft 365")

                InfoBar.success(
                    title="Signed Out",
                    content="Successfully signed out of Microsoft 365.",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP_RIGHT
                )
            return

        # Start OAuth flow
        try:
            auth_service = MicrosoftAuthService(ms.client_id, ms.tenant_id)

            self.activity_log.add_info("Starting Microsoft authentication...")
            self.activity_log.set_status("Authenticating...", "busy")

            # Open browser for authentication
            InfoBar.info(
                title="Authenticating",
                content="Opening browser for Microsoft authentication...",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )

            # Perform authentication (this will open browser)
            token = auth_service.authenticate()

            if token:
                # Store access token securely
                self.state_store.set_secret('microsoft_access_token', token['access_token'])

                # Update state
                self.state_store.update_connections(
                    lambda s: setattr(s.connections.microsoft, 'is_authenticated', True)
                )
                self.state_store.update_connections(
                    lambda s: setattr(s.connections.microsoft, 'token_expiry', token.get('expires_at'))
                )

                self.activity_log.add_success("Microsoft 365 authentication successful")
                self.activity_log.set_status("Ready", "success")

                InfoBar.success(
                    title="Authentication Successful",
                    content="Successfully authenticated with Microsoft 365.",
                    parent=self,
                    duration=3000,
                    position=InfoBarPosition.TOP_RIGHT
                )
            else:
                self.activity_log.add_error("Authentication failed or cancelled")
                self.activity_log.set_status("Ready", "success")
                self._show_error("Authentication failed or was cancelled.")

        except Exception as e:
            self.activity_log.add_error(f"Authentication error: {str(e)}")
            self.activity_log.set_status("Ready", "success")
            self._show_error(f"Authentication error: {str(e)}")

    def _on_test_connection_clicked(self):
        """Handle Freshservice test connection button click."""
        from ..services.freshservice import FreshserviceAPIService

        # Get configuration from state
        fs = self.state_store.state.connections.freshservice
        api_key = self.state_store.get_secret('freshservice_api_key')

        if not fs.domain or not api_key:
            self._show_error("Please enter Freshservice domain and API key first.")
            return

        # Test connection
        try:
            InfoBar.info(
                title="Testing Connection",
                content="Connecting to Freshservice...",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )

            fs_service = FreshserviceAPIService(fs.domain, api_key)
            success, message = fs_service.test_connection()

            if success:
                # Update state
                from datetime import datetime
                self.state_store.update_connections(
                    lambda s: setattr(s.connections.freshservice, 'is_connected', True)
                )
                self.state_store.update_connections(
                    lambda s: setattr(s.connections.freshservice, 'last_test_time', datetime.now())
                )

                InfoBar.success(
                    title="Connection Successful",
                    content=message or "Successfully connected to Freshservice.",
                    parent=self,
                    duration=3000,
                    position=InfoBarPosition.TOP_RIGHT
                )
            else:
                self.state_store.update_connections(
                    lambda s: setattr(s.connections.freshservice, 'is_connected', False)
                )
                self._show_error(f"Connection failed: {message}")

        except Exception as e:
            self.state_store.update_connections(
                lambda s: setattr(s.connections.freshservice, 'is_connected', False)
            )
            self._show_error(f"Connection error: {str(e)}")

    def _on_preview_clicked(self):
        """Handle preview button click."""
        # Get Claude API key
        api_key = self._get_claude_key()
        if not api_key:
            self._show_error("Please configure Claude API key in the Microsoft card.")
            return

        # Prepare settings
        settings = self._get_generation_settings()

        # Disable generation controls
        self.generation_card.set_generation_enabled(False)
        self.review_card.show_progress()
        self.last_action_label.setText("Last: Generating preview...")

        # Start preview generation
        self.generator_service.generate_preview(api_key, settings)

    def _on_generate_clicked(self):
        """Handle generate button click."""
        # Get Claude API key
        api_key = self._get_claude_key()
        if not api_key:
            self._show_error("Please configure Claude API key in the Microsoft card.")
            return

        # Prepare settings
        settings = self._get_generation_settings()

        # Confirm if large batch
        if settings['email_count'] > 50:
            result = MessageBox(
                "Confirm Generation",
                f"Generate {settings['email_count']} emails? This may take several minutes.",
                self
            ).exec()
            if not result:
                return

        # Clear existing drafts
        self.state_store.update_drafts(lambda s: s.clear_drafts())
        self.review_card.clear_table()

        # Disable generation controls
        self.generation_card.set_generation_enabled(False)
        self.review_card.show_progress()
        self.last_action_label.setText("Last: Generating drafts...")

        # Start generation
        self.generator_service.generate_drafts(api_key, settings)

    def _on_clear_clicked(self):
        """Handle clear button click."""
        result = MessageBox(
            "Confirm Clear",
            "Clear all drafts? This cannot be undone.",
            self
        ).exec()

        if result:
            self.state_store.update_drafts(lambda s: s.clear_drafts())
            self.review_card.clear_table()
            self.last_action_label.setText("Last: Cleared")

            InfoBar.success(
                title="Cleared",
                content="All drafts have been cleared.",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )

    def _on_review_row_clicked(self, draft_id: int):
        """Handle review row click."""
        self.review_sheet.show_draft(draft_id)

    def _on_view_all_details(self):
        """Handle view all details button click."""
        drafts = self.state_store.state.drafts

        if not drafts:
            self._show_error("No drafts to view.")
            return

        # Create HTML file with all details
        from datetime import datetime
        import webbrowser
        import os

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ticket_details_{timestamp}.html"
        filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)

        try:
            html = self._generate_html_report(drafts)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            # Open in browser
            webbrowser.open(f'file://{filepath}')

            InfoBar.success(
                title="Report Generated",
                content=f"Opened {len(drafts)} tickets in browser.",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )

        except Exception as e:
            self._show_error(f"Failed to generate report: {str(e)}")

    def _generate_html_report(self, drafts: list) -> str:
        """Generate HTML report for all drafts."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ticket Details Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; background: #f5f5f5; }
        h1 { color: #2c3e50; }
        .ticket { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .ticket-header { border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; }
        .ticket-id { color: #3498db; font-size: 24px; font-weight: bold; }
        .field { margin: 10px 0; }
        .field-label { font-weight: bold; color: #7f8c8d; display: inline-block; width: 120px; }
        .field-value { color: #2c3e50; }
        .subject { font-size: 18px; font-weight: 600; color: #2c3e50; margin: 15px 0; }
        .body { background: #ecf0f1; padding: 15px; border-radius: 4px; white-space: pre-wrap; font-family: monospace; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .status-draft { background: #f39c12; color: white; }
        .status-ready { background: #27ae60; color: white; }
        .status-sent { background: #2980b9; color: white; }
        .status-error { background: #e74c3c; color: white; }
        .summary { background: white; padding: 20px; margin-bottom: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        @media print { body { margin: 20px; } .ticket { page-break-inside: avoid; } }
    </style>
</head>
<body>
    <h1>IT Ticket Email Generator - Draft Report</h1>
    <div class="summary">
        <strong>Generated:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """<br>
        <strong>Total Drafts:</strong> """ + str(len(drafts)) + """<br>
        <strong>Ready to Send:</strong> """ + str(sum(1 for d in drafts if d.status == EmailStatus.READY)) + """
    </div>
"""

        for draft in drafts:
            status_class = f"status-{draft.status.value.lower()}"
            html += f"""
    <div class="ticket">
        <div class="ticket-header">
            <span class="ticket-id">Ticket #{draft.id}</span>
            <span class="status {status_class}">{draft.status.value.upper()}</span>
        </div>
        <div class="field"><span class="field-label">Type:</span><span class="field-value">{draft.type.value}</span></div>
        <div class="field"><span class="field-label">Priority:</span><span class="field-value">{draft.priority}</span></div>
        <div class="field"><span class="field-label">Category:</span><span class="field-value">{draft.category}</span></div>
"""
            if draft.subcategory:
                html += f"""        <div class="field"><span class="field-label">Sub-Category:</span><span class="field-value">{draft.subcategory}</span></div>\n"""
            if draft.item:
                html += f"""        <div class="field"><span class="field-label">Item:</span><span class="field-value">{draft.item}</span></div>\n"""

            html += f"""        <div class="field"><span class="field-label">Recipient:</span><span class="field-value">{draft.recipient}</span></div>
        <div class="subject">{draft.subject}</div>
        <div class="body">{draft.body}</div>
    </div>
"""

        html += """
</body>
</html>
"""
        return html

    def _on_export_csv(self):
        """Handle export CSV."""
        drafts = self.state_store.state.drafts

        if not drafts:
            self._show_error("No drafts to export.")
            return

        # Get file path
        default_name = CSVExporter.get_default_filename()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Drafts to CSV",
            default_name,
            "CSV Files (*.csv)"
        )

        if file_path:
            try:
                CSVExporter.export_drafts(drafts, file_path)

                InfoBar.success(
                    title="Exported",
                    content=f"Exported {len(drafts)} drafts to {file_path}",
                    parent=self,
                    duration=3000,
                    position=InfoBarPosition.TOP_RIGHT
                )

                self.last_action_label.setText(f"Last: Exported {len(drafts)} drafts")

            except Exception as e:
                self._show_error(f"Export failed: {str(e)}")

    def _on_mark_ready(self):
        """Handle mark ready for selected drafts."""
        draft_ids = self.review_card.get_selected_draft_ids()

        if not draft_ids:
            self._show_error("No drafts selected.")
            return

        # Mark as ready
        for draft_id in draft_ids:
            self.state_store.update_drafts(
                lambda s: s.update_draft_status(draft_id, EmailStatus.READY)
            )

        InfoBar.success(
            title="Marked Ready",
            content=f"{len(draft_ids)} drafts marked as ready.",
            parent=self,
            duration=2000,
            position=InfoBarPosition.TOP_RIGHT
        )

    def _on_mark_draft_ready(self, draft_id: int):
        """Mark single draft as ready from detail sheet."""
        self.state_store.update_drafts(
            lambda s: s.update_draft_status(draft_id, EmailStatus.READY)
        )

        self.activity_log.add_success(f"Marked draft #{draft_id} as ready")

        InfoBar.success(
            title="Marked Ready",
            content="Draft marked as ready.",
            parent=self,
            duration=2000,
            position=InfoBarPosition.TOP_RIGHT
        )

    def _on_confirm_send(self):
        """Handle confirm send button - send all ready drafts."""
        import time
        from datetime import datetime

        # Get ready drafts
        ready_drafts = [d for d in self.state_store.state.drafts if d.status == EmailStatus.READY]

        if not ready_drafts:
            self._show_error("No ready drafts to send.")
            return

        # Confirm
        result = MessageBox(
            "Confirm Send",
            f"Send {len(ready_drafts)} ready emails? This will send them via Microsoft Graph API.",
            self
        ).exec()

        if not result:
            self.activity_log.add_warning("Send cancelled by user")
            return

        # Check authentication
        if not self.state_store.state.connections.microsoft.is_authenticated:
            self._show_error("Please authenticate with Microsoft 365 first.")
            self.activity_log.add_error("Send failed: Not authenticated")
            return

        # Start sending
        self.activity_log.add_info(f"Starting to send {len(ready_drafts)} emails...")
        self.activity_log.set_status(f"Sending 0/{len(ready_drafts)}...", "busy")

        # Disable button during send
        self.confirm_send_button.setEnabled(False)
        self.last_action_label.setText("Last: Sending emails...")

        sent_count = 0
        failed_count = 0
        wait_time_ms = self.state_store.state.generation.wait_time_ms

        # Get access token
        access_token = self.state_store.get_secret('microsoft_access_token')
        if not access_token:
            self._show_error("No access token found. Please authenticate again.")
            self.activity_log.add_error("Send failed: No access token")
            self.confirm_send_button.setEnabled(True)
            self.activity_log.set_status("Ready", "success")
            return

        # Import email sender
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from email_sender import EmailSender

        # Create sender
        ms = self.state_store.state.connections.microsoft
        sender = EmailSender(access_token, ms.sender_email)

        for draft in ready_drafts:
            try:
                self.activity_log.add_info(f"Sending email #{draft.id}: {draft.subject[:50]}...")

                # Actually send via Microsoft Graph API
                result = sender.send_email(
                    to_email=draft.recipient,
                    subject=draft.subject,
                    body=draft.body,
                    body_type="Text"
                )

                if result['success']:
                    # Mark as sent
                    self.state_store.update_drafts(
                        lambda s: s.update_draft_status(draft.id, EmailStatus.SENT)
                    )
                    draft.sent_timestamp = datetime.now()

                    sent_count += 1
                    self.activity_log.add_success(f"✓ Email #{draft.id} sent successfully")
                    self.activity_log.set_status(f"Sending {sent_count}/{len(ready_drafts)}...", "busy")
                else:
                    # Mark as error
                    failed_count += 1
                    error_msg = result.get('error', 'Unknown error')
                    self.state_store.update_drafts(
                        lambda s: s.update_draft_status(draft.id, EmailStatus.ERROR, error_msg)
                    )
                    self.activity_log.add_error(f"✗ Email #{draft.id} failed: {error_msg}")

                # Wait between sends
                if wait_time_ms > 0:
                    time.sleep(wait_time_ms / 1000)

            except Exception as e:
                failed_count += 1
                self.state_store.update_drafts(
                    lambda s: s.update_draft_status(draft.id, EmailStatus.ERROR, str(e))
                )
                self.activity_log.add_error(f"✗ Email #{draft.id} failed: {str(e)}")

        # Complete
        self.confirm_send_button.setEnabled(True)
        self.activity_log.set_status("Send complete", "success")

        if failed_count == 0:
            self.activity_log.add_success(f"All {sent_count} emails sent successfully!")
            self.last_action_label.setText(f"Last: Sent {sent_count} emails")

            InfoBar.success(
                title="Send Complete",
                content=f"Successfully sent {sent_count} emails.",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )
        else:
            self.activity_log.add_warning(f"Sent {sent_count}, Failed {failed_count}")
            self.last_action_label.setText(f"Last: Sent {sent_count}, Failed {failed_count}")

            InfoBar.warning(
                title="Send Partial",
                content=f"Sent {sent_count} emails, {failed_count} failed.",
                parent=self,
                duration=3000,
                position=InfoBarPosition.TOP_RIGHT
            )

    def _on_verify_tickets(self):
        """Handle verify tickets button - verify sent emails created Freshservice tickets."""
        from datetime import datetime
        import sys
        from pathlib import Path

        # Get sent drafts
        sent_drafts = [d for d in self.state_store.state.drafts if d.status == EmailStatus.SENT]

        if not sent_drafts:
            self._show_error("No sent drafts to verify.")
            return

        # Check Freshservice connection
        fs = self.state_store.state.connections.freshservice
        if not fs.is_connected:
            self._show_error("Please connect to Freshservice first.")
            self.activity_log.add_error("Verification failed: Freshservice not connected")
            return

        # Get API key
        fs_api_key = self.state_store.get_secret('freshservice_api_key')
        if not fs_api_key:
            self._show_error("Freshservice API key not found.")
            self.activity_log.add_error("Verification failed: No API key")
            return

        # Start verification
        self.activity_log.add_info(f"Starting verification for {len(sent_drafts)} sent emails...")
        self.activity_log.set_status("Verifying...", "busy")
        self.verify_button.setEnabled(False)
        self.last_action_label.setText("Last: Verifying tickets...")

        try:
            # Import required modules
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from freshservice_client import FreshserviceClient
            from ticket_verifier import TicketVerifier

            # Create clients
            fs_client = FreshserviceClient(fs.domain, fs_api_key)
            verifier = TicketVerifier(fs_client)

            # Prepare sent emails data
            sent_emails_data = []
            batch_start_time = None

            for draft in sent_drafts:
                # Get the earliest sent timestamp as batch start time
                if draft.sent_timestamp:
                    if batch_start_time is None or draft.sent_timestamp < batch_start_time:
                        batch_start_time = draft.sent_timestamp

                # Build email data for verifier
                sent_emails_data.append({
                    'number': draft.id,
                    'subject': draft.subject,
                    'priority': draft.priority,
                    'type': draft.type.value,
                    'category': f"{draft.category} > {draft.subcategory} > {draft.item}".strip(' > ')
                })

            # Default to now if no timestamps
            if batch_start_time is None:
                batch_start_time = datetime.now()

            self.activity_log.add_info(f"Batch start time: {batch_start_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Get sender email
            ms = self.state_store.state.connections.microsoft
            sender_email = str(ms.sender_email) if ms.sender_email else None

            # Verify batch
            self.activity_log.add_info("Querying Freshservice API...")
            verification_results = verifier.verify_batch(
                sent_emails=sent_emails_data,
                recipient_email=str(ms.recipient_email) if ms.recipient_email else "unknown",
                batch_start_time=batch_start_time,
                sender_email=sender_email
            )

            # Process results
            summary = verification_results['summary']
            found_count = verification_results['total_found']
            not_found_count = verification_results['total_not_found']
            passed_count = summary['passed']
            failed_count = summary['failed']

            # Log detailed results
            self.activity_log.add_info(f"Found {found_count}/{len(sent_drafts)} tickets in Freshservice")

            for result in verification_results['results']:
                ticket_num = result['ticket_number']
                status = result['status']
                overall = result['overall_result']

                if status == 'NOT_FOUND':
                    self.activity_log.add_error(f"✗ Ticket #{ticket_num}: NOT FOUND in Freshservice")
                elif overall == 'PASS':
                    self.activity_log.add_success(f"✓ Ticket #{ticket_num}: PASS (all fields match)")
                elif overall == 'FAIL':
                    match_count = result['match_count']
                    mismatch_count = result['mismatch_count']
                    self.activity_log.add_warning(f"⚠ Ticket #{ticket_num}: FAIL ({match_count} match, {mismatch_count} mismatch)")

            # Summary
            pass_rate = summary['pass_rate']
            self.activity_log.add_info(f"Pass rate: {pass_rate:.1f}% ({passed_count}/{found_count})")

            # Show final result
            self.verify_button.setEnabled(True)
            self.activity_log.set_status("Verification complete", "success")
            self.last_action_label.setText(f"Last: Verified {found_count} tickets")

            if not_found_count == 0 and failed_count == 0:
                InfoBar.success(
                    title="Verification Complete",
                    content=f"All {found_count} tickets verified successfully!",
                    parent=self,
                    duration=3000,
                    position=InfoBarPosition.TOP_RIGHT
                )
            elif not_found_count > 0:
                InfoBar.warning(
                    title="Verification Partial",
                    content=f"{not_found_count} tickets not found in Freshservice. See activity log.",
                    parent=self,
                    duration=5000,
                    position=InfoBarPosition.TOP_RIGHT
                )
            else:
                InfoBar.warning(
                    title="Verification Complete",
                    content=f"{passed_count} passed, {failed_count} failed. See activity log.",
                    parent=self,
                    duration=5000,
                    position=InfoBarPosition.TOP_RIGHT
                )

        except Exception as e:
            self.verify_button.setEnabled(True)
            self.activity_log.add_error(f"Verification error: {str(e)}")
            self.activity_log.set_status("Ready", "success")
            self._show_error(f"Verification failed: {str(e)}")

    def _on_draft_generated(self, draft):
        """Handle draft generated signal."""
        # Add to state
        self.state_store.update_drafts(lambda s: s.add_draft(draft))

        # Add to table (streaming)
        self.review_card.add_draft_row(draft)

        # Update next ticket number
        self.state_store.update_state(
            lambda s: setattr(s.generation, 'next_ticket_number', draft.id + 1)
        )

        # Log
        self.activity_log.add_success(f"Generated draft #{draft.id}: {draft.subject[:40]}...")

    def _on_progress_updated(self, current: int, total: int):
        """Handle progress update."""
        self.last_action_label.setText(f"Last: Generating {current}/{total}...")
        self.activity_log.set_status(f"Generating {current}/{total}...", "busy")

    def _on_generation_complete(self):
        """Handle generation complete."""
        self.generation_card.set_generation_enabled(True)
        self.review_card.hide_progress()

        count = len(self.state_store.state.drafts)
        self.last_action_label.setText(f"Last: Generated {count} drafts")

        self.activity_log.add_success(f"Generation complete: {count} drafts created")
        self.activity_log.set_status("Ready", "success")

        InfoBar.success(
            title="Generation Complete",
            content=f"Successfully generated {count} drafts.",
            parent=self,
            duration=3000,
            position=InfoBarPosition.TOP_RIGHT
        )

    def _on_generation_error(self, error_message: str):
        """Handle generation error."""
        self.generation_card.set_generation_enabled(True)
        self.review_card.hide_progress()
        self.last_action_label.setText("Last: Error")

        self.activity_log.add_error(f"Generation failed: {error_message}")
        self.activity_log.set_status("Ready", "success")

        self._show_error(error_message)

    def _on_drafts_changed(self, drafts):
        """Handle drafts list change."""
        self.drafts_count_label.setText(f"Drafts: {len(drafts)}")

        # Enable "Confirm Send" button if there are ready drafts
        ready_count = sum(1 for d in drafts if d.status == EmailStatus.READY)
        self.confirm_send_button.setEnabled(ready_count > 0)

        # Enable "Verify Tickets" button if there are sent drafts
        sent_count = sum(1 for d in drafts if d.status == EmailStatus.SENT)
        self.verify_button.setEnabled(sent_count > 0)

    def _on_connections_changed(self, connections):
        """Handle connections state change."""
        ms_status = "✓" if connections.microsoft.is_authenticated else "✖"
        fs_status = "✓" if connections.freshservice.is_connected else "✖"
        self.status_label.setText(f"MS {ms_status} | FS {fs_status}")

    def _on_preflight_changed(self, preflight):
        """Handle preflight state change."""
        self.confirm_send_button.setEnabled(preflight.all_passed)

    def _on_theme_changed(self, is_dark: bool):
        """Handle theme change."""
        mode = self.theme_manager.get_current_mode()
        self.state_store.update_state(lambda s: setattr(s.ui, 'theme', mode))

        # Refresh activity log colors for new theme
        self.activity_log.refresh_theme()

    # Helper methods
    def _get_claude_key(self) -> str:
        """Get Claude API key from secure storage."""
        # Retrieve from secure memory storage
        key = self.state_store.get_secret('claude_api_key')

        # Return empty string if not configured
        if not key or key == "":
            return ""

        return key

    def _get_generation_settings(self) -> dict:
        """Get generation settings from state."""
        gen = self.state_store.state.generation
        ms = self.state_store.state.connections.microsoft

        return {
            'email_count': gen.email_count,
            'quality': gen.quality,
            'wait_time_ms': gen.wait_time_ms,
            'mode': gen.mode,
            'custom_prompt': gen.custom_prompt,
            'next_ticket_number': gen.next_ticket_number,
            'recipient_email': str(ms.recipient_email)
        }

    def _show_error(self, message: str):
        """Show error message."""
        MessageBox("Error", message, self).exec()

    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        geometry = self.state_store.state.ui.window_geometry
        geometry.x = self.x()
        geometry.y = self.y()
        geometry.width = self.width()
        geometry.height = self.height()

        self.state_store.save()

        event.accept()
