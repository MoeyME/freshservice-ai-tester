"""
Main application window with frameless design and 12-column grid layout.
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLabel, QSpacerItem, QSizePolicy
)
from qfluentwidgets import (
    FluentWindow, NavigationItemPosition,
    TransparentToolButton, PushButton, BodyLabel, CaptionLabel,
    FluentIcon
)

from ..state.store import StateStore
from ..utils.theme import ThemeManager
from .connection_cards import MicrosoftCard, FreshserviceCard


class MainWindow(FluentWindow):
    """
    Main application window with modern Fluent Design.

    Features:
    - Frameless window with acrylic background
    - 12-column responsive grid layout
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
        # Columns 0-2: Left dock (3/12)
        # Columns 3-8: Center workspace (6/12)
        # Columns 9-11: Right rail (3/12)
        for i in range(12):
            if 0 <= i <= 2:
                main_layout.setColumnStretch(i, 1)
            elif 3 <= i <= 8:
                main_layout.setColumnStretch(i, 2)
            elif 9 <= i <= 11:
                main_layout.setColumnStretch(i, 1)

        # Row 0: Header (fixed height)
        # Row 1: Main content (expanding)
        # Row 2: Footer (fixed height)
        main_layout.setRowStretch(0, 0)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 0)

        # Create UI sections
        self._create_title_bar()
        self._create_left_dock(main_layout)
        self._create_center_workspace(main_layout)
        self._create_right_rail(main_layout)
        self._create_sticky_footer(main_layout)

    def _create_title_bar(self):
        """Create custom title bar with theme toggle and settings."""
        # Title bar is handled by FluentWindow
        # Add custom buttons to navigation
        self.navigationInterface.addItem(
            routeKey='theme',
            icon=FluentIcon.CONSTRACT,
            text='Theme',
            onClick=self._on_theme_toggle,
            position=NavigationItemPosition.TOP
        )

        self.navigationInterface.addItem(
            routeKey='settings',
            icon=FluentIcon.SETTING,
            text='Settings',
            onClick=self._on_settings_clicked,
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.addItem(
            routeKey='help',
            icon=FluentIcon.HELP,
            text='Help',
            onClick=self._on_help_clicked,
            position=NavigationItemPosition.BOTTOM
        )

    def _create_left_dock(self, layout: QGridLayout):
        """
        Create left dock with connection cards.

        Args:
            layout: Main grid layout
        """
        # Scroll area for connections
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Container for cards
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

        # Spacer to push cards to top
        container_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        scroll_area.setWidget(container)

        # Add to grid: Row 1, Columns 0-2
        layout.addWidget(scroll_area, 1, 0, 1, 3)

    def _create_center_workspace(self, layout: QGridLayout):
        """
        Create center workspace with generation and review cards.

        Args:
            layout: Main grid layout
        """
        # Placeholder for now
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)

        label = BodyLabel("Center Workspace")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(label)

        # Add to grid: Row 1, Columns 3-8
        layout.addWidget(center_widget, 1, 3, 1, 6)

    def _create_right_rail(self, layout: QGridLayout):
        """
        Create right rail with actions and logs.

        Args:
            layout: Main grid layout
        """
        # Placeholder for now
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        label = BodyLabel("Right Rail")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(label)

        # Add to grid: Row 1, Columns 9-11
        layout.addWidget(right_widget, 1, 9, 1, 3)

    def _create_sticky_footer(self, layout: QGridLayout):
        """
        Create sticky footer with status and primary CTA.

        Args:
            layout: Main grid layout
        """
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
        self.confirm_send_button = PushButton("Confirm & Send...")
        self.confirm_send_button.setEnabled(False)
        footer_layout.addWidget(self.confirm_send_button)

        # Add to grid: Row 2, span all columns
        layout.addWidget(footer, 2, 0, 1, 12)

    def _init_connections(self):
        """Initialize signal connections."""
        # Connect state changes
        self.state_store.drafts_changed.connect(self._on_drafts_changed)
        self.state_store.connections_changed.connect(self._on_connections_changed)
        self.state_store.preflight_changed.connect(self._on_preflight_changed)

        # Connect theme changes
        self.theme_manager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_toggle(self):
        """Handle theme toggle button click."""
        self.theme_manager.toggle_theme()

    def _on_settings_clicked(self):
        """Handle settings button click."""
        # TODO: Show settings dialog
        print("[INFO] Settings clicked")

    def _on_help_clicked(self):
        """Handle help button click."""
        # TODO: Show help dialog
        print("[INFO] Help clicked")

    def _on_drafts_changed(self, drafts):
        """
        Handle drafts list change.

        Args:
            drafts: List of DraftEmail objects
        """
        self.drafts_count_label.setText(f"Drafts: {len(drafts)}")

    def _on_connections_changed(self, connections):
        """
        Handle connections state change.

        Args:
            connections: ConnectionsState object
        """
        # Update status label
        ms_status = "✓" if connections.microsoft.is_authenticated else "✖"
        fs_status = "✓" if connections.freshservice.is_connected else "✖"
        self.status_label.setText(f"MS {ms_status} | FS {fs_status}")

    def _on_preflight_changed(self, preflight):
        """
        Handle preflight state change.

        Args:
            preflight: PreflightState object
        """
        # Enable/disable send button based on preflight
        self.confirm_send_button.setEnabled(preflight.all_passed)

    def _on_theme_changed(self, is_dark: bool):
        """
        Handle theme change.

        Args:
            is_dark: True if dark mode
        """
        # Update state
        mode = self.theme_manager.get_current_mode()
        self.state_store.update_state(lambda s: setattr(s.ui, 'theme', mode))

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
