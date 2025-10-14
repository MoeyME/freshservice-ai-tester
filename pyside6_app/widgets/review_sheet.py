"""
Review detail sheet - slide-in drawer for email preview.
"""

from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QLabel
)
from qfluentwidgets import (
    TransparentToolButton, PushButton, SimpleCardWidget,
    SubtitleLabel, BodyLabel, CaptionLabel, TextEdit,
    InfoBadge, InfoLevel, FluentIcon
)

from ..state.store import StateStore
from ..state.models import DraftEmail, EmailStatus


class ReviewDetailSheet(QWidget):
    """
    Slide-in detail sheet for email preview.

    Signals:
        closed: Emitted when sheet closes
        mark_ready_clicked: Emitted when mark ready button clicked (draft_id: int)
    """

    closed = Signal()
    mark_ready_clicked = Signal(int)

    def __init__(self, state_store: StateStore, parent: QWidget = None):
        """
        Initialize review detail sheet.

        Args:
            state_store: Application state store
            parent: Parent widget
        """
        super().__init__(parent)
        self.state_store = state_store
        self.current_draft_id = None

        # Set up widget
        self.setFixedWidth(480)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet("""
            ReviewDetailSheet {
                background-color: palette(base);
                border-left: 1px solid palette(mid);
            }
        """)

        # Create UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet("background-color: palette(base); border-bottom: 1px solid palette(mid);")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)

        self.title_label = SubtitleLabel("Email Preview")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        close_button = TransparentToolButton(FluentIcon.CLOSE)
        close_button.setFixedSize(32, 32)
        close_button.clicked.connect(self.close_sheet)
        header_layout.addWidget(close_button)

        layout.addWidget(header)

        # Scrollable body
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)
        scroll_layout.setContentsMargins(16, 16, 16, 16)

        # Subject card
        subject_card = SimpleCardWidget()
        subject_card_layout = QVBoxLayout(subject_card)
        subject_card_layout.setSpacing(8)

        subject_card_layout.addWidget(CaptionLabel("Subject"))
        self.subject_label = BodyLabel("")
        self.subject_label.setWordWrap(True)
        subject_card_layout.addWidget(self.subject_label)

        scroll_layout.addWidget(subject_card)

        # Detected fields card
        fields_card = SimpleCardWidget()
        fields_card_layout = QVBoxLayout(fields_card)
        fields_card_layout.setSpacing(12)

        fields_card_layout.addWidget(SubtitleLabel("Detected Fields"))

        self.fields_grid = QGridLayout()
        self.fields_grid.setSpacing(8)
        self.fields_grid.setColumnStretch(1, 1)

        # Create field labels (will be populated dynamically)
        self.field_labels = {}

        fields_card_layout.addLayout(self.fields_grid)
        scroll_layout.addWidget(fields_card)

        # Body card
        body_card = SimpleCardWidget()
        body_card_layout = QVBoxLayout(body_card)
        body_card_layout.setSpacing(8)

        body_card_layout.addWidget(CaptionLabel("Email Body"))
        self.body_text = TextEdit()
        self.body_text.setReadOnly(True)
        self.body_text.setFixedHeight(200)
        body_card_layout.addWidget(self.body_text)

        scroll_layout.addWidget(body_card)

        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Footer
        footer = QWidget()
        footer.setFixedHeight(56)
        footer.setStyleSheet("background-color: palette(base); border-top: 1px solid palette(mid);")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 0, 16, 0)

        self.status_badge = InfoBadge.attension("Draft", self)
        footer_layout.addWidget(self.status_badge)

        footer_layout.addStretch()

        self.mark_ready_button = PushButton("Mark Ready")
        self.mark_ready_button.setIcon(FluentIcon.COMPLETED)
        self.mark_ready_button.clicked.connect(self._on_mark_ready)
        footer_layout.addWidget(self.mark_ready_button)

        self.copy_button = PushButton("Copy")
        self.copy_button.setIcon(FluentIcon.COPY)
        self.copy_button.clicked.connect(self._on_copy)
        footer_layout.addWidget(self.copy_button)

        layout.addWidget(footer)

        # Initially hidden
        self.setVisible(False)

    def show_draft(self, draft_id: int):
        """
        Show draft details.

        Args:
            draft_id: Draft ID to show
        """
        draft = self.state_store.state.get_draft_by_id(draft_id)
        if not draft:
            return

        self.current_draft_id = draft_id

        # Update UI
        self.subject_label.setText(draft.subject)
        self.body_text.setPlainText(draft.body)

        # Update fields
        self._populate_fields(draft)

        # Update status badge
        if draft.status == EmailStatus.DRAFT:
            self.status_badge.setLevel(InfoLevel.ATTENTION)
            self.status_badge.setText("Draft")
        elif draft.status == EmailStatus.READY:
            self.status_badge.setLevel(InfoLevel.SUCCESS)
            self.status_badge.setText("Ready")
        elif draft.status == EmailStatus.SENT:
            self.status_badge.setLevel(InfoLevel.SUCCESS)
            self.status_badge.setText("Sent")
        elif draft.status == EmailStatus.ERROR:
            self.status_badge.setLevel(InfoLevel.ERROR)
            self.status_badge.setText("Error")

        # Show sheet with animation
        self.show_sheet()

    def _populate_fields(self, draft: DraftEmail):
        """
        Populate detected fields grid.

        Args:
            draft: DraftEmail object
        """
        # Clear existing
        while self.fields_grid.count():
            item = self.fields_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.field_labels.clear()

        row = 0

        # Add fields
        fields = [
            ("ID", str(draft.id)),
            ("Type", draft.type.value),
            ("Priority", draft.priority),
            ("Category", draft.category),
        ]

        if draft.subcategory:
            fields.append(("Sub-Category", draft.subcategory))

        if draft.item:
            fields.append(("Item", draft.item))

        fields.append(("Recipient", str(draft.recipient)))

        if draft.error_message:
            fields.append(("Error", draft.error_message))

        for label_text, value_text in fields:
            label = CaptionLabel(label_text + ":")
            label.setStyleSheet("color: gray;")
            self.fields_grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignRight)

            value = BodyLabel(value_text)
            value.setWordWrap(True)
            self.fields_grid.addWidget(value, row, 1)

            self.field_labels[label_text] = value
            row += 1

    def show_sheet(self):
        """Show sheet with slide-in animation."""
        if not self.isVisible():
            self.setVisible(True)

            # Animate from right
            self.animation = QPropertyAnimation(self, b"geometry")
            parent_rect = self.parent().rect()

            start_rect = QRect(
                parent_rect.right(),
                0,
                self.width(),
                parent_rect.height()
            )
            end_rect = QRect(
                parent_rect.right() - self.width(),
                0,
                self.width(),
                parent_rect.height()
            )

            self.animation.setDuration(300)
            self.animation.setStartValue(start_rect)
            self.animation.setEndValue(end_rect)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.start()

    def close_sheet(self):
        """Close sheet with slide-out animation."""
        if self.isVisible():
            # Animate to right
            self.animation = QPropertyAnimation(self, b"geometry")
            parent_rect = self.parent().rect()

            start_rect = self.geometry()
            end_rect = QRect(
                parent_rect.right(),
                0,
                self.width(),
                parent_rect.height()
            )

            self.animation.setDuration(250)
            self.animation.setStartValue(start_rect)
            self.animation.setEndValue(end_rect)
            self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
            self.animation.finished.connect(lambda: self.setVisible(False))
            self.animation.start()

            self.closed.emit()

    def _on_mark_ready(self):
        """Handle mark ready button click."""
        if self.current_draft_id is not None:
            self.mark_ready_clicked.emit(self.current_draft_id)

            # Update status badge
            self.status_badge.setLevel(InfoLevel.SUCCESS)
            self.status_badge.setText("Ready")

    def _on_copy(self):
        """Handle copy button click."""
        if self.current_draft_id is not None:
            from PySide6.QtWidgets import QApplication

            draft = self.state_store.state.get_draft_by_id(self.current_draft_id)
            if draft:
                text = f"Subject: {draft.subject}\n\n{draft.body}"
                QApplication.clipboard().setText(text)

                from qfluentwidgets import InfoBar, InfoBarPosition
                InfoBar.success(
                    title="Copied",
                    content="Email content copied to clipboard.",
                    parent=self,
                    duration=2000,
                    position=InfoBarPosition.TOP
                )
