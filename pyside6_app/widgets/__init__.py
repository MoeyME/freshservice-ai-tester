"""Widget modules.

NOTE: Widgets are NOT imported at module level to avoid creating QWidgets
before QApplication exists. Import directly from submodules:
    from pyside6_app.widgets.main_window_phase2 import MainWindow
"""

# Do NOT add imports here - they will trigger widget creation before QApplication
__all__ = []
