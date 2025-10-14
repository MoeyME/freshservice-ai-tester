"""
Freshservice API service for PySide6 app.
Wraps the existing freshservice_client.py module.
"""

from typing import Tuple
import sys
from pathlib import Path

# Add parent directory to path to import freshservice_client.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from freshservice_client import FreshserviceClient


class FreshserviceAPIService:
    """Service for Freshservice API operations."""

    def __init__(self, domain: str, api_key: str):
        """
        Initialize Freshservice API service.

        Args:
            domain: Freshservice domain (e.g., 'yourcompany.freshservice.com')
            api_key: Freshservice API key
        """
        self.client = FreshserviceClient(domain, api_key)

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to Freshservice API.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            success = self.client.test_connection()

            if success:
                return True, "Successfully connected to Freshservice API"
            else:
                return False, "Failed to connect - invalid credentials or network error"

        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def get_recent_tickets(self, email: str = None, limit: int = 10):
        """
        Get recent tickets.

        Args:
            email: Optional email filter
            limit: Maximum number of tickets to return

        Returns:
            List of ticket dictionaries
        """
        try:
            tickets = self.client.get_tickets_by_email(email, per_page=limit)
            return tickets
        except Exception as e:
            print(f"[ERROR] Failed to get tickets: {e}")
            return []
