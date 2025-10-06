"""
Utility functions for file reading and data processing.
"""

import csv
import random
from typing import List, Dict, Tuple


def read_categories(file_path: str = "categories.csv") -> List[Dict[str, str]]:
    """
    Read IT ticket categories from hierarchical CSV file.

    Args:
        file_path: Path to categories CSV file with Category, Sub-Category, Item columns

    Returns:
        List of dictionaries with category, subcategory, and item information

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        Exception: If CSV is malformed or empty
    """
    try:
        # Try UTF-8 first, fall back to cp1252 (Windows encoding)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                categories = []
                for row in reader:
                    # Strip whitespace from column names and values
                    category = row.get('Category', '').strip() or row.get('Category ', '').strip()
                    subcategory = row.get('Sub-Category', '').strip()
                    item = row.get('Item', '').strip()

                    # Only add if we have at least a category
                    if category:
                        categories.append({
                            'category': category,
                            'subcategory': subcategory,
                            'item': item
                        })
        except UnicodeDecodeError:
            # Fall back to Windows cp1252 encoding
            with open(file_path, 'r', encoding='cp1252') as f:
                reader = csv.DictReader(f)
                categories = []
                for row in reader:
                    # Strip whitespace from column names and values
                    category = row.get('Category', '').strip() or row.get('Category ', '').strip()
                    subcategory = row.get('Sub-Category', '').strip()
                    item = row.get('Item', '').strip()

                    # Only add if we have at least a category
                    if category:
                        categories.append({
                            'category': category,
                            'subcategory': subcategory,
                            'item': item
                        })

        if not categories:
            raise Exception("Categories CSV file is empty or has no valid entries")

        return categories

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Categories file not found: {file_path}\n"
            f"Please create a CSV file with 'Category', 'Sub-Category', 'Item' columns."
        )
    except KeyError as e:
        raise Exception(
            f"Invalid CSV format in {file_path}\n"
            f"Expected columns: 'Category', 'Sub-Category', 'Item'\n"
            f"Missing column: {str(e)}"
        )
    except Exception as e:
        raise Exception(f"Error reading categories file: {str(e)}")


