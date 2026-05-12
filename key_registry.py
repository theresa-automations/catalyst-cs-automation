"""
KEY REGISTRY v1.0
==================
Resolves Catalyst CS credentials from Windows Credential Manager (keyring).
Falls back to environment variables if keyring is unavailable or key not stored.

Why this exists:
    secrets.env stores tokens in plain text — readable by any process,
    accidentally committed to git, or exposed in error logs.
    Windows Credential Manager (DPAPI) encrypts values at rest and
    never exposes them as plain text in the shell or process environment.

Usage:
    import key_registry
    secrets = key_registry.load_all()   # {env_var_name: value}
    # Inject into subprocess env as normal — MCP config references unchanged.

To migrate: run setup_keyring.py once, then secrets.env becomes offline backup.
"""

import os

try:
    import keyring as _keyring
    _KEYRING_AVAILABLE = True
except ImportError:
    _KEYRING_AVAILABLE = False

SERVICE_NAME = "catalyst-cs"

# Registered secrets: env var name (used in MCP config) → keyring key name
# These must match exactly what mcp.json references via ${VAR_NAME}.
REGISTRY = {
    "SHOPIFY_TOKEN_CATALYSTCASE":      "SHOPIFY_TOKEN_CATALYSTCASE",
    "SHOPIFY_TOKEN_CATALYSTLIFESTYLE": "SHOPIFY_TOKEN_CATALYSTLIFESTYLE",
}


def keyring_available() -> bool:
    """True if keyring package is installed."""
    return _KEYRING_AVAILABLE


def get_key(name: str) -> str | None:
    """
    Resolve a single key by its env var name.
    Tries Windows Credential Manager first, then falls back to os.environ.
    Returns None if not found in either.
    """
    if _KEYRING_AVAILABLE:
        val = _keyring.get_password(SERVICE_NAME, name)
        if val:
            return val
    return os.environ.get(name)


def load_all() -> dict:
    """
    Load all registered keys.
    Returns {env_var_name: value} for every key that resolves.
    Partial results are returned — missing keys are silently skipped
    (the orchestrator's validate_secrets() will catch them downstream).
    """
    result = {}
    for name in REGISTRY:
        val = get_key(name)
        if val:
            result[name] = val
    return result


def all_stored_in_keyring() -> bool:
    """True if every registered key is present in keyring (migration complete)."""
    if not _KEYRING_AVAILABLE:
        return False
    return all(
        _keyring.get_password(SERVICE_NAME, name) is not None
        for name in REGISTRY
    )
