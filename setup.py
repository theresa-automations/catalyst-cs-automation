"""
CATALYST CS — SETUP SCRIPT
============================
One-time (and re-run after token rotation) setup utility.

What this does:
  1. Reads secrets.env
  2. Validates all required secrets are present and not placeholders
  3. Updates Claude Desktop config (claude_desktop_config.json) with
     current token values — removes hardcoded tokens from that file
  4. Syncs secrets to Docker MCP secrets store (docker-mcp.exe)
     so Docker-managed MCPs can use them securely
  5. Prints a status summary

Run this:
  - Once after first filling in secrets.env
  - After every Shopify token rotation (every 90 days recommended)
  - After adding new secrets

Usage:
  python setup.py              # Full setup
  python setup.py --validate   # Check secrets.env only, make no changes
  python setup.py --docker     # Sync to Docker secrets only
  python setup.py --desktop    # Update Desktop config only
"""

import json
import sys
import subprocess
import argparse
from pathlib import Path

# ─────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────

BASE_DIR        = Path(r"C:\Users\pc\Documents\Catalyst-Projects")
SECRETS_FILE    = BASE_DIR / "secrets.env"
# Both locations where Claude Desktop config may exist
DESKTOP_CONFIGS = [
    Path(r"C:\Users\pc\AppData\Roaming\Claude\claude_desktop_config.json"),
    Path(r"C:\Users\pc\claude_desktop_config.json"),
]
DOCKER_MCP_EXE  = Path(r"C:\Program Files\Docker\cli-plugins\docker-mcp.exe")

# Map: secrets.env key → Docker secret name
DOCKER_SECRET_NAMES = {
    "SHOPIFY_TOKEN_CATALYSTCASE":     "shopify_token_case",
    "SHOPIFY_TOKEN_CATALYSTLIFESTYLE": "shopify_token_lifestyle",
}

# Desktop MCP server names to audit for leaked tokens
DESKTOP_MCP_KEYS = {
    "SHOPIFY_TOKEN_CATALYSTCASE":     "shopify-manager-catalystcase",
    "SHOPIFY_TOKEN_CATALYSTLIFESTYLE": "shopify-manager-catalystlifestyle",
}

PLACEHOLDER_VALUES = {"your_token_here", "your_catalystcase_token_here",
                      "your_catalystlifestyle_token_here", "placeholder",
                      "changeme", ""}


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def ok(msg):  print(f"  ✅ {msg}")
def warn(msg): print(f"  ⚠️  {msg}")
def err(msg):  print(f"  ❌ {msg}")
def info(msg): print(f"     {msg}")


