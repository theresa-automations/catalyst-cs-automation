# Catalyst CS — AI Automation Roadmap
**Version:** 1.0
**Date:** March 2026
**Status:** Phase 3 complete — accumulating accuracy data for Phase 4 graduation
**Prepared for:** Catalyst Products CS Team

---

## Overview

This document outlines the strategy for transitioning the Catalyst CS email workflow from
manual review to data-driven, graduated automation. It covers how each new phase integrates
with the existing system, what gets built, and how the system proves itself before any
category is trusted to send automatically.

**Core principle: Every step is tested before the next layer is added.**

---

## The Existing System (Baseline)

The current automation runs as a 3-step pipeline via Windows Task Scheduler (every 2 hours):

```
Run 1 — Triage      Fetches unread emails, classifies them, applies Gmail labels
Run 2 — Cleanup     Removes REVIEW_DRAFT label from threads already attended to
Run 3 — Draft       Fetches order data from Shopify, reads KB from Google Drive,
                    creates a ready-to-review Gmail draft
```

After the draft is created:

```
Human opens Gmail draft → edits if needed → clicks Send
```

Everything is currently **Human-in-the-Loop (HITL)**. No email is sent without a human
reviewing and approving it.

**What the existing system does well:**
- Classifies 100% of inbound emails without human effort
- Filters B2B, spam, and automated senders before they reach the CS agent
- Pulls live Shopify order data and knowledge base content into every draft
- Operates 6am–11pm WAT, 7 days a week

**What it does not yet do:**
- Track whether drafts were edited or sent as-is
- Auto-send any category of email
- Handle Amazon Seller Central messages
- Use Python-hardened flows for deterministic replies (e.g. order tracking)

---

## How the Roadmap Integrates with the Existing System

The new roadmap **extends** the existing pipeline — it does not replace it.

### Current pipeline:
```
Triage → Cleanup → Draft → [Human reviews in Gmail] → Human sends
```

### Pipeline after all phases are complete:
```
[Every 2 hours — existing]
Triage → Cleanup → Draft →
    ├── Graduated categories ──→ AUTO-SEND + log to BigQuery
    └── Non-graduated ─────────→ REVIEW_DRAFT → Human reviews → Human sends
                                                                      ↓
                                              [Background worker — every 30 min]
                                              Thread-Tracer reconciler
                                              → compares draft vs. sent version
                                              → calculates accuracy score
                                              → logs result to BigQuery
                                              → updates graduation status per category

[Parallel pipeline — Amazon, Phase 5]
SP-API webhook → Python fetches order data → Claude drafts reply →
    → "Pending Approval" queue → Human clicks Approve → SP-API sends
```

Each phase plugs into this architecture at a specific point:

| Phase | Where it plugs in | Change to existing flow |
|-------|-------------------|------------------------|
| 1 — Infrastructure | Underneath everything | None yet — setup only |
| 2 — WISMO + hardened flows | Triage (new labels) + Draft (Python branch) | Triage gets WISMO labels; Draft gets Python shortcut for hardened categories |
| 3 — Thread-Tracer | Draft (UUID injection) + new background worker | Draft appends hidden UUID; reconciler runs separately |
| 4 — Graduation logic | Draft (graduation check) | Graduated categories skip REVIEW_DRAFT and send directly |
| 5 — Amazon connector | Entirely new parallel pipeline | No change to Gmail pipeline |

---

## Auto-Reply Candidates

WISMO (Where Is My Order) is the **first pilot** because it is the most deterministic —
a Python script fetches the tracking link directly from Shopify, no AI guesswork involved.
But the graduation system is built generically. **Any category can graduate** once it
proves itself through the accuracy counter.

Candidates in order of predictability:

