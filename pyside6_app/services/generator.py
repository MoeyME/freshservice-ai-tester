"""
Async wrapper for content generation service.
"""

import sys
import os
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Slot

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from content_generator import ContentGenerator
from utils import read_categories, read_priorities_and_types, generate_distribution
from ..state.models import DraftEmail, EmailStatus, TicketType, QualityLevel


class GeneratorWorker(QRunnable):
    """
    Worker for async email generation.

    Signals are emitted via a Signals object since QRunnable doesn't inherit QObject.
    """

    class Signals(QObject):
        """Signals for generator worker."""
        draft_generated = Signal(DraftEmail)
        progress_updated = Signal(int, int)  # current, total
        generation_complete = Signal()
        error_occurred = Signal(str)

    def __init__(self, api_key: str, settings: dict, categories: list, priorities: list, types: list):
        """
        Initialize generator worker.

        Args:
            api_key: Claude API key
            settings: Generation settings dict
            categories: List of categories
            priorities: List of priorities
            types: List of ticket types
        """
        super().__init__()
        self.signals = self.Signals()
        self.api_key = api_key
        self.settings = settings
        self.categories = categories
        self.priorities = priorities
        self.types = types
        self._is_cancelled = False

    def cancel(self):
        """Request cancellation."""
        self._is_cancelled = True

    @Slot()
    def run(self):
        """Run generation in background thread."""
        try:
            # Create generator
            quality_map = {
                QualityLevel.BASIC: "basic",
                QualityLevel.REALISTIC: "realistic",
                QualityLevel.POLISHED: "polished"
            }
            quality = quality_map.get(self.settings['quality'], "realistic")

            generator = ContentGenerator(
                api_key=self.api_key,
                temperature=0.85,
                writing_quality=quality
            )

            email_count = self.settings['email_count']
            wait_time_ms = self.settings['wait_time_ms']
            next_ticket_num = self.settings['next_ticket_number']
            recipient = self.settings['recipient_email']
            custom_prompt = self.settings.get('custom_prompt', '')
            use_custom = self.settings['mode'] == 'custom' and custom_prompt

            # Generate distribution if not using custom mode
            if not use_custom:
                distribution = generate_distribution(
                    email_count,
                    self.categories,
                    self.priorities,
                    self.types
                )
            else:
                # For custom mode, create dummy distribution
                distribution = [
                    {
                        "category": "Custom",
                        "subcategory": "",
                        "item": "",
                        "priority": "Priority 3",
                        "type": "Incident"
                    }
                    for _ in range(email_count)
                ]

            # Generate emails
            for i, item in enumerate(distribution):
                if self._is_cancelled:
                    return

                ticket_num = next_ticket_num + i

                try:
                    # Generate content
                    if use_custom:
                        subject, body = generator.generate_email_content(
                            category="Custom",
                            subcategory="",
                            item="",
                            priority=item["priority"],
                            ticket_type=item["type"],
                            ticket_number=ticket_num,
                            custom_instructions=custom_prompt,
                            ticket_index=i + 1,
                            total_tickets=email_count
                        )
                    else:
                        subject, body = generator.generate_email_content(
                            category=item["category"],
                            subcategory=item.get("subcategory", ""),
                            item=item.get("item", ""),
                            priority=item["priority"],
                            ticket_type=item["type"],
                            ticket_number=ticket_num
                        )

                    # Create draft
                    draft = DraftEmail(
                        id=ticket_num,
                        type=TicketType.INCIDENT if item["type"] == "Incident" else TicketType.SERVICE_REQUEST,
                        priority=item["priority"],
                        category=item["category"],
                        subcategory=item.get("subcategory", ""),
                        item=item.get("item", ""),
                        subject=subject,
                        body=body,
                        recipient=recipient,
                        status=EmailStatus.DRAFT
                    )

                    # Emit draft generated signal
                    self.signals.draft_generated.emit(draft)

                    # Emit progress
                    self.signals.progress_updated.emit(i + 1, email_count)

                    # Wait between generations
                    if wait_time_ms > 0 and i < email_count - 1:
                        import time
                        time.sleep(wait_time_ms / 1000.0)

                except Exception as e:
                    # Emit error for this specific draft
                    error_msg = f"Failed to generate ticket #{ticket_num}: {str(e)}"
                    self.signals.error_occurred.emit(error_msg)

            # Complete
            self.signals.generation_complete.emit()

        except Exception as e:
            self.signals.error_occurred.emit(f"Generation failed: {str(e)}")


class GeneratorService(QObject):
    """
    Service for async email generation.

    Signals:
        draft_generated: Emitted when a draft is generated (DraftEmail)
        progress_updated: Emitted on progress (current: int, total: int)
        generation_complete: Emitted when all generation complete
        error_occurred: Emitted on error (error_message: str)
    """

    draft_generated = Signal(DraftEmail)
    progress_updated = Signal(int, int)
    generation_complete = Signal()
    error_occurred = Signal(str)

    def __init__(self, parent: QObject = None):
        """Initialize generator service."""
        super().__init__(parent)
        self.thread_pool = QThreadPool.globalInstance()
        self.current_worker = None

    def generate_drafts(self, api_key: str, settings: dict) -> bool:
        """
        Start async draft generation.

        Args:
            api_key: Claude API key
            settings: Generation settings (email_count, quality, mode, etc.)

        Returns:
            True if generation started successfully
        """
        try:
            # Load categories and priorities
            categories = read_categories()
            priorities_data = read_priorities_and_types()
            priorities = priorities_data['priorities']
            types = priorities_data['types']

            # Create worker
            self.current_worker = GeneratorWorker(
                api_key=api_key,
                settings=settings,
                categories=categories,
                priorities=priorities,
                types=types
            )

            # Connect signals
            self.current_worker.signals.draft_generated.connect(self.draft_generated.emit)
            self.current_worker.signals.progress_updated.connect(self.progress_updated.emit)
            self.current_worker.signals.generation_complete.connect(self.generation_complete.emit)
            self.current_worker.signals.error_occurred.connect(self.error_occurred.emit)

            # Start in thread pool
            self.thread_pool.start(self.current_worker)

            return True

        except Exception as e:
            self.error_occurred.emit(f"Failed to start generation: {str(e)}")
            return False

    def generate_preview(self, api_key: str, settings: dict) -> bool:
        """
        Generate preview (3 sample emails).

        Args:
            api_key: Claude API key
            settings: Generation settings

        Returns:
            True if preview started successfully
        """
        # Override email count to 3 for preview
        preview_settings = settings.copy()
        preview_settings['email_count'] = 3

        return self.generate_drafts(api_key, preview_settings)

    def cancel_generation(self):
        """Cancel current generation."""
        if self.current_worker:
            self.current_worker.cancel()
            self.current_worker = None
