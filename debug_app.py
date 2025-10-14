"""Debug script to find QWidget creation issue."""

import sys

print("=== Debug: Import Tracing ===")
print("1. Importing pyside6_app.app module...")

try:
    from pyside6_app.app import main
    print("   [OK] Import successful")

    print("\n2. Calling main()...")
    main()

except Exception as e:
    print(f"   [ERROR] {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
