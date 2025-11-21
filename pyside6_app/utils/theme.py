"""
Theme manager for light/dark mode switching.
"""

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme, setThemeColor, isDarkTheme
from typing import Optional

from ..state.models import ThemeMode


class ThemeManager(QObject):
    """
    Manages application theme (light/dark) with OS integration.

    Signals:
        theme_changed: Emitted when theme changes (bool: is_dark)
    """

    theme_changed = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize theme manager."""
        super().__init__(parent)
        self._current_mode = ThemeMode.AUTO
        self._is_dark = False

    def set_theme(self, mode: ThemeMode) -> None:
        """
        Set theme mode.

        Args:
            mode: Theme mode (auto/light/dark)
        """
        self._current_mode = mode

        if mode == ThemeMode.DARK:
            setTheme(Theme.DARK)
            self._is_dark = True
        elif mode == ThemeMode.LIGHT:
            setTheme(Theme.LIGHT)
            self._is_dark = False
        else:  # AUTO
            # For AUTO mode, detect OS theme
            setTheme(Theme.AUTO)
            # Force check after a brief delay to ensure theme is applied
            QTimer.singleShot(100, lambda: self._update_auto_theme())
            return  # Don't emit signal yet for AUTO mode

        # Force refresh all widgets to apply theme
        app = QApplication.instance()
        if app:
            # Process events to ensure theme is applied
            app.processEvents()
            
            # Update all widgets
            from qfluentwidgets import TableWidget
            for widget in app.allWidgets():
                try:
                    # Skip TableWidget as it has a different update() signature
                    if isinstance(widget, TableWidget):
                        widget.style().unpolish(widget)
                        widget.style().polish(widget)
                        widget.repaint()
                    else:
                        widget.style().unpolish(widget)
                        widget.style().polish(widget)
                        widget.update()
                except Exception:
                    # Some widgets might not support polish/unpolish
                    try:
                        if isinstance(widget, TableWidget):
                            widget.repaint()
                        else:
                            widget.update()
                    except Exception:
                        pass
        
        # Emit signal after theme is set
        QTimer.singleShot(50, lambda: self.theme_changed.emit(self._is_dark))

    def _update_auto_theme(self):
        """Update dark mode status for AUTO theme."""
        self._is_dark = isDarkTheme()
        self.theme_changed.emit(self._is_dark)

    def toggle_theme(self) -> None:
        """Toggle between light and dark mode."""
        # If currently in AUTO mode, determine current state first
        if self._current_mode == ThemeMode.AUTO:
            current_dark = isDarkTheme()
            # Switch to opposite of current
            if current_dark:
                self.set_theme(ThemeMode.LIGHT)
            else:
                self.set_theme(ThemeMode.DARK)
        else:
            # Toggle between light and dark
            if self._is_dark:
                self.set_theme(ThemeMode.LIGHT)
            else:
                self.set_theme(ThemeMode.DARK)

    def is_dark(self) -> bool:
        """Check if currently in dark mode."""
        return self._is_dark

    def get_current_mode(self) -> ThemeMode:
        """Get current theme mode setting."""
        return self._current_mode

    def set_accent_color(self, color: QColor) -> None:
        """
        Set custom accent color.

        Args:
            color: Accent color
        """
        setThemeColor(color)
