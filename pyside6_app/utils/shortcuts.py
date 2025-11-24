"""
Keyboard shortcut definitions and setup.
"""

from typing import Dict, Callable, List
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget


# Shortcut definitions: name -> (key_sequence, description)
SHORTCUTS = {
    'generate': ('Ctrl+G', 'Generate draft emails'),
    'preview': ('Ctrl+P', 'Generate preview (3 samples)'),
    'send': ('Ctrl+Return', 'Send ready emails'),
    'export': ('Ctrl+E', 'Export drafts to CSV'),
    'select_all': ('Ctrl+A', 'Select all drafts'),
    'clear_selection': ('Escape', 'Clear selection / Close panel'),
    'toggle_theme': ('Ctrl+T', 'Toggle light/dark theme'),
    'help': ('F1', 'Open help'),
    'settings': ('Ctrl+,', 'Open settings'),
    'close_sheet': ('Escape', 'Close detail panel'),
    'refresh': ('F5', 'Refresh current view'),
    'authenticate': ('Ctrl+Shift+A', 'Authenticate with Microsoft'),
}


def setup_shortcuts(window: QWidget, handlers: Dict[str, Callable]) -> List[QShortcut]:
    """
    Set up keyboard shortcuts for the application.

    Args:
        window: Main window widget
        handlers: Dictionary mapping shortcut names to handler functions

    Returns:
        List of QShortcut objects (keep references to prevent garbage collection)
    """
    shortcuts = []

    for name, (key_seq, description) in SHORTCUTS.items():
        if name in handlers:
            shortcut = QShortcut(QKeySequence(key_seq), window)
            shortcut.activated.connect(handlers[name])
            shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
            shortcuts.append(shortcut)

    return shortcuts


def get_shortcut_text(name: str) -> str:
    """
    Get the key sequence text for a shortcut.

    Args:
        name: Shortcut name

    Returns:
        Key sequence string (e.g., "Ctrl+G") or empty string if not found
    """
    if name in SHORTCUTS:
        return SHORTCUTS[name][0]
    return ""


def get_shortcut_description(name: str) -> str:
    """
    Get the description for a shortcut.

    Args:
        name: Shortcut name

    Returns:
        Description string or empty string if not found
    """
    if name in SHORTCUTS:
        return SHORTCUTS[name][1]
    return ""


def format_tooltip_with_shortcut(text: str, shortcut_name: str) -> str:
    """
    Format a tooltip to include the keyboard shortcut.

    Args:
        text: Base tooltip text
        shortcut_name: Name of the shortcut

    Returns:
        Formatted tooltip with shortcut (e.g., "Generate drafts (Ctrl+G)")
    """
    shortcut = get_shortcut_text(shortcut_name)
    if shortcut:
        return f"{text} ({shortcut})"
    return text


def get_all_shortcuts() -> Dict[str, tuple]:
    """
    Get all available shortcuts.

    Returns:
        Dictionary of all shortcuts with their key sequences and descriptions
    """
    return SHORTCUTS.copy()
