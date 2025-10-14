"""Test Generation Card UI improvements."""
import sys
from PySide6.QtWidgets import QApplication
from pyside6_app.state.store import StateStore
from pyside6_app.widgets.generation_card import GenerationCard

def test_ui():
    """Test that Generation Card displays correctly."""
    app = QApplication(sys.argv)

    try:
        store = StateStore()
        card = GenerationCard(store)

        # Check widgets exist
        print("[UI Components]")
        print(f"  Email count spinbox: {card.email_count_spinbox is not None}")
        print(f"  Email count label: {card.email_count_label is not None}")
        print(f"  Wait time spinbox: {card.wait_time_spinbox is not None}")
        print(f"  Mode segment: {card.mode_segment is not None}")
        print(f"  Mode description: {card.mode_description is not None}")

        # Check values
        print("\n[Current Values]")
        print(f"  Email count: {card.email_count_spinbox.value()}")
        print(f"  Email count range: {card.email_count_spinbox.minimum()} - {card.email_count_spinbox.maximum()}")
        print(f"  Wait time: {card.wait_time_spinbox.value()} ms")
        print(f"  Wait time range: {card.wait_time_spinbox.minimum()} - {card.wait_time_spinbox.maximum()} ms")
        print(f"  Mode description: {card.mode_description.text()}")

        # Check if spinboxes are editable
        print("\n[Editability]")
        print(f"  Email count editable: {not card.email_count_spinbox.isReadOnly()}")
        print(f"  Wait time editable: {not card.wait_time_spinbox.isReadOnly()}")

        print("\n[OK] All UI components initialized successfully!")
        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        app.quit()

if __name__ == "__main__":
    sys.exit(test_ui())
