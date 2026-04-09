#!/usr/bin/env python3
"""
catalyst_kb_embedder.py — Phase 3.5b
KB Data Cleaning + Embedding Store

Step 1: Parse CANONICAL KB files → extract T0 entries (trigger → canonical Q+A + variants)
Step 2: SHA-256 dedup → embed via OpenAI text-embedding-3-small → store to BQ kb_embeddings

One row per Skill Function. Skips rows whose content_hash already exists in BQ.
Run manually to rebuild/refresh the KB embedding store.
"""

import os
import re
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import bigquery
from google.oauth2 import service_account

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [KB_EMBEDDER] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
KB_DIR          = Path(__file__).parent / "Claude_KB" / "Skills"
BQ_PROJECT      = "cs-mcp-gateway"
BQ_DATASET      = "catalyst_cs_accuracy"
BQ_TABLE        = "kb_embeddings"
FULL_TABLE_ID   = f"{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}"
EMBEDDING_MODEL = "text-embedding-3-small"   # OpenAI — locked; change requires full re-embed
BQ_CREDS_PATH   = r"C:\Users\pc\gdrive-mcp-server\credentials\bigquery-service-account.json"
OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY", "")

# ── BQ Schema ──────────────────────────────────────────────────────────────────
BQ_SCHEMA = [
    bigquery.SchemaField("kb_id",              "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("filename",           "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("function_name",      "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("canonical_question", "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("canonical_answer",   "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("question_variants",  "STRING",    mode="REPEATED"),
    bigquery.SchemaField("embedding",          "FLOAT64",   mode="REPEATED"),
    bigquery.SchemaField("intent_cluster",     "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("category",           "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("store",              "STRING",    mode="NULLABLE"),
    bigquery.SchemaField("embedding_model",    "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("content_hash",       "STRING",    mode="REQUIRED"),
    bigquery.SchemaField("created_at",         "TIMESTAMP", mode="REQUIRED"),
]


# ── BQ Client ──────────────────────────────────────────────────────────────────
def get_bq_client() -> bigquery.Client:
    creds = service_account.Credentials.from_service_account_file(
        BQ_CREDS_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return bigquery.Client(project=BQ_PROJECT, credentials=creds)


def ensure_table_exists(client: bigquery.Client) -> None:
    """Create kb_embeddings table if it doesn't exist."""
    dataset_ref = client.dataset(BQ_DATASET)
    table_ref   = dataset_ref.table(BQ_TABLE)
    try:
        client.get_table(table_ref)
        log.info("BQ table already exists: %s", FULL_TABLE_ID)
    except Exception:
        table = bigquery.Table(table_ref, schema=BQ_SCHEMA)
        client.create_table(table)
        log.info("Created BQ table: %s", FULL_TABLE_ID)


def fetch_existing_hashes(client: bigquery.Client) -> set:
    """Return set of content_hash values already in BQ."""
    try:
        rows = client.query(
            f"SELECT content_hash FROM `{FULL_TABLE_ID}`"
        ).result()
        return {row.content_hash for row in rows}
    except Exception:
        return set()


# ── Filename → Metadata ────────────────────────────────────────────────────────
def parse_filename_meta(filename: str) -> dict:
    """
    CANONICAL_skill_warranty-claim-us.md
    → store=us, category=warranty-claim, intent_cluster=warranty
    """
    stem = filename.replace("CANONICAL_skill_", "").replace(".md", "")

    if stem.endswith("-us"):
        store    = "us"
        category = stem[:-3]
    elif stem.endswith("-intl"):
        store    = "intl"
        category = stem[:-5]
    else:
        store    = "both"
        category = stem

    # intent_cluster = first hyphen-separated token of category
    intent_cluster = category.split("-")[0]

    return {"store": store, "category": category, "intent_cluster": intent_cluster}


# ── KB File Parser ─────────────────────────────────────────────────────────────
def parse_kb_file(path: Path) -> list[dict]:
    """
    Parse one CANONICAL skill file into a list of T0 entries,
    one per ### Function N block.

    Each entry:
      function_name       — e.g. "Warranty Policy Explanation"
      canonical_question  — T0: normalized trigger line
      canonical_answer    — T0: all Approved Language lines joined
      question_variants   — list of example strings
    """
    text = path.read_text(encoding="utf-8")

    # Split on function headers: ### Function N: <Title>
    func_pattern = re.compile(
        r"^###\s+Function\s+\d+[:\s]+(.+)$", re.MULTILINE
    )
    splits = func_pattern.split(text)
    # splits = [preamble, title1, body1, title2, body2, ...]

    entries = []
    for i in range(1, len(splits), 2):
        function_name = splits[i].strip()
        body          = splits[i + 1] if i + 1 < len(splits) else ""

        canonical_question = _extract_trigger(body, function_name)
        canonical_answer   = _extract_approved_language(body)
        question_variants  = _extract_examples(body)

        if not canonical_answer:
            # Skip functions with no Approved Language block (e.g. pure escalation stubs)
            log.debug("Skipping %s — no Approved Language found", function_name)
            continue

        entries.append(
            {
                "function_name":      function_name,
                "canonical_question": canonical_question,
                "canonical_answer":   canonical_answer,
                "question_variants":  question_variants,
            }
        )

    log.info("  Parsed %d functions from %s", len(entries), path.name)
    return entries


def _extract_trigger(body: str, function_name: str) -> str:
    """
    Extract T0 canonical question from **Trigger:** line.
    Falls back to function_name if not found.
    Normalizes to lowercase, strips markdown.
    """
    m = re.search(r"\*\*Trigger:\*\*\s*(.+)", body)
    if m:
        raw = m.group(1).strip()
        # Strip any markdown bold/italic
        raw = re.sub(r"\*+", "", raw)
        return raw.strip()
    # Fallback: use function name as-is (already descriptive T0)
    return function_name


def _extract_approved_language(body: str) -> str:
    """
    Extract all blockquote lines (> "...") under **Approved Language:** sections.
    Joins them with newlines. Returns empty string if none found.
    """
    # Find content between **Approved Language:** and **Forbidden:** (or end of block)
    sections = re.findall(
        r"\*\*Approved Language[^:]*:\*\*\s*(.*?)(?=\*\*Forbidden:|###|\Z)",
        body,
        re.DOTALL,
    )
    lines = []
    for section in sections:
        for line in section.splitlines():
            line = line.strip()
            if line.startswith(">"):
                # Strip leading > and quotes
                clean = line.lstrip(">").strip().strip('"').strip(""").strip(""")
                if clean:
                    lines.append(clean)
    return "\n".join(lines)


def _extract_examples(body: str) -> list[str]:
    """
    Extract example strings from **Examples:** line.
    Handles formats: "A" / "B" / "C"
    """
    m = re.search(r"\*\*Examples?:\*\*\s*(.+)", body)
    if not m:
        return []
    raw = m.group(1).strip()
    # Split on " / " or " | "
    parts = re.split(r'"\s*/\s*"|\s*/\s*', raw)
    variants = []
    for p in parts:
        clean = p.strip().strip('"').strip(""").strip(""").strip()
        if clean:
            variants.append(clean)
    return variants


# ── Content Hash ───────────────────────────────────────────────────────────────
def make_content_hash(canonical_question: str, canonical_answer: str) -> str:
    content = f"{canonical_question.strip()}|{canonical_answer.strip()}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ── Embedder ───────────────────────────────────────────────────────────────────
def load_embedder():
    """Validate OpenAI client is available and API key is set."""
    try:
        from openai import OpenAI
    except ImportError:
        log.error("openai package not installed. Run: pip install openai")
        raise
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    log.info("Embedding provider: OpenAI / %s", EMBEDDING_MODEL)
    return OpenAI(api_key=OPENAI_API_KEY)


def embed_texts(client, texts: list[str]) -> list[list[float]]:
    """Embed a list of texts via OpenAI. Returns list of float lists."""
    response = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
    return [item.embedding for item in response.data]


# ── Main ───────────────────────────────────────────────────────────────────────
def run_embedder():
    log.info("=" * 60)
    log.info("Phase 3.5b — KB Embedder starting")
    log.info("=" * 60)

    # 1. Init BQ
    client = get_bq_client()
    ensure_table_exists(client)
    existing_hashes = fetch_existing_hashes(client)
    log.info("Existing entries in BQ: %d", len(existing_hashes))

    # 2. Parse all KB files
    kb_files = sorted(KB_DIR.glob("CANONICAL_skill_*.md"))
    if not kb_files:
        log.error("No CANONICAL KB files found in: %s", KB_DIR)
        return

    log.info("Found %d KB files", len(kb_files))

    all_entries = []
    for kb_file in kb_files:
        meta    = parse_filename_meta(kb_file.name)
        entries = parse_kb_file(kb_file)
        for entry in entries:
            entry.update(
                {
                    "filename":      kb_file.name,
                    "store":         meta["store"],
                    "category":      meta["category"],
                    "intent_cluster": meta["intent_cluster"],
                }
            )
            entry["content_hash"] = make_content_hash(
                entry["canonical_question"], entry["canonical_answer"]
            )
        all_entries.extend(entries)

    log.info("Total functions parsed: %d", len(all_entries))

    # 3. Dedup — skip entries already in BQ
    new_entries = [e for e in all_entries if e["content_hash"] not in existing_hashes]
    log.info("New entries to embed: %d  (skipping %d duplicates)",
             len(new_entries), len(all_entries) - len(new_entries))

    if not new_entries:
        log.info("KB is fully up to date. Nothing to embed.")
        return

    # 4. Embed
    model  = load_embedder()
    texts  = [e["canonical_question"] for e in new_entries]
    vectors = embed_texts(model, texts)

    # 5. Build BQ rows
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for entry, vector in zip(new_entries, vectors):
        rows.append(
            {
                "kb_id":              str(uuid.uuid4()),
                "filename":           entry["filename"],
                "function_name":      entry["function_name"],
                "canonical_question": entry["canonical_question"],
                "canonical_answer":   entry["canonical_answer"],
                "question_variants":  entry["question_variants"],
                "embedding":          vector,
                "intent_cluster":     entry["intent_cluster"],
                "category":           entry["category"],
                "store":              entry["store"],
                "embedding_model":    EMBEDDING_MODEL,
                "content_hash":       entry["content_hash"],
                "created_at":         now,
            }
        )

    # 6. Insert to BQ
    errors = client.insert_rows_json(FULL_TABLE_ID, rows)
    if errors:
        log.error("BQ insert errors: %s", errors)
    else:
        log.info("Inserted %d rows to %s", len(rows), FULL_TABLE_ID)

    log.info("Phase 3.5b complete.")


if __name__ == "__main__":
    run_embedder()
