"""
CATALYST CS AUTOMATION SCRIPT v4.7
====================================
Orchestrates the Catalyst CS workflow via Claude CLI.
Runs hourly, 6:00 AM - 11:00 PM WAT, 7 days a week.

Four sequential Claude runs per cycle:
    Run 1 - Triage    (catalyst_triage.md)          :  15 min timeout - Gmail only
    Run 2 - Cleanup   (catalyst_cleanup.md)         :   8 min timeout - Gmail only
    Run 3 - Hardened  (catalyst_hardened_flows.md)  :  15 min timeout - Gmail + Shopify (no GDrive)
    Run 4 - Draft     (catalyst_draft.md)           :  30 min timeout - Gmail + Shopify + GDrive

Post-run steps (after every draft cycle):
    Run 5 - Reconciler  (catalyst_reconciler.py)        : matches sent emails -> accuracy scores
    Run 6 - Dashboard   (catalyst_accuracy_dashboard.py): Mondays only — weekly accuracy report

All files live in: C:\\Users\\pc\\Documents\\Catalyst-Projects\\

Changes in v4.7:
    - Phase 3d Accuracy Dashboard integrated as Run 6.
    - Runs on the first Monday draft cycle of the week (WAT).
    - is_monday() helper checks WAT day before firing.
    - Dashboard imported as _dashboard (graceful skip if file missing).

Changes in v4.6:
    - Phase 3 Thread-Tracer (3a): Draft agent appends one JSON line per draft to
      bq_staging.jsonl via local-files MCP after each draft creation.
    - flush_bq_staging() runs after the draft step: reads bq_staging.jsonl,
      inserts all rows to BigQuery draft_log via Python client, clears the file.
    - BigQuery write uses same service account + project as Phase 1b (cs-mcp-gateway).
    - BigQuery MCP in .mcp.json project ID corrected to cs-mcp-gateway (was my-mcp-drive-486418).
    - Note: BigQuery MCP is read-only (confirmed). All writes go through Python client.

Changes in v4.5:
    - Added Run 3 — Hardened Flows (catalyst_hardened_flows.md)
      Handles deterministic email categories (WISMO first) before the LLM draft run.
      No KB lookup, no LLM creativity — pure Shopify data + fixed templates.
      Emails processed by hardened run receive REVIEW_DRAFT before draft runs,
      so the draft run skips them automatically via its -label:REVIEW_DRAFT filter.
    - Draft renamed from Run 3 to Run 4.
    - Added --hardened-only CLI flag.

Changes in v4.4:
    - Python pre-filter: B2B rules 0-3 now run in Python before Claude is invoked.
      Claude only receives emails that need LLM classification (Rule 4 fallback).
      Typical reduction: ~80-90% fewer emails passed to Claude on each triage run.
    - Triage prompt receives a pre-filtered email list injected into the prompt,
      skipping the Gmail fetch step entirely when pre-filter runs successfully.
    - Pre-filter stats logged per run (emails caught, emails passed to Claude).

Changes in v4.3:
    - Triage search now excludes AI_PROCESSED emails (-label:AI_PROCESSED) to avoid
      re-fetching hundreds of already-processed emails each cycle (root cause of timeouts)
    - Triage timeout bumped from 10 to 15 minutes as additional safety buffer

Changes in v4.2:
    - Split draft into cleanup (Run 2) + draft (Run 3) to fix persistent timeout
    - Cleanup: removes REVIEW_DRAFT label where cs@ has already replied (fast, Gmail-only)
    - Draft: purely draft generation - no cleanup overhead

Changes in v4.1:
    - Split combined workflow into two focused runs (fixes timeout issue)
    - Run 1 (triage) and Run 2 (draft) logged separately for clarity

Task Scheduler setup:
    Trigger:  Daily at 6:00 AM
    Repeat:   Every 1 hour for 17 hours (covers 6am-11pm)
    Action:   python "C:\\Users\\pc\\Documents\\Catalyst-Projects\\catalyst_cs_automation.py"
    Run as:   Your Windows user account (needs network & file access)
"""

import subprocess
import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

try:
    from google.cloud import bigquery as _bq
    _BQ_AVAILABLE = True
except ImportError:
    _BQ_AVAILABLE = False

try:
    import catalyst_reconciler as _reconciler
    _RECONCILER_AVAILABLE = True
