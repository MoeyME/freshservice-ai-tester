"""Test QApplication scope issue."""
import sys

# Check if QApplication already exists
from PySide6.QtWidgets import QApplication
existing = QApplication.instance()
print(f"Existing QApplication: {existing}")

if existing is None:
    print("Creating new QApplication...")
    app = QApplication(sys.argv)
    print(f"  Created: {app}")
else:
    print("Using existing QApplication")
    app = existing

print("\nNow importing FluentWindow...")
from qfluentwidgets import FluentWindow

print("Creating FluentWindow...")
try:
    window = FluentWindow()
    print("  OK - FluentWindow created!")
    window.show()
    sys.exit(app.exec())
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()
