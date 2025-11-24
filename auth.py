"""
Microsoft Graph API authentication module using MSAL.
Handles OAuth flow for sending emails via Microsoft Graph API.
"""

from typing import Optional
import msal
import requests
import urllib3
import os
import json
from pathlib import Path

# Disable SSL warnings for corporate networks with self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Disable SSL verification globally for corporate networks
# This affects all requests including MSAL internal polling
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Patch requests to disable SSL verification for MSAL (which uses requests internally)
# This is needed for corporate networks with self-signed certificates
_original_request = requests.Session.request
def _patched_request(self, *args, **kwargs):
    kwargs['verify'] = False  # Force disable, not just default
    return _original_request(self, *args, **kwargs)
requests.Session.request = _patched_request


def get_token_cache_path() -> Path:
    """Get the path for the MSAL token cache file."""
    appdata = os.getenv('APPDATA')
    if appdata:
        cache_dir = Path(appdata) / "ITTicketEmailGenerator"
    else:
        cache_dir = Path.home() / ".itticketemailgenerator"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "msal_token_cache.json"


class GraphAuthenticator:
    """Handles Microsoft Graph API authentication using MSAL."""

    # Microsoft Graph API scopes needed for sending emails
    SCOPES = ["Mail.Send"]
    AUTHORITY_URL = "https://login.microsoftonline.com/{tenant_id}"
    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

    def __init__(self, client_id: str, tenant_id: str, client_secret: Optional[str] = None):
        """
        Initialize the authenticator.

        Args:
            client_id: Azure AD application (client) ID
            tenant_id: Azure AD tenant (directory) ID
            client_secret: Optional client secret for confidential client flow
        """
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.client_secret = client_secret
        self.authority = self.AUTHORITY_URL.format(tenant_id=tenant_id)
        self.app = None
        self.access_token = None

        # Initialize token cache for persistent authentication
        self._cache = msal.SerializableTokenCache()
        self._cache_path = get_token_cache_path()
        self._load_cache()

    def _load_cache(self) -> None:
        """Load token cache from disk."""
        try:
            if self._cache_path.exists():
                with open(self._cache_path, 'r', encoding='utf-8') as f:
                    self._cache.deserialize(f.read())
        except Exception as e:
            print(f"[WARNING] Failed to load token cache: {e}")

    def _save_cache(self) -> None:
        """Save token cache to disk."""
        try:
            if self._cache.has_state_changed:
                with open(self._cache_path, 'w', encoding='utf-8') as f:
                    f.write(self._cache.serialize())
        except Exception as e:
            print(f"[WARNING] Failed to save token cache: {e}")

    def _get_app(self) -> msal.PublicClientApplication:
        """Get or create the MSAL PublicClientApplication."""
        if self.app is None:
            import requests
            http_client = requests.Session()
            http_client.verify = False

            self.app = msal.PublicClientApplication(
                client_id=self.client_id,
                authority=self.authority,
                http_client=http_client,
                token_cache=self._cache
            )
        return self.app

    def try_get_token_silent(self) -> Optional[str]:
        """
        Try to acquire a token silently from the cache.
        This uses refresh tokens to get new access tokens without user interaction.

        Returns:
            Access token if available in cache and valid/refreshable, None otherwise
        """
        app = self._get_app()

        # Get accounts from cache
        accounts = app.get_accounts()
        if not accounts:
            return None

        # Try to get token silently for the first account
        # MSAL will automatically refresh if the access token is expired
        # but the refresh token is still valid (typically 90 days)
        result = app.acquire_token_silent(self.SCOPES, account=accounts[0])

        if result and "access_token" in result:
            self.access_token = result["access_token"]
            self._save_cache()
            return self.access_token

        return None

    def is_authenticated(self) -> bool:
        """
        Check if there's a valid (or refreshable) token in the cache.

        Returns:
            True if authentication is possible without user interaction
        """
        return self.try_get_token_silent() is not None

    def sign_out(self) -> None:
        """Sign out by clearing the token cache."""
        app = self._get_app()
        accounts = app.get_accounts()
        for account in accounts:
            app.remove_account(account)
        self._save_cache()
        self.access_token = None

    def authenticate_device_flow(self) -> str:
        """
        Authenticate using device code flow (interactive, no client secret needed).
        User will be prompted to visit a URL and enter a code.

        Returns:
            Access token for Microsoft Graph API

        Raises:
            Exception: If authentication fails
        """
        # First try to get token silently from cache
        silent_token = self.try_get_token_silent()
        if silent_token:
            print("[OK] Using cached authentication (token refreshed silently)")
            return silent_token

        # Get the MSAL app (creates if needed, uses cache)
        app = self._get_app()

        # Initiate device flow
        flow = app.initiate_device_flow(scopes=self.SCOPES)

        if "user_code" not in flow:
            raise Exception(
                f"Failed to create device flow. Error: {flow.get('error_description', 'Unknown error')}"
            )

        # Display instructions to user
        print("\n" + "="*60)
        print("MICROSOFT AUTHENTICATION REQUIRED")
        print("="*60)
        print(flow["message"])
        print("="*60 + "\n")

        # Wait for user to authenticate
        # The device flow will poll until user authenticates or timeout (default ~15 min)
        print("[INFO] Waiting for authentication... (polling every 5 seconds)")
        try:
            result = app.acquire_token_by_device_flow(flow)
        except KeyboardInterrupt:
            print("\n[CANCELLED] Authentication cancelled by user.")
            raise Exception("Authentication cancelled by user")
        except Exception as e:
            print(f"\n[ERROR] Network error during authentication polling: {e}")
            raise Exception(f"Network error during authentication: {e}")

        # Check if authentication succeeded
        if "access_token" in result:
            self.access_token = result["access_token"]
            self._save_cache()  # Persist token cache to disk
            print("[OK] Authentication successful!\n")
            return self.access_token
        else:
            # Authentication failed - check for specific error
            error = result.get("error", "unknown_error")
            error_msg = result.get("error_description", "Unknown error")

            # Provide helpful messages for common errors
            if "expired" in error_msg.lower() or "expired" in error.lower():
                print(f"\n[ERROR] Device code expired. Please try again and complete authentication faster.")
            elif "cancel" in error_msg.lower() or "cancel" in error.lower():
                print(f"\n[ERROR] Authentication was cancelled or timed out.")
                print("        This can happen if:")
                print("        - The device code expired (15 minute timeout)")
                print("        - Network issues prevented polling from detecting your login")
                print("        - You cancelled in the browser")
            else:
                print(f"\n[ERROR] Authentication failed: {error_msg}")

            raise Exception(f"Authentication failed: {error_msg}")

    def authenticate_client_credentials(self) -> str:
        """
        Authenticate using client credentials flow (non-interactive, requires client secret).
        This is for confidential client applications.

        Returns:
            Access token for Microsoft Graph API

        Raises:
            Exception: If authentication fails or client secret is missing
        """
        if not self.client_secret:
            raise Exception("Client secret is required for client credentials flow")

        # Create a confidential client application
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )

        # Acquire token
        result = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

        if "access_token" in result:
            self.access_token = result["access_token"]
            print("[OK] Authentication successful!\n")
            return self.access_token
        else:
            error_msg = result.get("error_description", result.get("error", "Unknown error"))
            raise Exception(f"Authentication failed: {error_msg}")

    def get_token(self) -> str:
        """
        Get the current access token.

        Returns:
            Current access token

        Raises:
            Exception: If not authenticated yet
        """
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate_device_flow() or authenticate_client_credentials() first.")
        return self.access_token


def validate_credentials(client_id: str, tenant_id: str) -> bool:
    """
    Validate that credentials are properly formatted.

    Args:
        client_id: Azure AD application ID
        tenant_id: Azure AD tenant ID

    Returns:
        True if credentials appear valid, False otherwise
    """
    # Basic validation - check for GUID format
    import re
    guid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

    if not guid_pattern.match(client_id):
        print(f"Error: Invalid client_id format. Expected GUID, got: {client_id}")
        return False

    if not guid_pattern.match(tenant_id):
        print(f"Error: Invalid tenant_id format. Expected GUID, got: {tenant_id}")
        return False

    return True
