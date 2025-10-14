"""Test the PySide6 app initialization."""

import sys
import traceback

try:
    print("1. Importing PySide6...")
    from PySide6.QtWidgets import QApplication
    print("   [OK] PySide6 imported")

    print("2. Importing StateStore...")
    from pyside6_app.state.store import StateStore
    print("   [OK] StateStore imported")

    print("3. Importing ThemeManager...")
    from pyside6_app.utils.theme import ThemeManager
    print("   [OK] ThemeManager imported")

    print("4. Importing MainWindow...")
    from pyside6_app.widgets.main_window_phase2 import MainWindow
    print("   [OK] MainWindow imported")

    print("5. Creating QApplication...")
    app = QApplication(sys.argv)
    print("   [OK] QApplication created")

    print("6. Creating StateStore...")
    state_store = StateStore()
    print(f"   [OK] StateStore created (config dir: {state_store.config_dir})")

    print("7. Creating ThemeManager...")
    theme_manager = ThemeManager()
    print("   [OK] ThemeManager created")

    print("8. Creating MainWindow...")
    main_window = MainWindow(state_store, theme_manager)
    print("   [OK] MainWindow created")

    print("9. Showing MainWindow...")
    main_window.show()
    print("   [OK] MainWindow shown")

    print("\n[SUCCESS] All initialization steps completed successfully!")
    print("Window should now be visible. Press Ctrl+C to exit.\n")

    sys.exit(app.exec())

except Exception as e:
    print(f"\n[ERROR] Error during initialization:")
    print(f"  {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
