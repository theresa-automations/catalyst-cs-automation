"""
CATALYST CS ACCURACY DASHBOARD v1.0
=====================================
Phase 3d: Weekly accuracy report — queries BigQuery and writes a plain-text report.

Triggered weekly (first Monday run) by the main orchestrator (catalyst_cs_automation.py).
Also runnable manually at any time: python catalyst_accuracy_dashboard.py

Output:
    - Printed to console
    - Written to: C:\\Users\\pc\\Documents\\Catalyst-Projects\\accuracy_report_YYYYMMDD.txt
    - Latest copy always at: C:\\Users\\pc\\Documents\\Catalyst-Projects\\accuracy_report_latest.txt

Report sections:
    1. Pipeline Health     — PENDING / RECONCILED / ABANDONED counts
    2. Accuracy by Category — per-category breakdown (all time)
    3. Last 7 Days         — daily trend
    4. Graduation Candidates — categories at ≥95% clean over 100+ emails
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    from google.cloud import bigquery as _bq
    _BQ_AVAILABLE = True
except ImportError:
    _BQ_AVAILABLE = False

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------

BASE_DIR   = Path(r"C:\Users\pc\Documents\Catalyst-Projects")
BQ_CREDS   = Path(r"C:\Users\pc\gdrive-mcp-server\credentials\bigquery-service-account.json")

BQ_PROJECT = "cs-mcp-gateway"
BQ_DATASET = "catalyst_cs_accuracy"

GRADUATION_THRESHOLD_PCT   = 95.0   # % PERFECT + MINOR_EDIT required
GRADUATION_THRESHOLD_COUNT = 100    # minimum reconciled emails required


# -----------------------------------------
# BQ CLIENT
# -----------------------------------------

def get_client():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(BQ_CREDS)
    return _bq.Client(project=BQ_PROJECT)


# -----------------------------------------
# QUERIES
# -----------------------------------------

def query_pipeline_health(client) -> dict:
    """PENDING / RECONCILED / ABANDONED counts from draft_log."""
    sql = f"""
    SELECT status, COUNT(*) AS count
    FROM `{BQ_PROJECT}.{BQ_DATASET}.draft_log`
    GROUP BY status
    ORDER BY status
    """
    rows = list(client.query(sql).result())
    result = {r["status"]: r["count"] for r in rows}
    total = sum(result.values())
    result["TOTAL"] = total
    return result


def query_accuracy_by_category(client) -> list:
    """All-time accuracy breakdown per email_category (joined from draft_log)."""
    sql = f"""
    SELECT
        d.email_category,
        COUNT(*)                                                         AS total,
        COUNTIF(a.result = 'PERFECT')                                    AS perfect,
        COUNTIF(a.result = 'MINOR_EDIT')                                 AS minor_edit,
        COUNTIF(a.result = 'MAJOR_EDIT')                                 AS major_edit,
        COUNTIF(a.result = 'REWRITE')                                    AS rewrite,
        ROUND(AVG(a.accuracy_score), 1)                                  AS avg_accuracy,
        ROUND(
            SAFE_DIVIDE(
                COUNTIF(a.result IN ('PERFECT', 'MINOR_EDIT')),
                COUNT(*)
            ) * 100, 1
        )                                                                AS pct_clean
    FROM `{BQ_PROJECT}.{BQ_DATASET}.accuracy_log` a
    JOIN `{BQ_PROJECT}.{BQ_DATASET}.draft_log` d USING (draft_id)
    GROUP BY d.email_category
    ORDER BY total DESC
    """
    return [dict(r) for r in client.query(sql).result()]


def query_last_7_days(client) -> list:
    """Daily reconciliation count and average accuracy for the last 7 days."""
    sql = f"""
    SELECT
        DATE(a.reconciled_at)           AS day,
        COUNT(*)                        AS reconciled,
        ROUND(AVG(a.accuracy_score), 1) AS avg_accuracy,
        COUNTIF(a.result = 'PERFECT')   AS perfect,
        COUNTIF(a.result = 'MINOR_EDIT') AS minor_edit,
        COUNTIF(a.result = 'MAJOR_EDIT') AS major_edit,
        COUNTIF(a.result = 'REWRITE')   AS rewrite
    FROM `{BQ_PROJECT}.{BQ_DATASET}.accuracy_log` a
    WHERE a.reconciled_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    GROUP BY day
    ORDER BY day
    """
    return [dict(r) for r in client.query(sql).result()]


def query_graduation_candidates(client) -> list:
    """Categories meeting graduation threshold: ≥95% clean over 100+ emails."""
    sql = f"""
    SELECT
        d.email_category,
        COUNT(*)                                                         AS total,
        ROUND(
            SAFE_DIVIDE(
                COUNTIF(a.result IN ('PERFECT', 'MINOR_EDIT')),
                COUNT(*)
            ) * 100, 1
        )                                                                AS pct_clean,
        ROUND(AVG(a.accuracy_score), 1)                                  AS avg_accuracy
    FROM `{BQ_PROJECT}.{BQ_DATASET}.accuracy_log` a
    JOIN `{BQ_PROJECT}.{BQ_DATASET}.draft_log` d USING (draft_id)
    GROUP BY d.email_category
    HAVING COUNT(*) >= {GRADUATION_THRESHOLD_COUNT}
       AND SAFE_DIVIDE(
               COUNTIF(a.result IN ('PERFECT', 'MINOR_EDIT')),
               COUNT(*)
           ) * 100 >= {GRADUATION_THRESHOLD_PCT}
    ORDER BY pct_clean DESC
    """
    return [dict(r) for r in client.query(sql).result()]


# -----------------------------------------
# REPORT BUILDER
# -----------------------------------------

def build_report(health: dict, by_category: list, last_7: list, grad_candidates: list) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []

    def hr(char="=", width=60):
        lines.append(char * width)

    def section(title):
        lines.append("")
        hr()
        lines.append(f"  {title}")
        hr()

    hr("=")
    lines.append("  CATALYST CS — WEEKLY ACCURACY REPORT")
    lines.append(f"  Generated: {now}")
    hr("=")

    # --- 1. Pipeline Health ---
    section("1. PIPELINE HEALTH  (draft_log all-time)")
    total       = health.get("TOTAL", 0)
    reconciled  = health.get("RECONCILED", 0)
    pending     = health.get("PENDING", 0)
    abandoned   = health.get("ABANDONED", 0)
    pct_rec = round(reconciled / total * 100, 1) if total else 0.0

    lines.append(f"  Total drafts created :  {total}")
    lines.append(f"  Reconciled           :  {reconciled}  ({pct_rec}%)")
    lines.append(f"  Pending (unsent)     :  {pending}")
    lines.append(f"  Abandoned (14d+)     :  {abandoned}")

    # --- 2. Accuracy by Category ---
    section("2. ACCURACY BY CATEGORY  (all time)")
    if not by_category:
        lines.append("  No data yet.")
    else:
        # Header
        lines.append(
            f"  {'Category':<40} {'Total':>6} {'Avg':>6} {'Clean%':>7}  "
            f"{'PERFECT':>7} {'MINOR':>6} {'MAJOR':>6} {'REWRITE':>7}"
        )
        lines.append("  " + "-" * 92)
        for row in by_category:
            cat      = (row["email_category"] or "UNKNOWN")[:40]
            total_r  = row["total"]
            avg_acc  = row["avg_accuracy"]
            pct_cln  = row["pct_clean"]
            perfect  = row["perfect"]
            minor    = row["minor_edit"]
            major    = row["major_edit"]
            rewrite  = row["rewrite"]
            flag = " ★" if (pct_cln or 0) >= GRADUATION_THRESHOLD_PCT and total_r >= GRADUATION_THRESHOLD_COUNT else ""
            lines.append(
                f"  {cat:<40} {total_r:>6} {avg_acc:>6.1f} {pct_cln:>7.1f}%"
                f"  {perfect:>7} {minor:>6} {major:>6} {rewrite:>7}{flag}"
            )
        lines.append("")
        lines.append("  ★ = graduation candidate (≥95% clean, ≥100 emails)")

    # --- 3. Last 7 Days ---
    section("3. LAST 7 DAYS  (daily trend)")
    if not last_7:
        lines.append("  No reconciled emails in the last 7 days.")
    else:
        lines.append(
            f"  {'Date':<12} {'Reconciled':>11} {'Avg Acc':>8}  "
            f"{'PERFECT':>7} {'MINOR':>6} {'MAJOR':>6} {'REWRITE':>7}"
        )
        lines.append("  " + "-" * 68)
        for row in last_7:
            lines.append(
                f"  {str(row['day']):<12} {row['reconciled']:>11} {row['avg_accuracy']:>8.1f}%"
                f"  {row['perfect']:>7} {row['minor_edit']:>6} {row['major_edit']:>6} {row['rewrite']:>7}"
            )

    # --- 4. Graduation Candidates ---
    section("4. GRADUATION CANDIDATES  (≥95% clean, ≥100 emails)")
    if not grad_candidates:
        lines.append(f"  None yet — threshold: {GRADUATION_THRESHOLD_PCT}% clean over {GRADUATION_THRESHOLD_COUNT}+ emails.")
        lines.append("  Keep accumulating data.")
    else:
        lines.append(
            f"  {'Category':<40} {'Total':>6} {'Clean%':>7} {'Avg Acc':>8}"
        )
        lines.append("  " + "-" * 66)
        for row in grad_candidates:
            lines.append(
                f"  {(row['email_category'] or 'UNKNOWN')[:40]:<40} "
                f"{row['total']:>6} {row['pct_clean']:>7.1f}% {row['avg_accuracy']:>8.1f}%"
            )
        lines.append("")
        lines.append("  ACTION: Review these categories with June. If confident,")
        lines.append("  toggle graduation config to enable auto-send (Phase 4b).")

    lines.append("")
    hr("=")
    lines.append("  END OF REPORT")
    hr("=")

    return "\n".join(lines)


# -----------------------------------------
# MAIN
# -----------------------------------------

def main():
    if not _BQ_AVAILABLE:
        print("ERROR: google-cloud-bigquery not installed.")
        print("Run: C:\\Python314\\python.exe -m pip install google-cloud-bigquery")
        sys.exit(1)

    if not BQ_CREDS.exists():
        print(f"ERROR: BigQuery credentials not found at {BQ_CREDS}")
        sys.exit(1)

    print("Connecting to BigQuery...")
    try:
        client = get_client()
    except Exception as e:
        print(f"ERROR: BigQuery client init failed: {e}")
        sys.exit(1)

    print("Querying pipeline health...")
    health = query_pipeline_health(client)

    print("Querying accuracy by category...")
    by_category = query_accuracy_by_category(client)

    print("Querying last 7 days trend...")
    last_7 = query_last_7_days(client)

    print("Querying graduation candidates...")
    grad_candidates = query_graduation_candidates(client)

    report = build_report(health, by_category, last_7, grad_candidates)

    # Print to console
    print("\n" + report)

    # Write dated report
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    dated_path = BASE_DIR / f"accuracy_report_{date_str}.txt"
    latest_path = BASE_DIR / "accuracy_report_latest.txt"

    try:
        dated_path.write_text(report, encoding="utf-8")
        latest_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {dated_path}")
        print(f"Latest copy at:  {latest_path}")
    except Exception as e:
        print(f"WARNING: Could not write report file: {e}")


if __name__ == "__main__":
    main()
