"""
Microsoft authentication service for PySide6 app.
Wraps the existing auth.py module.
"""

from typing import Optional, Dict
import sys
from pathlib import Path

# Add parent directory to path to import auth.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from auth import GraphAuthenticator


class MicrosoftAuthService:
    """Service for Microsoft Graph API authentication."""

    def __init__(self, client_id: str, tenant_id: str, client_secret: Optional[str] = None):
        """
        Initialize authentication service.

        Args:
            client_id: Azure AD application (client) ID
            tenant_id: Azure AD tenant (directory) ID
            client_secret: Optional client secret
        """
        self.authenticator = GraphAuthenticator(client_id, tenant_id, client_secret)

    def authenticate(self) -> Optional[Dict]:
        """
        Perform device code flow authentication.

        Returns:
            Dictionary with token info or None if failed
        """
        try:
            access_token = self.authenticator.authenticate_device_flow()

            if access_token:
                return {
                    'access_token': access_token,
                    'expires_at': None  # TODO: Calculate expiry from token
                }

            return None

        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
            return None

    def get_token(self) -> Optional[str]:
        """
        Get current access token.

        Returns:
            Access token or None if not authenticated
        """
        try:
            return self.authenticator.get_token()
        except Exception:
            return None
