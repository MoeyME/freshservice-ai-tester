"""
Terminal UI styling and color utilities for the IT Ticket Email Generator.
Uses ANSI escape codes for cross-platform terminal colors and formatting.
"""

# ANSI Color Codes
class Colors:
    """ANSI color codes for terminal styling."""
    # Reset
    RESET = '\033[0m'

    # Text Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright Text Colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background Colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'


def print_header(text: str, width: int = 80):
    """Print a major section header with styling."""
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}{'═' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}{text.center(width)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{'═' * width}{Colors.RESET}\n")


def print_section(text: str, width: int = 80):
    """Print a section header with styling."""
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_BLUE}{'─' * width}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}{text}{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * width}{Colors.RESET}")


def print_subsection(text: str):
    """Print a subsection header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")


def print_success(text: str, prefix: str = "✓"):
    """Print a success message."""
    print(f"{Colors.BRIGHT_GREEN}{prefix} {text}{Colors.RESET}")


def print_error(text: str, prefix: str = "✗"):
    """Print an error message."""
    print(f"{Colors.BRIGHT_RED}{prefix} {text}{Colors.RESET}")


def print_warning(text: str, prefix: str = "⚠"):
    """Print a warning message."""
    print(f"{Colors.BRIGHT_YELLOW}{prefix} {text}{Colors.RESET}")


def print_info(text: str, prefix: str = "ℹ"):
    """Print an info message."""
    print(f"{Colors.BRIGHT_BLUE}{prefix} {text}{Colors.RESET}")


def print_progress(current: int, total: int, text: str, end: str = ""):
    """Print a progress indicator."""
    percentage = (current / total * 100) if total > 0 else 0
    bar_length = 30
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_length - filled)

    print(
        f"\r{Colors.BRIGHT_CYAN}[{bar}]{Colors.RESET} "
        f"{Colors.BRIGHT_WHITE}{percentage:.0f}%{Colors.RESET} "
        f"{Colors.DIM}({current}/{total}){Colors.RESET} "
        f"{text}",
        end=end,
        flush=True
    )


def print_status(status: str, text: str):
    """Print a status message with color-coded status."""
    status_upper = status.upper()
    if status_upper in ["OK", "SUCCESS", "COMPLETED", "SENT"]:
        color = Colors.BRIGHT_GREEN
    elif status_upper in ["ERROR", "FAILED", "FAILURE"]:
        color = Colors.BRIGHT_RED
    elif status_upper in ["WARNING", "PENDING"]:
        color = Colors.BRIGHT_YELLOW
    elif status_upper in ["INFO", "GENERATING", "SENDING"]:
        color = Colors.BRIGHT_BLUE
    else:
        color = Colors.BRIGHT_WHITE

    print(f"{color}[{status_upper}]{Colors.RESET} {text}")


def print_divider(char: str = "─", width: int = 80, color: str = None):
    """Print a divider line."""
    if color:
        print(f"{color}{char * width}{Colors.RESET}")
    else:
        print(f"{Colors.BRIGHT_BLACK}{char * width}{Colors.RESET}")


def print_key_value(key: str, value: str, key_width: int = 25):
    """Print a key-value pair with aligned formatting."""
    print(f"{Colors.CYAN}{key:<{key_width}}{Colors.RESET} {Colors.BRIGHT_WHITE}{value}{Colors.RESET}")


def print_menu_option(number: str, text: str, description: str = ""):
    """Print a menu option."""
    if description:
        print(f"{Colors.BRIGHT_YELLOW}{number}.{Colors.RESET} {Colors.BRIGHT_WHITE}{text}{Colors.RESET} {Colors.DIM}({description}){Colors.RESET}")
    else:
        print(f"{Colors.BRIGHT_YELLOW}{number}.{Colors.RESET} {Colors.BRIGHT_WHITE}{text}{Colors.RESET}")


def format_number(num: int) -> str:
    """Format a number with color."""
    return f"{Colors.BRIGHT_CYAN}{num:,}{Colors.RESET}"


def format_currency(amount: float) -> str:
    """Format a currency amount with color."""
    return f"{Colors.BRIGHT_GREEN}${amount:.4f}{Colors.RESET}"


def format_email(email: str) -> str:
    """Format an email address with color."""
    return f"{Colors.BRIGHT_MAGENTA}{email}{Colors.RESET}"


def format_ticket_number(num: int) -> str:
    """Format a ticket number with color."""
    return f"{Colors.BRIGHT_YELLOW}#{num}{Colors.RESET}"


def clear_line():
    """Clear the current line in the terminal."""
    print('\r' + ' ' * 120 + '\r', end='', flush=True)


def print_box(title: str, content: list, width: int = 80):
    """Print content in a box with a title."""
    inner_width = width - 4

    # Top border
    print(f"{Colors.BRIGHT_CYAN}╔{'═' * (inner_width + 2)}╗{Colors.RESET}")

    # Title
    if title:
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.BRIGHT_WHITE}{title.ljust(inner_width)}{Colors.RESET} {Colors.BRIGHT_CYAN}║{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}╠{'═' * (inner_width + 2)}╣{Colors.RESET}")

    # Content
    for line in content:
        print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} {line.ljust(inner_width)} {Colors.BRIGHT_CYAN}║{Colors.RESET}")

    # Bottom border
    print(f"{Colors.BRIGHT_CYAN}╚{'═' * (inner_width + 2)}╝{Colors.RESET}")


def print_summary_box(stats: dict):
    """Print a summary statistics box."""
    content = []
    for key, value in stats.items():
        formatted_value = value
        if isinstance(value, int):
            formatted_value = f"{Colors.BRIGHT_CYAN}{value:,}{Colors.RESET}"
        elif isinstance(value, float):
            formatted_value = f"{Colors.BRIGHT_GREEN}{value:.2f}{Colors.RESET}"
        content.append(f"{Colors.CYAN}{key}:{Colors.RESET} {formatted_value}")

    print_box("SUMMARY", content)
