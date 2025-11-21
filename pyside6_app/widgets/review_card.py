"""
Review card with draft table and bulk actions.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView,
    QScrollArea, QSizePolicy
)
from qfluentwidgets import (
    ElevatedCardWidget, TableWidget, PushButton, IndeterminateProgressBar,
    SubtitleLabel, CaptionLabel, FluentIcon, Action, RoundMenu
)

from ..state.store import StateStore
from ..state.models import DraftEmail, EmailStatus


class ReviewCard(ElevatedCardWidget):
    """
    Review card with draft table.

    Signals:
        row_clicked: Emitted when row clicked (draft_id: int)
        export_csv_clicked: Emitted when export CSV clicked
        select_all_clicked: Emitted when select all clicked
        select_none_clicked: Emitted when select none clicked
        mark_ready_clicked: Emitted when mark ready clicked
    """

    row_clicked = Signal(int)  # draft_id
    export_csv_clicked = Signal()
    view_all_clicked = Signal()
    select_all_clicked = Signal()
    select_none_clicked = Signal()
    mark_ready_clicked = Signal()

    def __init__(self, state_store: StateStore, parent: QWidget = None):
        """
        Initialize review card.

        Args:
            state_store: Application state store
            parent: Parent widget
        """
        super().__init__(parent)
        self.state_store = state_store

        # Create UI
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header with actions
        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        header_label = SubtitleLabel("Draft Review")
        header_row.addWidget(header_label)

        # Scrollable button container for smaller screens
        button_scroll = QScrollArea()
        button_scroll.setWidgetResizable(True)
        button_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        button_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        button_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        button_scroll.setMaximumHeight(40)
        button_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)

        # Action buttons
        self.select_all_button = PushButton("Select All")
        self.select_all_button.setIcon(FluentIcon.ACCEPT)
        self.select_all_button.clicked.connect(self.select_all_clicked.emit)
        button_layout.addWidget(self.select_all_button)

        self.select_none_button = PushButton("Select None")
        self.select_none_button.setIcon(FluentIcon.CANCEL)
        self.select_none_button.clicked.connect(self.select_none_clicked.emit)
        button_layout.addWidget(self.select_none_button)

        self.view_all_button = PushButton("View All Details")
        self.view_all_button.setIcon(FluentIcon.DOCUMENT)
        self.view_all_button.clicked.connect(self.view_all_clicked.emit)
        button_layout.addWidget(self.view_all_button)

        self.export_button = PushButton("Export CSV")
        self.export_button.setIcon(FluentIcon.SAVE)
        self.export_button.clicked.connect(self.export_csv_clicked.emit)
        button_layout.addWidget(self.export_button)

        self.mark_ready_button = PushButton("Mark Ready")
        self.mark_ready_button.setIcon(FluentIcon.COMPLETED)
        self.mark_ready_button.clicked.connect(self.mark_ready_clicked.emit)
        button_layout.addWidget(self.mark_ready_button)

        button_scroll.setWidget(button_container)
        header_row.addWidget(button_scroll)

        layout.addLayout(header_row)

        # Progress bar (shown during generation)
        self.progress_bar = IndeterminateProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Table
        self.table = TableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Type", "Priority", "Category", "Subject", "Status", "Recipient"
        ])

        # Set column widths - optimized for smaller screens
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 40)   # ID - compact
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(1, 70)   # Type - reduced
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 70)   # Priority - reduced
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 100)  # Category - reduced
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Subject - gets remaining space
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 60)   # Status - reduced
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 150)  # Recipient - reduced

        # Enable selection
        self.table.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(TableWidget.SelectionMode.MultiSelection)

        # Connect row click
        self.table.cellClicked.connect(self._on_row_clicked)

        layout.addWidget(self.table)

        # Status label
        self.status_label = CaptionLabel("No drafts")
        layout.addWidget(self.status_label)

        # Load initial state
        self._load_from_state()

        # Connect signals
        self._init_connections()

    def _init_connections(self):
        """Initialize signal connections."""
        self.state_store.drafts_changed.connect(self._on_drafts_changed)

    def _load_from_state(self):
        """Load drafts from state."""
        self._populate_table(self.state_store.state.drafts)

    def _populate_table(self, drafts: list):
        """
        Populate table with drafts.

        Args:
            drafts: List of DraftEmail objects
        """
        self.table.setRowCount(0)  # Clear existing

        for draft in drafts:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(str(draft.id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            # Type
            type_item = QTableWidgetItem(draft.type.value)
            self.table.setItem(row, 1, type_item)

            # Priority
            priority_item = QTableWidgetItem(draft.priority)
            self.table.setItem(row, 2, priority_item)

            # Category
            category_text = draft.category
            if draft.subcategory:
                category_text += f" > {draft.subcategory}"
            if draft.item:
                category_text += f" > {draft.item}"
            category_item = QTableWidgetItem(category_text)
            self.table.setItem(row, 3, category_item)

            # Subject (truncated)
            subject = draft.subject
            if len(subject) > 70:
                subject = subject[:67] + "..."
            subject_item = QTableWidgetItem(subject)
            self.table.setItem(row, 4, subject_item)

            # Status
            status_item = QTableWidgetItem(self._get_status_icon(draft.status) + " " + draft.status.value.title())
            self.table.setItem(row, 5, status_item)

            # Recipient
            recipient_item = QTableWidgetItem(str(draft.recipient))
            self.table.setItem(row, 6, recipient_item)

        # Update status label
        count = len(drafts)
        if count == 0:
            self.status_label.setText("No drafts")
        else:
            ready_count = sum(1 for d in drafts if d.status == EmailStatus.READY)
            self.status_label.setText(f"{count} drafts ({ready_count} ready)")

    def _get_status_icon(self, status: EmailStatus) -> str:
        """Get icon for status."""
        if status == EmailStatus.DRAFT:
            return "📝"
        elif status == EmailStatus.READY:
            return "✅"
        elif status == EmailStatus.SENT:
            return "✓"
        elif status == EmailStatus.ERROR:
            return "✖"
        return "•"

    def _on_row_clicked(self, row: int, column: int):
        """Handle row click."""
        # Get draft ID from first column
        id_item = self.table.item(row, 0)
        if id_item:
            draft_id = int(id_item.text())
            self.row_clicked.emit(draft_id)

    def _on_drafts_changed(self, drafts: list):
        """Handle drafts list change."""
        self._populate_table(drafts)

    def add_draft_row(self, draft: DraftEmail):
        """
        Add a single draft row (for streaming results).

        Args:
            draft: DraftEmail object
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Populate columns
        self.table.setItem(row, 0, QTableWidgetItem(str(draft.id)))
        self.table.setItem(row, 1, QTableWidgetItem(draft.type.value))
        self.table.setItem(row, 2, QTableWidgetItem(draft.priority))

        category_text = draft.category
        if draft.subcategory:
            category_text += f" > {draft.subcategory}"
        if draft.item:
            category_text += f" > {draft.item}"
        self.table.setItem(row, 3, QTableWidgetItem(category_text))

        subject = draft.subject
        if len(subject) > 70:
            subject = subject[:67] + "..."
        self.table.setItem(row, 4, QTableWidgetItem(subject))

        self.table.setItem(row, 5, QTableWidgetItem(self._get_status_icon(draft.status) + " " + draft.status.value.title()))
        self.table.setItem(row, 6, QTableWidgetItem(str(draft.recipient)))

        # Update status
        count = self.table.rowCount()
        self.status_label.setText(f"{count} drafts")

    def update_row_status(self, draft_id: int, status: EmailStatus):
        """
        Update status of a specific row.

        Args:
            draft_id: Draft ID
            status: New status
        """
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            if id_item and int(id_item.text()) == draft_id:
                status_item = self.table.item(row, 5)
                if status_item:
                    status_item.setText(self._get_status_icon(status) + " " + status.value.title())
                break

    def get_selected_draft_ids(self) -> list:
        """
        Get IDs of selected drafts.

        Returns:
            List of draft IDs
        """
        selected_rows = set(item.row() for item in self.table.selectedItems())
        draft_ids = []

        for row in selected_rows:
            id_item = self.table.item(row, 0)
            if id_item:
                draft_ids.append(int(id_item.text()))

        return draft_ids

    def select_all_rows(self):
        """Select all rows."""
        self.table.selectAll()

    def clear_selection(self):
        """Clear selection."""
        self.table.clearSelection()

    def clear_table(self):
        """Clear all rows."""
        self.table.setRowCount(0)
        self.status_label.setText("No drafts")

    def show_progress(self):
        """Show progress bar."""
        self.progress_bar.setVisible(True)
        self.progress_bar.start()

    def hide_progress(self):
        """Hide progress bar."""
        self.progress_bar.stop()
        self.progress_bar.setVisible(False)
