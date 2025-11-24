"""
Input validators for email, domain, and other fields.
"""

import re
from typing import Tuple


class EmailValidator:
    """RFC-compliant email validator."""

    # Basic RFC 5322 email pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}'
        r'[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    )

    @classmethod
    def validate(cls, email: str) -> Tuple[bool, str]:
        """
        Validate email address.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email address is required"

        if not cls.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"

        if len(email) > 254:
            return False, "Email address too long (max 254 characters)"

        local, _, domain = email.rpartition('@')
        if len(local) > 64:
            return False, "Local part too long (max 64 characters)"

        return True, ""


class DomainValidator:
    """Domain name validator."""

    DOMAIN_PATTERN = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )

    FRESHSERVICE_PATTERN = re.compile(
        r'^[a-z0-9-]+\.freshservice\.com$'
    )

    @classmethod
    def validate(cls, domain: str) -> Tuple[bool, str]:
        """
        Validate domain name.

        Args:
            domain: Domain name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not domain:
            return False, "Domain is required"

        if not cls.DOMAIN_PATTERN.match(domain):
            return False, "Invalid domain format"

        if len(domain) > 253:
            return False, "Domain too long (max 253 characters)"

        return True, ""

    @classmethod
    def validate_freshservice(cls, domain: str) -> Tuple[bool, str]:
        """
        Validate Freshservice domain format.

        Args:
            domain: Freshservice domain to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not domain:
            return False, "Freshservice domain is required"

        if not cls.FRESHSERVICE_PATTERN.match(domain):
            return False, "Must be in format: yourcompany.freshservice.com"

        return True, ""


class GUIDValidator:
    """GUID/UUID validator."""

    GUID_PATTERN = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )

    @classmethod
    def validate(cls, guid: str) -> Tuple[bool, str]:
        """
        Validate GUID format.

        Args:
            guid: GUID string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not guid:
            return False, "GUID is required"

        if not cls.GUID_PATTERN.match(guid):
            return False, "Invalid GUID format (expected: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)"

        return True, ""


class APIKeyValidator:
    """API key validators for various services."""

    # Claude API key pattern (starts with sk-ant-)
    CLAUDE_PATTERN = re.compile(r'^sk-ant-[a-zA-Z0-9_-]{20,}$')

    # Freshservice API key pattern (typically alphanumeric)
    FRESHSERVICE_PATTERN = re.compile(r'^[a-zA-Z0-9]{20,}$')

    @classmethod
    def validate_claude(cls, key: str) -> Tuple[bool, str]:
        """
        Validate Claude API key format.

        Args:
            key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not key:
            return False, "Claude API key is required"

        if not key.startswith("sk-ant-"):
            return False, "Claude API key must start with 'sk-ant-'"

        if len(key) < 30:
            return False, "API key appears too short"

        if not cls.CLAUDE_PATTERN.match(key):
            return False, "Invalid API key format"

        return True, ""

    @classmethod
    def validate_freshservice(cls, key: str) -> Tuple[bool, str]:
        """
        Validate Freshservice API key format.

        Args:
            key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not key:
            return False, "Freshservice API key is required"

        if len(key) < 20:
            return False, "API key appears too short"

        return True, ""
