"""Quick test to verify GenerationCard initializes without errors."""
import sys
from PySide6.QtWidgets import QApplication
from pyside6_app.state.store import StateStore
from pyside6_app.widgets.generation_card import GenerationCard

def test_generation_card():
    """Test that GenerationCard can be instantiated."""
    app = QApplication(sys.argv)

    try:
        state_store = StateStore()
        card = GenerationCard(state_store)
        print("[OK] GenerationCard created successfully")
        print("[OK] Mode segment created:", card.mode_segment is not None)
        print("[OK] Lint button type:", type(card.lint_prompt_button).__name__)
        return 0
    except Exception as e:
        print(f"[ERROR] Error creating GenerationCard: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        app.quit()

if __name__ == "__main__":
    sys.exit(test_generation_card())
