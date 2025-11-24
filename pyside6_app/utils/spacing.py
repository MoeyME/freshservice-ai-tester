"""
Consistent spacing values for UI components.
"""


class Spacing:
    """Standard spacing values for consistent UI layout."""

    # Extra small - tight spacing (within groups)
    XS = 4

    # Small - between related items
    SM = 8

    # Medium - form fields, list items
    MD = 12

    # Large - between sections
    LG = 16

    # Extra large - card margins, major sections
    XL = 24

    # Double extra large - page margins
    XXL = 32


class Margins:
    """Standard margin tuples (left, top, right, bottom)."""

    # No margins
    NONE = (0, 0, 0, 0)

    # Card content margins
    CARD = (16, 16, 16, 16)

    # Card header margins
    CARD_HEADER = (16, 12, 16, 12)

    # Form content margins
    FORM = (0, 0, 0, 0)

    # Dialog content margins
    DIALOG = (24, 24, 24, 24)

    # Page/window content margins
    PAGE = (16, 16, 16, 16)

    # Compact margins for tight spaces
    COMPACT = (8, 8, 8, 8)


class Sizes:
    """Standard size values for UI elements."""

    # Button heights
    BUTTON_SMALL = 28
    BUTTON_NORMAL = 36
    BUTTON_LARGE = 44

    # Icon sizes
    ICON_SMALL = 16
    ICON_NORMAL = 20
    ICON_LARGE = 24

    # Minimum widths
    MIN_BUTTON_WIDTH = 80
    MIN_INPUT_WIDTH = 120
    MIN_CARD_WIDTH = 200

    # Maximum widths
    MAX_INPUT_WIDTH = 400
    MAX_DIALOG_WIDTH = 600


def apply_card_margins(layout):
    """
    Apply standard card margins to a layout.

    Args:
        layout: QLayout to apply margins to
    """
    layout.setContentsMargins(*Margins.CARD)


def apply_form_spacing(layout):
    """
    Apply standard form spacing to a layout.

    Args:
        layout: QLayout to apply spacing to
    """
    layout.setSpacing(Spacing.MD)


def apply_section_spacing(layout):
    """
    Apply standard section spacing to a layout.

    Args:
        layout: QLayout to apply spacing to
    """
    layout.setSpacing(Spacing.LG)
