"""Test MainWindow initialization step by step."""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject

# Create QApp first
app = QApplication(sys.argv)
print("QApplication created")

# Import after QApp
from qfluentwidgets import FluentWindow
from pyside6_app.state.store import StateStore
from pyside6_app.utils.theme import ThemeManager

print("Creating StateStore...")
state_store = StateStore()
print("  OK")

print("Creating ThemeManager...")
theme_manager = ThemeManager()
print("  OK")

# Test creating a bare FluentWindow
print("\nTest 1: Create bare FluentWindow...")
try:
    test_window = FluentWindow()
    print("  OK - FluentWindow works!")
    test_window.close()
except Exception as e:
    print(f"  FAILED: {e}")

# Now test our custom MainWindow but with minimal init
print("\nTest 2: Create MainWindow subclass with minimal init...")

class MinimalWindow(FluentWindow):
    def __init__(self):
        print("  - Calling super().__init__()...")
        super().__init__()
        print("  - super().__init__() completed")

try:
    minimal = MinimalWindow()
    print("  OK - MinimalWindow works!")
    minimal.close()
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test with our actual imports
print("\nTest 3: Import and create actual MainWindow...")
try:
    from pyside6_app.widgets.main_window_phase2 import MainWindow
    print("  - Imported MainWindow")

    print("  - Creating MainWindow instance...")
    main_window = MainWindow(state_store, theme_manager)
    print("  OK - MainWindow created!")

    main_window.show()
    sys.exit(app.exec())

except Exception as e:
    print(f"  FAILED: {e}")
    import traceback
    traceback.print_exc()
