"""Test migration from .env.local file."""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from pyside6_app.state.store import StateStore

def test_migration():
    """Test that migration loads all config from .env.local."""
    app = QApplication(sys.argv)

    try:
        # Create state store
        store = StateStore()

        # Manually trigger migration from .env.local
        env_file = Path(".env.local")
        if env_file.exists():
            print(f"[INFO] Running migration from {env_file}...")
            if store.migrate_from_env(env_file):
                print("[OK] Migration successful!")
            else:
                print("[ERROR] Migration failed!")
                return 1
        else:
            print("[ERROR] .env.local file not found!")
            return 1

        # Check if appstate.json exists now
        appstate_file = store.config_dir / "appstate.json"
        print(f"\n[INFO] AppState file: {appstate_file}")
        print(f"[INFO] File exists: {appstate_file.exists()}")

        # Check migrated values
        state = store.state

        print("\n[Microsoft 365 Configuration]")
        print(f"  Client ID: {state.connections.microsoft.client_id}")
        print(f"  Tenant ID: {state.connections.microsoft.tenant_id}")
        print(f"  Sender: {state.connections.microsoft.sender_email}")
        print(f"  Recipient: {state.connections.microsoft.recipient_email}")

        print("\n[Claude API Configuration]")
        print(f"  API Key (last 4): {state.connections.claude.api_key_last_four}")
        print(f"  Is Configured: {state.connections.claude.is_configured}")

        print("\n[Freshservice Configuration]")
        print(f"  Domain: {state.connections.freshservice.domain}")
        print(f"  API Key (last 4): {state.connections.freshservice.api_key_last_four}")

        # Validation
        errors = []
        if not state.connections.microsoft.client_id:
            errors.append("Missing Client ID")
        if not state.connections.microsoft.tenant_id:
            errors.append("Missing Tenant ID")
        if not state.connections.microsoft.sender_email:
            errors.append("Missing Sender Email")
        if not state.connections.microsoft.recipient_email:
            errors.append("Missing Recipient Email")
        if not state.connections.claude.api_key_last_four:
            errors.append("Missing Claude API Key")
        if not state.connections.freshservice.domain:
            errors.append("Missing Freshservice Domain")

        if errors:
            print("\n[ERRORS]")
            for error in errors:
                print(f"  - {error}")
            return 1
        else:
            print("\n[OK] All configuration loaded successfully!")
            return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        app.quit()

if __name__ == "__main__":
    sys.exit(test_migration())
