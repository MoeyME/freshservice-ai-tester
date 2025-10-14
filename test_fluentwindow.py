"""Test FluentWindow creation."""
import sys
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow

print("Creating QApplication...")
app = QApplication(sys.argv)
print("  OK")

print("Creating FluentWindow...")
window = FluentWindow()
print("  OK")

print("Setting window title...")
window.setWindowTitle("Test")
print("  OK")

print("Success!")
window.show()
sys.exit(app.exec())
