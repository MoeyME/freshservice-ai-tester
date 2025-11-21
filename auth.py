"""
Microsoft Graph API authentication module using MSAL.
Handles OAuth flow for sending emails via Microsoft Graph API.
"""

from typing import Optional
import msal
import requests
import urllib3
import os

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

    def authenticate_device_flow(self) -> str:
        """
        Authenticate using device code flow (interactive, no client secret needed).
        User will be prompted to visit a URL and enter a code.

        Returns:
            Access token for Microsoft Graph API

        Raises:
            Exception: If authentication fails
        """
        # Create custom HTTP client that disables SSL verification
        # This is needed for corporate networks with self-signed certificates
        import requests
        http_client = requests.Session()
        http_client.verify = False

        # Create a public client application with custom HTTP client
        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            http_client=http_client
        )

        # Initiate device flow
        flow = self.app.initiate_device_flow(scopes=self.SCOPES)

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
            result = self.app.acquire_token_by_device_flow(flow)
        except KeyboardInterrupt:
            print("\n[CANCELLED] Authentication cancelled by user.")
            raise Exception("Authentication cancelled by user")
        except Exception as e:
            print(f"\n[ERROR] Network error during authentication polling: {e}")
            raise Exception(f"Network error during authentication: {e}")

        # Check if authentication succeeded
        if "access_token" in result:
            self.access_token = result["access_token"]
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
