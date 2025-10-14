"""Minimal test to find QWidget issue."""
import sys

# Test 1: Can we import PySide6?
print("Test 1: Import PySide6")
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
print("  OK")

# Test 2: Can we import qfluentwidgets before QApp?
print("Test 2: Import qfluentwidgets (NO QApp yet)")
try:
    from qfluentwidgets import Theme, setTheme
    print("  OK - qfluentwidgets imported without QApp")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 3: Create QApplication
print("Test 3: Create QApplication")
app = QApplication(sys.argv)
print("  OK")

# Test 4: Import state/theme
print("Test 4: Import state modules")
from pyside6_app.state.store import StateStore
from pyside6_app.utils.theme import ThemeManager
print("  OK")

# Test 5: Import widgets
print("Test 5: Import main window")
from pyside6_app.widgets.main_window_phase2 import MainWindow
print("  OK")

# Test 6: Create instances
print("Test 6: Create state store")
state_store = StateStore()
print("  OK")

print("Test 7: Create theme manager")
theme_manager = ThemeManager()
print("  OK")

print("Test 8: Create main window")
main_window = MainWindow(state_store, theme_manager)
print("  OK")

print("Test 9: Show window")
main_window.show()
print("  OK")

print("\nAll tests passed! Window should be visible.")
print("Press Ctrl+C to exit")

sys.exit(app.exec())