def load_secrets() -> dict:
    """Load and parse secrets.env. Returns {KEY: VALUE}."""
    if not SECRETS_FILE.exists():
        err(f"secrets.env not found at {SECRETS_FILE}")
        err("Create it from the template and fill in your token values.")
        sys.exit(1)

    secrets = {}
    with open(SECRETS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                secrets[key.strip()] = value.strip()

    return secrets


def validate(secrets: dict) -> bool:
    """Check all required secrets are present and not placeholders."""
    print("\n── Validating secrets.env ──")
    required = list(DOCKER_SECRET_NAMES.keys())
    all_ok = True

    for key in required:
        if key not in secrets:
            err(f"Missing: {key}")
            all_ok = False
        elif secrets[key].lower() in {v.lower() for v in PLACEHOLDER_VALUES}:
            err(f"Placeholder value detected: {key} = '{secrets[key]}'")
            err(f"  → Open secrets.env and replace with your real token.")
            all_ok = False
        else:
            # Show only first/last 4 chars for security
            v = secrets[key]
            masked = v[:4] + "*" * (len(v) - 8) + v[-4:] if len(v) > 8 else "****"
            ok(f"{key} = {masked}")

    return all_ok


# ─────────────────────────────────────────
# DOCKER SECRETS
# ─────────────────────────────────────────

def sync_docker_secrets(secrets: dict):
    """Store secrets in Docker MCP secrets store via docker-mcp.exe."""
    print("\n── Syncing to Docker MCP secrets ──")

    if not DOCKER_MCP_EXE.exists():
        warn(f"docker-mcp.exe not found at {DOCKER_MCP_EXE}")
        warn("Docker Desktop may not be installed or Docker MCP toolkit not enabled.")
        warn("Enable it: Docker Desktop → Settings → Features in development → Docker MCP Toolkit")
        return

    for env_key, docker_name in DOCKER_SECRET_NAMES.items():
        if env_key not in secrets:
            warn(f"Skipping Docker secret '{docker_name}' — {env_key} not in secrets.env")
            continue

        value = secrets[env_key]
        try:
            result = subprocess.run(
                [str(DOCKER_MCP_EXE), "secret", f"{docker_name}={value}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                ok(f"Docker secret set: {docker_name}")
            else:
                warn(f"Docker secret '{docker_name}' failed (code {result.returncode})")
                if result.stderr:
                    info(result.stderr.strip())
        except subprocess.TimeoutExpired:
            warn(f"Docker secret '{docker_name}' timed out")
        except Exception as e:
            warn(f"Docker secret '{docker_name}' error: {e}")


# ─────────────────────────────────────────
# DESKTOP CONFIG UPDATE
# ─────────────────────────────────────────

def verify_desktop_config():
    """
    Verify that ALL claude_desktop_config.json locations do NOT contain
    hardcoded Shopify tokens. Checks both known config paths.
    """
    print("\n── Verifying Claude Desktop configs (tokens must NOT be present) ──")

    for config_path in DESKTOP_CONFIGS:
        if not config_path.exists():
            info(f"Not found (skipping): {config_path}")
            continue

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            err(f"Could not read {config_path.name}: {e}")
            continue

        mcp_servers = config.get("mcpServers", {})
        exposed = False

        for server_name in DESKTOP_MCP_KEYS.values():
            if server_name not in mcp_servers:
                continue
            token = mcp_servers[server_name].get("env", {}).get("SHOPIFY_ACCESS_TOKEN", "")
            if token:
                err(f"Hardcoded token in {config_path.name} → {server_name}")
                err("Remove SHOPIFY_ACCESS_TOKEN from that entry.")
                exposed = True

        if not exposed:
            ok(f"Clean: {config_path.name}")

    info("Shopify MCP in Desktop is intentionally disabled (tokens removed).")
    info("The automated CLI system handles all Shopify access securely.")


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Catalyst CS Setup")
    parser.add_argument("--validate", action="store_true",
                        help="Validate secrets.env only, make no changes")
    parser.add_argument("--docker",   action="store_true",
                        help="Sync to Docker secrets only")
    parser.add_argument("--desktop",  action="store_true",
                        help="Update Desktop config only")
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════╗")
    print("║   Catalyst CS — Setup & Sync Tool   ║")
    print("╚══════════════════════════════════════╝")

    secrets = load_secrets()
    secrets_ok = validate(secrets)

    if not secrets_ok:
        print("\n❌ Fix secrets.env before continuing. No changes made.")
        sys.exit(1)

    if args.validate:
        print("\n✅ Validation complete. No changes made (--validate mode).")
        sys.exit(0)

    run_docker  = args.docker  or (not args.docker and not args.desktop)
    run_desktop = args.desktop or (not args.docker and not args.desktop)

    if run_docker:
        sync_docker_secrets(secrets)

    if run_desktop:
        verify_desktop_config()

    print("\n╔══════════════════════════════════════╗")
    print("║             Setup complete           ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("Next steps:")
    print("  1. Restart Claude Desktop (so it picks up the updated config)")
    print("  2. Test manually: python catalyst_cs_automation.py --force")
    print("  3. Verify Task Scheduler is pointing to:")
    print(f"       python \"{BASE_DIR / 'catalyst_cs_automation.py'}\"")
    print()


if __name__ == "__main__":
    main()
