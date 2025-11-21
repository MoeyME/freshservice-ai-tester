"""
State store with persistence to JSON and signal emission.
"""

import json
import os
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
from PySide6.QtCore import QObject, Signal

from .models import AppState


class StateStore(QObject):
    """
    Central state store with persistence and signals.

    Signals:
        state_changed: Emitted when any state changes
        drafts_changed: Emitted when drafts list changes
        connections_changed: Emitted when connection state changes
        preflight_changed: Emitted when preflight state changes
    """

    # Signals
    state_changed = Signal(AppState)
    drafts_changed = Signal(list)  # List[DraftEmail]
    connections_changed = Signal(object)  # ConnectionsState
    preflight_changed = Signal(object)  # PreflightState

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize state store.

        Args:
            config_dir: Directory for storing state file (default: user's AppData/Roaming)
        """
        super().__init__()

        # Determine config directory
        if config_dir is None:
            appdata = os.getenv('APPDATA')
            if appdata:
                config_dir = Path(appdata) / "ITTicketEmailGenerator"
            else:
                config_dir = Path.home() / ".itticketemailgenerator"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.config_dir / "appstate.json"
        self.backup_file = self.config_dir / "appstate.backup.json"

        # Load or create state
        self._state = self.load() or AppState()

        # Secure in-memory storage for sensitive keys (never saved to disk)
        self._secrets = {}
        self._load_secrets()

        # Debounce timer for auto-save (prevent excessive writes)
        self._save_pending = False

    @property
    def state(self) -> AppState:
        """Get current state (read-only access)."""
        return self._state

    def update_state(self, updater: Callable[[AppState], None]) -> None:
        """
        Update state with a function and emit signals.

        Args:
            updater: Function that modifies the state
        """
        updater(self._state)
        self._state.update_last_modified()

        # Emit signals
        self.state_changed.emit(self._state)
        self._schedule_save()

    def update_drafts(self, updater: Callable[[AppState], None]) -> None:
        """Update drafts and emit specific signal."""
        updater(self._state)
        self._state.update_last_modified()
        self.drafts_changed.emit(self._state.drafts)
        self.state_changed.emit(self._state)
        self._schedule_save()

    def update_connections(self, updater: Callable[[AppState], None]) -> None:
        """Update connections and emit specific signal."""
        updater(self._state)
        self._state.update_last_modified()
        self.connections_changed.emit(self._state.connections)
        self.state_changed.emit(self._state)
        self._schedule_save()

    def update_preflight(self, updater: Callable[[AppState], None]) -> None:
        """Update preflight and emit specific signal."""
        updater(self._state)
        self._state.update_last_modified()
        self.preflight_changed.emit(self._state.preflight)
        self.state_changed.emit(self._state)
        self._schedule_save()

    def _schedule_save(self) -> None:
        """Schedule auto-save (debounced)."""
        if not self._save_pending:
            self._save_pending = True
            # Save immediately for now; can add QTimer for debouncing if needed
            self.save()
            self._save_pending = False

    def save(self) -> None:
        """Save state to JSON file with backup."""
        try:
            # Create backup of existing file
            if self.state_file.exists():
                import shutil
                shutil.copy2(self.state_file, self.backup_file)

            # Write new state
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self._state.to_dict(), f, indent=2, default=str)

        except Exception as e:
            print(f"[ERROR] Failed to save state: {e}")
            # If save failed and we have a backup, restore it
            if self.backup_file.exists():
                import shutil
                shutil.copy2(self.backup_file, self.state_file)

    def load(self) -> Optional[AppState]:
        """Load state from JSON file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AppState.from_dict(data)
        except Exception as e:
            print(f"[WARNING] Failed to load state: {e}")
            # Try loading from backup
            try:
                if self.backup_file.exists():
                    with open(self.backup_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return AppState.from_dict(data)
            except Exception as backup_error:
                print(f"[WARNING] Failed to load backup state: {backup_error}")

        return None

    def reset(self) -> None:
        """Reset state to defaults."""
        self._state = AppState()
        self.state_changed.emit(self._state)
        self.save()

    def _load_secrets(self) -> None:
        """Load sensitive secrets from .env.local file (kept in memory only)."""
        try:
            # Try .env.local first, then .env
            env_file = Path(".env.local") if Path(".env.local").exists() else Path(".env")

            if not env_file.exists():
                return

            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")

                        # Store sensitive keys in memory
                        if key == 'CLAUDE_API_KEY':
                            self._secrets['claude_api_key'] = value
                        elif key == 'FRESHSERVICE_API_KEY':
                            self._secrets['freshservice_api_key'] = value

        except Exception as e:
            print(f"[WARNING] Failed to load secrets: {e}")

    def get_secret(self, key: str) -> Optional[str]:
        """
        Get a secret value from secure memory storage.

        Args:
            key: Secret key (e.g., 'claude_api_key', 'freshservice_api_key')

        Returns:
            Secret value or None if not found
        """
        return self._secrets.get(key)

    def set_secret(self, key: str, value: str) -> None:
        """
        Set a secret value in secure memory storage.

        Args:
            key: Secret key
            value: Secret value
        """
        self._secrets[key] = value

    def migrate_from_env(self, env_file: Path) -> bool:
        """
        Migrate configuration from .env file (one-time migration from tkinter app).

        Args:
            env_file: Path to .env file

        Returns:
            True if migration successful
        """
        try:
            if not env_file.exists():
                return False

            env_vars = {}
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        env_vars[key] = value

            # Migrate to AppState
            if 'CLIENT_ID' in env_vars:
                self._state.connections.microsoft.client_id = env_vars['CLIENT_ID']
            if 'TENANT_ID' in env_vars:
                self._state.connections.microsoft.tenant_id = env_vars['TENANT_ID']
            if 'SENDER_EMAIL' in env_vars:
                self._state.connections.microsoft.sender_email = env_vars['SENDER_EMAIL']
            if 'RECIPIENT_EMAIL' in env_vars:
                self._state.connections.microsoft.recipient_email = env_vars['RECIPIENT_EMAIL']

            # Claude API
            if 'CLAUDE_API_KEY' in env_vars:
                key = env_vars['CLAUDE_API_KEY']
                if key and len(key) >= 4:
                    self._state.connections.claude.api_key_last_four = key[-4:]
                    self._state.connections.claude.is_configured = True

            # Freshservice
            if 'FRESHSERVICE_DOMAIN' in env_vars:
                self._state.connections.freshservice.domain = env_vars['FRESHSERVICE_DOMAIN']
            if 'FRESHSERVICE_API_KEY' in env_vars:
                key = env_vars['FRESHSERVICE_API_KEY']
                if key and len(key) >= 4:
                    self._state.connections.freshservice.api_key_last_four = key[-4:]

            if 'NUM_EMAILS' in env_vars:
                try:
                    self._state.generation.email_count = int(env_vars['NUM_EMAILS'])
                except ValueError:
                    pass
            if 'WAIT_TIME_MS' in env_vars:
                try:
                    self._state.generation.wait_time_ms = int(env_vars['WAIT_TIME_MS'])
                except ValueError:
                    pass

            # Try to migrate ticket counter
            counter_file = env_file.parent / "ticket_counter.json"
            if counter_file.exists():
                try:
                    with open(counter_file, 'r', encoding='utf-8') as f:
                        counter_data = json.load(f)
                        # Old format uses 'last_ticket_number', next is +1
                        last_num = counter_data.get('last_ticket_number', 0)
                        self._state.generation.next_ticket_number = last_num + 1
                except Exception:
                    pass

            self._state.update_last_modified()
            self.save()

            print(f"[OK] Successfully migrated configuration from {env_file}")
            return True

        except Exception as e:
            print(f"[ERROR] Migration failed: {e}")
            return False
