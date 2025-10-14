"""
Main application bootstrap.
"""

import sys
import traceback
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from .state.store import StateStore
from .utils.theme import ThemeManager


class Application:
    """Main application controller."""

    def __init__(self):
        """Initialize application."""
        # Create QApplication
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("IT Ticket Email Generator")
        self.qt_app.setOrganizationName("Dahlsens")
        self.qt_app.setApplicationVersion("2.0.0")

        # High DPI support
        self.qt_app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        self.qt_app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

        # Initialize state store
        self.state_store = StateStore()

        # Check for migration from tkinter app
        env_file = Path(".env.local") if Path(".env.local").exists() else Path(".env")
        if env_file.exists() and not (self.state_store.config_dir / "appstate.json").exists():
            print(f"[INFO] Detected {env_file.name} file. Attempting migration...")
            if self.state_store.migrate_from_env(env_file):
                print("[OK] Migration successful!")
            else:
                print("[WARNING] Migration failed. Starting with defaults.")

        # Initialize theme manager
        self.theme_manager = ThemeManager()

        # Import MainWindow after QApplication is created
        from .widgets.main_window_phase2 import MainWindow

        # Create main window
        self.main_window = MainWindow(self.state_store, self.theme_manager)

        # Set up exception handling
        sys.excepthook = self._exception_handler

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Exit code
        """
        try:
            self.main_window.show()
            return self.qt_app.exec()
        except Exception as e:
            self._show_error_dialog(
                "Application Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\nThe application will now exit."
            )
            return 1

    def _exception_handler(self, exc_type, exc_value, exc_traceback):
        """
        Global exception handler.

        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        # Format traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = ''.join(tb_lines)

        # Log to file
        log_file = self.state_store.config_dir / "crash.log"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Crash at: {Path.now().isoformat()}\n")
                f.write(tb_text)
                f.write(f"{'='*80}\n")
        except Exception:
            pass

        # Show error dialog
        self._show_error_dialog(
            "Critical Error",
            f"A critical error occurred:\n\n{exc_value}\n\n"
            f"Details have been saved to:\n{log_file}\n\n"
            "The application will now exit."
        )

        sys.exit(1)

    def _show_error_dialog(self, title: str, message: str):
        """
        Show error message dialog.

        Args:
            title: Dialog title
            message: Error message
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


def main():
    """Main entry point."""
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
