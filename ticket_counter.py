"""
Persistent ticket counter to track ticket numbers across sessions.
"""

import os
import json


class TicketCounter:
    """Manages persistent ticket numbering across sessions."""

    COUNTER_FILE = "ticket_counter.json"

    def __init__(self):
        self.counter_file = self.COUNTER_FILE
        self.current_number = self.load_counter()

    def load_counter(self) -> int:
        """
        Load the current ticket counter from file.

        Returns:
            Current ticket number (starts at 1 if file doesn't exist)
        """
        if os.path.exists(self.counter_file):
            try:
                with open(self.counter_file, 'r') as f:
                    data = json.load(f)
                    return data.get('last_ticket_number', 0) + 1
            except (json.JSONDecodeError, IOError):
                return 1
        return 1

    def save_counter(self, last_number: int):
        """
        Save the last ticket number to file.

        Args:
            last_number: The last ticket number used
        """
        try:
            with open(self.counter_file, 'w') as f:
                json.dump({
                    'last_ticket_number': last_number
                }, f)
        except IOError as e:
            print(f"Warning: Could not save ticket counter: {e}")

    def get_next_number(self) -> int:
        """
        Get the next ticket number.

        Returns:
            Next ticket number
        """
        number = self.current_number
        self.current_number += 1
        return number

    def get_range(self, count: int) -> tuple:
        """
        Get a range of ticket numbers.

        Args:
            count: Number of tickets needed

        Returns:
            Tuple of (start_number, end_number)
        """
        start = self.current_number
        end = self.current_number + count - 1
        self.current_number = end + 1
        return (start, end)

    def finalize(self):
        """Save the current counter state to file."""
        self.save_counter(self.current_number - 1)

    def reset(self):
        """Reset counter to 1 (mainly for testing)."""
        self.current_number = 1
        self.save_counter(0)

    def get_current(self) -> int:
        """Get current ticket number without incrementing."""
        return self.current_number
