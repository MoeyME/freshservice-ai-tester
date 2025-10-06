"""
Freshservice API Client
Handles authentication and API calls to Freshservice for ticket verification.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import time


class FreshserviceClient:
    """Client for interacting with Freshservice API."""

    def __init__(self, domain: str, api_key: str):
        """
        Initialize Freshservice client.

        Args:
            domain: Freshservice domain (e.g., 'yourcompany.freshservice.com')
            api_key: Freshservice API key for authentication
        """
        self.domain = domain.replace('https://', '').replace('http://', '')
        if not self.domain.endswith('.freshservice.com'):
            if not self.domain.endswith('.freshservice.com'):
                self.domain = f"{self.domain}.freshservice.com"

        self.base_url = f"https://{self.domain}/api/v2"
        self.api_key = api_key
        self.auth = (api_key, 'X')  # API key as username, 'X' as password

    def test_connection(self) -> bool:
        """
        Test the API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/tickets",
                auth=self.auth,
                params={'per_page': 1},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

    def get_tickets_by_email(
        self,
        email: Optional[str] = None,
        updated_since: Optional[str] = None,
        per_page: int = 100
    ) -> List[Dict]:
        """
        Get tickets by requester email.

        Args:
            email: Requester email address (optional - if not provided, gets all tickets)
            updated_since: ISO 8601 timestamp to filter tickets (e.g., '2025-01-15T10:00:00Z')
            per_page: Number of results per page (max 100)

        Returns:
            List of ticket dictionaries
        """
        try:
            params = {
                'per_page': per_page
            }

            # Only add email filter if provided
            if email:
                params['email'] = email

            if updated_since:
                params['updated_since'] = updated_since

            all_tickets = []
            page = 1

            while True:
                params['page'] = page
                response = requests.get(
                    f"{self.base_url}/tickets",
                    auth=self.auth,
                    params=params,
                    timeout=30
                )

                if response.status_code != 200:
                    print(f"Error fetching tickets: {response.status_code} - {response.text}")
                    break

                data = response.json()
                tickets = data.get('tickets', [])

                if not tickets:
                    break

                all_tickets.extend(tickets)

                # Check if there are more pages
                # Freshservice uses Link header or we can check if we got fewer results than per_page
                if len(tickets) < per_page:
                    break

                page += 1
                time.sleep(0.5)  # Rate limiting courtesy

            return all_tickets

        except Exception as e:
            print(f"Error getting tickets by email: {str(e)}")
            return []

    def get_ticket_by_id(self, ticket_id: int) -> Optional[Dict]:
        """
        Get a specific ticket by ID.

        Args:
            ticket_id: Freshservice ticket ID

        Returns:
            Ticket dictionary or None if not found
        """
        try:
            response = requests.get(
                f"{self.base_url}/tickets/{ticket_id}",
                auth=self.auth,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('ticket')
            else:
                print(f"Error fetching ticket {ticket_id}: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error getting ticket by ID: {str(e)}")
            return None

    def search_tickets_by_subject(
        self,
        subject_contains: str,
        email: Optional[str] = None,
        updated_since: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for tickets by subject content.

        Args:
            subject_contains: String to search for in subject
            email: Optional requester email filter
            updated_since: Optional timestamp filter

        Returns:
            List of matching tickets
        """
        # Get tickets by email first (if provided), then filter by subject
        if email:
            tickets = self.get_tickets_by_email(email, updated_since)
        else:
            # If no email, get recent tickets (this might be slow for large accounts)
            tickets = self.get_tickets_by_email_range(updated_since)

        # Filter by subject
        matching_tickets = [
            ticket for ticket in tickets
            if subject_contains.lower() in ticket.get('subject', '').lower()
        ]

        return matching_tickets

    def get_tickets_by_email_range(
        self,
        updated_since: Optional[str] = None,
        per_page: int = 100,
        max_tickets: int = 500
    ) -> List[Dict]:
        """
        Get recent tickets within a time range.

        Args:
            updated_since: ISO 8601 timestamp
            per_page: Results per page
            max_tickets: Maximum tickets to retrieve

        Returns:
            List of tickets
        """
        try:
            params = {'per_page': per_page}

            if updated_since:
                params['updated_since'] = updated_since

            all_tickets = []
            page = 1

            while len(all_tickets) < max_tickets:
                params['page'] = page
                response = requests.get(
                    f"{self.base_url}/tickets",
                    auth=self.auth,
                    params=params,
                    timeout=30
                )

                if response.status_code != 200:
                    break

                data = response.json()
                tickets = data.get('tickets', [])

                if not tickets:
                    break

                all_tickets.extend(tickets)

                if len(tickets) < per_page:
                    break

                page += 1
                time.sleep(0.5)

            return all_tickets[:max_tickets]

        except Exception as e:
            print(f"Error getting tickets by range: {str(e)}")
            return []

    def get_ticket_fields(self) -> List[Dict]:
        """
        Get all ticket field definitions.

        Returns:
            List of field definitions
        """
        try:
            response = requests.get(
                f"{self.base_url}/ticket_fields",
                auth=self.auth,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('ticket_fields', [])
            else:
                print(f"Error fetching ticket fields: {response.status_code}")
                return []

        except Exception as e:
            print(f"Error getting ticket fields: {str(e)}")
            return []

    @staticmethod
    def format_timestamp(dt: datetime) -> str:
        """
        Format datetime to Freshservice API timestamp format.

        Args:
            dt: Datetime object

        Returns:
            ISO 8601 formatted string
        """
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def validate_freshservice_credentials(domain: str, api_key: str) -> bool:
    """
    Validate Freshservice credentials format.

    Args:
        domain: Freshservice domain
        api_key: API key

    Returns:
        True if credentials format is valid
    """
    if not domain or not api_key:
        return False

    # API key should be at least 10 characters (relaxed validation)
    if len(api_key) < 10:
        return False

    return True
