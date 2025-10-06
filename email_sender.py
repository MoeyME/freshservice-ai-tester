"""
Email sending functionality using Microsoft Graph API.
"""

import requests
import time
from typing import Dict, Optional


class EmailSender:
    """Sends emails using Microsoft Graph API."""

    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"
    SEND_MAIL_ENDPOINT = "{graph_url}/users/{user_email}/sendMail"

    def __init__(self, access_token: str, sender_email: str):
        """
        Initialize the email sender.

        Args:
            access_token: Microsoft Graph API access token
            sender_email: Email address of the sender
        """
        self.access_token = access_token
        self.sender_email = sender_email
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        body_type: str = "Text"
    ) -> Dict[str, any]:
        """
        Send an email via Microsoft Graph API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            body_type: "Text" or "HTML"

        Returns:
            Dictionary with status and any error information

        Response format:
            {
                "success": bool,
                "error": str or None,
                "status_code": int or None
            }
        """
        endpoint = self.SEND_MAIL_ENDPOINT.format(
            graph_url=self.GRAPH_ENDPOINT,
            user_email=self.sender_email
        )

        # Construct email message
        email_message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": body_type,
                    "content": body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_email
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=email_message,
                timeout=30
            )

            if response.status_code == 202:
                # 202 Accepted - email queued for sending
                return {
                    "success": True,
                    "error": None,
                    "status_code": 202
                }
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_detail = error_json["error"].get("message", error_detail)
                except:
                    pass

                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_detail}",
                    "status_code": response.status_code
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout - email may not have been sent",
                "status_code": None
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "status_code": None
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "status_code": None
            }

    def send_email_with_delay(
        self,
        to_email: str,
        subject: str,
        body: str,
        delay_seconds: int = 10,
        show_countdown: bool = True
    ) -> Dict[str, any]:
        """
        Send an email with a delay and optional countdown display.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            delay_seconds: Seconds to wait before sending
            show_countdown: Whether to display countdown

        Returns:
            Dictionary with status and any error information
        """
        if show_countdown and delay_seconds > 0:
            print(f"  Waiting {delay_seconds} seconds before next email...", end="", flush=True)
            for remaining in range(delay_seconds, 0, -1):
                print(f"\r  Waiting {remaining} seconds before next email...{' ' * 10}", end="", flush=True)
                time.sleep(1)
            print("\r" + " " * 60 + "\r", end="", flush=True)  # Clear the line

        return self.send_email(to_email, subject, body)

    def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if email format appears valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def test_connection(self) -> bool:
        """
        Test the Graph API connection by fetching user profile.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            endpoint = f"{self.GRAPH_ENDPOINT}/me"
            response = requests.get(endpoint, headers=self.headers, timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                print(f"✓ Connected as: {user_data.get('displayName', 'Unknown')} ({user_data.get('mail', self.sender_email)})")
                return True
            else:
                print(f"✗ Connection test failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Connection test failed: {str(e)}")
            return False
