"""
Configuration loader for environment variables and .env files
"""

import os
from typing import Optional


def load_env_file(filename: str = ".env.example") -> dict:
    """
    Load environment variables from .env or .env.example file.

    Args:
        filename: Name of the env file to load

    Returns:
        Dictionary of environment variables
    """
    env_vars = {}

    # Try .env first, then .env.local, then .env.example
    env_files = [".env", ".env.local", ".env.example"]

    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith('#'):
                            continue

                        # Parse KEY=VALUE
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()

                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]

                            env_vars[key] = value

                print(f"[OK] Loaded configuration from {env_file}")
                return env_vars
            except Exception as e:
                print(f"Warning: Could not load {env_file}: {e}")
                continue

    return env_vars


def get_config(key: str, env_vars: dict, prompt: str, validation_func=None, error_msg: str = "Invalid input") -> str:
    """
    Get configuration value from env vars or prompt user.

    Args:
        key: Environment variable key
        env_vars: Dictionary of environment variables
        prompt: Prompt to show user if value not in env
        validation_func: Optional validation function
        error_msg: Error message for validation failure

    Returns:
        Configuration value
    """
    # Check if value exists in env vars
    value = env_vars.get(key, '').strip()

    if value:
        print(f"{prompt}{value}")
        return value

    # Otherwise prompt user
    while True:
        value = input(prompt).strip()
        if not value:
            print("Error: Input cannot be empty")
            continue

        if validation_func and not validation_func(value):
            print(error_msg)
            continue

        return value


def get_integer_config(key: str, env_vars: dict, prompt: str, min_value: int = 1, max_value: Optional[int] = None) -> Optional[int]:
    """
    Get integer configuration value from env vars or prompt user.

    Args:
        key: Environment variable key
        env_vars: Dictionary of environment variables
        prompt: Prompt to show user if value not in env
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Integer value or None if not in env vars
    """
    # Check if value exists in env vars
    value = env_vars.get(key, '').strip()

    if value:
        try:
            int_value = int(value)
            if int_value >= min_value and (max_value is None or int_value <= max_value):
                print(f"{prompt}{int_value}")
                return int_value
        except ValueError:
            pass

    return None


def get_optional_config(key: str, env_vars: dict, default: str = "") -> str:
    """
    Get optional configuration value from env vars.

    Args:
        key: Environment variable key
        env_vars: Dictionary of environment variables
        default: Default value if not found

    Returns:
        Configuration value or default
    """
    return env_vars.get(key, default).strip()
