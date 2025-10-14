"""Test that Claude API key is retrieved correctly."""
import sys
from PySide6.QtWidgets import QApplication
from pyside6_app.state.store import StateStore
from pyside6_app.widgets.main_window_phase2 import MainWindow
from pyside6_app.utils.theme import ThemeManager

def test_claude_key():
    """Test that _get_claude_key() works correctly."""
    app = QApplication(sys.argv)

    try:
        store = StateStore()
        theme_manager = ThemeManager()

        # Create main window (this would have caused the error before)
        window = MainWindow(store, theme_manager)

        # Test the _get_claude_key method
        claude_key = window._get_claude_key()

        print("[Claude API Key Retrieval]")
        if claude_key:
            print(f"  Key retrieved: {'*' * (len(claude_key) - 4)}{claude_key[-4:]}")
            print(f"  Key length: {len(claude_key)} characters")
            print("[OK] Successfully retrieved Claude API key!")
            return 0
        else:
            print("  No key found (but no error - this is expected if not configured)")
            print("[OK] Method works correctly (returns empty string when no key)")
            return 0

    except AttributeError as e:
        print(f"[ERROR] AttributeError: {e}")
        print("This means the code is still trying to access claude_api_key from wrong object")
        return 1
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        app.quit()

if __name__ == "__main__":
    sys.exit(test_claude_key())
