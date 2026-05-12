"""
SETUP KEYRING — One-time secrets migration
==========================================
Reads secrets.env and stores each value in Windows Credential Manager
via the Python keyring package (uses DPAPI encryption).

Run once:
    pip install keyring
    python setup_keyring.py

After confirming all keys are stored, secrets.env becomes an offline
backup only — the orchestrator will load from keyring at runtime.

To verify a stored key:
    python -c "import keyring; print(keyring.get_password('catalyst-cs', 'SHOPIFY_TOKEN_CATALYSTCASE'))"

To remove a key from Credential Manager:
    python -c "import keyring; keyring.delete_password('catalyst-cs', 'SHOPIFY_TOKEN_CATALYSTCASE')"
"""

from pathlib import Path

try:
    import keyring
except ImportError:
    print("ERROR: keyring not installed.")
    print("Run:   pip install keyring")
    raise SystemExit(1)

SECRETS_FILE = Path(r"C:\Users\pc\Documents\Catalyst-Projects\secrets.env")
SERVICE_NAME = "catalyst-cs"


def migrate():
    if not SECRETS_FILE.exists():
        print(f"ERROR: secrets.env not found at {SECRETS_FILE}")
        raise SystemExit(1)

    print(f"Reading from: {SECRETS_FILE}")
    print(f"Storing into: Windows Credential Manager (service='{SERVICE_NAME}')\n")

    stored = 0
    skipped = 0

    with open(SECRETS_FILE, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                print(f"  Line {line_num}: skipped (no '=')")
                skipped += 1
                continue
            key, _, value = line.partition("=")
            key   = key.strip()
            value = value.strip().strip('"').strip("'")
            if not key or not value:
                skipped += 1
                continue
            keyring.set_password(SERVICE_NAME, key, value)
            print(f"  Stored:  {key}  ({len(value)} chars)")
            stored += 1

    print(f"\n{stored} key(s) stored, {skipped} line(s) skipped.")

    print("\n--- Verification ---")
    all_ok = True
    with open(SECRETS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key = line.partition("=")[0].strip()
            val = keyring.get_password(SERVICE_NAME, key)
            if val:
                print(f"  OK:      {key}")
            else:
                print(f"  MISSING: {key}  <-- check this")
                all_ok = False

    if all_ok:
        print("\nAll keys verified in Credential Manager.")
        print("secrets.env is now an offline backup — keep it safe but it is not")
        print("loaded at runtime once the orchestrator is updated to use keyring.")
    else:
        print("\nWARNING: Some keys are missing. Re-run this script or check secrets.env.")


if __name__ == "__main__":
    migrate()
