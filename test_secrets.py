"""Test that secrets are loaded from .env.local."""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from pyside6_app.state.store import StateStore

def test_secrets():
    """Test that API keys are loaded into secure memory."""
    app = QApplication(sys.argv)

    try:
        store = StateStore()

        # Check secrets in memory
        claude_key = store.get_secret('claude_api_key')
        fs_key = store.get_secret('freshservice_api_key')

        print("[Secrets in Memory]")
        print(f"  Claude API Key: {'*' * (len(claude_key) - 4) + claude_key[-4:] if claude_key else 'Not found'}")
        print(f"  Freshservice API Key: {'*' * (len(fs_key) - 4) + fs_key[-4:] if fs_key else 'Not found'}")

        # Check state (should only have last 4 chars)
        print("\n[State Storage (appstate.json)]")
        print(f"  Claude last 4: {store.state.connections.claude.api_key_last_four}")
        print(f"  Claude configured: {store.state.connections.claude.is_configured}")
        print(f"  Freshservice last 4: {store.state.connections.freshservice.api_key_last_four}")

        if claude_key and fs_key:
            print("\n[OK] All secrets loaded successfully!")
            return 0
        else:
            print("\n[ERROR] Some secrets missing!")
            return 1

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        app.quit()

if __name__ == "__main__":
    sys.exit(test_secrets())
