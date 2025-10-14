"""Test QApplication.instance() after creation."""
import sys
from PySide6.QtWidgets import QApplication

print("Step 1: Check for existing QApplication")
existing = QApplication.instance()
print(f"  Result: {existing}")

print("\nStep 2: Create QApplication")
app = QApplication(sys.argv)
print(f"  Created: {app}")

print("\nStep 3: Check instance again")
instance = QApplication.instance()
print(f"  Result: {instance}")
print(f"  Same object? {instance is app}")

print("\nStep 4: Import our widgets")
from pyside6_app.widgets.main_window_phase2 import MainWindow
print("  Imported MainWindow")

print("\nStep 5: Check instance one more time")
instance2 = QApplication.instance()
print(f"  Result: {instance2}")
print(f"  Still same? {instance2 is app}")

print("\nStep 6: Create StateStore and ThemeManager")
from pyside6_app.state.store import StateStore
from pyside6_app.utils.theme import ThemeManager
state_store = StateStore()
theme_manager = ThemeManager()
print("  Created successfully")

print("\nStep 7: Try creating MainWindow")
try:
    main_window = MainWindow(state_store, theme_manager)
    print("  SUCCESS!")
    main_window.show()
    sys.exit(app.exec())
except Exception as e:
    print(f"  FAILED: {e}")
    import traceback
    traceback.print_exc()