| Category | Why it's a candidate | What makes it harder than WISMO |
|----------|---------------------|--------------------------------|
| WISMO (order tracking) | Python fetch + fixed template = near-zero hallucination risk | Stuck/unfulfilled orders need human escalation |
| Shipping (general) | Tracking query, consistent answer | Some require carrier investigation |
| Order Modification | Cancel/modify has clear Shopify outcomes | Edge cases: partially shipped orders |
| Return Processing | Return label generation is procedural | Policy exceptions exist |
| Warranty (acknowledgment step) | Initial receipt confirmation is formulaic | Replacement decisions always need human |
| General Compatibility | Product specs are static KB data | New device releases create edge cases |

---

## Full Roadmap

---

### Phase 1 — Prerequisites
*Foundation infrastructure. Nothing else can be built without these.*

**1a — Shopify CLI Installation** ✅ COMPLETE
- Installed Shopify CLI on Windows CMD/CLI and authenticated against both stores
  (catalystcase.myshopify.com + catalystlifestyle.myshopify.com)
- Shopify CLI is a development tool for building Shopify apps/themes; recent versions also
  support GraphQL and bulk operations against the Admin API via terminal commands, and use
  ShopifyQL for analytics queries. It is NOT a general-purpose SQL tool and does not run
  inside Python scripts — Python scripts in Phase 2 will query the Shopify Admin API directly
  via HTTP (REST/GraphQL) using an access token.
- **Test:** ✅ Passed — test order query run against both stores, data returned correctly

