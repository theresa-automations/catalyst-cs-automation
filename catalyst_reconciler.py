"""
CATALYST CS RECONCILER v1.0
============================
Thread-Tracer Phase 3c: Matches sent emails against BigQuery draft_log,
computes accuracy scores, and logs results to accuracy_log.

Runs every 30 minutes via a separate Windows Task Scheduler task.
Independent of the main hourly 4-step pipeline.

How it works:
    1. Fetch recent Gmail Sent messages (last 60 min) via Claude CLI + Gmail MCP
    2. Query BigQuery draft_log for all PENDING records
    3. Match sent messages to drafts via thread_id (stable across draft -> send lifecycle)
       NOTE: Gmail assigns a NEW message_id when a draft is sent — draft message_id
       does NOT match the sent message_id. thread_id is the correct join key.
    4. For each match: compute Levenshtein accuracy score, write to accuracy_log,
       update draft_log status -> RECONCILED
    5. Age out: PENDING records older than 14 days -> ABANDONED
       (prevents abandoned drafts from polluting accuracy scores)

Result thresholds:
    PERFECT      edit_distance = 0
    MINOR_EDIT   edit_pct < 5%
    MAJOR_EDIT   edit_pct 5-50%
    REWRITE      edit_pct > 50%

BigQuery writes: Python client (BigQuery MCP is read-only).
Gmail reads:     Claude CLI + Gmail MCP (consistent with existing pipeline).
semantic_match:  Always FALSE for now — embedding check deferred to Phase 4.
"""

import subprocess
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    from google.cloud import bigquery as _bq
    _BQ_AVAILABLE = True
except ImportError:
    _BQ_AVAILABLE = False

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------

BASE_DIR       = Path(r"C:\Users\pc\Documents\Catalyst-Projects")
CLAUDE_CLI     = Path(r"C:\Users\pc\.local\bin\claude.exe")
CLAUDE_CLI_DIR = Path(r"C:\Users\pc\.claude")
MCP_CONFIG     = Path(r"C:\Users\pc\.claude\mcp.json")
BQ_CREDS       = Path(r"C:\Users\pc\gdrive-mcp-server\credentials\bigquery-service-account.json")
LOG_FILE       = BASE_DIR / "reconciler_log.txt"

BQ_PROJECT  = "cs-mcp-gateway"
BQ_DATASET  = "catalyst_cs_accuracy"
DRAFT_TABLE = "draft_log"
ACC_TABLE   = "accuracy_log"

LOOKBACK_MINUTES = 60   # fetch Sent emails from last N minutes
ABANDON_DAYS     = 14   # PENDING records older than N days -> ABANDONED
GMAIL_TIMEOUT    = 300  # seconds — Claude CLI timeout for Gmail fetch

AGENT_ID = "cs@catalystcase.com"

LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB


# -----------------------------------------
# LOGGING
# -----------------------------------------

def log(message: str):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    line = f"[{timestamp}] {line_text(message)}"
    print(line)
    try:
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > LOG_MAX_BYTES:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
            archive = BASE_DIR / f"reconciler_log_{ts}.txt"
            LOG_FILE.rename(archive)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def line_text(message: str) -> str:
    return message


# -----------------------------------------
# LEVENSHTEIN DISTANCE
# -----------------------------------------

def levenshtein(s1: str, s2: str) -> int:
    """
    Compute Levenshtein edit distance between two strings.
    Uses two-row DP for memory efficiency — O(m*n) time, O(n) space.
    Works correctly for email-length strings (200-1000 chars typical).
    """
    m, n = len(s1), len(s2)
    if m == 0:
        return n
    if n == 0:
        return m
    prev = list(range(n + 1))
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, prev
    return prev[n]


def classify_result(edit_pct: float) -> str:
    if edit_pct == 0.0:
        return "PERFECT"
    elif edit_pct < 5.0:
        return "MINOR_EDIT"
    elif edit_pct <= 50.0:
        return "MAJOR_EDIT"
    else:
        return "REWRITE"


# -----------------------------------------
# BIGQUERY CLIENT + SCHEMA MIGRATION
# -----------------------------------------

def get_bq_client():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(BQ_CREDS)
    return _bq.Client(project=BQ_PROJECT)


