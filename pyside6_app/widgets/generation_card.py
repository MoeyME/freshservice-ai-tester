"""
Generation settings card for configuring email generation.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QButtonGroup, QLabel
)
from qfluentwidgets import (
    ElevatedCardWidget, SpinBox, RadioButton, SegmentedWidget,
    TextEdit, PushButton, PrimaryPushButton,
    SubtitleLabel, CaptionLabel, InfoBadge, FluentIcon
)

from ..state.store import StateStore
from ..state.models import QualityLevel, GenerationMode


class GenerationCard(ElevatedCardWidget):
    """
    Generation settings card.

    Signals:
        preview_clicked: Emitted when preview button clicked
        generate_clicked: Emitted when generate button clicked
        clear_clicked: Emitted when clear button clicked
    """

    preview_clicked = Signal()
    generate_clicked = Signal()
    clear_clicked = Signal()

    def __init__(self, state_store: StateStore, parent: QWidget = None):
        """
        Initialize generation card.

        Args:
            state_store: Application state store
            parent: Parent widget
        """
        super().__init__(parent)
        self.state_store = state_store

        # Create UI
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = SubtitleLabel("Generation Settings")
        layout.addWidget(header)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setHorizontalSpacing(12)

        # Email count with next ticket number
        email_count_row = QHBoxLayout()
        self.email_count_spinbox = SpinBox()
        self.email_count_spinbox.setRange(1, 1000)
        self.email_count_spinbox.setFixedWidth(120)
        self.email_count_spinbox.setValue(5)  # Set default value
        email_count_row.addWidget(self.email_count_spinbox)

        self.email_count_label = CaptionLabel("emails")
        email_count_row.addWidget(self.email_count_label)

        email_count_row.addSpacing(20)

        self.next_ticket_label = CaptionLabel("")
        email_count_row.addWidget(self.next_ticket_label)
        email_count_row.addStretch()

        form_layout.addRow(CaptionLabel("Count:"), email_count_row)

        # Quality radio buttons
        quality_row = QHBoxLayout()
        self.quality_button_group = QButtonGroup(self)

        self.basic_radio = RadioButton("Basic (7th grade)")
        self.basic_radio.setToolTip("Simple, direct language")
        self.quality_button_group.addButton(self.basic_radio, 0)
        quality_row.addWidget(self.basic_radio)

        self.realistic_radio = RadioButton("Realistic (10th grade)")
        self.realistic_radio.setToolTip("Natural, typical IT user language")
        self.quality_button_group.addButton(self.realistic_radio, 1)
        quality_row.addWidget(self.realistic_radio)

        self.polished_radio = RadioButton("Polished")
        self.polished_radio.setToolTip("Professional, well-written")
        self.quality_button_group.addButton(self.polished_radio, 2)
        quality_row.addWidget(self.polished_radio)

        quality_row.addStretch()
        form_layout.addRow(CaptionLabel("Quality:"), quality_row)

        # Wait time
        wait_time_row = QHBoxLayout()
        self.wait_time_spinbox = SpinBox()
        self.wait_time_spinbox.setRange(0, 60000)
        self.wait_time_spinbox.setValue(10)  # Set default value
        self.wait_time_spinbox.setSingleStep(10)  # Increment by 10ms
        self.wait_time_spinbox.setFixedWidth(120)
        wait_time_row.addWidget(self.wait_time_spinbox)

        wait_time_label = CaptionLabel("milliseconds between emails")
        wait_time_row.addWidget(wait_time_label)
        wait_time_row.addStretch()

        form_layout.addRow(CaptionLabel("Delay:"), wait_time_row)

        # Mode segmented widget with description
        mode_row = QVBoxLayout()
        self.mode_segment = SegmentedWidget()
        self.mode_segment.addItem("guided", "Guided (from categories)", onClick=None)
        self.mode_segment.addItem("custom", "Custom (free-form prompt)", onClick=None)
        self.mode_segment.setFixedWidth(500)
        mode_row.addWidget(self.mode_segment)

        self.mode_description = CaptionLabel("Guided: Generate tickets based on categories from CSV file")
        self.mode_description.setWordWrap(True)
        mode_row.addWidget(self.mode_description)

        form_layout.addRow(CaptionLabel("Mode:"), mode_row)

        layout.addLayout(form_layout)

        # Custom prompt area (shown when custom mode)
        self.custom_prompt_container = QWidget()
        custom_prompt_layout = QVBoxLayout(self.custom_prompt_container)
        custom_prompt_layout.setContentsMargins(0, 0, 0, 0)
        custom_prompt_layout.setSpacing(8)

        custom_header_row = QHBoxLayout()
        custom_header_row.addWidget(CaptionLabel("Custom Prompt:"))
        custom_header_row.addStretch()

        self.lint_prompt_button = PushButton("Lint Prompt", self)
        self.lint_prompt_button.setIcon(FluentIcon.SEARCH)
        custom_header_row.addWidget(self.lint_prompt_button)

        custom_prompt_layout.addLayout(custom_header_row)

        self.custom_prompt_text = TextEdit()
        self.custom_prompt_text.setPlaceholderText(
            "Example: Generate tickets about printer issues where users are "
            "frustrated because printing is urgent for customer quotes..."
        )
        self.custom_prompt_text.setFixedHeight(100)
        custom_prompt_layout.addWidget(self.custom_prompt_text)

        self.char_count_label = CaptionLabel("0 / 5000 characters")
        custom_prompt_layout.addWidget(self.char_count_label)

        layout.addWidget(self.custom_prompt_container)
        self.custom_prompt_container.setVisible(False)  # Hidden by default

        # Action buttons
        button_row = QHBoxLayout()

        self.preview_button = PushButton("Preview")
        self.preview_button.setIcon(FluentIcon.VIEW)
        button_row.addWidget(self.preview_button)

        self.generate_button = PrimaryPushButton("Generate Draft")
        self.generate_button.setIcon(FluentIcon.SEND)
        button_row.addWidget(self.generate_button)

        self.clear_button = PushButton("Clear")
        self.clear_button.setIcon(FluentIcon.DELETE)
        button_row.addWidget(self.clear_button)

        button_row.addStretch()

        layout.addLayout(button_row)

        # Load initial state
        self._load_from_state()

        # Connect signals
        self._init_connections()

    def _init_connections(self):
        """Initialize signal connections."""
        # Input changes -> update state
        self.email_count_spinbox.valueChanged.connect(self._on_email_count_changed)
        self.basic_radio.toggled.connect(lambda: self._on_quality_changed(QualityLevel.BASIC))
        self.realistic_radio.toggled.connect(lambda: self._on_quality_changed(QualityLevel.REALISTIC))
        self.polished_radio.toggled.connect(lambda: self._on_quality_changed(QualityLevel.POLISHED))
        self.wait_time_spinbox.valueChanged.connect(self._on_wait_time_changed)
        self.mode_segment.currentItemChanged.connect(self._on_mode_changed)
        self.custom_prompt_text.textChanged.connect(self._on_custom_prompt_changed)

        # Buttons
        self.preview_button.clicked.connect(self.preview_clicked.emit)
        self.generate_button.clicked.connect(self.generate_clicked.emit)
        self.clear_button.clicked.connect(self.clear_clicked.emit)
        self.lint_prompt_button.clicked.connect(self._on_lint_prompt)

        # State changes
        self.state_store.state_changed.connect(self._on_state_changed)

    def _load_from_state(self):
        """Load values from state."""
        gen = self.state_store.state.generation

        self.email_count_spinbox.setValue(gen.email_count)
        self.wait_time_spinbox.setValue(gen.wait_time_ms)

        # Quality
        if gen.quality == QualityLevel.BASIC:
            self.basic_radio.setChecked(True)
        elif gen.quality == QualityLevel.REALISTIC:
            self.realistic_radio.setChecked(True)
        else:
            self.polished_radio.setChecked(True)

        # Mode
        if gen.mode == GenerationMode.GUIDED:
            self.mode_segment.setCurrentItem("guided")
        else:
            self.mode_segment.setCurrentItem("custom")

        # Custom prompt
        self.custom_prompt_text.setPlainText(gen.custom_prompt)

        # Update UI
        self._update_next_ticket_label()
        self._update_char_count()

    def _update_next_ticket_label(self):
        """Update next ticket number label."""
        next_num = self.state_store.state.generation.next_ticket_number
        self.next_ticket_label.setText(f"Next: #{next_num}")

    def _update_char_count(self):
        """Update character count label."""
        text = self.custom_prompt_text.toPlainText()
        count = len(text)
        self.char_count_label.setText(f"{count} / 5000 characters")

        # Warn if approaching limit
        if count > 4500:
            self.char_count_label.setStyleSheet("color: orange;")
        elif count >= 5000:
            self.char_count_label.setStyleSheet("color: red;")
        else:
            self.char_count_label.setStyleSheet("")

    def _on_email_count_changed(self, value: int):
        """Handle email count change."""
        self.state_store.update_state(
            lambda s: setattr(s.generation, 'email_count', value)
        )

    def _on_quality_changed(self, quality: QualityLevel):
        """Handle quality change."""
        self.state_store.update_state(
            lambda s: setattr(s.generation, 'quality', quality)
        )

    def _on_wait_time_changed(self, value: int):
        """Handle wait time change."""
        self.state_store.update_state(
            lambda s: setattr(s.generation, 'wait_time_ms', value)
        )

    def _on_mode_changed(self, key: str):
        """Handle mode change."""
        mode = GenerationMode.CUSTOM if key == "custom" else GenerationMode.GUIDED

        self.state_store.update_state(
            lambda s: setattr(s.generation, 'mode', mode)
        )

        # Update description
        if mode == GenerationMode.GUIDED:
            self.mode_description.setText("Guided: Generate tickets based on categories from CSV file")
        else:
            self.mode_description.setText("Custom: Generate tickets based on your custom prompt below")

        # Show/hide custom prompt area
        self.custom_prompt_container.setVisible(mode == GenerationMode.CUSTOM)

    def _on_custom_prompt_changed(self):
        """Handle custom prompt text change."""
        text = self.custom_prompt_text.toPlainText()

        # Truncate if exceeds limit
        if len(text) > 5000:
            text = text[:5000]
            self.custom_prompt_text.setPlainText(text)
            cursor = self.custom_prompt_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.custom_prompt_text.setTextCursor(cursor)

        self.state_store.update_state(
            lambda s: setattr(s.generation, 'custom_prompt', text)
        )

        self._update_char_count()

    def _on_lint_prompt(self):
        """Lint custom prompt for issues."""
        text = self.custom_prompt_text.toPlainText()

        issues = []

        # Check length
        if len(text) < 20:
            issues.append("Prompt too short (min 20 characters)")

        # Check for forbidden terms (example heuristic)
        forbidden = ["hack", "exploit", "malicious", "destroy", "delete database"]
        for term in forbidden:
            if term.lower() in text.lower():
                issues.append(f"Contains forbidden term: '{term}'")

        # Check for placeholder text
        if "Example:" in text or "..." in text:
            issues.append("Contains placeholder text")

        # Show results
        if issues:
            from qfluentwidgets import MessageBox
            MessageBox(
                "Prompt Issues Found",
                "\n".join(f"• {issue}" for issue in issues),
                self
            ).exec()
        else:
            from qfluentwidgets import InfoBar, InfoBarPosition
            InfoBar.success(
                title="Prompt OK",
                content="No issues found with custom prompt.",
                parent=self,
                duration=2000,
                position=InfoBarPosition.TOP_RIGHT
            )

    def _on_state_changed(self, state):
        """Handle state changes."""
        self._update_next_ticket_label()

    def set_generation_enabled(self, enabled: bool):
        """Enable/disable generation controls."""
        self.preview_button.setEnabled(enabled)
        self.generate_button.setEnabled(enabled)