except ImportError:
    _RECONCILER_AVAILABLE = False

try:
    import catalyst_accuracy_dashboard as _dashboard
    _DASHBOARD_AVAILABLE = True
except ImportError:
    _DASHBOARD_AVAILABLE = False

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------

BASE_DIR        = Path(r"C:\Users\pc\Documents\Catalyst-Projects")
KB_CACHE_DIR    = BASE_DIR / "kb_cache"
LABEL_CACHE     = BASE_DIR / "label_cache.json"
CACHE_TTL_HOURS = 24
CLAUDE_CLI_PATH = Path(r"C:\Users\pc\.local\bin\claude.exe")
TRIAGE_FILE     = BASE_DIR / "catalyst_triage.md"
CLEANUP_FILE    = BASE_DIR / "catalyst_cleanup.md"
HARDENED_FILE   = BASE_DIR / "catalyst_hardened_flows.md"
DRAFT_FILE      = BASE_DIR / "catalyst_draft.md"
MCP_CONFIG_PATH = Path(r"C:\Users\pc\.claude\mcp.json")
CLAUDE_CLI_DIR  = Path(r"C:\Users\pc\.claude")
SECRETS_FILE    = BASE_DIR / "secrets.env"
LOG_FILE        = BASE_DIR / "automation_log.txt"
BQ_STAGING_FILE = BASE_DIR / "bq_staging.jsonl"
BQ_PROJECT      = "cs-mcp-gateway"
BQ_DATASET      = "catalyst_cs_accuracy"
BQ_TABLE        = "draft_log"
BQ_CREDENTIALS  = Path(r"C:\Users\pc\gdrive-mcp-server\credentials\bigquery-service-account.json")

BUSINESS_HOUR_START = 6    # 6:00 AM WAT
BUSINESS_HOUR_END   = 23   # 11:00 PM WAT
WAT_OFFSET          = 1    # WAT = UTC+1

TRIAGE_TIMEOUT   = 900   # 15 minutes  - Gmail only
CLEANUP_TIMEOUT  = 480   #  8 minutes  - Gmail only (2 searches instead of N reads)
HARDENED_TIMEOUT = 900   # 15 minutes  - Gmail + Shopify (no GDrive)
DRAFT_TIMEOUT    = 1800  # 30 minutes  - Shopify + GDrive + Gmail

LOG_MAX_BYTES   = 5 * 1024 * 1024  # 5 MB - rotate log at this size


# -----------------------------------------
# BIGQUERY STAGING FLUSH (Thread-Tracer 3a)
# -----------------------------------------