def ensure_accuracy_log_schema(client):
    """
    One-time migration: add thread_id and message_id to accuracy_log if missing.
    These were in the roadmap schema but not in the original test_bigquery.py creation.
    Idempotent — safe to run every time.
    """
    try:
        table_ref = client.dataset(BQ_DATASET).table(ACC_TABLE)
        table = client.get_table(table_ref)
        existing = {f.name for f in table.schema}
        new_fields = []
        if "thread_id" not in existing:
            new_fields.append(_bq.SchemaField(
                "thread_id", "STRING", mode="NULLABLE",
                description="Gmail thread ID for conversation-level grouping"
            ))
        if "message_id" not in existing:
            new_fields.append(_bq.SchemaField(
                "message_id", "STRING", mode="NULLABLE",
                description="Gmail message ID of the sent message (audit — NOT the draft message_id)"
            ))
        if new_fields:
            table.schema = table.schema + new_fields
            client.update_table(table, ["schema"])
            log(f"Schema migration: added {[f.name for f in new_fields]} to {ACC_TABLE}")
        else:
            log(f"Schema check: {ACC_TABLE} fields OK, no migration needed.")
    except Exception as e:
        log(f"WARNING: Schema migration check failed: {e}. Continuing anyway.")


# -----------------------------------------
# GMAIL FETCH (via Claude CLI + Gmail MCP)
# -----------------------------------------

