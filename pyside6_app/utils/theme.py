"""
Theme manager for light/dark mode switching.
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor
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
            setTheme(Theme.AUTO)
            self._is_dark = isDarkTheme()

        self.theme_changed.emit(self._is_dark)

    def toggle_theme(self) -> None:
        """Toggle between light and dark mode."""
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