def flush_bq_staging():
    """
    Read bq_staging.jsonl written by the draft agent, insert all rows into
    BigQuery draft_log, then clear the file.
    Called once after the draft run completes.
    """
    if not BQ_STAGING_FILE.exists() or BQ_STAGING_FILE.stat().st_size == 0:
        log("BQ staging: no rows to flush.")
        return

    if not _BQ_AVAILABLE:
        log("WARNING: google-cloud-bigquery not installed — skipping BQ flush.")
        return

    rows = []
    try:
        with open(BQ_STAGING_FILE, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    log(f"WARNING: BQ staging line {line_num} is invalid JSON, skipped: {e}")
    except Exception as e:
        log(f"ERROR: Could not read bq_staging.jsonl: {e}")
        return

    if not rows:
        log("BQ staging: file had no valid rows.")
        BQ_STAGING_FILE.write_text("", encoding="utf-8")
        return

    log(f"BQ staging: flushing {len(rows)} row(s) to BigQuery...")
    inserted = 0
    failed = 0

    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(BQ_CREDENTIALS)
        client = _bq.Client(project=BQ_PROJECT)
        table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"

        for row in rows:
            try:
                # Parameterized query — BigQuery handles all special characters
                # (backslashes, quotes, newlines) safely. No manual escaping needed.
                sql = f"""
                INSERT INTO `{table_id}`
                  (draft_id, thread_id, message_id, created_at, email_category,
                   sender_email, subject, claude_draft, shopify_order_id, store, status)
                VALUES
                  (@draft_id, @thread_id, @message_id,
                   TIMESTAMP(@created_at),
                   @email_category, @sender_email, @subject, @claude_draft,
                   @shopify_order_id, @store, 'PENDING')
                """
                job_config = _bq.QueryJobConfig(
                    query_parameters=[
                        _bq.ScalarQueryParameter("draft_id",         "STRING", row.get("draft_id")),
                        _bq.ScalarQueryParameter("thread_id",        "STRING", row.get("thread_id")),
                        _bq.ScalarQueryParameter("message_id",       "STRING", row.get("message_id")),
                        _bq.ScalarQueryParameter("created_at",       "STRING", row.get("created_at")),
                        _bq.ScalarQueryParameter("email_category",   "STRING", row.get("email_category")),
                        _bq.ScalarQueryParameter("sender_email",     "STRING", row.get("sender_email")),
                        _bq.ScalarQueryParameter("subject",          "STRING", row.get("subject")),
                        _bq.ScalarQueryParameter("claude_draft",     "STRING", row.get("claude_draft")),
                        _bq.ScalarQueryParameter("shopify_order_id", "STRING", row.get("shopify_order_id")),
                        _bq.ScalarQueryParameter("store",            "STRING", row.get("store")),
                    ]
                )
                job = client.query(sql, job_config=job_config)
                job.result()
                inserted += 1
            except Exception as e:
                log(f"ERROR: BQ insert failed for draft_id={row.get('draft_id', '?')}: {e}")
                failed += 1

    except Exception as e:
        log(f"ERROR: BigQuery client init failed: {e}")
        return

    log(f"BQ staging flush: {inserted} inserted, {failed} failed.")

    # Clear the staging file after flush (even if some rows failed — avoid re-inserting)
    try:
        BQ_STAGING_FILE.write_text("", encoding="utf-8")
        log("BQ staging: file cleared.")
    except Exception as e:
        log(f"WARNING: Could not clear bq_staging.jsonl: {e}")


# -----------------------------------------
# LOGGING
# -----------------------------------------

def log(message: str):
    """Write timestamped message to console and log file."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    line = f"[{timestamp}] {message}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def rotate_log_if_needed():
    """Archive log file if it exceeds LOG_MAX_BYTES."""
    try:
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > LOG_MAX_BYTES:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
            archive = BASE_DIR / f"automation_log_{ts}.txt"
            LOG_FILE.rename(archive)
            log(f"Log rotated -> {archive.name}")
    except Exception as e:
        log(f"WARNING: Log rotation failed: {e}")


# -----------------------------------------
# BUSINESS HOURS
# -----------------------------------------

def is_business_hours() -> bool:
    now_utc = datetime.now(timezone.utc)
    wat_time = now_utc + timedelta(hours=WAT_OFFSET)
    return BUSINESS_HOUR_START <= wat_time.hour < BUSINESS_HOUR_END


def is_monday() -> bool:
    """True if today is Monday in WAT (UTC+1). Used to trigger the weekly dashboard."""
    wat_time = datetime.now(timezone.utc) + timedelta(hours=WAT_OFFSET)
    return wat_time.weekday() == 0  # 0 = Monday


def get_wat_time() -> str:
    now_utc = datetime.now(timezone.utc)
    wat_time = now_utc + timedelta(hours=WAT_OFFSET)
    return wat_time.strftime("%H:%M")


# -----------------------------------------
# SECRETS LOADING
# -----------------------------------------

def load_secrets() -> dict:
    """
    Load secrets from secrets.env.
    Injected as env vars so ~/.claude/mcp.json ${VAR} references resolve at runtime.
    """
    secrets = {}

    if not SECRETS_FILE.exists():
        log(f"ERROR: secrets.env not found at {SECRETS_FILE}")
        return secrets

    try:
        with open(SECRETS_FILE, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    log(f"WARNING: secrets.env line {line_num} skipped (no '='): {line[:40]}")
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")  # Strip accidental quotes
                if key:
                    secrets[key] = value

        log(f"Secrets loaded: {list(secrets.keys())}")
    except Exception as e:
        log(f"ERROR reading secrets.env: {e}")

    return secrets


def validate_secrets(secrets: dict):
    required = ["SHOPIFY_TOKEN_CATALYSTCASE", "SHOPIFY_TOKEN_CATALYSTLIFESTYLE"]
    placeholders = {"your_token_here", "your_catalystcase_token_here",
                    "your_catalystlifestyle_token_here", "placeholder", "changeme", ""}
    for key in required:
        if key not in secrets:
            log(f"WARNING: Secret '{key}' missing - Shopify MCP will fail")
        elif secrets[key].lower() in placeholders:
            log(f"WARNING: Secret '{key}' is a placeholder - Shopify MCP will fail")


# -----------------------------------------
# PYTHON PRE-FILTER (Rules 0-3, no LLM)
# -----------------------------------------
#
# Replicates catalyst_triage.md Rules 0-3 in pure Python.
# Emails matched here are tagged B2B_FILTERED by Claude in a single
# batch call. Only unmatched emails proceed to LLM classification (Rule 4).
# This typically reduces Claude's per-email LLM calls by 80-90%.

PRIORITY_B2B_DOMAINS = [
    "@members.wayfair.com", "@wayfair.com", "@spacious.hk", "@hongkongpost.hk",
    "@hkpost.com", "@qq.com", "@flexport.com", "@supplychain.amazon.com",
    "@reddit.com", "@redditmail.com", "@openai.com", "@composio.dev",
    "@photobucket.com", "@3cx.net", "@loopreturns.com", "@tryredoservice.com",
    "@deliverr.com", "@outbrain.com", "@teads.com", "@einpresswire.com",
    "@elixa.app", "@blacksheeprestaurants.com", "@gs1hk.org",
]
PRIORITY_B2B_ADDRESSES = ["gemini-notes@google.com"]
SPAM_SENDER_PREFIXES   = ["noreply@", "no-reply@", "donotreply@", "mailer-daemon@"]
SHOPIFY_ALWAYS_B2B     = ["mailer@shopify.com"]
VANCHAT_SENDER         = "mailer@vanchat.io"
FILLOUT_SENDER         = "notifications@fillout.com"
ECSHIP_PATTERNS        = ["ecship", "ec-ship", "no_reply@", "@hongkongpost.hk", "@hkpost.com"]
PAYPAL_SENDERS         = ["@paypal.com", "@paypal.com.hk"]
AMAZON_SENDERS         = ["@amazon.com", "@amazon.co.uk", "@amazon.ca"]

PROMOTIONAL_SUBJECT_KW = [
    "you'll love", "up to % off", "deals", "steals", "update your card",
    "listings based on your search", "% off", "find out why", "competitors",
    "pr distribution", "press release", "media outreach", "growth service",
]
SPAM_CONTENT_KW = [
    "exhibition", "trade show", "event invitation", "conference",
    "webinar", "seminar", "workshop",
]
B2B_CONTENT_KW = [
    "invoice", "do not reply", "pirateship", "partnership",
    "wholesale", "our products", "introducing our",
]
PROMO_KW = [
    "promotion", "promotional", "payout", "discount", "marketing", "newsletter",
    "unsubscribe", "campaign", "special offer", "limited time", "flash sale",
    "payment received", "funds transferred", "earnings", "affiliate",
    "advertisement", "marketing pitch", "sales outreach", "partnership proposal",
    "bulk supplier", "sponsored", "limited time offer",
]
REPLY_PITCH_KW = [
    "portfolio", "creative", "content creation", "media", "agency",
    "services", "proposal",
]


def _is_chinese(text: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in text)


def _strip_quoted_lines(text: str) -> str:
    """Remove lines starting with '>' (quoted email reply content)."""
    return "\n".join(line for line in text.splitlines() if not line.strip().startswith(">"))


def prefilter_email(sender: str, subject: str, body: str):
    """
    Apply Rules 0-3 from catalyst_triage.md in pure Python.
    Returns 'B2B_FILTERED' if matched, or None if the email needs LLM (Rule 4).
    """
    s  = sender.lower()
    su = subject.lower()
    b  = body.lower()
    content = su + " " + b

    # Rule 0 - Fillout warranty form: pass to Claude for warranty routing (Rule 0 in triage prompt)
    if FILLOUT_SENDER in s:
        return None

    # Rule 0.1 - Shopify system emails
    if any(addr in s for addr in SHOPIFY_ALWAYS_B2B):
        return "B2B_FILTERED"

    # Rule 0.2 - VanChat relay: needs LLM subtype detection; pass through
    if VANCHAT_SENDER in s:
        return None

    # Rule 0.5 - PayPal / Amazon: needs LLM for chargeback subtype detection
    if any(d in s for d in PAYPAL_SENDERS + AMAZON_SENDERS):
        return None

    # Rule 1a - Postal & EC-Ship
    if any(p in s for p in ECSHIP_PATTERNS):
        return "B2B_FILTERED"

    # Rule 1b - "Re:" business pitch
    if su.startswith("re:") and any(kw in content for kw in REPLY_PITCH_KW):
        if not any(d in s for d in PRIORITY_B2B_DOMAINS + PRIORITY_B2B_ADDRESSES):
            return "B2B_FILTERED"

    # Rule 1 - Known B2B domains / spam sender prefixes
    if (any(d in s for d in PRIORITY_B2B_DOMAINS)
            or any(a in s for a in PRIORITY_B2B_ADDRESSES)
            or any(s.startswith(p) for p in SPAM_SENDER_PREFIXES)):
        return "B2B_FILTERED"

    # Rule 1.5 - Promotional / Chinese subjects
    if _is_chinese(subject) or any(kw in su for kw in PROMOTIONAL_SUBJECT_KW):
        return "B2B_FILTERED"

    # Rule 2 - Event / trade show content
    if any(kw in content for kw in SPAM_CONTENT_KW):
        return "B2B_FILTERED"

    # Rule 3 - B2B & promotional content (quoted lines stripped to avoid false positives)
    b_unquoted = _strip_quoted_lines(b)
    content_unquoted = su + " " + b_unquoted
    if any(kw in content_unquoted for kw in B2B_CONTENT_KW + PROMO_KW):
        return "B2B_FILTERED"

    # Rule 4 - needs LLM
    return None


# -----------------------------------------
# MINIMAL MCP CONFIG GENERATOR
# -----------------------------------------
# Each workflow only loads the MCPs it actually needs.
# Prevents unused MCPs (linkedin, gdrive-personal, memory, MCP_DOCKER)
# from hanging Claude CLI startup and blocking the run.

MCP_SETS = {
    "triage":   ["gmail", "local-files"],
    "cleanup":  ["gmail", "local-files"],
    "hardened": ["gmail", "shopify-manager-catalystcase",
                 "shopify-manager-catalystlifestyle", "local-files"],
    "draft":    ["gmail", "shopify-manager-catalystcase",
                 "shopify-manager-catalystlifestyle", "gdrive", "local-files", "bigquery"],
}


def build_mcp_config(workflow: str) -> Path:
    """
    Read the full mcp.json, extract only the servers needed for this workflow,
    write a trimmed config to a temp file, and return its path.
    Falls back to the full MCP config if anything fails.
    """
    needed = MCP_SETS.get(workflow, [])
    try:
        full = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
        servers = full.get("mcpServers", {})
        trimmed = {k: v for k, v in servers.items() if k in needed}
        out = BASE_DIR / f"_mcp_{workflow}.json"
        out.write_text(
            json.dumps({"mcpServers": trimmed}, indent=2),
            encoding="utf-8"
        )
        log(f"MCP config ({workflow}): {list(trimmed.keys())}")
        return out
    except Exception as e:
        log(f"WARNING: Could not build minimal MCP config ({e}) - using full config.")
        return MCP_CONFIG_PATH


# -----------------------------------------
# PRE-FLIGHT CHECKS
# -----------------------------------------

def preflight_checks() -> bool:
    errors = []
    if not CLAUDE_CLI_PATH.exists():
        errors.append(f"Claude CLI not found: {CLAUDE_CLI_PATH}")
    if not TRIAGE_FILE.exists():
        errors.append(f"Triage workflow not found: {TRIAGE_FILE}")
    if not CLEANUP_FILE.exists():
        errors.append(f"Cleanup workflow not found: {CLEANUP_FILE}")
    if not HARDENED_FILE.exists():
        errors.append(f"Hardened flows workflow not found: {HARDENED_FILE}")
    if not DRAFT_FILE.exists():
        errors.append(f"Draft workflow not found: {DRAFT_FILE}")
    if not MCP_CONFIG_PATH.exists():
        errors.append(f"MCP config not found: {MCP_CONFIG_PATH}")
    for e in errors:
        log(f"ERROR: {e}")
    return len(errors) == 0


# -----------------------------------------
# CLAUDE CLI RUNNER
# -----------------------------------------

PREAMBLE = (
    "Execute the following workflow immediately and completely. "
    "Do not ask for confirmation. Do not summarise what you are about to do. "
    "Begin execution now.\n\n"
)


def _kill_process_tree(pid: int):
    """
    Kill a process and all its children on Windows using taskkill /F /T.
    Prevents MCP server (node.exe) orphans when Claude CLI times out.
    """
    try:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True, timeout=10
        )
    except Exception:
        pass


def _run_prompt(label: str, prompt: str, timeout: int, env: dict,
                mcp_config: Path = None) -> bool:
    """
    Core runner: launches Claude CLI, enforces timeout via process-tree kill.
    Used by both run_claude_prompt and run_claude.
    """
    cfg = mcp_config or MCP_CONFIG_PATH
    log(f"-- Starting {label} (timeout: {timeout // 60} min) --")
    proc = None
    try:
        proc = subprocess.Popen(
            [str(CLAUDE_CLI_PATH), "--mcp-config", str(cfg),
             "--dangerously-skip-permissions", "-p", prompt],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding="utf-8", errors="replace", env=env
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_process_tree(proc.pid)
            proc.communicate()  # drain pipes after kill
            log(f"[WARN] {label} timed out after {timeout // 60} minutes.")
            return False

        if stdout:
            log(f"-- {label} Output --")
            log(stdout)
        if stderr:
            log(f"-- {label} Stderr --")
            log(stderr)

        if proc.returncode == 0:
            log(f"[OK] {label} completed successfully.")
            return True
        else:
            log(f"[WARN] {label} exited with code: {proc.returncode}")
            return False

    except FileNotFoundError:
        log(f"ERROR: Claude CLI not found: {CLAUDE_CLI_PATH}")
        return False
    except Exception as e:
        if proc:
            _kill_process_tree(proc.pid)
        log(f"ERROR: {label} unexpected exception: {e}")
        return False


def run_claude_prompt(label: str, prompt: str, timeout: int, env: dict,
                      mcp_config: Path = None) -> bool:
    """Run Claude CLI with a pre-built prompt string."""
    return _run_prompt(label, prompt, timeout, env, mcp_config)


def run_claude(label: str, workflow_file: Path, timeout: int, env: dict,
               mcp_config: Path = None) -> bool:
    """Run Claude CLI with a workflow file."""
    with open(workflow_file, "r", encoding="utf-8") as f:
        prompt = PREAMBLE + f.read()
    return _run_prompt(label, prompt, timeout, env, mcp_config)


# -----------------------------------------
# CACHE UTILITIES
# -----------------------------------------

def cache_is_fresh(path: Path, ttl_hours: int = CACHE_TTL_HOURS) -> bool:
    """Return True if a cache file exists and was written within ttl_hours."""
    if not path.exists():
        return False
    age = datetime.now(timezone.utc) - datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc
    )
    return age.total_seconds() < ttl_hours * 3600


def load_label_cache():
    """Return cached label map {name: id} if fresh, else None."""
    if not cache_is_fresh(LABEL_CACHE):
        return None
    try:
        data = json.loads(LABEL_CACHE.read_text(encoding="utf-8"))
        return data.get("labels")
    except Exception:
        return None


def save_label_cache(labels: dict):
    try:
        LABEL_CACHE.write_text(
            json.dumps({"cached_at": datetime.now(timezone.utc).isoformat(),
                        "labels": labels}, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        log(f"WARNING: Could not write label cache: {e}")


# -----------------------------------------
# TRIAGE PROMPT BUILDER (with pre-filter injection)
# -----------------------------------------

def build_triage_prompt(base_prompt: str, env: dict, mcp_config: Path = None):
    """
    Attempt a fast pre-filter fetch via a minimal Claude CLI call.
    Returns (final_prompt, stats_dict).

    If the fetch succeeds, injects a pre-classified email manifest into the
    triage prompt so Claude skips the Gmail fetch and jumps straight to
    Rule 4 LLM classification for the unfiltered emails only.

    If the fetch fails for any reason, falls back to the unmodified base_prompt.
    """
    stats = {"prefilter_attempted": False, "b2b_caught": 0, "passed_to_llm": 0}

    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y/%m/%d")
    fetch_prompt = (
        "Use gmail search_emails to fetch all messages matching: "
        f"`in:inbox after:{cutoff} -label:AI_PROCESSED`. "
        "For each message return ONLY a JSON array - no other text:\n"
        '[{"id":"<msg_id>","sender":"<from>","subject":"<subject>",'
        '"snippet":"<first 300 chars of body>"}]\n'
        "If there are no messages, return: []"
    )

    try:
        cfg = mcp_config or MCP_CONFIG_PATH
        result = subprocess.run(
            [str(CLAUDE_CLI_PATH), "--mcp-config", str(cfg),
             "--dangerously-skip-permissions", "-p", fetch_prompt],
            capture_output=True, encoding="utf-8", errors="replace",
            timeout=180, env=env
        )
        raw = result.stdout.strip()
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            return base_prompt, stats

        emails = json.loads(match.group())
        stats["prefilter_attempted"] = True

        b2b_ids, llm_emails = [], []
        for em in emails:
            tag = prefilter_email(
                em.get("sender", ""),
                em.get("subject", ""),
                em.get("snippet", ""),
            )
            if tag == "B2B_FILTERED":
                b2b_ids.append(em["id"])
            else:
                llm_emails.append(em)

        stats["b2b_caught"]    = len(b2b_ids)
        stats["passed_to_llm"] = len(llm_emails)

        log(f"Pre-filter: {len(b2b_ids)} B2B caught in Python, "
            f"{len(llm_emails)} passed to Claude LLM")

        injection = (
            "\n\n---\n"
            "## PRE-FILTER RESULTS (Python pre-processed - skip STEP 1 fetch)\n\n"
            f"Already classified as B2B_FILTERED ({len(b2b_ids)} emails):\n"
            f"Message IDs: {json.dumps(b2b_ids)}\n"
            "-> In STEP 5, batch-label ALL these IDs as B2B_FILTERED + AI_PROCESSED in one call.\n\n"
            f"Needs LLM classification ({len(llm_emails)} emails):\n"
        )
        if llm_emails:
            for em in llm_emails:
                injection += (
                    f"- ID: {em['id']} | From: {em['sender']} "
                    f"| Subject: {em['subject']} | Body: {em['snippet']}\n"
                )
            injection += (
                "\n-> Apply Rules 0.2-4 ONLY to these emails (Rules 0-1.5 already passed).\n"
                "-> EXCEPTION: For emails from notifications@fillout.com, apply Rule 0 (warranty form routing) regardless.\n"
                "-> Skip STEP 1 Gmail fetch - use the email data above directly.\n"
            )
        else:
            injection += "None - all emails were pre-classified. Skip STEPS 1-4.\n"

        injection += "---\n"
        return base_prompt + injection, stats

    except Exception as e:
        log(f"Pre-filter fetch failed ({e}) - falling back to standard triage prompt.")
        return base_prompt, stats


# -----------------------------------------
# MAIN AUTOMATION
# -----------------------------------------

def run_automation(force: bool = False,
                   run_triage: bool = True,
                   run_cleanup: bool = True,
                   run_hardened: bool = True,
                   run_draft: bool = True):
    rotate_log_if_needed()
    log("=" * 55)
    log("Catalyst CS Automation v4.6 started")
    log(f"WAT time: {get_wat_time()}  |  Force: {force}  |  "
        f"Triage: {run_triage}  |  Cleanup: {run_cleanup}  |  "
        f"Hardened: {run_hardened}  |  Draft: {run_draft}")

    if not force and not is_business_hours():
        log(f"Outside operating hours ({BUSINESS_HOUR_START}:00-{BUSINESS_HOUR_END}:00 WAT). Skipping.")
        log("=" * 55)
        sys.exit(0)

    log("Within operating hours. Proceeding...")

    if not preflight_checks():
        log("Pre-flight checks failed. Aborting.")
        log("=" * 55)
        sys.exit(1)

    secrets = load_secrets()
    validate_secrets(secrets)

    # Build subprocess environment
    env = os.environ.copy()
    env["PYTHONUTF8"]        = "1"
    env["PYTHONIOENCODING"]  = "utf-8"
    env["CLAUDE_CONFIG_DIR"] = str(CLAUDE_CLI_DIR)
    for key, value in secrets.items():
        env[key] = value

    log(f"MCP config: {MCP_CONFIG_PATH}")

    triage_ok   = True
    cleanup_ok  = True
    hardened_ok = True
    draft_ok    = True

    # Run 1: Triage (with Python pre-filter)
    if run_triage:
        triage_cfg = build_mcp_config("triage")
        base_prompt = PREAMBLE + TRIAGE_FILE.read_text(encoding="utf-8")
        triage_prompt, pf_stats = build_triage_prompt(base_prompt, env, triage_cfg)
        if pf_stats["prefilter_attempted"]:
            log(f"Pre-filter active: {pf_stats['b2b_caught']} B2B, "
                f"{pf_stats['passed_to_llm']} to LLM")
        triage_ok = run_claude_prompt("TRIAGE", triage_prompt, TRIAGE_TIMEOUT, env,
                                      triage_cfg)

    # Run 2: Cleanup
    if run_cleanup:
        cleanup_cfg = build_mcp_config("cleanup")
        cleanup_ok = run_claude("CLEANUP", CLEANUP_FILE, CLEANUP_TIMEOUT, env,
                                cleanup_cfg)

    # Run 3: Hardened Flows (deterministic categories — no LLM creativity)
    # Runs before draft so processed emails get REVIEW_DRAFT and are skipped by draft.
    if run_hardened:
        hardened_cfg = build_mcp_config("hardened")
        hardened_ok = run_claude("HARDENED", HARDENED_FILE, HARDENED_TIMEOUT, env,
                                 hardened_cfg)

    # Run 4: Draft (runs even if prior steps had issues)
    if run_draft:
        if not run_hardened:
            log("[WARN] --draft-only flag: hardened flows skipped. WISMO emails may be drafted via LLM path instead of hardened template.")
        draft_cfg = build_mcp_config("draft")
        draft_ok = run_claude("DRAFT", DRAFT_FILE, DRAFT_TIMEOUT, env, draft_cfg)
        flush_bq_staging()

    # Run 5: Reconciler — runs after every full cycle (or draft-only run)
    # Matches sent emails against BigQuery draft_log, logs accuracy scores.
    # Called here instead of a separate scheduled task to keep everything in one pipeline.
    if run_draft:
        if _RECONCILER_AVAILABLE:
            log("-- Starting RECONCILER --")
            try:
                _reconciler.main()
            except Exception as e:
                log(f"[WARN] Reconciler raised an exception: {e}. Pipeline continues.")
        else:
            log("[WARN] catalyst_reconciler.py not importable — skipping reconciler step.")

    # Run 6: Accuracy Dashboard — Mondays only, after every draft cycle.
    # Generates weekly accuracy report and writes to accuracy_report_latest.txt.
    if run_draft and is_monday():
        if _DASHBOARD_AVAILABLE:
            log("-- Starting ACCURACY DASHBOARD (Monday run) --")
            try:
                _dashboard.main()
            except Exception as e:
                log(f"[WARN] Dashboard raised an exception: {e}. Pipeline continues.")
        else:
            log("[WARN] catalyst_accuracy_dashboard.py not importable — skipping dashboard.")

    # Summary
    all_ok = all([
        triage_ok   or not run_triage,
        cleanup_ok  or not run_cleanup,
        hardened_ok or not run_hardened,
        draft_ok    or not run_draft,
    ])

    if all_ok:
        log("[OK] Full cycle complete.")
    else:
        issues = []
        if run_triage   and not triage_ok:   issues.append("Triage")
        if run_cleanup  and not cleanup_ok:  issues.append("Cleanup")
        if run_hardened and not hardened_ok: issues.append("Hardened")
        if run_draft    and not draft_ok:    issues.append("Draft")
        log(f"[WARN] Issues in: {', '.join(issues)}. Check output above.")

    log("Automation run complete.")
    log("=" * 55)


# -----------------------------------------
# ENTRY POINT
# -----------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Catalyst CS Automation v4.6")
    parser.add_argument("--force",          action="store_true", help="Bypass hours check")
    parser.add_argument("--triage-only",    action="store_true", help="Run triage only")
    parser.add_argument("--cleanup-only",   action="store_true", help="Run cleanup only")
    parser.add_argument("--hardened-only",  action="store_true", help="Run hardened flows only")
    parser.add_argument("--draft-only",     action="store_true", help="Run draft only")
    args = parser.parse_args()

    # If any *-only flag is set, disable the others
    only_flags = (args.triage_only or args.cleanup_only
                  or args.hardened_only or args.draft_only)

    run_automation(
        force=args.force,
        run_triage=args.triage_only    or not only_flags,
        run_cleanup=args.cleanup_only  or not only_flags,
        run_hardened=args.hardened_only or not only_flags,
        run_draft=args.draft_only      or not only_flags,
    )