def fetch_sent_emails() -> list:
    """
    Fetch recent Sent emails via Claude CLI + Gmail MCP.
    Returns a list of dicts: {thread_id, message_id, subject, body, sent_at}
    Returns [] on any failure — reconciler will log and exit cleanly.

    Uses the same pre-filter pattern as the main orchestrator:
    Claude CLI returns a JSON array, Python parses it.
    """
    since = (datetime.now(timezone.utc) - timedelta(minutes=LOOKBACK_MINUTES)).strftime("%Y/%m/%d")

    # Build a minimal MCP config with only the gmail server
    mcp_trimmed = {"mcpServers": {}}
    try:
        full = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
        servers = full.get("mcpServers", {})
        if "gmail" in servers:
            mcp_trimmed["mcpServers"]["gmail"] = servers["gmail"]
        else:
            log("ERROR: 'gmail' not found in mcp.json — cannot fetch Sent emails.")
            return []
    except Exception as e:
        log(f"ERROR: Could not read mcp.json: {e}")
        return []

    mcp_path = BASE_DIR / "_mcp_reconciler.json"
    try:
        mcp_path.write_text(json.dumps(mcp_trimmed, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"ERROR: Could not write reconciler MCP config: {e}")
        return []

    prompt = (
        f"Use gmail search_emails to fetch all messages matching: `in:sent after:{since}`. "
        "For each message return ONLY a JSON array — no other text, no explanation:\n"
        '[{"thread_id":"<thread_id>","message_id":"<message_id>","subject":"<subject>",'
        '"body":"<full plain text body of the sent message>","sent_at":"<date sent, ISO 8601>"}]\n'
        "If there are no sent messages in this period, return: []"
    )

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["CLAUDE_CONFIG_DIR"] = str(CLAUDE_CLI_DIR)

    try:
        result = subprocess.run(
            [str(CLAUDE_CLI), "--mcp-config", str(mcp_path),
             "--dangerously-skip-permissions", "-p", prompt],
            capture_output=True, encoding="utf-8", errors="replace",
            timeout=GMAIL_TIMEOUT, env=env
        )
        raw = result.stdout.strip()
        if result.returncode != 0:
            log(f"WARNING: Claude CLI exited with code {result.returncode}")
            if result.stderr:
                log(f"Stderr: {result.stderr[:300]}")

        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            log(f"WARNING: No JSON array in Gmail Sent response. Raw output (first 300 chars): {raw[:300]}")
            return []

        emails = json.loads(match.group())
        log(f"Gmail Sent fetch: {len(emails)} message(s) found in last {LOOKBACK_MINUTES} min.")
        return emails

    except subprocess.TimeoutExpired:
        log(f"WARNING: Gmail Sent fetch timed out after {GMAIL_TIMEOUT}s.")
        return []
    except json.JSONDecodeError as e:
        log(f"ERROR: Could not parse Gmail Sent JSON: {e}")
        return []
    except Exception as e:
        log(f"ERROR: Gmail Sent fetch failed: {e}")
        return []


# -----------------------------------------
# BIGQUERY — FETCH PENDING DRAFTS
# -----------------------------------------

def fetch_pending_drafts(client) -> list:
    """
    Query draft_log for all PENDING records.
    Returns list of dicts with all columns needed for matching and scoring.
    """
    sql = f"""
    SELECT draft_id, thread_id, message_id, created_at,
           email_category, sender_email, subject, claude_draft, store
    FROM `{BQ_PROJECT}.{BQ_DATASET}.{DRAFT_TABLE}`
    WHERE status = 'PENDING'
    ORDER BY created_at ASC
    """
    try:
        rows = list(client.query(sql).result())
        result = [dict(row) for row in rows]
        log(f"BigQuery: {len(result)} PENDING draft(s) found.")
        return result
    except Exception as e:
        log(f"ERROR: Could not fetch PENDING drafts from BigQuery: {e}")
        return []


# -----------------------------------------
# RECONCILIATION LOGIC
# -----------------------------------------

def reconcile(client, sent_emails: list, pending_drafts: list) -> list:
    """
    Match sent emails to pending drafts via thread_id.
    Compute accuracy scores and write results.
    Returns list of reconciled draft_ids.

    Matching logic:
    - thread_id is the primary key (stable across draft -> send).
    - message_id in draft_log is the DRAFT's message_id, NOT the sent message_id.
      The sent message gets a new message_id — stored in accuracy_log for audit only.
    - If a thread has multiple PENDING drafts, match the most recent one
      (handles edge case of re-drafting the same thread).
    """
    if not sent_emails:
        log("No sent emails to reconcile.")
        return []

    if not pending_drafts:
        log("No PENDING drafts in BigQuery to reconcile against.")
        return []

    # Build lookup: thread_id -> list of pending drafts (most recent last)
    pending_by_thread: dict = {}
    for draft in pending_drafts:
        tid = draft.get("thread_id")
        if not tid:
            continue
        if tid not in pending_by_thread:
            pending_by_thread[tid] = []
        pending_by_thread[tid].append(draft)

    reconciled_ids = []
    now = datetime.now(timezone.utc).isoformat()

    for sent in sent_emails:
        tid = sent.get("thread_id")
        if not tid:
            continue
        if tid not in pending_by_thread:
            continue

        candidates = pending_by_thread[tid]
        # Take the most recently created draft for this thread
        draft = max(candidates, key=lambda d: d.get("created_at") or "")

        claude_text = draft.get("claude_draft") or ""
        sent_text   = sent.get("body") or ""

        dist    = levenshtein(claude_text, sent_text)
        total   = len(claude_text)
        edit_pct     = round((dist / total * 100), 4) if total > 0 else 0.0
        accuracy     = round(max(0.0, min(100.0, 100.0 - edit_pct)), 4)
        result_label = classify_result(edit_pct)

        draft_id   = draft["draft_id"]
        sent_msg_id = sent.get("message_id")  # sent message's ID (differs from draft message_id)
        category    = draft.get("email_category", "")

        # --- Write to accuracy_log ---
        try:
            sql_insert = f"""
            INSERT INTO `{BQ_PROJECT}.{BQ_DATASET}.{ACC_TABLE}`
              (draft_id, thread_id, message_id, reconciled_at, final_sent,
               edit_distance, total_chars, edit_pct, accuracy_score, result,
               semantic_match, agent_id)
            VALUES
              (@draft_id, @thread_id, @message_id, TIMESTAMP(@reconciled_at),
               @final_sent, @edit_distance, @total_chars, @edit_pct,
               @accuracy_score, @result, FALSE, @agent_id)
            """
            job_config = _bq.QueryJobConfig(query_parameters=[
                _bq.ScalarQueryParameter("draft_id",       "STRING",  draft_id),
                _bq.ScalarQueryParameter("thread_id",      "STRING",  tid),
                _bq.ScalarQueryParameter("message_id",     "STRING",  sent_msg_id),
                _bq.ScalarQueryParameter("reconciled_at",  "STRING",  now),
                _bq.ScalarQueryParameter("final_sent",     "STRING",  sent_text),
                _bq.ScalarQueryParameter("edit_distance",  "INT64",   dist),
                _bq.ScalarQueryParameter("total_chars",    "INT64",   total),
                _bq.ScalarQueryParameter("edit_pct",       "FLOAT64", edit_pct),
                _bq.ScalarQueryParameter("accuracy_score", "FLOAT64", accuracy),
                _bq.ScalarQueryParameter("result",         "STRING",  result_label),
                _bq.ScalarQueryParameter("agent_id",       "STRING",  AGENT_ID),
            ])
            client.query(sql_insert, job_config=job_config).result()
        except Exception as e:
            log(f"ERROR: accuracy_log insert failed for draft_id={draft_id}: {e}")
            continue

        # --- Update draft_log -> RECONCILED ---
        try:
            sql_update = f"""
            UPDATE `{BQ_PROJECT}.{BQ_DATASET}.{DRAFT_TABLE}`
            SET status = 'RECONCILED'
            WHERE draft_id = @draft_id
            """
            uc = _bq.QueryJobConfig(query_parameters=[
                _bq.ScalarQueryParameter("draft_id", "STRING", draft_id)
            ])
            client.query(sql_update, job_config=uc).result()
        except Exception as e:
            log(f"ERROR: draft_log status update failed for draft_id={draft_id}: {e}")
            continue

        log(
            f"RECONCILED | draft_id={draft_id} | category={category} "
            f"| result={result_label} | accuracy={accuracy:.1f}% | edit_distance={dist}"
        )
        reconciled_ids.append(draft_id)

        # Remove from pending_by_thread so the same thread isn't matched twice
        pending_by_thread.pop(tid, None)

    return reconciled_ids


# -----------------------------------------
# ABANDON OLD DRAFTS
# -----------------------------------------

def abandon_old_drafts(client) -> int:
    """
    Mark PENDING drafts older than ABANDON_DAYS as ABANDONED.
    These are drafts the CS agent never sent — excluded from accuracy scoring.
    Returns number of records abandoned (best-effort count via a follow-up query).
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ABANDON_DAYS)).isoformat()
    try:
        sql = f"""
        UPDATE `{BQ_PROJECT}.{BQ_DATASET}.{DRAFT_TABLE}`
        SET status = 'ABANDONED'
        WHERE status = 'PENDING'
        AND created_at < TIMESTAMP(@cutoff)
        """
        job_config = _bq.QueryJobConfig(query_parameters=[
            _bq.ScalarQueryParameter("cutoff", "STRING", cutoff)
        ])
        client.query(sql, job_config=job_config).result()
        log(f"ABANDONED: swept PENDING drafts older than {ABANDON_DAYS} days (cutoff: {cutoff[:10]}).")
        return 0  # BigQuery DML doesn't return row count directly
    except Exception as e:
        log(f"ERROR: Abandon sweep failed: {e}")
        return 0


# -----------------------------------------
# MAIN
# -----------------------------------------

def main():
    log("=" * 55)
    log("Catalyst CS Reconciler v1.0 started")

    if not _BQ_AVAILABLE:
        log("ERROR: google-cloud-bigquery not installed. Run: pip install google-cloud-bigquery")
        log("=" * 55)
        if __name__ == "__main__":
            sys.exit(1)
        return

    if not CLAUDE_CLI.exists():
        log(f"ERROR: Claude CLI not found at {CLAUDE_CLI}")
        log("=" * 55)
        if __name__ == "__main__":
            sys.exit(1)
        return

    if not BQ_CREDS.exists():
        log(f"ERROR: BigQuery credentials not found at {BQ_CREDS}")
        log("=" * 55)
        if __name__ == "__main__":
            sys.exit(1)
        return

    # Step 0: BigQuery client + schema migration
    try:
        client = get_bq_client()
    except Exception as e:
        log(f"ERROR: BigQuery client init failed: {e}")
        log("=" * 55)
        if __name__ == "__main__":
            sys.exit(1)
        return

    ensure_accuracy_log_schema(client)

    # Step 1: Fetch sent emails from Gmail
    sent_emails = fetch_sent_emails()

    # Step 2: Fetch pending drafts from BigQuery
    pending_drafts = fetch_pending_drafts(client)

    # Step 3: Reconcile
    reconciled_ids = reconcile(client, sent_emails, pending_drafts)

    # Step 4: Abandon old drafts
    abandon_old_drafts(client)

    # Summary
    log(f"Run complete | Reconciled: {len(reconciled_ids)} | "
        f"Sent emails checked: {len(sent_emails)} | "
        f"Pending drafts checked: {len(pending_drafts)}")
    log("=" * 55)


if __name__ == "__main__":
    main()
