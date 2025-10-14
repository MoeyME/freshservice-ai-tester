"""Test that the application can start without errors."""
import sys
from pyside6_app.app import Application

def test_startup():
    """Test application initialization."""
    try:
        print("Creating Application instance...")
        app = Application()
        print("[OK] Application created successfully")
        print("[OK] Main window created:", app.main_window is not None)
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to create application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_startup())
