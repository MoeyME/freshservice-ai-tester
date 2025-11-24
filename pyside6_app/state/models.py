"""
Pydantic models for application state management.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
import re


class ThemeMode(str, Enum):
    """Theme mode options."""
    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


class QualityLevel(str, Enum):
    """Email quality levels."""
    BASIC = "basic"
    REALISTIC = "realistic"
    POLISHED = "polished"


class GenerationMode(str, Enum):
    """Generation mode."""
    GUIDED = "guided"
    CUSTOM = "custom"


class EmailStatus(str, Enum):
    """Email draft status."""
    DRAFT = "draft"
    READY = "ready"
    SENT = "sent"
    ERROR = "error"


class TicketType(str, Enum):
    """Ticket type options."""
    INCIDENT = "Incident"
    SERVICE_REQUEST = "Service Request"


class WindowGeometry(BaseModel):
    """Window position and size."""
    x: int = 100
    y: int = 100
    width: int = Field(default=1600, ge=1280)
    height: int = Field(default=900, ge=720)


class UIState(BaseModel):
    """UI-specific state."""
    theme: ThemeMode = ThemeMode.AUTO
    window_geometry: WindowGeometry = Field(default_factory=WindowGeometry)
    left_dock_width: int = Field(default=280, ge=200, le=400)
    right_rail_width: int = Field(default=320, ge=200, le=500)
    activity_log_collapsed: bool = False


class MicrosoftConnection(BaseModel):
    """Microsoft 365 connection state."""
    client_id: str = ""
    tenant_id: str = ""
    sender_email: str = ""
    recipient_email: str = ""
    token_expiry: Optional[datetime] = None
    is_authenticated: bool = False

    @field_validator('client_id', 'tenant_id')
    @classmethod
    def validate_guid(cls, v: str) -> str:
        """Validate GUID format."""
        if v and not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v, re.IGNORECASE):
            raise ValueError('Invalid GUID format')
        return v

    @field_validator('sender_email', 'recipient_email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format (allow empty)."""
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class ClaudeConnection(BaseModel):
    """Claude API connection state."""
    api_key_last_four: str = ""
    is_configured: bool = False


class FreshserviceConnection(BaseModel):
    """Freshservice connection state."""
    domain: str = ""
    api_key_last_four: str = ""
    is_connected: bool = False
    last_test_time: Optional[datetime] = None

    @field_validator('domain')
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate Freshservice domain format."""
        if v and not re.match(r'^[a-z0-9-]+\.freshservice\.com$', v):
            raise ValueError('Invalid Freshservice domain format')
        return v


class ConnectionsState(BaseModel):
    """All connection states."""
    microsoft: MicrosoftConnection = Field(default_factory=MicrosoftConnection)
    claude: ClaudeConnection = Field(default_factory=ClaudeConnection)
    freshservice: FreshserviceConnection = Field(default_factory=FreshserviceConnection)


class GenerationSettings(BaseModel):
    """Email generation settings."""
    email_count: int = Field(default=5, ge=1, le=1000)
    quality: QualityLevel = QualityLevel.REALISTIC
    wait_time_ms: int = Field(default=10, ge=0, le=5000)
    mode: GenerationMode = GenerationMode.GUIDED
    custom_prompt: str = Field(default="", max_length=5000)
    next_ticket_number: int = Field(default=1, ge=1)


class DraftEmail(BaseModel):
    """Individual email draft."""
    id: int
    type: TicketType
    priority: str  # Priority 1-4
    category: str
    subcategory: str = ""
    item: str = ""
    subject: str
    body: str
    recipient: EmailStr
    status: EmailStatus = EmailStatus.DRAFT
    error_message: Optional[str] = None
    sent_timestamp: Optional[datetime] = None


class PreflightState(BaseModel):
    """Preflight check state."""
    auth_checked: bool = False
    fs_checked: bool = False
    drafts_checked: bool = False
    dry_run_checked: bool = False
    rate_limit_checked: bool = False
    all_passed: bool = False


class NetworkSettings(BaseModel):
    """Network configuration."""
    proxy_enabled: bool = False
    proxy_url: Optional[str] = None
    request_timeout_ms: int = Field(default=30000, ge=1000)
    retry_attempts: int = Field(default=3, ge=0, le=5)


class PrivacySettings(BaseModel):
    """Privacy and data settings."""
    safe_mode: bool = False
    telemetry_enabled: bool = False


class GeneralSettings(BaseModel):
    """General application settings."""
    launch_on_startup: bool = False
    language: str = "en-US"


class AppSettings(BaseModel):
    """Application settings."""
    general: GeneralSettings = Field(default_factory=GeneralSettings)
    network: NetworkSettings = Field(default_factory=NetworkSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)


class SendBatchHistory(BaseModel):
    """Historical send batch record."""
    batch_id: str
    timestamp: datetime
    emails_sent: int
    emails_succeeded: int
    emails_failed: int
    recipient: EmailStr


class AppState(BaseModel):
    """Root application state model."""
    model_config = ConfigDict(validate_assignment=True)

    version: str = "2.0.0"
    last_modified: datetime = Field(default_factory=datetime.now)
    first_run_complete: bool = False  # Set to True after onboarding
    ui: UIState = Field(default_factory=UIState)
    connections: ConnectionsState = Field(default_factory=ConnectionsState)
    generation: GenerationSettings = Field(default_factory=GenerationSettings)
    drafts: List[DraftEmail] = Field(default_factory=list)
    preflight: PreflightState = Field(default_factory=PreflightState)
    settings: AppSettings = Field(default_factory=AppSettings)
    history: List[SendBatchHistory] = Field(default_factory=list, max_length=100)

    def update_last_modified(self) -> None:
        """Update the last modified timestamp."""
        self.last_modified = datetime.now()

    def add_draft(self, draft: DraftEmail) -> None:
        """Add a draft email."""
        self.drafts.append(draft)
        self.update_last_modified()

    def clear_drafts(self) -> None:
        """Clear all drafts."""
        self.drafts.clear()
        self.preflight.drafts_checked = False
        self.preflight.all_passed = False
        self.update_last_modified()

    def get_draft_by_id(self, draft_id: int) -> Optional[DraftEmail]:
        """Get draft by ID."""
        for draft in self.drafts:
            if draft.id == draft_id:
                return draft
        return None

    def update_draft_status(self, draft_id: int, status: EmailStatus, error_message: Optional[str] = None) -> None:
        """Update draft status."""
        draft = self.get_draft_by_id(draft_id)
        if draft:
            draft.status = status
            draft.error_message = error_message
            if status == EmailStatus.SENT:
                draft.sent_timestamp = datetime.now()
            self.update_last_modified()

    def add_history(self, batch: SendBatchHistory) -> None:
        """Add send batch to history."""
        self.history.append(batch)
        # Keep only last 100
        if len(self.history) > 100:
            self.history = self.history[-100:]
        self.update_last_modified()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppState':
        """Create from dictionary."""
        return cls.model_validate(data)
