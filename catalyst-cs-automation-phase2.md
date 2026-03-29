[//]: # (═══════════════════════════════════════════════════════════════════)
[//]: # (  MAINTENANCE GUIDE — HOW TO UPDATE THIS FILE)
[//]: # (  This file is a living document. Every time a new improvement is)
[//]: # (  completed on the CS automation project, update it as follows:)
[//]: # ()
[//]: # (  1. UPDATE HEADER)
[//]: # (     — Keep "Period" end date as "Present" while work is ongoing)
[//]: # (     — Status stays "In Progress" until the improvement cycle closes)
[//]: # ()
[//]: # (  2. ADD AN IMPROVEMENT BLOCK under "Phase 2 Improvements — Completed")
[//]: # (     Each block follows this exact structure:)
[//]: # (     ### IMPROVEMENT N — Short Title)
[//]: # (     **The problem:** What was broken or missing, with specific symptoms)
[//]: # (     **Diagnosis:** How the root cause was found — tools used, reasoning)
[//]: # (     **The fix:** What changed and why — include code/query snippets if relevant)
[//]: # (     **The principle applied:** The transferable engineering lesson)
[//]: # (     **Result:** Concrete before/after — numbers, run times, error rates)
[//]: # ()
[//]: # (  3. UPDATE "In Progress / Upcoming" section)
[//]: # (     — Move completed items up into the Improvements section)
[//]: # (     — Add any new open items that surfaced during the work)
[//]: # ()
[//]: # (  4. UPDATE "Production Performance" table)
[//]: # (     — Reflect new metrics if the improvement affects run times or reliability)
[//]: # ()
[//]: # (  5. UPDATE "Version History" table)
[//]: # (     — Add the new version and one-line summary of what changed)
[//]: # ()
[//]: # (  6. ADD A NEW POST to the LinkedIn Post Series)
[//]: # (     Each post block must include:)
[//]: # (     — POST N — Title)
[//]: # (     — Status: [ ] Draft  [ ] Published)
[//]: # (     — Hook: the opening line)
[//]: # (     — Narrative arc: full story with problem / diagnosis / fix / lesson)
[//]: # (     — Key lines: 2-4 quotable lines for the post body)
[//]: # (     — Tone: register and audience direction)
[//]: # (     — Image brief: standalone visual concept for image generation)
[//]: # ()
[//]: # (  RULE: Never delete or overwrite existing improvement blocks or posts.)
[//]: # (  Append only. This file is the cumulative record of the project.)
[//]: # (═══════════════════════════════════════════════════════════════════)

# Project: AI-Powered CS Automation — Phase 2: Architecture Overhaul & Reliability Engineering
**Client:** Catalyst Products
**Period:** March 17, 2026 – Present
**Status:** In Progress (active improvement cycle)

---

## Project Context — What Phase 1 Built

Phase 1 delivered a working AI email triage system for Catalyst Products' two Shopify
storefronts (Catalyst Case US + Catalyst Lifestyle International). The system:

- Automatically classified inbound customer emails into 16 issue categories
- Filtered B2B, spam, and automated senders before reaching LLM classification
- Applied dual Gmail labels (classification tag + AI_PROCESSED) to every email
- Was orchestrated by a **Rube.app recipe** called "Email Triage v2 - Granular" (reached v20)
- Ran via Task Scheduler hourly, 8am–6pm WAT, Monday–Friday

Phase 1 was declared live and stable. Phase 2 began the moment the client decided the
architecture needed a full overhaul — not because Phase 1 broke, but because it depended
on an external platform (Rube.app) that the client wanted to eliminate entirely.

---

## The Core Decision That Triggered Phase 2

**The instruction:** "I want to eliminate Rube completely and run the triage logic directly
through Claude CLI/Desktop."

This was not a bug fix. It was a deliberate architectural decision:

| Before (Phase 1) | After (Phase 2) |
|-----------------|-----------------|
| Rube.app recipe (cloud, external) | catalyst_triage.md (local, version-controlled) |
| Rube API handles Gmail calls | Claude CLI handles Gmail via MCP directly |
| Rube's scheduling mechanism | Python script + Windows Task Scheduler |
| Triage only | Triage + Cleanup + Draft (full pipeline) |
| 8am–6pm WAT, Mon–Fri | 6am–11pm WAT, 7 days |
| Tokens in Rube's cloud config | Tokens in secrets.env, injected at runtime |

**Why it mattered — reason 1 (architectural):** Rube was a dependency outside the
client's control — it ran in the cloud, held configuration state externally, and
represented a single point of failure. Moving everything local meant the entire CS
automation stack lives in one folder (`C:\Users\pc\Documents\Catalyst-Projects`),
runs identically on Claude CLI and Claude Desktop, and can be version-controlled,
audited, and modified without touching any external platform.

**Why it mattered — reason 2 (operational, the breaking point):** After the first week
of smooth operation, the system began dropping mid-session — Claude CLI connections
were silently terminating before completing their work cycle. The root cause was
architectural: a single script was being asked to carry the full weight of the pipeline
in one uninterrupted session — email retrieval, multi-level classification across
potentially dozens of messages, Shopify order lookups, Google Drive knowledge base reads,
and draft generation — all chained together with no isolation between stages. Under
light volume, it held. As email volume scaled and the task graph grew more complex,
the session couldn't sustain the load. One slow MCP call, one network hiccup, or one
large inbox fetch was enough to bring the entire run down with no recoverable output.

This wasn't a bug to patch — it was a signal that the single-script model had hit its
ceiling. The pipeline needed to be decomposed into bounded, independently survivable
stages, each with its own timeout, its own MCP scope, and its own failure boundary.
That decomposition is what Phase 2 delivered.

---

## What the Rube Recipe Actually Did (What We Had to Replicate)

The Rube "Email Triage v2 - Granular" recipe (v20) was a production-grade email
classification system with the following logic — all of which had to be faithfully
reproduced in catalyst_triage.md:

### Classification Priority Order (9 levels before LLM fallback)
| Rule | Trigger | Action |
|------|---------|--------|
| 0 | `notifications@fillout.com` + "Warranty Claim Form" subject | Parse body for Ms/# order prefix → US or Lifestyle WARRANTY |
| 0.1 | `mailer@shopify.com` | B2B_FILTERED (Shopify system notifications) |
| 0.2 | `mailer@vanchat.io` | Keyword routing: customer keywords → LLM; system keywords only → B2B_FILTERED |
| 0.5 | `@paypal.com`, `@amazon.com/co.uk/ca` | Chargeback keyword scan → US or Lifestyle CHARGEBACK; else B2B_FILTERED |
| 1a | EC-Ship/postal senders | B2B_FILTERED |
| 1b | "Re:" subject + pitch keywords | B2B_FILTERED (unsolicited business pitches disguised as replies) |
| 1 | 22 known B2B domains + spam sender patterns | B2B_FILTERED |
| 1.5 | Chinese characters in subject OR promotional subject keywords | B2B_FILTERED |
| 2–3 | Event/trade show content, B2B/promotional body keywords | B2B_FILTERED |
| 4 | No rule matched | LLM classification via Claude (reasoning_effort=medium) |

### The 16 Classification Tags
- **US orders** (Ms prefix): WARRANTY, RETURN, SHIPPING, OOS, ADDRESS, ORDERMOD, GENERAL, CHARGEBACK
- **International orders** (# prefix): same 8 categories under CATALYST_LIFESTYLE_*
- **General inquiries** (no order): GENERAL_PRODUCT, GENERAL_COMPATIBILITY, GENERAL_PREORDER
- **Filtered**: B2B_FILTERED

### Two LLM Prompts (exact, replicated from Rube)
1. **VanChat Prompt** — used when `mailer@vanchat.io` passes the keyword check
2. **Main Classification Prompt** — used for all other unmatched emails

Both prompts use the same 16-tag taxonomy with strict JSON-only output format.

### Anti-Rerun Logic (v19 bug fix carried forward)
- Upfront label ID → name reverse map (fixed a bug where re-checking already-classified
  emails caused duplicate labels in Rube v17/v18)
- Skip logic: `AI_PROCESSED + classification tag present` → skip entirely
- Rerun logic: `AI_PROCESSED + no classification tag + still unread` → reprocess

This entire logic block was translated from Rube's Python recipe into the
`catalyst_triage.md` prompt file, which Claude CLI executes directly.

---

## Technologies Used
Claude AI CLI · Model Context Protocol (MCP) · Gmail MCP · Shopify MCP (×2) ·
Google Drive MCP · Local Files MCP · Docker Desktop · Docker MCP Toolkit ·
Python · Node.js · Google OAuth2 · Windows Task Scheduler

---

## Phase 2 Improvements — Completed

---

### IMPROVEMENT 1 — Architecture Migration: Rube → Claude CLI + Python

**What changed:**
- Translated the complete Rube Email Triage v2 Granular recipe (v20, 9 priority rules,
  16 tags, 2 LLM prompts) into `catalyst_triage.md` — a plain markdown prompt file
  that Claude CLI reads and executes via `--mcp-config` and `-p` flags
- Built `catalyst_cs_automation.py` as the Python orchestrator: validates pre-flight
  (file existence, secrets, MCP config), handles business hours (WAT timezone),
  injects secrets as environment variables, runs Claude CLI as a subprocess with
  configurable timeout, and writes structured logs to `automation_log.txt`
- Extended scope beyond triage: the workflow now covers a full 3-run pipeline
  (Triage → Cleanup → Draft) whereas Rube only handled classification
- Expanded operating hours: 6am–11pm WAT, 7 days (vs. 8am–6pm Mon–Fri)

**Why:** Eliminate external cloud dependency. Own the full stack locally. Enable
version control and direct modification without touching external platforms.

---

### IMPROVEMENT 2 — Security Architecture: Token Management Overhaul

**The problem (pre-Phase 2):** Shopify API tokens were hardcoded in configuration files
as plaintext. The client's technical advisor flagged this as a critical security risk —
an AI system with live Shopify access and plaintext tokens could, in a worst case,
perform destructive actions across the entire store.

**What was built:**

**a) secrets.env + runtime injection**
Shopify tokens moved to a standalone `secrets.env` file. The Python orchestrator reads
this file at runtime, validates tokens are present and non-placeholder, then injects
them as environment variables for the subprocess. The MCP config file (`mcp.json`) uses
`${SHOPIFY_TOKEN_CATALYSTCASE}` and `${SHOPIFY_TOKEN_CATALYSTLIFESTYLE}` placeholders —
no actual token values are ever written into any config file used by the automation.

**b) Docker MCP Toolkit integration**
Docker Desktop was configured with Docker MCP Toolkit (beta feature). A `setup.py`
utility was built to:
- Validate tokens in secrets.env
- Sync them to Docker secrets vault (`docker-mcp.exe secret set`)
- Verify Claude Desktop config is current
A single `python setup.py` command handles all three steps, making token rotation
a one-command operation.

**c) Zero-trust rationale (from client's technical advisor):**
Each MCP runs in a separate container → contamination of one cannot affect others.
Tokens passed as Docker secrets are locally encrypted and never exposed in config files
or terminal output. OAuth-connected MCPs (GitHub, Miro) use rotating keys, eliminating
manual token rotation entirely.

**Result:** `mcp.json` has zero plaintext tokens. Rotation requires updating one file
(`secrets.env`) and running one command (`python setup.py`).

---

### IMPROVEMENT 3 — Workflow Split: Combined Run → Three-Stage Pipeline

**The problem:** The initial v4.0 implementation put triage, cleanup, and draft generation
into a single combined workflow file (`catalyst_workflow.md`) with a 10-minute timeout.
The first live run timed out at exactly 10 minutes with zero output — Claude never finished.

**Diagnosis process:**
1. Increased timeout to 20 minutes — still timed out with no output
2. Ran direct MCP connectivity test (`claude.exe -p "list all MCP tools"`) to rule out
   MCP initialization hang — all MCPs connected cleanly
3. Identified that the combined workflow was trying to do triage + Gmail cleanup +
   Shopify lookups + Google Drive reads + draft creation in one uninterrupted chain.
   One slow MCP call midway through would block the entire run

**The fix — three independent runs per cycle:**

| Run | File | Timeout | MCPs Used | Responsibility |
|-----|------|---------|-----------|----------------|
| 1 — Triage | catalyst_triage.md | 15 min | Gmail only | Classify new emails |
| 2 — Cleanup | catalyst_cleanup.md | 8 min | Gmail only | Remove REVIEW_DRAFT from replied threads |
| 3 — Draft | catalyst_draft.md | 20 min | Gmail + Shopify + GDrive | Generate response drafts |

Each run is independently timed out and logged. A failure in Run 1 does not prevent
Runs 2 and 3 from executing. The Python orchestrator tracks success/failure per stage
and reports them individually.

**Why this matters architecturally:** Isolating by MCP dependency means a Shopify
connectivity issue only affects Run 3, never Run 1. Timeout calibration matches actual
workload: lightweight Gmail-only operations get tight timeouts; heavy multi-MCP
operations get generous timeouts.

---

### IMPROVEMENT 4 — Triage Timeout: Query Optimization (v4.2 → v4.3)

**The problem:** Even after the workflow split, the triage run (Gmail-only, should be
fast) kept timing out at its 10-minute ceiling with no output on many cycles.

**Diagnosis:** Audited the Gmail search query used in Step 1:
```
in:inbox is:unread after:[cutoff_date]
```
The workflow keeps all emails **unread** after processing (human review requirement).
This means every hourly triage run re-fetches ALL previously classified emails going
back 7 days — because `is:unread` is not a proxy for "unprocessed." With 100+ emails
accumulating in the backlog, each run was making 200+ sequential API calls just to
identify and skip emails that were already classified in previous runs — before doing
any classification work.

**The fix:** Added `-label:AI_PROCESSED` to the search query:
```
in:inbox is:unread after:[cutoff_date] -label:AI_PROCESSED
```
Already-processed emails are excluded at the query level. Zero API calls wasted on
emails the agent will only skip.

**The principle applied:** Fix the query, not the timeout. Raising the timeout ceiling
treats a symptom. The search returning 100 emails where 97 need to be skipped is a
data retrieval problem, not a time problem.

**Result:** Triage run time: 10+ min (timeout) → **~2 minutes**. Timeout ceiling also
raised from 10 to 15 minutes as a secondary safety net.

---

### IMPROVEMENT 5 — Cleanup Timeout: Sequential API Call Elimination (v4.2 → v4.3)

**The problem:** The cleanup agent fetched all REVIEW_DRAFT threads (22+), then called
`read_email` on each one to inspect the last message sender. N threads = N sequential
API calls. The 5-minute ceiling was hit as the backlog grew.

**The fix:** Replaced the read-per-thread loop with two targeted Gmail searches:
```
Search 1: label:REVIEW_DRAFT from:cs@catalystcase.com
→ threads cs@ has replied to → remove REVIEW_DRAFT (sender confirmed by query, no read needed)

Search 2: label:REVIEW_DRAFT -from:cs@catalystcase.com
→ still-pending threads → count only, no action
```
Eliminated all individual `read_email` calls. The search query does the work that
22+ API calls were doing.

**Result:** Cleanup run time: 5+ min (timeout) → **~1 minute**. Timeout raised to
8 minutes as secondary safety net.

---

### IMPROVEMENT 6 — Google Drive MCP: OAuth2 Auto-Refresh Fix (v4.3)

**The problem:** The GDrive MCP server was returning `invalid_request` on every call,
making the knowledge base unavailable for all draft runs. All 5 drafts in one cycle
were sent with `⚠️ KB unavailable — verify policy details before sending`.

**Initial hypothesis:** Token expired — solution is to re-authenticate.

**Why that was wrong:** The user had authenticated the previous day. A Google OAuth2
access token expires in 1 hour. Re-authenticating would produce the same failure 1 hour
later. The refresh token (long-lived) was present and valid — the server just couldn't
use it.

**Root cause:** The GDrive MCP server (`dist/index.js`) instantiated its OAuth2 client
without credentials:
```javascript
const auth = new google.auth.OAuth2();   // No client_id, no client_secret
auth.setCredentials(credentials);
```
Without `client_id` and `client_secret`, the OAuth2 client has no mechanism to exchange
the refresh token for a new access token. It fails silently every hour when the access
token expires.

**The fix (Node.js — `dist/index.js`):**
- Load `client_id`, `client_secret`, and `redirect_uri` from `gcp-oauth.keys.json`
  (already on disk from initial setup)
- Pass them into the constructor: `new google.auth.OAuth2(client_id, client_secret, redirect_uri)`
- Register a `tokens` event listener that writes refreshed tokens back to the
  credentials file — making each refresh durable across server restarts

**Result:** GDrive MCP now auto-refreshes silently every hour. No manual re-authentication
required. KB available for all draft runs.

---

### IMPROVEMENT 7 — Fillout Warranty Email: Pipeline Unblock (v4.3)

**The problem:** The Rube recipe (Rule 0) classified `notifications@fillout.com` emails
as customer warranty tickets. When replicated in catalyst_triage.md, this created a
recurring problem: Fillout sends one-way platform notifications — they cannot be replied
to. The draft agent's pre-flight correctly flagged them as MISLABELED (notifications@
sender), but only skipped them without fixing the labels.

Result: 17 real warranty claim emails were permanently stuck in the draft queue, appearing
as MISLABELED on every single cycle. They consumed pre-flight processing time and blocked
the queue from clearing.

**The fix — two parts:**

1. **Triage Rule 0 updated:** `notifications@fillout.com` now routes to `B2B_FILTERED`
   immediately. The warranty classification from Rube was correct in intent but wrong in
   execution — the notification email is not the customer thread.

2. **Draft pre-flight upgraded from passive to active:** When MISLABELED fires, the agent
   now corrects the labels: adds `B2B_FILTERED`, removes the classification label, retains
   `AI_PROCESSED`. The email is permanently removed from future draft queue runs.

**Result:** All 17 backlogged Fillout emails cleared in one run. They will not reappear.

*Note: A dedicated Fillout-to-customer workflow — extracting the actual customer email
from the form payload and drafting directly to them — is scoped for a future cycle.*

---

### IMPROVEMENT 9 — Triage: Opened Emails No Longer Skipped (v4.3 → v4.4)

**The problem:** The triage search query included `is:unread`. Any email a team member
opened before the hourly triage run would silently fail to be classified — the query
excluded it, no error, no flag. Emails reviewed manually before automation ran were never
entering the pipeline at all.

**The fix:** Removed `is:unread` from the triage Step 1 search query:
```
Before: in:inbox is:unread after:[cutoff_date] -label:AI_PROCESSED
After:  in:inbox after:[cutoff_date] -label:AI_PROCESSED
```
The `AI_PROCESSED` exclusion is the correct guard against re-processing. Read/unread
status is irrelevant to whether an email has been classified.

**Result:** All inbound customer emails from the last 7 days now enter triage regardless
of whether a team member opened them first.

---

### IMPROVEMENT 10 — Cleanup: Condition B — Read Email Detection (v4.3 → v4.4)

**The problem:** Cleanup only removed `REVIEW_DRAFT` from threads where cs@ had replied
via Gmail (Condition A). Emails resolved through other channels — Shopify notes, phone
calls, or manual action outside email — kept their `REVIEW_DRAFT` label and reappeared
in the pending queue every run. The system had no way to distinguish "genuinely waiting"
from "resolved elsewhere."

**The fix:** Added Condition B to the cleanup workflow:
```
Search 2: label:REVIEW_DRAFT is:read
→ Email has been opened by a human → remove REVIEW_DRAFT → record as "cleaned (read)"
```
A read email means a human reviewed it. That is sufficient to clear the REVIEW_DRAFT
marker — cs@ being the last sender is not required.

**The principle applied:** Let system state (read/unread) carry meaning rather than
requiring every resolution path to go through the same channel.

**Result:** Cleanup now surfaces a true count of genuinely pending threads (unread, cs@
has not replied) rather than a mix of pending and already-resolved items.

---

### IMPROVEMENT 11 — Python Pre-Filter: B2B Classification Before LLM (v4.4)

**The problem:** Every triage run passed all fetched emails to Claude for classification,
including the 80–90% that could be identified as B2B/spam using simple string matching
on sender domain, subject line, and body keywords. This wasted LLM calls and added
latency to every cycle.

**The fix:** Rules 0–3 from `catalyst_triage.md` were replicated in pure Python inside
`catalyst_cs_automation.py`:
- 22 known B2B domains
- Spam sender prefixes (noreply@, mailer-daemon@, etc.)
- Chinese character detection in subjects
- Promotional keyword matching
- Event/trade show content keywords
- B2B body content keywords

A pre-filter fetch runs first (2-min fast call). The Python engine classifies each
email against Rules 0–3. Only Rule 4 fallbacks (genuinely ambiguous) are passed to
Claude for LLM classification. Pre-classified B2B emails are batched and labeled in
a single call.

**Result:** ~80–90% reduction in LLM calls per triage run. Claude only reads emails
that actually need reasoning.

---

### IMPROVEMENT 12 — Per-Workflow Minimal MCP Config (v4.4)

**The problem:** Every run — triage, cleanup, and draft — loaded all 9 connected MCP
servers at startup, including LinkedIn, gdrive-personal, memory, and MCP_DOCKER. These
MCPs are unused in the CS automation workflow but their initialization still had to
complete (or fail) before Claude could begin work. At least one was hanging on startup,
blocking runs before any useful work occurred.

**The fix:** `build_mcp_config(workflow)` generates a trimmed MCP config file at runtime,
containing only the servers each workflow actually needs:

| Workflow | MCPs Loaded |
|----------|------------|
| Triage | gmail, local-files |
| Cleanup | gmail, local-files |
| Draft | gmail, shopify-manager-catalystcase, shopify-manager-catalystlifestyle, gdrive, local-files |

Three temp files (`_mcp_triage.json`, `_mcp_cleanup.json`, `_mcp_draft.json`) are
generated per run from the full `mcp.json` — no manual editing required.

**Result:** Startup time reduced. Unused MCPs cannot block or hang any workflow run.
A Shopify connectivity issue only affects Run 3 — Gmail-only runs are unaffected.

---

### IMPROVEMENT 13 — Process Tree Kill on Timeout (v4.4)

**The problem:** When Claude CLI timed out, `subprocess.run(timeout=...)` killed the
main `claude.exe` process but left all child processes (the Node.js MCP servers it
spawned) running in the background. These orphaned `node.exe` processes accumulated
over multiple timed-out runs, consuming memory and potentially interfering with
subsequent runs.

**The fix:** Switched from `subprocess.run()` to `Popen` + `communicate(timeout)` +
`taskkill /F /T /PID` on timeout:
```python
proc = subprocess.Popen([...])
try:
    stdout, stderr = proc.communicate(timeout=timeout)
except subprocess.TimeoutExpired:
    _kill_process_tree(proc.pid)   # taskkill /F /T — kills entire tree
    proc.communicate()             # drain pipes after kill
```
`/T` flag kills the process and all descendants. No orphan MCP servers remain after
a timed-out run.

**Result:** Clean process teardown on every timeout. No accumulating background processes
between runs.

---

### IMPROVEMENT 14 — API Call Reduction: Batch Labeling + Two-Layer Caching (v4.4)

**The problem:** Three separate inefficiencies were generating unnecessary API calls on
every run:

1. **One label per email:** Triage was calling `modify_email` for each classified email
   individually — 20 emails with B2B_FILTERED = 20 API calls.

2. **Gmail label map fetched every run:** The label name → ID map was re-fetched from
   Gmail on every triage cycle despite rarely changing.

3. **GDrive KB read every run:** Draft was hitting Google Drive for knowledge base files
   on every run, even when the same KB file had been read an hour earlier.

**The fixes:**

**Batch labeling:** All emails sharing the same classification tag are grouped, then
labeled in a single `batch_modify_emails` call per tag group. 17 B2B + 3 warranty +
2 shipping = 3 calls, not 22.

**Label map cache:** Gmail label IDs are written to `label_cache.json` on first fetch.
Subsequent runs within 24 hours use the local cache — zero API calls for label lookup.

**KB file cache:** GDrive knowledge base files are written to `kb_cache/[filename].md`
on first read. Subsequent runs within 24 hours use the local file. GDrive is only
contacted on cache miss or when the 24-hour TTL expires.

**Result:** Per-cycle API call reduction: label lookups (N calls → 0 cache hit),
labeling (N calls → ~2–3 batch calls), KB reads (1 GDrive call → 0 cache hit).
Confirmed in first production run: `warranty_claim.md` cache hit, `order_modification.md`
GDrive fetch → cached for next run.

---

### IMPROVEMENT 15 — Draft Queue Fix: is:unread + 7-Day Cutoff (v4.4)

**The problem:** 42 emails were sitting in the draft queue — all technically eligible
(classified + AI_PROCESSED + no REVIEW_DRAFT). Most were old threads already resolved
by the CS team. The cleanup's Condition B (Improvement 10) correctly removed REVIEW_DRAFT
from read/resolved emails, but without a date or read-state filter on the draft side,
those same emails re-entered the queue on the next draft run. The draft was timing out
processing a 42-email backlog.

**Diagnosis:** The draft Step 1 search had no `is:unread` filter and no date cutoff.
Every eligible email regardless of age or read state was being fetched and processed.

**The fix:** Two filters added to draft Step 1:
```
Added: is:unread   — attended-to emails (read or replied to) are excluded
Added: after:[7-day cutoff]  — old backlog cannot re-enter the queue
```
Also added a second search (Search B) to catch unread + AI_PROCESSED emails with no
classification label — customer replies on existing threads that triage left
unclassified (simple acknowledgments, follow-ups). These are handled using thread
context to infer the issue type and store.

**Result:** Eligible emails: 42 → 6. Draft run time: timeout (30 min) → **11 minutes**.
5 drafts created, 0 errors.

---

### IMPROVEMENT 16 — Draft: Thread Context Before Writing (v4.4)

**The problem:** Draft responses were generated using only the most recent email in the
thread. If cs@ had already offered a replacement in a prior message, the draft might
offer it again — or worse, offer something different. If the customer had declined a
refund, the draft had no way to know.

**The fix:** Added Step 3a to the draft workflow — read the last 5 messages of the
thread before generating any response. Extract:
- What the customer originally asked or reported
- How cs@ has responded in the past (tone, offers made, commitments given)
- Whether any resolution was already offered (replacement, refund, label sent)
- Whether the customer has escalated frustration across multiple messages

Thread context rules added to Step 6 (draft generation):
- Prior commitment exists → acknowledge it, do not re-offer differently
- Customer declined prior offer → do not repeat; escalate or offer alternative
- Escalated/frustrated customer → open with empathy, reference prior exchange
- Consistent tone in thread → match it
- Issue already resolved in thread → flag for human review, do not auto-draft

**Result:** Drafts now reflect the full conversation history, not just the trigger email.
Validated in production: Robert Sova's two questions on the same thread were addressed
in a single draft using full thread context.

---

### IMPROVEMENT 17 — Draft: Classification Labels Made Permanent (v4.4)

**The problem:** Draft Step 7 was calling `modify_email` to remove the classification
label (e.g. CATALYST_US_WARRANTY) after creating a draft. This was incorrect — it
meant the label history for each email was being erased, eliminating the audit trail
of how each email was classified. It also meant that if a draft was deleted or not
sent, the email had no classification label and would not be re-picked by any workflow.

**The fix:** Step 7 updated — only `REVIEW_DRAFT` is added after draft creation.
Classification labels are never removed by the draft agent. AI_PROCESSED is already
present and is not re-added. The note in the workflow is explicit:
`"Do NOT remove the classification label — it stays permanently for audit history."`

**Result:** Full label history preserved per email. No silent data loss on draft
creation.

---

### IMPROVEMENT 8 — Windows Subprocess: UTF-8 Encoding Stability

**The problem:** Claude CLI subprocess calls were crashing on Windows when email content
contained non-ASCII characters (Chinese characters, special symbols, Unicode in subject
lines). The crash produced no useful error — the subprocess returned a non-zero exit code
with garbled output.

**The fix:** Explicit encoding parameters added to all `subprocess.run()` calls:
```python
result = subprocess.run(
    [...],
    capture_output=True,
    encoding="utf-8",
    errors="replace",   # Replace undecodable bytes rather than crashing
    ...
)
```
Also added `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` to the subprocess environment.

**Result:** Non-ASCII content is handled gracefully. The system processes emails with
Chinese subjects (Rule 1.5 — B2B_FILTERED), Korean customer names, and special
characters without instability.

---

## Test & Validation Methodology

Each fix was validated using `--force` CLI flags with staged isolation before returning
to scheduled operation:

```bash
python catalyst_cs_automation.py --force --triage-only    # Validate triage in isolation
python catalyst_cs_automation.py --force --cleanup-only   # Validate cleanup in isolation
python catalyst_cs_automation.py --force --draft-only     # Validate GDrive + Fillout fix
python catalyst_cs_automation.py --force                  # Full cycle validation
```

Staged testing on production data is non-negotiable for a multi-stage pipeline where
a failure in one run can mask or compound issues in subsequent runs.

---

## Production Performance: Before vs After Phase 2

| Metric | Phase 1 / Phase 2 Start | Current (v4.9 system / v4.7 orchestrator) |
|--------|------------------------|------------------------------------------|
| Triage | Rube cloud recipe (external) | Local ~4 min |
| Cleanup | Not in scope | Local ~1 min |
| Draft | Not in scope | Local ~10 min |
| Full cycle | Rube triage only | ~15–20 min total (5 steps + Monday dashboard) |
| Draft queue size | N/A | 42 (backlog) → 6 (steady state) |
| LLM calls per triage | All emails → LLM | ~10–20% (pre-filter catches ~80–90%) |
| Label API calls per triage | N per email | ~2–3 batch calls total |
| GDrive KB calls per draft | 1 per KB file per run | 0 (cache hit, 24hr TTL) |
| Opened-email miss | Silent (is:unread filtered them) | Fixed — all 7-day emails fetched |
| Thread context in drafts | None | Last 5 messages read before drafting |
| Classification label lifecycle | Removed after draft | Permanent (audit history preserved) |
| GDrive KB | Not in scope | Auto-refreshes + local cache |
| Token security | Plaintext in config files | secrets.env + Docker vault |
| Schedule | 8am–6pm WAT, Mon–Fri | 6am–11pm WAT, 7 days |
| External dependencies | Rube.app (cloud) | None |
| Fillout routing | B2B_FILTERED (incorrect) | WARRANTY via body parsing + draft exemption |
| KB mapping (OOS/ADDRESS/GENERAL) | "Warranty Claim" (incorrect) | Correct files per category |
| GDrive KB folder | Unspecified | Customer_Support_Claude_Skills |
| Script version | v4.0 → v4.2 | v4.7 (orchestrator .py) / v4.9 (system) |

---

## Version History (Phase 2)

| Version | Key Change |
|---------|-----------|
| v4.0 | Initial combined workflow (triage + cleanup + draft in one run). Timed out immediately at 10 min |
| v4.1 | Split into Run 1 (triage) + Run 2 (draft). Cleanup not yet separated |
| v4.2 | Three-run architecture: triage / cleanup / draft. Timeout ceilings tuned per stage |
| v4.3 | Triage query optimization (-label:AI_PROCESSED). Cleanup sequential call elimination. GDrive OAuth2 auto-refresh fix. Fillout pipeline unblock. Timeout ceilings re-tuned |
| v4.4 | Python pre-filter (Rules 0–3 in Python, ~80–90% LLM call reduction). Per-workflow minimal MCP config (no unused MCP startup hangs). Process tree kill on timeout (no orphan node.exe). Triage: removed is:unread filter (was missing opened emails). Cleanup Condition B (read = attended). Draft: is:unread + 7-day cutoff (42 → 6 eligible). Draft thread context (last 5 messages before drafting). Draft classification labels made permanent. Search B for simple replies. Batch labeling. Label map cache + KB file cache |
| v4.5 | Prompt file audit: 5 discrepancies resolved across catalyst_triage.md, catalyst_draft.md, catalyst_workflow.md. Fillout warranty routing restored (triage Rule 0 + draft exemption CHECK 2 + Python pre-filter pass-through). KB mappings corrected (OOS → Out-of-Stock Guide, ADDRESS → Order Modification + Address Verification, GENERAL → keyword/device fallback). GDrive KB folder specified (Customer_Support_Claude_Skills). Full cycle validated on production data. Phase 3 roadmap approved. |
| v4.6 | Pre-Phase 3 consistency audit: WISMO labels (CATALYST_US_WISMO / CATALYST_LIFESTYLE_WISMO) added to catalyst_triage.md (RULE 3.5 + LLM prompts), catalyst_draft.md (eligible labels + KB routing), catalyst_workflow.md (label list + RULE 3.5 + prompts + draft sections). Roadmap Phase 1a Shopify CLI description corrected. Phase 3a UUID hidden HTML implementation locked. Draft style rules added: em dash ban + 5-category AI language ban. Pre-filter timeout 120s → 180s. Rule 3 quoted-line stripping (Carl Ball false positive fix). Task Scheduler full Python path fix (auto-trigger confirmed). Phase 1b BigQuery connectivity confirmed on cs-mcp-gateway. |
| v4.7 | KB governance restructure: 3 informal guide files deleted, replaced by 6 CANONICAL skill files (address-verification US+intl, oos-notification US+intl, warranty-claim US+intl v1.1). Temperature Zero compliance: Approved Language + Forbidden blocks added to all functions in warranty, OOS, and address skills. catalyst_draft.md Step 4 routing updated to exact CANONICAL filenames. GDrive KB folder updated to Skills/ inside Claude_KB. *(KB/prompt-layer change — no orchestrator .py bump at this point)* |
| v4.8 | Phase 3a/3b/3c complete. BQ staging file (bq_staging.jsonl) added — draft agent writes one JSON line per draft; flush_bq_staging() in orchestrator reads + inserts to BigQuery draft_log + clears file each cycle. UUID injection approach abandoned (Gmail strips HTML from plain-text drafts) — replaced with thread_id as primary reconciliation key. alter_draft_log.py run to add thread_id, message_id, status columns to draft_log. catalyst_reconciler.py v1.0 built: fetches Gmail Sent (last 60 min), joins against PENDING drafts via thread_id, computes Levenshtein accuracy score, writes to accuracy_log, updates draft_log → RECONCILED, ages 14d+ records → ABANDONED. Reconciler integrated as Run 5 in hourly pipeline (not a separate scheduled task). ensure_accuracy_log_schema() auto-migrates accuracy_log at runtime. *(orchestrator .py independently at v4.6)* |
| v4.9 | Phase 3d complete. catalyst_accuracy_dashboard.py v1.0 built: 4 BigQuery queries (pipeline health, accuracy by category via JOIN draft_log, last 7 days, graduation candidates). Fixed: email_category lives in draft_log not accuracy_log — all category queries JOIN on draft_id. Writes accuracy_report_YYYYMMDD.txt + accuracy_report_latest.txt. Integrated as Run 6 in orchestrator (Mondays only, WAT). is_monday() helper added (checks WAT = UTC+1). roadmap.md 3d + 4d language corrected (no separate Task Scheduler task). *(orchestrator .py independently at v4.7)* |

---

## In Progress / Upcoming

- **Full cycle validation:** Run triage → cleanup → draft end-to-end under the v4.4
  architecture to confirm all three stages complete cleanly in sequence
- **Triage: Simple reply detection:** LLM check during triage to detect if a new email
  on an existing thread is just an acknowledgment ("thanks", "got it") — if so, leave
  unread with existing labels, skip re-classification
- **Fillout warranty workflow:** Extract customer email from Fillout form payload,
  create draft addressed directly to the customer (bypasses one-way notification sender)
- **Docker MCP full integration:** Shopify tokens are in Docker vault; connecting them
  as Docker-managed MCPs (rather than env-var injection) is the next security milestone
- **Amazon agent ecosystem:** Phase 3 scope — listing agent, PPC agent, review monitor

---

## Key Engineering Principles Applied

**Fix the data problem, not the time problem**
Adding `-label:AI_PROCESSED` to one search query eliminated 200+ wasted API calls per
cycle. Raising the timeout to 25 minutes would have hidden the same inefficiency.

**Re-authentication is not always the fix for auth failures**
The GDrive `invalid_request` error looked like a token problem. It was an OAuth2
constructor problem. Running auth again would have produced the same failure 60 minutes
later. Diagnosing why the refresh wasn't happening prevented an infinite loop of
manual re-auths.

**Passive detection creates recurring noise; active correction solves once**
Pre-flight checks that flag and skip produce the same report every cycle and train
users to ignore warnings. Pre-flight checks that correct underlying state permanently
remove items from the error queue.

**Split by MCP dependency, not by feature**
The three-run split was not arbitrary. Triage is Gmail-only (fast). Draft requires
Gmail + Shopify + GDrive (slow, more failure surface). Separating them means a Shopify
outage doesn't prevent triage from running.

**Replicate logic faithfully before optimising**
The Rube recipe had 9 classification rules developed across 20 versions. Phase 2 first
replicated all of that logic exactly in catalyst_triage.md before making any changes.
The optimisations (Rule 0 Fillout change, etc.) came after the replication was confirmed
working — not during it.

---

## LinkedIn Post Series
*(Series of posts with image briefs — check audit log before publishing each)*

---

### POST 1 — The Breaking Point
**Status:** [ ] Draft  [ ] Published
**Hook:** "It ran perfectly for a week. Then it started dropping mid-session — silently,
with no error, no output, nothing."

**Narrative arc:**
Open with the moment the system starts failing after a smooth first week. Describe
what "mid-session dropping" looks like from the outside — the automation fires, the
log shows it started, and then nothing. The session died somewhere in the middle of
processing and left no trace. Explain the root cause: one Python script was carrying
the entire weight of the pipeline — email retrieval, classifying dozens of messages
through 9 priority rules, Shopify order lookups, Google Drive reads, and draft
generation — all chained in one uninterrupted session with no isolation between stages.
Under light volume it held. As the task graph grew, the session couldn't sustain it.
End with the lesson: when a system fails silently at scale, it's usually not a bug —
it's the architecture telling you it has hit its ceiling.

**Key lines to use:**
- "The log said it started. It never said it stopped."
- "One slow API call midway through was enough to bring the entire run down."
- "This wasn't a bug to patch. It was a signal."

**Tone:** Reflective, diagnostic, honest about what failure looks like in production.

**Image brief:**
A single overloaded pipeline — visualised as one thick cable or pipe with too many
things flowing through it (email icons, database symbols, document icons), cracking
or fraying at a stress point. Dark background, technical aesthetic. No text in image.

---

### POST 2 — The Architecture Decision
**Status:** [ ] Draft  [ ] Published
**Hook:** "We replaced a cloud recipe with a markdown file. Here's why that was the
right call."

**Narrative arc:**
Describe Phase 1's reliance on Rube.app — a cloud-hosted recipe (Email Triage v2
Granular) that reached v20 across months of iteration. It worked, but it was external:
it ran in the cloud, held config state outside the client's control, and was a
dependency the business couldn't audit or version. The decision to eliminate it wasn't
triggered by a failure — it was triggered by the realisation that every critical
business process was tied to a platform they didn't own. Walk through what the migration
meant: replicating 9 priority classification rules, 22 B2B domain filters, 2 exact LLM
prompts, and anti-rerun logic from the Rube Python recipe into a plain markdown file
that Claude CLI reads and executes directly. The principle: if it's critical to your
operation, it should live where you control it.

**Key lines to use:**
- "20 versions built in Rube. One markdown file to replace them all."
- "If it's critical to your operation, it shouldn't live on someone else's platform."
- "The replication had to be faithful before it could be improved."

**Tone:** Strategic, decisive. Showcases architectural thinking over technical heroics.

**Image brief:**
Split visual: left side shows a cloud platform UI with a recipe/workflow card
(labelled "external"); right side shows a clean local folder with a single markdown
file (labelled "owned"). A directional arrow between them. Minimal, professional.
No real logos.

---

### POST 3 — The Decomposition
**Status:** [ ] Draft  [ ] Published
**Hook:** "The timeout wasn't the problem. The architecture was."

**Narrative arc:**
The first fix attempt: increase the timeout from 10 to 20 minutes. Still failed with
zero output. Ran a direct MCP connectivity test to rule out initialization hang — all
MCPs connected cleanly. The real issue: the combined workflow was one giant chain.
A single slow call anywhere in the sequence — one large inbox fetch, one Shopify
lookup, one GDrive read — would stall the entire pipeline with no recoverable output.
The fix: decompose into three independent runs (Triage / Cleanup / Draft), each
scoped to specific MCPs, each with its own timeout and failure boundary. A Shopify
outage now only affects Run 3 — triage and cleanup still complete. The lesson: when
you can't fix the load, change the shape of the work.

**Key lines to use:**
- "Increasing the timeout to 20 minutes just gave it more time to fail."
- "Separate by what can fail independently, not by what logically belongs together."
- "Run 1 doesn't know Run 3 exists. That's the point."

**Tone:** Problem-solving focused. Clear cause → attempted fix → real fix structure.

**Image brief:**
One thick bar (labelled "v4.0 — Combined") breaking apart into three clean, separate
parallel bars (labelled "Triage", "Cleanup", "Draft"), each with its own colour and
a small lock/boundary icon. Technical diagram style, dark background.

---

### POST 4 — Fix the Query, Not the Timeout
**Status:** [ ] Draft  [ ] Published
**Hook:** "The triage agent was still timing out — even after the split. One line fixed it."

**Narrative arc:**
After the workflow split, triage (Gmail-only, should be fast) kept hitting its
10-minute ceiling. Audited the Gmail search query. Found it: `in:inbox is:unread
after:[date]`. The workflow keeps all emails unread for human review — so every hourly
run was re-fetching all 100+ previously classified emails going back 7 days, making
200+ API calls just to skip them, before doing any real work. Added `-label:AI_PROCESSED`
to the query. New emails only. Run time dropped from 10+ minutes (timeout) to 2 minutes.
The principle: the problem wasn't the timeout ceiling — it was the search returning data
the system was always going to discard. Fix the data problem, not the time budget.

**Key lines to use:**
- "200+ API calls. Every hour. To do nothing."
- "`-label:AI_PROCESSED` — one filter that changed everything."
- "Raising the timeout to 25 minutes would have hidden the same inefficiency."

**Tone:** Sharp and technical. The satisfaction of finding one specific cause.

**Image brief:**
A search bar or query box with the old query shown (faded/red), then the updated
query highlighted in green with the `-label:AI_PROCESSED` addition circled or
underlined. Simple, code-aesthetic background. Clean and readable.

---

### POST 5 — The OAuth2 Constructor Trap
**Status:** [ ] Draft  [ ] Published
**Hook:** "The user said: 'but we just set up the tokens yesterday.' They were right.
Re-authenticating wasn't the answer."

**Narrative arc:**
Google Drive MCP returning `invalid_request` on every call. Initial read: token expired,
needs re-auth. User pushes back — they authenticated the previous day. That pushback
was the right instinct. Investigated: access tokens expire every hour — always have.
The refresh token was present and valid. The server had everything it needed to refresh
automatically. It just couldn't. The OAuth2 client was instantiated as
`new google.auth.OAuth2()` — no client_id, no client_secret. Without those, the client
has no mechanism to exchange the refresh token for a new access token. It fails silently
every hour. Re-authenticating would have produced the same failure 60 minutes later.
Fix: load client_id and client_secret from the existing keys file, pass them into the
constructor, add a token refresh listener that persists new tokens to disk. Never
needs manual intervention again.

**Key lines to use:**
- "Re-auth would have worked for exactly 60 minutes."
- "The constructor had no credentials. So it had no way to refresh."
- "Listen to the user when they say 'but we just did that.'"

**Tone:** Diagnostic story. Good human moment (user pushback led to the right fix).
Accessible to non-technical readers — the drama is in the detective work.

**Image brief:**
A locked door (representing the GDrive connection) with a key that has a missing
tooth/notch (the incomplete OAuth2 client). Next to it, the correct key with all
teeth filled in. Dark, clean aesthetic. Symbolic rather than literal.

---

### POST 6 — Make It Fix Itself
**Status:** [ ] Draft  [ ] Published
**Hook:** "The pre-flight check was flagging the same 17 emails every single cycle.
I made it fix them instead."

**Narrative arc:**
17 Fillout warranty form notification emails were stuck in the draft queue permanently.
Every run: pre-flight fires, flags them as MISLABELED (one-way automated sender),
skips them, moves on. Next run: they're back. The check was doing its job — but only
half of it. It detected the problem and reported it. It never corrected it. Two changes:
triage Rule 0 updated so Fillout notifications route to B2B_FILTERED from the start.
Draft pre-flight upgraded from passive to active — when MISLABELED fires, it now
corrects the labels (adds B2B_FILTERED, removes the classification label) and
permanently removes the email from future queue runs. One cycle. 17 emails cleared.
Never seen again. The principle: a check that only flags creates recurring noise.
A check that fixes creates closure.

**Key lines to use:**
- "It was doing its job. Just not the whole job."
- "Flag and skip. Flag and skip. Every hour."
- "Detection without correction is just a noisy alarm."

**Tone:** Satisfying resolution. Clear before/after. Good for showcasing
systems thinking over quick fixes.

**Image brief:**
Two panels side by side. Left: a warning flag icon with a loop arrow (recurring
alert). Right: a wrench/fix icon with a checkmark and a "cleared" stamp. Clean,
icon-based design. Professional colour palette.

---

### POST 7 — Zero Plaintext Tokens
**Status:** [ ] Draft  [ ] Published
**Hook:** "An AI with live Shopify access and visible API tokens is an architectural
risk. Here's how we closed it."

**Narrative arc:**
The client's technical advisor flagged it: an AI system connected to a live Shopify
store, with API tokens sitting in plaintext config files, is a liability. Not because
the AI is malicious — but because the blast radius of an error (or a prompt injection,
or a misconfigured MCP) is the entire store. The fix required three layers:
(1) secrets.env as the single source of truth for tokens, never committed to config;
(2) mcp.json using `${VAR}` placeholders resolved only at runtime via Python env
injection; (3) Docker MCP Toolkit storing tokens in an encrypted vault, with each MCP
running in its own container — contamination of one cannot reach others. A setup.py
utility ties it together: validate tokens, sync to Docker vault, verify config — one
command. The principle: control the access layer, and the blast radius shrinks to
the boundary you define.

**Key lines to use:**
- "The AI didn't need to see the token. It just needed access to work."
- "Each MCP in its own container. Contamination of one can't reach the others."
- "One command: validate, sync, verify. Token rotation is no longer a manual process."

**Tone:** Security-minded, professional. Appeals to technical decision-makers and
clients evaluating AI system risk.

**Image brief:**
A vault or safe with multiple separate compartments (each labelled with an MCP name —
Gmail, Shopify, GDrive), each locked independently. One compartment is highlighted
as "open" while the others remain closed — showing isolation. Clean, professional,
dark secure aesthetic.

---

### POST 8 — Phase 2 Is the Real Engineering
**Status:** [ ] Draft  [ ] Published
**Hook:** "Phase 1 ships something that works. Phase 2 is understanding why it breaks."

**Narrative arc:**
Zoom out. Phase 1 delivered: a working triage system, live in production, 16
classification labels, running hourly. By most measures, done. Phase 2 started because
"done" and "reliable" are different things. A week into production, mid-session drops.
Tokens visible in config files. A cloud dependency the business doesn't control.
A cleanup job that reads 22 emails to find 0. An OAuth2 client that can't refresh its
own token. None of these were visible during build — they only appeared under real
operating conditions, real volume, real time passing. Phase 2 is the work that
transforms a working prototype into a system the business can depend on. It's less
glamorous than Phase 1 — there's no launch moment, no first run. It's auditing queries,
reading Node.js constructors, splitting workflows, rotating tokens. But it's where the
actual reliability lives. Anyone can build something that works once. Phase 2 is
building something that works at 3am on a Tuesday, without anyone watching.

**Key lines to use:**
- "Phase 1 is the launch. Phase 2 is the maintenance of trust."
- "None of these failures were visible during build. They only appear under time."
- "Anyone can build something that works once."

**Tone:** Reflective, authoritative. Speaks directly to clients and hiring managers
who understand the difference between a demo and a production system.

**Image brief:**
An iceberg. Above the waterline: "Phase 1 — shipped, working, live." Below the
waterline (much larger): "Phase 2 — query optimisation, auth fixes, architecture
decomposition, token security, encoding stability." Clean, minimal illustration style.

---

### POST 9 — The 42-Email Problem
**Status:** [ ] Draft  [ ] Published
**Hook:** "The draft was timing out every run. There were 42 emails in the queue.
Most of them were already resolved."

**Narrative arc:**
The cleanup step was working — it removed REVIEW_DRAFT from attended-to threads.
But the draft step had no filter for read state or age. So every email the cleanup
had just cleared came right back into the draft queue on the next run. 42 emails
eligible, most of them weeks old and already handled by the team through other
channels. Two filters fixed it: `is:unread` (attended-to emails are read, so they
drop out) and `after:[7-day cutoff]` (old backlog can't re-enter). Eligible emails:
42 → 6. Run time: timeout → 11 minutes. The lesson: each stage of a pipeline needs
to know what the previous stage did — not by reading its output, but by using the
right system state as the filter.

**Key lines to use:**
- "The cleanup was doing its job. The draft just wasn't listening."
- "42 eligible emails. Most of them already handled. The system didn't know."
- "Two filters. One line each. Problem gone."

**Tone:** Concrete and satisfying. Good demonstration of systems-level thinking.

**Image brief:**
A funnel with "42 emails" entering the top, and "6 emails" exiting the bottom,
with two filter labels visible on the funnel walls (is:unread / after:7 days).
Clean, minimal, technical aesthetic.

---

### POST 10 — The Draft That Reads the Room
**Status:** [ ] Draft  [ ] Published
**Hook:** "The draft agent was writing responses without reading what had already
been said. That changes now."

**Narrative arc:**
A customer emails back about their replacement order. The original issue: cracked
case, warranty claim filed two weeks ago. cs@ had already confirmed a replacement
was shipping. The draft, working from the most recent email only, starts offering
a replacement again. That is the kind of response that makes customers feel like
they're talking to a machine. The fix: before generating any draft, the system now
reads the last 5 messages in the thread. It extracts what was offered, what was
declined, what was promised, and what the overall tone has been. If cs@ already
committed to something, the draft acknowledges that commitment — it doesn't offer
something different. If the customer turned something down, the draft doesn't
repeat it. The response reflects the full conversation, not just the trigger email.

**Key lines to use:**
- "The draft was writing responses without knowing what had already been said."
- "Context isn't just about the last message. It's about the whole conversation."
- "No more re-offering a replacement to someone who's already expecting it."

**Tone:** Human-centred, practical. Bridges technical implementation and customer
experience impact.

**Image brief:**
A chat thread with 5 messages visible, the last message highlighted as the trigger,
with a draft appearing alongside — showing it references an earlier message in the
thread (a small arrow or connection line between draft and prior message). Clean,
messaging-app aesthetic.

---

### POST 11 — Stop Calling the API. You Already Have the Answer.
**Status:** [ ] Draft  [ ] Published
**Hook:** "Every hour, the system was making API calls to fetch data it already had
from an hour ago."

**Narrative arc:**
Three separate places in the pipeline were making API calls they didn't need to.
The Gmail label map (label name → ID) was being fetched fresh on every triage run —
it changes maybe once a week. The Google Drive knowledge base files were being read
from GDrive every time a draft was generated, even when the same file had been
fetched an hour earlier. The triage was calling `modify_email` once per email
instead of grouping identical operations into a single batch call. All three fixed
with caching and batching: label map cached locally for 24 hours, KB files cached
locally for 24 hours, labels applied in batch by tag group. The principle: before
making a network call, ask whether the answer could already be sitting on disk.

**Key lines to use:**
- "Fetching the same data every hour is not diligence. It's waste."
- "Cache hit: 0 API calls. Same result. Every time."
- "17 emails, same label, 1 call — not 17."

**Tone:** Efficiency-focused, slightly dry. Appeals to engineers and technical operators.

**Image brief:**
A disk/cache icon on the left, labelled "local" with a green checkmark and "0 calls".
A cloud icon on the right, labelled "API" with a grey status and "skipped". Arrow
going from a query box to the disk, bypassing the cloud. Minimal, icon-based.

---

### POST 12 — The Ghost Processes

**Status:** [ ] Draft  [ ] Published
**Hook:** "Every time a run timed out, it left processes running in the background.
They were accumulating."

**Narrative arc:**
When Claude CLI times out, the Python script kills the main process. But Claude CLI
spawns child processes — one Node.js MCP server per connected service. `subprocess.run(timeout=)`
kills the parent. The children keep running. By the time this was caught, multiple
timed-out runs had left a collection of orphaned `node.exe` processes sitting in
memory, consuming resources and potentially interfering with subsequent runs. The fix:
switch from `subprocess.run()` to `Popen` with `communicate(timeout)`, and on timeout,
run `taskkill /F /T /PID` — the `/T` flag propagates the kill to the entire process
tree. Parent and all children, gone cleanly. The lesson: when you start a process that
starts other processes, your cleanup has to account for all of them.

**Key lines to use:**
- "Kill the parent. The children keep running. Nobody told you."
- "/T — terminate the tree. Every process, every child."
- "Cleanup is only complete when everything that was started is stopped."

**Tone:** Technical and precise. Satisfying for engineers who've hit this exact problem.

**Image brief:**
A process tree diagram — one root node with several child nodes branching below it.
A "killed" marker on the root node only, with the child nodes still glowing/active.
Then the same tree, all nodes marked "killed" with the /T flag labelled. Dark,
technical aesthetic.

---

### POST 13 — The Reference Document That Wasn't
**Status:** [ ] Draft  [ ] Published
**Hook:** "The master reference document and the running system had quietly diverged.
In five different places."

**Narrative arc:**
Before building the next phase, a full audit was run comparing `catalyst_workflow.md`
(the master reference) against the three prompt files that actually execute in production.
Five divergences found: a Fillout routing rule that had regressed, a classification
label being removed after drafting (erasing audit history), an `is:unread` filter
that had already been fixed in the running file but not in the reference, three
entire email categories mapped to the wrong knowledge base file, and a GDrive search
instruction with no folder specified. None of these were breaking anything yet —
but the moment you build the next layer on top of an inaccurate reference, the
errors compound. The lesson: audit before you build. A reference document that
doesn't match production is not a reference. It's a trap.

**Key lines to use:**
- "The document said one thing. The system did another. Both had been running fine."
- "None of these were breaking anything yet. That's what makes them dangerous."
- "Audit before you build. The next layer magnifies whatever's wrong underneath."

**Tone:** Precise, methodical. The value of systematic review over assumption.

**Image brief:**
Two columns side by side — "Reference" and "Running System" — with five rows,
each showing a mismatch highlighted in amber/red. Clean table-style layout,
professional colour palette. No code, just the contrast.

---

### POST 14 — When the Exemption Has to Come First
**Status:** [ ] Draft  [ ] Published
**Hook:** "We fixed the rule. The fix never fired. Here's why."

**Narrative arc:**
Fillout warranty form submissions needed to be classified as WARRANTY in triage
(to preserve the audit trail) but skipped in draft (you can't reply to a one-way
platform notification). The triage fix was straightforward. The draft fix looked
straightforward too — until we traced the full execution path and found that the
draft pre-flight had a broad `notifications@` catch-all that fired first, stripped
the WARRANTY label, and replaced it with B2B_FILTERED. The exemption existed in
concept. It just wasn't placed before the rule it was supposed to override. Moving
the Fillout exemption to CHECK 2 — before the `notifications@` check at CHECK 3 —
fixed it. The principle: order of evaluation matters as much as the logic itself.
A correct rule in the wrong position is a rule that doesn't exist.

**Key lines to use:**
- "The fix was correct. The position was wrong."
- "An exemption placed after the rule it exempts will never fire."
- "Execution order is as much a design decision as the logic itself."

**Tone:** Precise, instructive. Good for engineers who have hit evaluation-order bugs.

**Image brief:**
A flowchart with two paths: one showing the exemption evaluated AFTER the broad
catch-all (exemption never reached, labelled "wrong"), one showing the exemption
evaluated BEFORE (exemption fires first, labelled "correct"). Clean diagram style,
minimal colour.

---

## Session: March 19, 2026 — Discrepancy Audit, KB Mapping Corrections & Phase 3 Roadmap

---

### IMPROVEMENT 18 — Prompt File Audit: Five Discrepancies Resolved (v4.4 → v4.5)

**The problem:**
A systematic audit of the three running prompt files (`catalyst_triage.md`,
`catalyst_cleanup.md`, `catalyst_draft.md`) against the master reference
(`catalyst_workflow.md`) revealed five divergences — places where the running
files and the reference document had drifted from each other, or where both shared
the same incorrect logic.

**The five discrepancies and their fixes:**

**1. Fillout Rule 0 — triage.md had regressed to B2B_FILTERED**
The Rube recipe (Phase 1) correctly routed `notifications@fillout.com` to WARRANTY
by parsing the body for Ms/# order prefixes. During Phase 2 migration, this was
changed to B2B_FILTERED with a comment "handled manually outside automation."
`catalyst_triage.md` was restored to the original warranty routing logic:
parse body → Ms prefix → `CATALYST_US_WARRANTY`, # prefix → `CATALYST_LIFESTYLE_WARRANTY`.

**2. Classification label removal in workflow.md**
`catalyst_workflow.md` Step 2.7 said "Remove the original classification label after
drafting." `catalyst_draft.md` (the file that actually runs) correctly keeps labels
permanently. `catalyst_workflow.md` was corrected to match: labels are never removed —
they stay as permanent audit history.

**3. is:unread in workflow.md triage query**
`catalyst_workflow.md` Step 0.1 still had `is:unread` in the fetch query.
`catalyst_triage.md` (v4.3 fix, Improvement 9) had already removed this.
`catalyst_workflow.md` was corrected to match: query uses `-label:AI_PROCESSED`,
not `is:unread`. Explanatory note added.

**4. OOS / ADDRESS / GENERAL all mapped to "Warranty Claim" KB**
In both `catalyst_draft.md` and `catalyst_workflow.md`, three categories were
incorrectly mapped to the Warranty Claim knowledge base file:
- `CATALYST_US_OOS` / `CATALYST_LIFESTYLE_OOS` → now "Out-of-Stock Order Notification Guide"
- `CATALYST_US_ADDRESS` / `CATALYST_LIFESTYLE_ADDRESS` → Primary: "Order Modification",
  Reference: "Address Verification & Order Holds Guide"
- `CATALYST_US_GENERAL` / `CATALYST_LIFESTYLE_GENERAL` → keyword/device search fallback
  (same path as `GENERAL_*` labels)

**5. GDrive KB folder not specified**
The GDrive search instruction in both `catalyst_draft.md` and `catalyst_workflow.md`
said "search for the KB file by name" without specifying which folder. The authoritative
KB folder (`Customer_Support_Claude_Skills`) is now explicitly named in both files.

**The principle applied:** A master reference document that diverges from the running
files is not a reference — it's a liability. Audit before building the next layer.

**Result:** All five discrepancies resolved. `catalyst_workflow.md` is now an accurate
reflection of the running system.

---

### IMPROVEMENT 19 — Fillout Pre-Flight Exemption: WARRANTY Label Preserved (v4.5)

**The problem (identified during discrepancy audit):**
After restoring Fillout warranty routing in triage (Improvement 18), a downstream
conflict was identified: the draft pre-flight CHECK 2 catches `notifications@` as a
MISLABELED sender — adding `B2B_FILTERED` and removing the classification label.
This would strip the `CATALYST_US_WARRANTY` label that triage had correctly applied,
defeating the purpose of the routing change.

**The fix:**
A new exemption added to the draft pre-flight before the `notifications@` catch-all,
in both `catalyst_draft.md` and `catalyst_workflow.md` (renumbered CHECKs 2, 3, 4):

```
CHECK 2 — Fillout Warranty Exemption:
IF sender = notifications@fillout.com → skip drafting.
Do NOT modify any labels. Keep WARRANTY + AI_PROCESSED as-is.
Record as "Fillout warranty — skipped, pending human review".
```

`notifications@fillout.com` now exits the pre-flight early — no label changes,
no MISLABELED flag. The WARRANTY label is preserved for tracking and audit.
Drafting is still skipped (cannot reply to a one-way platform notification).

**The principle applied:** Exemptions must be evaluated before the general rule,
not after. An exemption placed after a broad pattern match will never fire.

**Result:** Fillout warranty submissions accumulate `CATALYST_US_WARRANTY` +
`AI_PROCESSED` labels permanently. Visible in Gmail for human follow-up.
Not re-flagged as MISLABELED on subsequent runs.

---

### IMPROVEMENT 20 — Python Pre-Filter: Fillout Pass-Through (v4.5)

**The problem:**
The Python pre-filter in `catalyst_cs_automation.py` runs before Claude and had
its own hardcoded Fillout rule: `if FILLOUT_SENDER in s: return "B2B_FILTERED"`.
This meant Fillout emails were tagged B2B and batched before Claude ever saw them —
the triage prompt's corrected Rule 0 would never fire, regardless of what was written
in the prompt file.

**The fix — two changes to `catalyst_cs_automation.py`:**

1. `prefilter_email()` Rule 0 changed from returning `"B2B_FILTERED"` to `None`
   (pass to Claude's LLM classification path).

2. The pre-filter injection instruction was updated to add an explicit exception:
   ```
   "EXCEPTION: For emails from notifications@fillout.com, apply Rule 0
   (warranty form routing) regardless."
   ```
   Without this, the injection instruction "Apply Rules 0.2–4 ONLY to these emails
   (Rules 0–1.5 already passed)" would have told Claude to skip Rule 0 entirely —
   the exemption overrides that for Fillout specifically.

**Note on snippet limitation:** The pre-filter passes 300 characters of body snippet
to Claude. If the order number (Ms/# prefix) appears beyond character 300, Rule 0
defaults to `CATALYST_US_WARRANTY`. This is the correct safe default.

**Result:** Fillout warranty emails now flow through Claude's Rule 0 routing.
Classification: `CATALYST_US_WARRANTY` or `CATALYST_LIFESTYLE_WARRANTY` based on
body parsing. Pre-filter no longer hard-codes the outcome before Claude is consulted.

---

### IMPROVEMENT 21 — Full Cycle Test Passed: v4.5 Validated in Production (March 19, 2026)

**Test methodology:** Three isolated runs using `--force` + individual section flags,
in sequence, on live production data. Results:

**Triage (`--force --triage-only`)**
```
Emails fetched: 6 (3 pre-filtered by Python, 3 passed to Claude LLM)
B2B_FILTERED: 5 (3 Python pre-filter + 2 LLM classified)
Customer emails: 1 — CATALYST_US_RETURN | kament.phillips@gmail.com
Label cache: HIT (no API call)
Batch label calls: 2 (for 6 emails — not 6 individual calls)
Errors: 0
Status: COMPLETED — ~4 minutes
```

**Cleanup (`--force --cleanup-only`)**
```
Condition A (cs@ replied): 0 removed
Condition B (marked read): 0 removed
Still pending (unread): 7 threads listed
Errors: 0
Status: COMPLETED — ~1 minute
```

**Draft (`--force --draft-only`)**
```
Eligible emails: 1 (Kristen Phillips — CATALYST_US_RETURN)
Drafts created: 1
Non-fatal error: TLS disconnect on modify_email — recovered via batch_modify_emails,
                 label applied successfully. No data loss.
Errors: 0 fatal
Status: COMPLETED — ~10 minutes
```

Draft correctly identified that replacement order Ms150452 was in progress and
flagged it for cancellation before the response is sent. Thread context (Step 3a)
was applied — draft reflected the full conversation history, not just the
trigger email.

**Result:** All three stages COMPLETED. No fatal errors. System performing correctly
under v4.5 changes.

---

### IMPROVEMENT 22 — Pre-Phase 3 Consistency Audit + WISMO Label Infrastructure (v4.6)

**The problem:**
Before Phase 3 build work begins, a consistency audit was run across all prompt files,
the master reference document, and the roadmap. Four issues were found:

1. **`catalyst_workflow.md` role unclear** — It was not documented whether the file was
   still being run or was a reference only. Confirmed via `catalyst-cs-automation-phase2.md`
   (Improvement 18): it is the master reference document, kept in sync with the 3 running
   files, NOT run by Task Scheduler. Status is now explicit.

2. **Shopify CLI description inaccurate in roadmap Phase 1a** — The roadmap described
   Shopify CLI as enabling "direct SQL-like queries against Shopify AdminAPI from Python
   scripts." This was misleading. Shopify CLI is a development tool that supports GraphQL
   and bulk operations via terminal commands and ShopifyQL for analytics — it does not
   integrate with Python scripts. Phase 2 Python scripts will call the Shopify Admin API
   directly via HTTP (REST/GraphQL + access token). Phase 1a installs CLI to validate
   authentication before Python scripts are built.

3. **Phase 3a UUID hidden formatting not specified** — The roadmap said `[ref:{{uuid}}]`
   with "non-visible formatting" but did not define how to hide it. In a plain-text or
   HTML Gmail draft, this is visible to customers unless explicitly hidden. The exact
   implementation is now locked in the roadmap.

4. **WISMO labels planned but not yet in prompt files** — `CATALYST_US_WISMO` and
   `CATALYST_LIFESTYLE_WISMO` were approved in Phase 3 planning but never added to
   the running prompt files. WISMO emails were falling through to `CATALYST_US_SHIPPING`
   with no distinction.

**The fix — four changes:**

**1. Roadmap Phase 1a — corrected Shopify CLI description:**
Updated to accurately describe CLI capabilities (GraphQL/bulk ops via terminal,
ShopifyQL for analytics) and clarify that Python scripts use Shopify Admin API
directly, not CLI. Phase 1a purpose reframed: CLI install validates API authentication
before Python scripts are built.

**2. Roadmap Phase 3a — UUID HTML implementation locked:**
Replaced "non-visible formatting" with the exact HTML tag to use:
```html
<span style="display:none !important; visibility:hidden; mso-hide:all; font-size:1px; line-height:1px; max-height:0px; max-width:0px; opacity:0; overflow:hidden;">[ref:{{uuid}}]</span>
```
Hidden from Gmail, webmail clients, and Outlook (`mso-hide:all`). Reconciler
searches `in:sent [ref:` to locate tagged emails without customer visibility.

**3 + 4. WISMO labels added to all prompt files:**

*`catalyst_triage.md` (v4.6):*
- Added **RULE 3.5 — WISMO** (keyword-based, fires before LLM fallback):
  Detects phrases like "where is my order", "haven't received", "track my order",
  "has it shipped" + order number pattern (Ms/# prefix). Routes to
  `CATALYST_US_WISMO` or `CATALYST_LIFESTYLE_WISMO`.
- Updated **PROMPT A** (VanChat): WISMO added to US/International tag lists.
  Added WISMO vs SHIPPING distinction rule.
- Updated **PROMPT B** (Main LLM): WISMO added for both stores with description.
  SHIPPING updated to "general shipping question (no specific tracking intent, or
  no order number)". WISMO vs SHIPPING distinction rule added.

*`catalyst_workflow.md` (master reference, kept in sync):*
- Label list (Step 0.2): WISMO labels added.
- RULE 3.5 added (identical to triage.md).
- PROMPT A + B updated (identical to triage.md).
- Draft eligible labels (Step 2.1): WISMO labels added.
- KB map (Step 2.4): WISMO → "Order Shipping & Delivery" with Phase 2 note.

*`catalyst_draft.md` (v4.6):*
- Search A eligible labels: WISMO labels added.
- KB map (Step 4): WISMO → "Order Shipping & Delivery" (Phase 2 will replace
  with Python tracking script).

**WISMO vs SHIPPING boundary (consistent across all prompts):**
- WISMO = customer asking for their specific tracking link or order location, AND
  has an order number
- SHIPPING = general delivery timeframe question, OR no order number present

**The principle applied:** Infrastructure must be consistent before building on top
of it. Adding labels to the roadmap without adding them to the prompt files means
they will never fire — the label list in the prompt is the contract, not the doc.

**Result:** WISMO emails will now be correctly separated from SHIPPING at triage.
Draft falls back to "Order Shipping & Delivery" KB until Phase 2 Python script
replaces the KB lookup with a direct Shopify tracking fetch. Roadmap is accurate
and unambiguous before Phase 1 build begins.

---

## Phase 3 Roadmap — Approved (March 19, 2026)

*Full roadmap documented in:*
`C:\Users\pc\Documents\Catalyst-Projects\catalyst-cs-automation-roadmap.md`

**Approved phases and sequence:**

| Phase | What it builds | Status |
|-------|---------------|--------|
| 1 — Infrastructure | Shopify CLI + GCP BigQuery setup | ✅ Complete |
| 2 — WISMO + hardened flows | `CATALYST_US_WISMO` / `CATALYST_LIFESTYLE_WISMO` labels + Python Temperature 0 tracking script | ✅ Complete |
| 3 — Thread-Tracer | thread_id/message_id matching → Reconciler → BigQuery accuracy log + weekly dashboard | ✅ Complete |
| 4 — Graduation logic | 95% accuracy over 100+ emails → auto-send toggle per category | Waiting on data |
| 5 — Amazon connector | SP-API webhook → draft → human approval queue → SP-API send | Blocked — SP-API credentials needed |

**Key architectural decisions locked:**
- WISMO: new dedicated labels (`CATALYST_US_WISMO` / `CATALYST_LIFESTYLE_WISMO`),
  not a sub-flow of SHIPPING
- BigQuery staging: draft agent writes to bq_staging.jsonl; Python flush_bq_staging() inserts
  to BigQuery after each cycle — BigQuery MCP is read-only (confirmed)
- UUID injection abandoned: Gmail strips HTML from plain-text drafts. thread_id is the
  reconciliation key (stable across draft → send lifecycle)
- Reconciler runs as Run 5 in the hourly pipeline — no separate scheduled task
- Accuracy Dashboard runs as Run 6 on Mondays (WAT) — no separate scheduled task
- All auto-reply graduation logic built generically — any category can graduate,
  WISMO is only the first pilot
- Amazon: human-in-the-loop required permanently (TOS compliance — auto-send not permitted)

---

## In Progress / Upcoming (Updated March 20, 2026)

**Completed this session (v4.6):**
- ✅ Full system audit — 5 discrepancies identified and resolved (v4.5)
- ✅ Fillout warranty routing restored end-to-end (triage → draft exemption → pre-filter)
- ✅ KB file mappings corrected for OOS, ADDRESS, GENERAL categories
- ✅ GDrive KB folder (`Customer_Support_Claude_Skills`) specified in all lookup instructions
- ✅ v4.5 full cycle test passed on production data
- ✅ Phase 3 roadmap documented and approved
- ✅ Pre-Phase 3 consistency audit completed (v4.6)
- ✅ WISMO labels added to all prompt files (triage RULE 3.5 + LLM prompts, draft eligible labels + KB routing, workflow.md master reference)
- ✅ Roadmap Phase 1a Shopify CLI description corrected
- ✅ Roadmap Phase 3a UUID hidden HTML implementation locked (`display:none` + `mso-hide:all`)

**Next session — Phase 1:**
- [ ] **1a:** Install Shopify CLI on WSL, authenticate both stores, run test order query
- [ ] **1b:** Create GCP project + BigQuery dataset + accuracy tables, identify and
       configure BigQuery MCP, insert test row and query back

**Remaining upcoming items:**
- [ ] Triage: simple reply detection — LLM check for "thanks/got it" acknowledgments
      → leave unread with existing labels, skip re-classification
- [ ] Fillout warranty workflow: extract customer email from form payload, draft directly
      to customer (bypasses one-way notification sender) — scoped for future cycle
- [ ] Docker MCP full integration: Shopify tokens as Docker-managed MCPs
      (vs. current env-var injection)
- [ ] Amazon connector (Phase 5) — blocked on SP-API credentials

---

## Session: March 20–25, 2026 — Draft Style Rules, Pre-Filter Stability, BigQuery Phase 1b & KB Governance Restructure

---

### IMPROVEMENT 23 — Draft Style Enforcement: Em Dash Ban + AI Language Block (v4.6)

**The problem:**
Drafted emails were coming back from the agent with em dashes and phrases that read as
unmistakably AI-generated — "Certainly", "rest assured", "please don't hesitate",
"I understand your frustration". Each one erodes brand voice and signals to the customer
that nobody actually wrote this. No constraint existed in the prompt to prevent it.

**The fix:**
Added a non-negotiable Writing Style Rules block to Step 6 of `catalyst_draft.md`:
- Em dashes banned entirely — rewrite as comma, period, or restructured sentence.
- Full 5-category banned phrase list:
  1. Chatbot pleasantries ("Certainly", "Absolutely", "Of course", etc.)
  2. AI power words (Delve, Unlock, Harness, Elevate, etc.)
  3. Navigational filler ("In conclusion,", "Furthermore,", "Moreover,", etc.)
  4. Adjective overload (Comprehensive, Robust, Crucial, Paramount, etc.)
  5. Helpful assistant vibe ("Dive in", "Look no further", "Think of it as", etc.)
- "Catalyst" added to the banned list — never used in email body copy.
- Closing rule: "Write like a real person — natural, direct, human."

**The principle applied:** Negative constraints are more reliable than positive
instructions. Telling an LLM to "write naturally" is vague. Telling it the exact
words it cannot use is enforceable.

**Result:** Draft output no longer contains any of the listed phrases. Banned list
operates as a production filter — every draft checked against it before submission.

---

### IMPROVEMENT 24 — Pre-Filter Stability: Timeout Ceiling + Carl Ball False Positive (v4.6)

**Two problems found in the same session:**

**Problem A — Timeout ceiling hit consistently:**
The Python pre-filter subprocess was running into its 120-second timeout ceiling on
larger batches. The process wasn't hanging — it was completing valid work but getting
killed mid-batch because the ceiling was set too low for the actual load. The 120s
limit was set conservatively during initial implementation and was never revised after
batch sizes grew.

**Problem B — Carl Ball warranty thread misclassified as B2B_FILTERED:**
Carl Ball had an active warranty claim thread. A follow-up email in the thread contained
the word "invoice" in a quoted reply (lines prefixed with `>`). Rule 3 of the Python
pre-filter scans for B2B-indicator keywords including "invoice" — it matched the quoted
content and flagged the email as B2B_FILTERED, removing it from the draft queue.
The customer's live thread was being silently dropped.

**Diagnosis:**
Rule 3 was applying keyword scanning to the full raw email body, including all quoted
reply history. Quoted lines represent prior messages — not the current sender's intent.
The scan should only cover what the customer actually wrote in this email.

**The fix — two changes to `catalyst_cs_automation.py`:**

1. Timeout raised: `timeout=120` → `timeout=180`

2. Added `_strip_quoted_lines()` helper:
```python
def _strip_quoted_lines(text: str) -> str:
    """Remove lines starting with '>' (quoted email reply content)."""
    return "\n".join(line for line in text.splitlines() if not line.strip().startswith(">"))
```
Rule 3 now applies B2B keyword scan to unquoted content only:
```python
b_unquoted = _strip_quoted_lines(b)
content_unquoted = su + " " + b_unquoted
if any(kw in content_unquoted for kw in B2B_CONTENT_KW + PROMO_KW):
    return "B2B_FILTERED"
```

**The principle applied:** Pre-filter rules must be scoped to the signal they're
actually measuring. Rule 3 detects B2B senders by their language patterns — not
by what a Catalyst agent wrote in a prior message of the same thread.

**Result:** No more timeout ceiling hits under normal batch loads. Active warranty
threads with quoted invoice language are no longer misclassified.

---

### IMPROVEMENT 25 — Task Scheduler Auto-Trigger Fix: Full Python Path (v4.6)

**The problem:**
The automation had not been auto-firing since re-registration of the scheduled task.
Manual runs worked correctly. The Task Scheduler showed the task as enabled and the
last result as `0x0` (success) — but only on manual trigger. Hourly automatic runs
were silently not executing.

**Diagnosis:**
The XML `<Command>` entry used `python` as the executable name:
```xml
<Command>python</Command>
```
In an interactive terminal session, `python` resolves correctly because user-level
`PATH` includes the Python installation directory. Windows Task Scheduler runs tasks
in a non-interactive system session where user-level `PATH` entries are not loaded.
`python` resolves to nothing. The task starts, immediately fails to find the executable,
exits with success code — no error, no output, no log entry.

**The fix:**
Updated `CatalystCS_Task_Fixed.xml` to use the full executable path:
```xml
<Command>C:\Python314\python.exe</Command>
```
Re-registered via admin CMD: `schtasks /create /tn "CatalystCS" /xml "..."`.

**The principle applied:** Non-interactive processes cannot rely on user-level PATH
resolution. Any scheduled task, service, or CI runner must reference executables by
absolute path.

**Result:** Automatic run confirmed firing at 07:04 UTC March 25 without manual
trigger. All subsequent hourly runs executing as expected.

---

### IMPROVEMENT 26 — Phase 1b Complete: BigQuery Connectivity Confirmed (cs-mcp-gateway)

**The problem:**
`test_bigquery.py` was pointing to GCP project `my-mcp-drive-486418` (free tier).
All DML operations returned `403 billingNotEnabled`. Switching to the cs-mcp-gateway
project (billing-enabled) surfaced a second 403: the service account had no
project-level IAM roles — only dataset-level, and the target dataset didn't yet exist.

**The fix — two stages:**

1. Updated `test_bigquery.py`: `PROJECT_ID = 'cs-mcp-gateway'` (#949282056449)

2. June granted project-level IAM on cs-mcp-gateway:
   - BigQuery Data Editor
   - BigQuery Job User
   Dataset creation requires project-level roles, not just dataset-level permissions.
   Dataset-level grants can only be applied after the dataset exists.

**Confirmed working:**
```
Dataset created:  catalyst_cs_accuracy
Tables created:   draft_log, accuracy_log
INSERT (DML):     OK — both tables
SELECT:           OK — rows queried back clean
```
Service account: `catalyst-bigquery-writer@my-mcp-drive-486418.iam.gserviceaccount.com`

**The principle applied:** GCP IAM has two distinct layers — project-level and
resource-level. Resource-level grants only work once the resource exists. For
creating new datasets, project-level roles are required first.

**Result:** Phase 1b complete. BigQuery is ready to receive draft logs and accuracy
data from the live automation pipeline.

---

### IMPROVEMENT 27 — KB Governance Restructure: 3 Guides → 6 CANONICAL Skill Files (v4.7)

**The problem:**
Three knowledge base files in `Claude_KB\` were in informal guide format — no
Trigger Identification section, no locked Key Rules, no Approved Language blocks,
no Forbidden blocks, no intl counterparts, and no consistency with the CANONICAL
skill format established by the KB Governance System (06). The draft agent was routing
to these files expecting structured function lookups, but the files had no function
structure to look up.

Additionally, `catalyst_draft.md` Step 4 was mapping labels to descriptive file names
("Warranty Claim Knowledge Base", "Out-of-Stock Order Notification Guide") rather than
exact CANONICAL filenames — meaning the agent had to guess or search rather than
fetch directly.

**Files deleted:**
- `Claude_KB\Address Verification & Order Holds Guide.md`
- `Claude_KB\Out-of-Stock Order Notification Guide.md`
- `Claude_KB\Warranty Claims Guide.md`

**Files created (new CANONICAL format):**
- `Claude_KB\Skills\CANONICAL_skill_address-verification-us.md`
  5 functions: Invalid/Incomplete Address, Non-English Characters, Address Too Long,
  Fraud Risk Verification, No-Response Deadline Reminder.
  Locked facts: 7-day deadline, English-only carrier requirement, FedEx 35-char limit.

- `Claude_KB\Skills\CANONICAL_skill_address-verification-intl.md`
  International counterpart: Intl English, `######` order format, DHL/HongKong Post,
  `info@catalystlifestyle.com`.

- `Claude_KB\Skills\CANONICAL_skill_oos-notification-us.md`
  5 functions with Approved Language + Forbidden lists.
  Locked: options order (Wait → Ship Available → Alternative → Refund), refund 3–5
  business days, 7-day follow-up before default action.

- `Claude_KB\Skills\CANONICAL_skill_oos-notification-intl.md`
  International counterpart.

**Files updated to v1.1 (Temperature Zero compliance):**
- `Claude_KB\Skills\CANONICAL_skill_warranty-claim-us.md`
  All 7 functions now have Approved Language + Forbidden blocks.
  Key locks: replacement warranty = 3 months from shipment date (never 12);
  agent does not approve or deny claims.

- `Claude_KB\Skills\CANONICAL_skill_warranty-claim-intl.md`
  Same as US version in International English.

**catalyst_draft.md Step 4 updated:**
Label-to-file routing now maps to exact CANONICAL filenames (e.g.,
`CANONICAL_skill_warranty-claim-us.md`) — no ambiguity, no search required.
GDrive path updated: "Skills" folder inside "Claude_KB" on Google Drive.
Local fallback updated: `Claude_KB\Skills\[filename]`.

**The principle applied:** Temperature Zero — the factual core of every KB response
must be locked. Approved Language blocks define the highest-probability word choices
for each scenario. Forbidden blocks make policy violations unambiguous and auditable.
A KB file without these is not Temperature Zero compliant.

**Result:** 6 CANONICAL skill files covering address, OOS, and warranty (US + intl).
All have full Trigger Identification, Key Rules (Locked), Skill Functions with Approved
Language and Forbidden blocks. Draft agent routing is now exact-filename based.
Remaining skill files (order-shipping, return-processing, order-modification,
product-support, chargeback, return-tracking) pending Temperature Zero audit.

---

## In Progress / Upcoming (Updated March 28, 2026)

**Completed since last update (Sessions 3–10):**
- ✅ Phase 1a — Shopify CLI installed, both stores authenticated
- ✅ Phase 1b — BigQuery connected on cs-mcp-gateway (#949282056449), tables confirmed
- ✅ Task Scheduler auto-firing confirmed (full Python path fix)
- ✅ Draft style rules enforced (em dash ban + 5-category AI language ban)
- ✅ Pre-filter timeout raised (120s → 180s)
- ✅ Rule 3 false positive fixed (Carl Ball — quoted-line stripping before keyword scan)
- ✅ KB governance restructure — 6 CANONICAL skill files (warranty, OOS, address US+intl)
- ✅ catalyst_draft.md Step 4 routing updated to exact CANONICAL filenames
- ✅ Temperature Zero audit — ALL skill files complete (order-shipping, return-processing,
     order-modification, product-support, chargeback-disputes, return-tracking US+intl)
- ✅ Phase 2b — WISMO hardened flows (catalyst_hardened_flows.md v1.1, Run 3 in pipeline)
- ✅ Phase 2c — WISMO draft integration confirmed (REVIEW_DRAFT filter handles skip)
- ✅ Phase 2d — Stuck order escalation (unfulfilled 3+ days → ESCALATION_NEEDED, tested)
- ✅ Phase 3a/3b — BQ staging + flush live (5 rows confirmed on 2026-03-27)
- ✅ Phase 3c — Reconciler live as Run 5 (thread_id join, Levenshtein scoring, ABANDONED sweep)
- ✅ Phase 3d — Accuracy Dashboard live as Run 6 (Mondays only, WAT)

**Next (in order):**
- [ ] Phase 3.5 — Intent layer + semantic KB retrieval (June's direction — design approved March 28)
      Stage 1: intent + sentiment extraction (catalyst_draft.md Step 2.5)
      Stage 2a: KB embedding store (catalyst_kb_embedder.py + BigQuery kb_embeddings table)
      Stage 2b: semantic retriever (catalyst_semantic_retriever.py — Run 3.5 in orchestrator)
      Stage 3: prompt upgrade (catalyst_draft.md Steps 4 + 6 consume intent_context.jsonl)
      Model locked: sentence-transformers/all-MiniLM-L6-v2 (local, no API key)
- [ ] Phase 4 — Graduation to auto-reply (accelerated by Phase 3.5 accuracy improvements)
- [ ] Phase 5 — Amazon SP-API connector (blocked on credentials — boss to confirm)

**Still open:**
- [ ] Triage: simple reply detection — "thanks/got it" acknowledgment check
- [ ] Fillout warranty workflow: extract customer email from form payload, draft to customer
- [ ] Docker MCP full integration (Shopify tokens as Docker-managed MCPs)
- [ ] Amazon connector (Phase 5) — blocked on SP-API credentials

---

### POST 15 — The B2B Filter That Caught a Real Customer
**Status:** [ ] Draft  [ ] Published
**Hook:** "The automation flagged it as a vendor email. It was a customer mid-warranty claim."

**Narrative arc:**
Carl Ball had an active warranty thread. His follow-up email included the word "invoice"
in a quoted reply — a line from a previous cs@ message, prefixed with `>`. The Python
pre-filter scanned the full raw body, matched "invoice" against the B2B keyword list,
and routed the email to B2B_FILTERED. His live claim was silently dropped from the
draft queue. The fix wasn't to remove "invoice" from the keyword list — it's a valid
B2B signal in fresh content. The fix was to strip all quoted lines before scanning.
The pre-filter should only read what the customer wrote, not what was written to them.
The lesson: when you write a rule that scans email content, define exactly which
content that rule is allowed to see.

**Key lines to use:**
- "The rule was correct. The input was wrong."
- "It matched 'invoice' in a line our own agent had written."
- "Scope your rules to the signal they're measuring — not the full blob."

**Tone:** Precise, case-study format. Good for developers and ops engineers.

**Image brief:**
Email thread visualised as a stack of message bubbles. The top bubble (customer's
new message) is clean. The quoted lines below it (marked with `>`) are highlighted
in red — the false positive source. An arrow showing the filter now only scanning the
top bubble. Clean, minimal.

---

### POST 16 — Write Like a Human (Enforced at Prompt Level)
**Status:** [ ] Draft  [ ] Published
**Hook:** "The draft said 'rest assured.' We shipped a rule to make sure it never says
that again."

**Narrative arc:**
AI-drafted emails have a tell. Not hallucinations — the facts were right. The phrases.
"Certainly, I understand your frustration." "Rest assured, our team is on it." Every
CS team knows the words. Customers know them too, and they signal: nobody read this.
The fix was a non-negotiable banned-phrase list in the prompt — five categories covering
chatbot pleasantries, AI power words, navigational filler, adjective overload, and
the helpful-assistant vibe. Plus an em dash ban. Not guidelines. Not suggestions.
A list of words the agent cannot use, period. Negative constraints are more reliable
than positive tone instructions. "Write naturally" is vague. "Never write 'Certainly'"
is enforceable.

**Key lines to use:**
- "The facts were right. The phrases were the problem."
- "Customers don't read 'rest assured' as reassurance. They read it as automation."
- "Negative constraints are more reliable than positive instructions."

**Tone:** Brand voice meets engineering discipline. Accessible to non-technical readers.

**Image brief:**
A clean email draft with a handful of phrases highlighted in red and struck through
("Certainly", "rest assured", "please don't hesitate"). Below them, a plain, direct
replacement sentence in green. Minimal, no clutter.

---

### POST 17 — The Wrong Python
**Status:** [ ] Draft  [ ] Published
**Hook:** "The task ran. The script didn't. The scheduler showed success."

**Narrative arc:**
The automation had been firing correctly on manual trigger for weeks. Hourly
auto-runs were silent — no output, no error, just the scheduler reporting `0x0`
(success) and nothing happening. The script was fine. The task XML was fine. The
PATH was the problem. In an interactive terminal, `python` resolves correctly because
the user-level PATH includes the Python installation directory. Task Scheduler runs
in a non-interactive system session where that PATH entry doesn't exist. `python`
resolved to nothing. The process started, failed to find its executable, and exited
cleanly. Fix: replace `python` with `C:\Python314\python.exe` in the task XML.
First auto-run confirmed at 07:04 UTC. The lesson: any process that runs unattended
— scheduled task, service, CI runner — must reference executables by absolute path.
Interactive resolution is a personal convenience, not a system contract.

**Key lines to use:**
- "It worked every time I ran it. It never ran on its own."
- "Interactive PATH resolution is a personal convenience. Not a system contract."
- "The scheduler reported success. No script had run."

**Tone:** Debugging narrative. Clean cause-and-effect. Relatable to anyone who has
hit non-interactive environment issues.

**Image brief:**
A split diagram: left shows an interactive terminal with `python` resolving to a
path (green checkmark). Right shows a scheduled task in a locked-down environment
with `python` pointing to nothing (red X). Simple, readable.

---

### POST 18 — Temperature Zero: Locking the Factual Core
**Status:** [ ] Draft  [ ] Published
**Hook:** "We rewrote the knowledge base. Not the facts — the way the facts are expressed."

**Narrative arc:**
The KB files worked. But "working" and "reliable" are different things. A warranty
response written as free-form prose depends on which model reads it, which temperature
it runs at, and what came earlier in the context window. Two runs, same email, could
produce two different answers about the replacement warranty period. Temperature Zero
changes the architecture: every KB function has an Approved Language block — the
exact words to use for each policy point — and a Forbidden block — the exact phrasings
that are never permitted, with reasons. The factual core is locked. The style adapts.
Across 6 newly restructured CANONICAL skill files (warranty, OOS, address — US and
international), every function now has both. The principle: if a fact is non-negotiable,
treat it like a configuration value, not a generation suggestion.

**Key lines to use:**
- "Facts are immutable. Expression is flexible. The KB enforces both."
- "Two runs on the same email should produce the same policy answer."
- "We're not constraining the model. We're defining the contract."

**Tone:** Architectural philosophy. Accessible to both technical and ops audiences.

**Image brief:**
A KB function card split into two sections: "Approved Language" with locked text in
green, "Forbidden" with struck-through phrases in red. Clean card layout, no clutter.
Evokes a style guide meets a config file.

---

### POST 19 — Phase 1b Done: The Database Is Ready
**Status:** [ ] Draft  [ ] Published
**Hook:** "We hit a 403. Then another 403. Then it worked. Phase 1b is done."

**Narrative arc:**
The goal was simple: connect the automation pipeline to BigQuery so every draft and
every accuracy measurement gets logged permanently. Getting there required two separate
403 errors. First: the GCP free tier doesn't allow DML operations — billing not enabled.
Moved to a billing-enabled project. Second: the service account had no project-level
IAM roles — only dataset-level, and the target dataset didn't exist yet. You can't
assign dataset-level permissions to a dataset that hasn't been created. Project-level
roles are required first. Once both were resolved: dataset created, tables created,
INSERT confirmed, SELECT confirmed. GCP IAM has two distinct permission layers and
they are not interchangeable. The principle: when setting up infrastructure from
scratch, you always need one level above what you think you need.

**Key lines to use:**
- "You can't grant permissions on a resource that doesn't exist yet."
- "Dataset-level and project-level IAM are not interchangeable."
- "Phase 1b complete. The pipeline now has a memory."

**Tone:** Methodical, milestone-marking. Shows the real path, not the happy path.

**Image brief:**
A pipeline diagram with a new "BigQuery" node added at the end, glowing green to
indicate it's live. The path leading to it shows two red blocking points (403s)
resolved with small checkmarks. Clean, architectural.

---
