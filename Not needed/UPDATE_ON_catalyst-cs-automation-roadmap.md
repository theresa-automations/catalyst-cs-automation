# Catalyst CS — AI Automation Roadmap
**Version:** 1.0
**Date:** March 2026
**Status:** Planning — Phase 1 ready to start
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

The current automation runs as a 3-step hourly pipeline via Windows Task Scheduler:

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
[Hourly cycle — existing]
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

**1a — Shopify CLI Installation**
- Install Shopify CLI on WSL (Ubuntu) and authenticate against both stores
  (catalystcase.myshopify.com + catalystlifestyle.myshopify.com)
- Enables direct SQL-like queries against Shopify AdminAPI from Python scripts
- **Test:** Run a test order query against both stores and confirm data returns correctly

**1b — Google Cloud Project + BigQuery Setup**
- Create Google Cloud Project with billing enabled
- Create BigQuery dataset: `catalyst_cs_accuracy`
- Create initial tables (schema below)
- Identify and configure a BigQuery MCP server so Claude can write directly to BigQuery
  from within the draft workflow (required for Phase 3 Thread-Tracer)
- **Test:** Insert a test row into each table via MCP, query it back, confirm structure

**BigQuery Schema — Accuracy Tracking:**

```sql
-- Table: draft_log
-- Records every draft created by the automation

draft_id         STRING    -- Unique UUID injected into every draft
created_at       TIMESTAMP -- When the draft was created
email_category   STRING    -- e.g. CATALYST_US_WISMO, CATALYST_US_RETURN
sender_email     STRING    -- Customer email address
subject          STRING    -- Email subject line
claude_draft     STRING    -- Full text of Claude's original draft
shopify_order_id STRING    -- Order number if applicable (nullable)
store            STRING    -- "catalystcase" or "catalystlifestyle"

-- Table: accuracy_log
-- Records the reconciliation result after the human sends

draft_id           STRING    -- FK → draft_log.draft_id
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

**How it works:**
The CS agent continues using Gmail exactly as they do today — no new tools, no new buttons.
The Thread-Tracer operates invisibly in the background.

```
1. Claude creates a draft → hidden UUID appended to the bottom of the email body
2. UUID + draft text staged to BigQuery draft_log table
3. Human reviews draft in Gmail → edits if needed → clicks Send (unchanged workflow)
4. Background reconciler runs every 30 minutes:
   → Searches Gmail Sent folder for emails containing a UUID
   → Pulls final sent text
   → Compares to staged draft text using Levenshtein distance
   → Logs result to BigQuery accuracy_log table
5. Accuracy scores accumulate per category over time
```

**3a — UUID Injection**
- Modify `catalyst_draft.md`: append `[ref:{{uuid}}]` (non-visible formatting) to
  every draft before creating it via Gmail API
- **Test:** Create a test draft, confirm UUID is present, confirm it does not disrupt
  the visual appearance of the email

**3b — Draft Staging** *(decision confirmed: direct BigQuery write)*
- Claude writes UUID + draft text + metadata directly to BigQuery `draft_log` at the
  moment of draft creation — no local file intermediary
- Requires a BigQuery MCP (to be identified and configured during Phase 1b setup)
- Benefits: live "Accuracy Ledger" accessible from anywhere, no sync engine needed,
  immediate write failure detection, supports multiple agents simultaneously
- **Test:** Create a draft, query BigQuery directly, confirm record exists with correct data

**3c — Python Reconciler**
- Runs every 30 minutes as a separate scheduled task (independent of the 3-run cycle)
- Searches Gmail Sent folder: `in:sent [ref:`
- For each match: extracts UUID, retrieves staged draft from BigQuery, computes
  Levenshtein distance, calculates accuracy score, writes to `accuracy_log`
- **Test:** Send a draft unedited → confirm PERFECT score.
  Edit a draft before sending → confirm score reflects the edit percentage.

**3d — Accuracy Dashboard**
- BigQuery query showing accuracy rate per category over time
- Weekly scheduled query auto-generates report
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
- Scheduled BigQuery query every Monday: accuracy rate per category, graduation candidates,
  recent edge cases, emails sent autonomously vs. human-reviewed
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

## Summary Table

| Phase | What it builds | Technology | Status |
|-------|---------------|------------|--------|
| 1 | Shopify CLI + BigQuery infrastructure | Shopify CLI, GCP, BigQuery | Ready to start |
| 2 | WISMO + first hardened auto-reply flow | Python, Shopify AdminAPI, Temperature 0 | Ready after Phase 1 |
| 3 | Accuracy counter (Thread-Tracer) | Python, BigQuery, Levenshtein distance | Ready after Phase 1 |
| 4 | Graduation to auto-reply | BigQuery queries, config toggle | Ready after Phase 3 |
| 5 | Amazon connector | SP-API, webhooks, Python | **Blocked — SP-API credentials needed** |

---

## Open Items (Decisions Needed)

| # | Question | Impact |
|---|----------|--------|
| ~~1~~ | ~~WISMO labels~~ | ✅ Resolved — new dedicated labels `CATALYST_US_WISMO` / `CATALYST_LIFESTYLE_WISMO` |
| ~~2~~ | ~~BigQuery staging~~ | ✅ Resolved — Claude writes directly to BigQuery via MCP/API |
| 3 | Amazon SP-API: developer registration status and credential availability for US, CA, UK? | Blocks Phase 5 entirely |

---

*Document maintained in: `C:\Users\pc\Documents\Catalyst-Projects\catalyst-cs-automation-roadmap.md`*
*Last updated: March 2026*