**1b — Google Cloud Project + BigQuery Setup** ✅ COMPLETE
- GCP project: cs-mcp-gateway (#949282056449)
- Dataset: `catalyst_cs_accuracy` — tables `draft_log` + `accuracy_log` created and confirmed
- Service account: catalyst-bigquery-writer@my-mcp-drive-486418.iam.gserviceaccount.com
- IAM: BigQuery Data Editor + Job User granted at project level
- **Test:** ✅ Passed — test rows inserted and queried back clean on 2026-03-25

**BigQuery Schema — Accuracy Tracking:**

> ⚠️ Schema updated March 2026: UUID injection approach abandoned (Gmail API only supports
> plain text drafts — HTML span tags are stripped). Replaced with native Gmail metadata
> (thread_id + message_id) as the matching key. No email body modification required.
> draft_id retained as internal record ID only (not injected into email).

```sql
-- Table: draft_log
-- Records every draft created by the automation

draft_id         STRING    -- Internal record ID (UUID generated at write time — NOT injected into email)
thread_id        STRING    -- Gmail thread ID (stable across draft → send lifecycle)
message_id       STRING    -- Gmail message ID of the draft (PRIMARY match key for reconciler)
created_at       TIMESTAMP -- When the draft was created
email_category   STRING    -- e.g. CATALYST_US_WISMO, CATALYST_US_RETURN
sender_email     STRING    -- Customer email address
subject          STRING    -- Email subject line
claude_draft     STRING    -- Full text of Claude's original draft
shopify_order_id STRING    -- Order number if applicable (nullable)
store            STRING    -- "catalystcase" or "catalystlifestyle"
status           STRING    -- "PENDING" / "RECONCILED" / "ABANDONED"
                           -- ABANDONED: draft created but never sent (aged out after 14 days)
                           -- Prevents abandoned drafts from polluting accuracy scores

-- Table: accuracy_log
-- Records the reconciliation result after the human sends

draft_id           STRING    -- FK → draft_log.draft_id
thread_id          STRING    -- Gmail thread ID (for conversation-level grouping)
message_id         STRING    -- Gmail message ID matched in Sent (primary match key)
reconciled_at      TIMESTAMP -- When the reconciler matched the sent email
final_sent         STRING    -- Full text of the email actually sent
edit_distance      INTEGER   -- Levenshtein character distance (0 = perfect)
total_chars        INTEGER   -- Total characters in claude_draft
edit_pct           FLOAT     -- edit_distance / total_chars * 100
accuracy_score     FLOAT     -- 100 - edit_pct (capped at 100)
result             STRING    -- "PERFECT" / "MINOR_EDIT" / "MAJOR_EDIT" / "REWRITE"
semantic_match     BOOLEAN   -- Did the meaning stay the same? (embedding check)
agent_id           STRING    -- Gmail account that sent (for multi-agent future use)
```

**Result thresholds:**

| Result | Condition |
|--------|-----------|
| PERFECT | edit_distance = 0 |
| MINOR_EDIT | edit_pct < 5% |
| MAJOR_EDIT | edit_pct 5–50% |
| REWRITE | edit_pct > 50% |

---

### Phase 2 — WISMO + Hardened Flows
*First auto-reply pilot. Python replaces LLM for deterministic order tracking replies.*

**2a — WISMO Triage Labels** *(decision confirmed)*
- Two new dedicated labels: `CATALYST_US_WISMO` and `CATALYST_LIFESTYLE_WISMO`
- Separated from `CATALYST_US_SHIPPING` / `CATALYST_LIFESTYLE_SHIPPING` entirely
- Update classification rules in `catalyst_triage.md` and Python pre-filter
- WISMO intent: customer has an existing order and is asking for location or delivery estimate
- Keywords: "track", "where is", "haven't received", "status", "delivery" + order number
- **Test:** Run triage on a "where is my order" email, confirm WISMO label is applied (not SHIPPING)

**2b — WISMO Python Script**
- Input: order number (extracted from email)
- Process: Shopify AdminAPI → fulfillment status → carrier name + tracking link
- Output: Temperature 0 template — no LLM creativity
- Template: *"Your order [#] was shipped via [Carrier] on [Date] and is currently [Status].
  You can track it here: [Link]."*
- Stuck order detection: if order is unfulfilled for 3+ days → route to human review,
  do not auto-reply
- **Test:** Run against a real fulfilled order, confirm tracking link is accurate.
  Run against an unfulfilled order, confirm human routing fires.

**2c — Draft Flow Integration**
- Modify `catalyst_draft.md`: if label = WISMO → use Python script output instead of
  LLM KB lookup
- Initially still creates Gmail draft + REVIEW_DRAFT label (human still reviews)
- Auto-send activates only after Phase 4 graduation threshold is met
- **Test:** End-to-end — WISMO email arrives → triage labels it → draft creates response
  with correct tracking link → appears in Gmail for review

**2d — Stuck Order Escalation**
- Python script checks fulfillment age before fetching tracking
- Unfulfilled 3+ days: apply `ESCALATION_NEEDED` label instead of WISMO draft
- **Test:** Simulate unfulfilled order in test environment, confirm escalation label fires

---

### Phase 3 — Thread-Tracer (Accuracy Counter)
*Silent auditor that tracks every draft vs. what was actually sent. Zero friction for CS agents.*

> ⚠️ Design updated March 2026: Original UUID injection approach replaced with native Gmail
> thread_id + message_id matching. Reason: Gmail API only accepts plain text drafts — HTML
> span tags used for UUID hiding are stripped at send time. The thread-based approach is
> cleaner, more reliable, and requires zero email body modification.

**How it works:**
The CS agent continues using Gmail exactly as they do today — no new tools, no new buttons.
The Thread-Tracer operates invisibly in the background.

```
1. Claude creates a draft → thread_id + message_id + draft text logged to BigQuery draft_log
2. Human reviews draft in Gmail → edits if needed → clicks Send (unchanged workflow)
3. Background reconciler runs every 30 minutes:
   → Pulls recent Gmail Sent messages (last 30-60 min)
   → Extracts message_id + thread_id from each sent message
   → Joins against BigQuery draft_log (message_id primary, thread_id secondary)
   → Pulls final sent text
   → Compares to staged draft text using Levenshtein distance
   → Logs result to BigQuery accuracy_log table
4. Accuracy scores accumulate per category over time
```

**Why thread_id + message_id beats UUID injection:**
- No email body mutation — thread_id and message_id are system-generated, immutable Gmail metadata
- Cannot be accidentally deleted by a CS agent editing the draft
- Easier to debug (structured IDs vs. body text search)
- Enables conversation-level accuracy tracking across long threads (future Phase 4 analysis)
- message_id is unique per message — handles multi-draft threads cleanly with no ambiguity

**3a — Draft Staging** *(replaces UUID Injection)*
- Modify `catalyst_draft.md` Step 7: after creating each draft, Claude logs to BigQuery `draft_log`:
  - `draft_id` (internal UUID, generated at write time — not injected into email)
  - `thread_id` (from Gmail draft response)
  - `message_id` (from Gmail draft response — PRIMARY reconciler key)
  - `claude_draft` (full draft text)
  - `email_category`, `sender_email`, `subject`, `shopify_order_id`, `store`
  - `status = "PENDING"`
- Direct BigQuery write via MCP — no local file intermediary
- **Test:** Create a draft, query BigQuery draft_log directly, confirm all fields present and correct

**3b — Draft Staging** *(decision confirmed: staging file → Python flush)*
- BigQuery MCP is read-only (confirmed March 2026) — direct MCP write is not possible.
- Implemented approach: draft agent writes one JSON line per draft to `bq_staging.jsonl`
  via local-files MCP; `flush_bq_staging()` in the orchestrator reads the file after the
  draft run, inserts all rows to BigQuery via Python client, then clears the file.
- Benefits: atomic flush per cycle, write failure isolated to Python layer, BigQuery MCP
  still available for read queries during draft run.
- **Test:** ✅ Passed — 5 rows inserted and confirmed on 2026-03-27

**3c — Python Reconciler**
- Runs every 30 minutes as a separate scheduled task (independent of the 3-run cycle)
- Query order (Gmail first, then BigQuery join — avoids full draft_log scan each cycle):
  1. Pull Gmail `in:sent` messages from the last 30-60 minutes
  2. Extract message_id + thread_id from each
  3. Join against BigQuery draft_log WHERE status = "PENDING" on message_id (primary),
     thread_id (secondary fallback)
  4. For each match: pull sent text, compute Levenshtein distance, write to accuracy_log,
     update draft_log status → "RECONCILED"
  5. Age out PENDING records older than 14 days → update status → "ABANDONED"
     (draft created but never sent — excluded from accuracy scores)
- **Test:** Send a draft unedited → confirm PERFECT score.
  Edit a draft before sending → confirm score reflects the edit percentage.
  Leave a draft unsent for 14+ days → confirm status flips to ABANDONED.

**3d — Accuracy Dashboard**
- BigQuery query showing accuracy rate per category over time
- Triggered weekly (first Monday run) by the main orchestrator — no separate scheduled task
- **Test:** Run query against test data, confirm output is readable by non-technical reviewer

---

### Phase 4 — Graduation to Auto-Reply
*Categories that prove themselves graduate from human review to autonomous sending.*

**Graduation threshold:** ≥ 95% PERFECT or MINOR_EDIT results over 100+ emails for a category.

**4a — Graduation Query**
- BigQuery query that flags categories meeting the threshold
- Output: list of categories + current accuracy rate + email count
- **Test:** Seed test data at threshold, confirm query flags correctly

**4b — Graduation Config**
- A config file (or BigQuery table) that the draft agent checks before processing each email
- If category is graduated → skip REVIEW_DRAFT, send directly
- If not graduated → existing REVIEW_DRAFT flow continues unchanged
- **Test:** Toggle a test category to graduated, confirm draft sends without human step

**4c — Exception Handling**
- If Python script fails (Shopify lookup error, no tracking data) → always route to
  human review regardless of graduation status
- If LLM confidence is low or KB file unavailable → always route to human review
- These "edge cases" surface in the accuracy dashboard for focused attention
- **Test:** Simulate a failed Shopify lookup in a graduated category, confirm human
  routing overrides auto-send

**4d — Weekly Accuracy Report**
- Triggered every Monday by the main orchestrator (same dashboard as Phase 3d, extended
  with graduation candidates, edge cases, emails sent autonomously vs. human-reviewed)
- No separate scheduled task — orchestrator handles the Monday trigger
- **Test:** Run report manually, confirm format is shareable with boss

---

### Phase 5 — Amazon Connector
*⚠️ BLOCKED — requires prerequisites listed below before any build work can begin.*

**Prerequisites — action required before this phase is scoped:**
- Amazon Developer registration on Seller Central (US, CA, UK marketplaces)
- SP-API credentials per marketplace: Client ID, Client Secret, Refresh Token
- Confirmation of which message types to target (Buyer-Seller Messages, A-to-Z claims, or both)

**Compliance note:** Amazon TOS does not count automated replies toward the 24-hour
response time requirement. All Amazon replies — even AI-drafted ones — must be approved
and submitted by a human or a policy-compliant SP-API integration. **Full auto-send is
not permitted for Amazon.** The architecture below is designed to satisfy compliance
while eliminating 90% of the manual writing effort.

**Planned architecture (pending credentials):**

```
Amazon sends SP-API notification (B2B_ANY_MESSAGE_CHANGED event)
    ↓
Webhook endpoint receives event (HMAC-validated)
    ↓
Python fetches order data from Shopify AdminAPI
    ↓
Claude drafts reply (same KB + accuracy logic as Gmail pipeline)
    ↓
Draft appears in "Pending Approval" queue (separate from Gmail REVIEW_DRAFT)
    ↓
Human clicks Approve
    ↓
SP-API sends message → 24-hour metric satisfied → accuracy counter logs result
```

| Step | Task | Blocked by |
|------|------|-----------|
| 5a | SP-API webhook endpoint setup | SP-API credentials |
| 5b | Connector script: webhook → extract message → route to draft agent | SP-API credentials |
| 5c | "Pending Approval" queue separate from Gmail pipeline | 5a, 5b |
| 5d | Human Approve → SP-API send | 5c |
| 5e | HMAC signature validation on all incoming webhooks | 5a |
| 5f | Amazon accuracy counter integrated into BigQuery | Phase 3 |

---

### Phase 3.5 — Intent Layer + Semantic KB Retrieval
*Upgrades the draft pipeline from category-based KB lookup to semantic, intent-aware response generation.*
*Directly accelerates Phase 4 graduation by improving accuracy scores.*

> Design approved: March 2026. Building in 3 stages.

**Why this comes before Phase 4:**
The current draft pipeline does `category label → fixed KB file → draft`. This produces correct but
generic responses. The intent layer adds semantic understanding — the system detects what the customer
actually wants (not just which category they fall into) and retrieves the most relevant KB content by
meaning, not keyword. The result is fewer human edits, lower edit_distance in Thread-Tracer, and
faster accumulation of PERFECT/MINOR_EDIT scores needed for Phase 4 graduation.

**Architecture:**
```
Current:   Triage → [Category label] → Draft (fixed KB file) → Human review → Send
Phase 3.5: Triage → [Category label] → Semantic Retriever → Draft (top-3 KB + intent + sentiment) → Human review → Send
```

**Key decisions locked:**
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` — local, free, no API key
- Model version field stored in `kb_embeddings` table — never change without full re-embed
- Category system stays — semantic retrieval works WITHIN category filter, not replacing it
- No new database — `kb_embeddings` lives in existing `catalyst_cs_accuracy` BigQuery dataset
- Hybrid fallback: if semantic retrieval fails → existing label→filename mapping continues

**New files:**
- `catalyst_kb_embedder.py` — offline script, run once + re-run when KB changes
- `catalyst_semantic_retriever.py` — Run 3.5 in orchestrator (before draft)
- `intent_context.jsonl` — staging file (same pattern as bq_staging.jsonl)

**Modified files:**
- `catalyst_draft.md` — Steps 2.5 (intent extraction), 4 (semantic KB lookup), 6 (enriched prompt)
- `catalyst_cs_automation.py` — new Run 3.5, version bump to v4.8

---

**3.5a — Intent + Sentiment Extraction** *(Stage 1)*
- Add Step 2.5 to `catalyst_draft.md`: Claude extracts structured JSON before drafting
- Fields: `primary_intent`, `secondary_intent`, `sentiment`, `escalation_risk`
- Standalone value: immediate tone + escalation improvement
- **Test:** Run 5 emails, confirm JSON output is accurate and feeds into draft correctly

**3.5b — KB Embedding Store** *(Stage 2a)*

> ⚠️ Revised per June's Monday Ops Call (2026-04-07): Original plan was to chunk and embed
> CANONICAL files directly. June's directive adds a mandatory DATA CLEANING pre-step before
> any embedding. Original plan preserved below for reference.

*Original plan (superseded):*
- New script `catalyst_kb_embedder.py`: reads all CANONICAL skill files, chunks by Function row,
  generates local embeddings, stores to BigQuery `kb_embeddings` table
- Schema: `kb_id`, `filename`, `chunk_text`, `embedding`, `category`, `store`,
  `embedding_model` (locked: `all-MiniLM-L6-v2`), `created_at`

*Revised plan (active):*

**Step 1 — KB Data Cleaning (pre-embedding)**
- Scan all CANONICAL skill files for semantically similar entries (same intent, said differently)
- **SHA-256 content hashing** — detect exact duplicate chunks programmatically before clustering
  (production best practice: hash chunk text, skip duplicates before any embedding work)
- Cluster remaining entries by semantic similarity
- For each cluster: measure word frequency + entropy → pick the T0 word (most probable/dominant)
- Collapse each cluster to ONE canonical entry (T0 question + T0 answer)
- Principle per June: "50 ways to ask, 1 answer" — store the variants for recognition, not retrieval

**Step 2 — Embedding Store**
- Embed the cleaned T0 canonical entries using `all-MiniLM-L6-v2`
- **50-token overlap** between chunks — prevents loss of context at chunk boundaries
  (recommended: 300–512 tokens per chunk, 50-token overlap)
- **Embedding cache by content hash** — if KB file unchanged since last run, skip re-embedding
  (cache key = SHA-256 of chunk text; 24-hour TTL or until KB file changes)
- Schema: `kb_id`, `filename`, `canonical_question` (T0), `canonical_answer` (T0),
  `question_variants` (array — all ways to ask), `embedding`, `intent_cluster`,
  `category`, `store`, `embedding_model` (locked: `all-MiniLM-L6-v2`), `content_hash`,
  `created_at`
- **Why T0 storage:** Prevents the LLM from hallucinating across 50 slightly different
  variations. One definitive answer = higher retrieval accuracy. (June, 2026-04-07)

> ℹ️ Shopify/Vanchat embed model — VanChat does not disclose their embed model publicly (support
> email pending). Not a blocker: VanChat runs its own retrieval independently; our RAG is
> email-pipeline only. Proceeding with `all-MiniLM-L6-v2`. Revisit if we integrate KB into VanChat.

- **Test:** Run embedder, query BQ, confirm T0 canonical entries stored with question_variants and content_hash

**3.5c — Semantic Retriever** *(Stage 2b)*
- New script `catalyst_semantic_retriever.py`: embeds incoming emails, queries `kb_embeddings`
  for top-3 semantic matches per email, writes to `intent_context.jsonl`
- Runs as Run 3.5 in orchestrator (between Hardened and Draft)
- **Retrieval method (revised per June + article):** Hybrid using **BM25 + cosine similarity**
  combined via **Reciprocal Rank Fusion (RRF)**
  - Convert incoming question to T0 first, then run both searches in parallel
  - BM25 keyword search (term frequency + document length aware) — better than simple exact match
  - Cosine similarity against `all-MiniLM-L6-v2` embeddings
  - RRF combines both result lists into a single ranked output
  - Default weights: semantic 0.7, keyword 0.3 (tunable)
- **Test:** Run on 5 real emails, inspect `intent_context.jsonl`, confirm matches are semantically correct

**3.5d — Prompt Upgrade** *(Stage 3)*
- Update `catalyst_draft.md` Steps 4 + 6: consume `intent_context.jsonl` (intent + top-3 KB matches)
  instead of rigid label→filename table
- Claude receives: email + intent/sentiment + top-3 KB chunks + Shopify data
- **Test:** Run 20 real emails, compare edit_distance in accuracy_log vs pre-3.5 baseline

**3.5e — Graph RAG** *(Future — after 3.5d confirmed working)*

> New phase added per June's Monday Ops Call (2026-04-07).

- For concepts that are semantically unrelated in embedding space but contextually linked
  (e.g. "AirPods" ↔ "charging", "Watch" ↔ "band compatibility", "packaging" ↔ "shipping")
- The embed model (trained externally, not by us) cannot be retrained — Graph RAG corrects for it
- Implementation: manually seeded `graph_pairs` table in BigQuery
  - Columns: `concept_a`, `concept_b`, `relationship_type`, `notes`
  - Initial pairs to build: AirPods↔charging, Watch↔band, packaging↔shipping (expand over time)
- Retriever checks graph pairs when cosine similarity returns no good match
- **Why it matters:** Unlocks retrieval for related concepts the embed model considers unrelated.
  Significantly improves accuracy for cross-category questions (e.g. AirPods + charging case combo)
- **Test:** Seed a relational pair, run a cross-concept query, confirm retriever surfaces correct KB entry

---

## Summary Table

| Phase | What it builds | Technology | Status |
|-------|---------------|------------|--------|
| 1 | Shopify CLI + BigQuery infrastructure | Shopify CLI, GCP, BigQuery | ✅ Complete (1a + 1b) |
| 2 | WISMO + hardened flows | Python, Shopify AdminAPI, Temperature 0 | ✅ Complete (2b, 2c, 2d) |
| 3 | Accuracy counter (Thread-Tracer) | Python, BigQuery, Levenshtein distance | ✅ Complete (3a/3b/3c/3d) |
| 3.5a | Intent + sentiment extraction | Claude structured JSON, BigQuery columns | ✅ Complete — passive validation pending live email |
| 3.5b | KB data cleaning + embedding store | Python, sentence-transformers, BigQuery | 🔄 Next — revised plan (T0 cleaning pre-step) |
| 3.5c | Semantic retriever (hybrid) | Python, cosine similarity + exact match | Not started |
| 3.5d | Prompt upgrade | catalyst_draft.md, intent_context.jsonl | Not started |
| 3.5e | Graph RAG — relational pairs | BigQuery graph_pairs table | Planned — after 3.5d |
| 4 | Graduation to auto-reply | BigQuery queries, config toggle | Waiting on Phase 3.5 data |
| 5 | Amazon connector | SP-API, webhooks, Python | **Blocked — SP-API credentials needed** |
| — | Pirate Ship automation | Python, Pirate Ship API | Planned — separate project, after Phase 3.5 |

---

## Open Items (Decisions Needed)

| # | Question | Impact |
|---|----------|--------|
| ~~1~~ | ~~WISMO labels~~ | ✅ Resolved — new dedicated labels `CATALYST_US_WISMO` / `CATALYST_LIFESTYLE_WISMO` |
| ~~2~~ | ~~BigQuery staging~~ | ✅ Resolved — Claude writes directly to BigQuery via MCP/API |
| 3 | Amazon SP-API: developer registration status and credential availability for US, CA, UK? | Blocks Phase 5 entirely |
| 4 | Shopify/Vanchat embed model: what embed model do these platforms use internally? | VanChat does not publicly disclose their embed model. Likely OpenAI (`text-embedding-ada-002` or `text-embedding-3-small`) given GPT-4o/Claude 3 LLM stack. Support email sent — awaiting response. **Not a blocker for Phase 3.5:** VanChat handles its own live chat retrieval independently (crawls Shopify directly). Our Phase 3.5 RAG is email-pipeline only. Mismatch only matters if we later feed our KB into VanChat — not on current roadmap. Proceeding with `all-MiniLM-L6-v2`. |
| 5 | USPS Web Tools account (User ID) — June to provide | Blocks WISMO live tracking enhancement |

---

*Document maintained in: `C:\Users\pc\Documents\Catalyst-Projects\catalyst-cs-automation-roadmap.md`*
*Last updated: April 2026 — Phase 3.5 revised per June's Monday Ops Call (2026-04-07)*
