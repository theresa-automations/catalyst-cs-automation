"""
alter_draft_log_intent.py
=========================
One-time schema migration — adds 4 intent/sentiment columns to BigQuery draft_log.

Run once before the next pipeline cycle after deploying catalyst_draft.md v4.4.

    python alter_draft_log_intent.py

New columns (all NULLABLE STRING):
    primary_intent    -- e.g. "replacement", "tracking_update"
    secondary_intent  -- optional secondary ask, or null
    sentiment         -- POSITIVE | NEUTRAL | FRUSTRATED | ANGRY | URGENT
    escalation_risk   -- LOW | MEDIUM | HIGH

Safe to re-run: each ALTER TABLE is run separately and will succeed even if
the column already exists (BigQuery silently allows re-adding nullable columns
with the same type in some SDK versions — but we catch errors either way).
"""

import os
import sys
from pathlib import Path

try:
    from google.cloud import bigquery
except ImportError:
    print("ERROR: google-cloud-bigquery not installed. Run: pip install google-cloud-bigquery")
    sys.exit(1)

BQ_PROJECT    = "cs-mcp-gateway"
BQ_DATASET    = "catalyst_cs_accuracy"
BQ_TABLE      = "draft_log"
BQ_CREDS_FILE = Path(r"C:\Users\pc\gdrive-mcp-server\credentials\bigquery-service-account.json")

NEW_COLUMNS = [
    ("primary_intent",   "STRING", "Intent extracted by draft agent — e.g. replacement, tracking_update"),
    ("secondary_intent", "STRING", "Optional secondary ask from customer, or null"),
    ("sentiment",        "STRING", "POSITIVE | NEUTRAL | FRUSTRATED | ANGRY | URGENT"),
    ("escalation_risk",  "STRING", "LOW | MEDIUM | HIGH — based on legal threats, contact count, tone"),
]


def main():
    if not BQ_CREDS_FILE.exists():
        print(f"ERROR: Credentials file not found: {BQ_CREDS_FILE}")
        sys.exit(1)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(BQ_CREDS_FILE)
    client = bigquery.Client(project=BQ_PROJECT)
    table_ref = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

    print(f"Fetching schema for {table_ref} ...")
    table = client.get_table(table_ref)
    existing_fields = {f.name for f in table.schema}
    print(f"Existing columns: {sorted(existing_fields)}")

    added = []
    skipped = []

    for col_name, col_type, description in NEW_COLUMNS:
        if col_name in existing_fields:
            print(f"  SKIP  {col_name} — already exists")
            skipped.append(col_name)
            continue

        sql = f"""
        ALTER TABLE `{table_ref}`
        ADD COLUMN IF NOT EXISTS {col_name} {col_type}
        OPTIONS (description = "{description}")
        """
        print(f"  ADD   {col_name} ({col_type}) ...")
        try:
            job = client.query(sql)
            job.result()
            print(f"        OK")
            added.append(col_name)
        except Exception as e:
            print(f"        ERROR: {e}")

    print()
    print(f"Done. Added: {added}. Skipped (already present): {skipped}.")
    if added:
        print("Schema migration complete — catalyst_draft.md v4.4 is safe to deploy.")


if __name__ == "__main__":
    main()