def read_priorities_and_types(file_path: str = "priorities_and_types.md") -> Dict[str, List[str]]:
    """
    Read priority levels and ticket types from markdown file.

    Args:
        file_path: Path to priorities and types markdown file

    Returns:
        Dictionary with 'priorities' and 'types' keys

    Raises:
        FileNotFoundError: If markdown file doesn't exist
        Exception: If file is malformed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract priorities (looking for "Priority 1", "Priority 2", etc. or "P1", "P2", etc.)
        priorities = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('###') and 'Priority' in line and '-' in line:
                # Extract priority level (e.g., "### Priority 1 - URGENT" -> "Priority 1")
                parts = line.replace('#', '').strip().split('-')
                if parts:
                    priority = parts[0].strip()
                    if priority:
                        priorities.append(priority)
            elif line.startswith('###') and 'P' in line and '-' in line and 'Priority' not in line:
                # Also support old format: "### P1 - Critical" -> "P1"
                parts = line.replace('#', '').strip().split('-')
                if parts:
                    priority = parts[0].strip()
                    if priority and priority.startswith('P') and len(priority) <= 3:
                        priorities.append(priority)

        # Extract ticket types (looking for ### Incident or ### Service Request)
        types = []
        in_types_section = False
        for line in content.split('\n'):
            line = line.strip()
            # Look for Type Definitions section
            if '## 3. Type Definitions' in line or '## Type Definitions' in line:
                in_types_section = True
                continue
            # Stop if we hit another major section
            if in_types_section and line.startswith('##') and not line.startswith('###'):
                in_types_section = False
            # Extract type names from ### headers in the types section
            if in_types_section and line.startswith('###'):
                ticket_type = line.replace('#', '').strip()
                # Only add recognized ticket types
                if ticket_type in ['Incident', 'Service Request']:
                    types.append(ticket_type)

        if not priorities:
            # Fallback to default priorities
            priorities = ["Priority 1", "Priority 2", "Priority 3", "Priority 4"]

        if not types:
            # Fallback to default types
            types = ["Incident", "Service Request"]

        return {
            "priorities": priorities,
            "types": types
        }

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Priorities file not found: {file_path}\n"
            f"Please create a markdown file defining priority levels and ticket types."
        )
    except Exception as e:
        raise Exception(f"Error reading priorities file: {str(e)}")


def generate_distribution(
    total: int,
    categories: List[Dict[str, str]],
    priorities: List[str],
    types: List[str]
) -> List[Dict[str, str]]:
    """
    Generate a balanced distribution of tickets across categories, priorities, and types.

    Args:
        total: Total number of tickets to generate
        categories: List of category dictionaries with category, subcategory, item
        priorities: List of priority levels
        types: List of ticket types

    Returns:
        List of dictionaries with category info, priority, and type for each ticket
    """
    distribution = []

    # Create weighted priority distribution (more Priority 3/4, fewer Priority 1/2 to be realistic)
    priority_weights = {
        "Priority 1": 0.1,  # 10%
        "Priority 2": 0.2,  # 20%
        "Priority 3": 0.4,  # 40%
        "Priority 4": 0.3,  # 30%
        "P1": 0.1,  # Support old format
        "P2": 0.2,
        "P3": 0.4,
        "P4": 0.3
    }

    # Create balanced type distribution
    type_weights = {
        "Incident": 0.6,         # 60%
        "Service Request": 0.4   # 40%
    }

    for i in range(total):
        # Select category randomly (not round-robin to avoid clustering)
        category_info = random.choice(categories)

        # Select priority based on weights
        priority = weighted_random_choice(priorities, priority_weights)

        # Select type based on weights
        ticket_type = weighted_random_choice(types, type_weights)

        distribution.append({
            "category": category_info['category'],
            "subcategory": category_info['subcategory'],
            "item": category_info['item'],
            "priority": priority,
            "type": ticket_type
        })

    # No need to shuffle since we're already selecting randomly
    return distribution


def weighted_random_choice(items: List[str], weights: Dict[str, float]) -> str:
    """
    Select an item from a list based on weights.

    Args:
        items: List of items to choose from
        weights: Dictionary mapping items to weights (0.0-1.0)

    Returns:
        Selected item
    """
    # Get weight for each item, default to equal weight if not specified
    default_weight = 1.0 / len(items)
    item_weights = [weights.get(item, default_weight) for item in items]

    # Normalize weights
    total_weight = sum(item_weights)
    if total_weight > 0:
        normalized_weights = [w / total_weight for w in item_weights]
    else:
        normalized_weights = [default_weight] * len(items)

    # Random selection
    rand = random.random()
    cumulative = 0.0

    for item, weight in zip(items, normalized_weights):
        cumulative += weight
        if rand <= cumulative:
            return item

    # Fallback (should not reach here)
    return items[0]


def calculate_distribution_stats(distribution: List[Dict[str, str]]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Calculate statistics about the distribution.

    Args:
        distribution: List of ticket distributions

    Returns:
        Tuple of (priority_counts, type_counts)
    """
    priority_counts = {}
    type_counts = {}

    for item in distribution:
        priority = item["priority"]
        ticket_type = item["type"]

        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        type_counts[ticket_type] = type_counts.get(ticket_type, 0) + 1

    return priority_counts, type_counts


def display_distribution_summary(priority_counts: Dict[str, int], type_counts: Dict[str, int]):
    """
    Display a summary of the distribution.

    Args:
        priority_counts: Dictionary of priority -> count
        type_counts: Dictionary of type -> count
    """
    from ui_styles import Colors, print_subsection, print_key_value, format_number

    total = sum(priority_counts.values())

    print_subsection("Distribution Summary")

    print(f"\n{Colors.BOLD}{Colors.BRIGHT_WHITE}Priorities:{Colors.RESET}")
    for priority in sorted(priority_counts.keys()):
        count = priority_counts[priority]
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int(percentage / 2)  # Scale to 50 chars max
        bar = '▓' * bar_length + '░' * (50 - bar_length)
        print(f"  {Colors.CYAN}{priority:<12}{Colors.RESET} {Colors.DIM}{bar}{Colors.RESET} {format_number(count)} {Colors.DIM}({percentage:.1f}%){Colors.RESET}")

    print(f"\n{Colors.BOLD}{Colors.BRIGHT_WHITE}Types:{Colors.RESET}")
    for ticket_type in sorted(type_counts.keys()):
        count = type_counts[ticket_type]
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int(percentage / 2)  # Scale to 50 chars max
        bar = '▓' * bar_length + '░' * (50 - bar_length)
        print(f"  {Colors.CYAN}{ticket_type:<12}{Colors.RESET} {Colors.DIM}{bar}{Colors.RESET} {format_number(count)} {Colors.DIM}({percentage:.1f}%){Colors.RESET}")
