# Catalyst CS Automation

AI-powered customer service pipeline for Catalyst Products a premium e-commerce company.
Automates email triage, draft generation, accuracy tracking, and graduated auto-send.

---

## What It Does

Runs every 2 hours (6am–11pm WAT, Mon–Fri) via Windows Task Scheduler.
Every cycle executes 6 sequential steps:

| Run | Step | What it does |
|-----|------|--------------|
| 1 | Cleanup | Removes REVIEW_DRAFT from threads already attended to |
| 2 | Triage | Fetches unread inbox emails, classifies into categories, applies Gmail labels |
| 3 | Hardened Flows | Deterministic handling for WISMO (order tracking) — no LLM, pure Shopify data |
| 4 | Draft | Fetches Shopify order data + KB, generates Gmail drafts for human review |
| 5 | Reconciler | Compares sent emails to original drafts, scores accuracy, logs to BigQuery |
| 6 | Dashboard | Mondays only — generates weekly accuracy report |

All emails are **Human-in-the-Loop** until a category earns ≥95% accuracy over 100+ emails.

---

## Architecture

```
Gmail Inbox
    │
    ▼
[Run 1 — Cleanup]        → Removes REVIEW_DRAFT from attended threads
    │
    ▼
[Run 2 — Triage]         → Gmail labels (CATALYST_US_*, CATALYST_LIFESTYLE_*, B2B_FILTERED)
    │
    ▼
[Run 3 — Hardened Flows] → WISMO: Shopify tracking data → fixed template → REVIEW_DRAFT
    │
    ▼
[Run 4 — Draft]          → Shopify data + KB lookup → Claude draft → REVIEW_DRAFT
    │                       └─ Logs draft metadata to bq_staging.jsonl
    │
    ▼ flush_bq_staging()
    │
[BigQuery — draft_log]   ← all draft metadata stored (PENDING)
    │
[Human reviews in Gmail] → edits if needed → clicks Send
    │
    ▼
[Run 5 — Reconciler]     → Gmail Sent → join draft_log via thread_id
    │                       → Levenshtein distance → accuracy_score → accuracy_log
    │                       → Updates draft_log: PENDING → RECONCILED (or ABANDONED after 14d)
    ▼
[Run 6 — Dashboard]      → Weekly accuracy report → accuracy_report_latest.txt
```

---

## Roadmap Status

| Phase | What it builds | Status |
|-------|---------------|--------|
| 1 | Shopify CLI + BigQuery infrastructure | ✅ Complete |
| 2 | WISMO + hardened flows | ✅ Complete |
| 3 | Thread-Tracer accuracy counter | ✅ Complete |
| 3.5 | Intent layer + semantic KB retrieval | 🔄 In progress |
| 4 | Graduation to auto-reply (≥95% accuracy, ≥100 emails) | ⏳ Waiting on data |
| 5 | Amazon SP-API connector | 🔒 Blocked — SP-API credentials needed |

---

## Key Files

| File | Purpose |
|------|---------|
| `catalyst_cs_automation.py` | Main orchestrator — runs all 6 steps |
| `catalyst_cleanup.md` | Cleanup prompt (Run 1) |
| `catalyst_triage.md` | Triage prompt (Run 2) |
| `catalyst_hardened_flows.md` | WISMO hardened flows prompt (Run 3) |
| `catalyst_draft.md` | Draft generation prompt (Run 4) |
| `catalyst_reconciler.py` | Accuracy reconciler (Run 5) |
| `catalyst_accuracy_dashboard.py` | Weekly accuracy report (Run 6) |
| `state_of_things_log.txt` | Session-by-session project log |
| `catalyst-cs-automation-roadmap.md` | Full phased roadmap with specs |
| `catalyst-cs-automation-phase2.md` | Architecture decisions + improvement history |

---

## BigQuery

**Project:** `cs-mcp-gateway`
**Dataset:** `catalyst_cs_accuracy`

| Table | Purpose |
|-------|---------|
| `draft_log` | Every draft created — thread_id, category, draft text, status |
| `accuracy_log` | Reconciliation results — edit distance, accuracy score, result label |
| `kb_embeddings` | *(Phase 3.5)* KB chunks + embeddings for semantic retrieval |

**Result thresholds:**
- `PERFECT` — edit_distance = 0
- `MINOR_EDIT` — edit_pct < 5%
- `MAJOR_EDIT` — edit_pct 5–50%
- `REWRITE` — edit_pct > 50%

---

## Email Categories

**US (catalystcase.com):**
`CATALYST_US_WISMO` `CATALYST_US_WARRANTY` `CATALYST_US_RETURN` `CATALYST_US_SHIPPING`
`CATALYST_US_OOS` `CATALYST_US_ADDRESS` `CATALYST_US_ORDERMOD` `CATALYST_US_GENERAL`
`CATALYST_US_CHARGEBACK`

**International (catalystlifestyle.com):**
`CATALYST_LIFESTYLE_WISMO` `CATALYST_LIFESTYLE_WARRANTY` `CATALYST_LIFESTYLE_RETURN`
`CATALYST_LIFESTYLE_SHIPPING` `CATALYST_LIFESTYLE_OOS` `CATALYST_LIFESTYLE_ADDRESS`
`CATALYST_LIFESTYLE_ORDERMOD` `CATALYST_LIFESTYLE_GENERAL` `CATALYST_LIFESTYLE_CHARGEBACK`

**Filtered:** `B2B_FILTERED` `AI_PROCESSED` `REVIEW_DRAFT` `ESCALATION_NEEDED`

---

## Setup

**Requirements:**
```
pip install google-cloud-bigquery openai google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Secrets** (not in repo — create `secrets.env`):
```
SHOPIFY_TOKEN_CATALYSTCASE=your_token
SHOPIFY_TOKEN_CATALYSTLIFESTYLE=your_token
```

**BigQuery credentials:** service account JSON at
`C:\Users\pc\gdrive-mcp-server\credentials\bigquery-service-account.json`

**Task Scheduler:** runs `catalyst_cs_automation.py` every 2 hours, 6am–11pm WAT, Mon–Fri.

---

## Accuracy Constitution

All agents operate under the **Catalyst Accuracy Constitution v1.0**:
- **LOCKED MODE** (Temp 0): facts, policies, specs — no creativity
- **FLEX MODE** (Temp 0.4–1.0): tone, expression — controlled creativity
- Facts are immutable. Expression is flexible.

---

*Last updated: April 2026*
