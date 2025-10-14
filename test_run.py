import sys
print("Starting app test...")
try:
    from pyside6_app.app import main
    print("Imported main successfully")
    main()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
