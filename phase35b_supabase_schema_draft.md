# Phase 3.5b - Supabase Implementation Plan v8.0
**Prepared by:** Theresa / Claude
**Date:** 2026-04-24
**Status:** Cascade embedding architecture confirmed by June — one dimension to lock before Stage 3b build

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| v5.0 | 2026-04-22 | Initial Supabase-first draft |
| v6.0 | 2026-04-24 | CS workflow best practices: approval log, retrieval log, feedback queue, staleness fields |
| v7.0 | 2026-04-24 | Two-table embedding design, language routing (based on incomplete understanding of June's architecture) |
| v8.0 | 2026-04-24 | Corrected: cascade embedding strategy confirmed by June. Both tables embed the same KB content. Language detection is query-time Python logic, not a KB storage attribute. `content_language` removed. `kb_chunk_embeddings_multilingual` renamed to `kb_chunk_embeddings_large`. MRL truncation dimension still TBD. |

---

## Objective

Design a **Supabase-native retrieval schema** for Catalyst CS automation that supports:

- semantic chunking and canonical-answer storage
- "50 ways to ask, 1 answer"
- hybrid retrieval (lexical + vector + RRF)
- June's cascade embedding strategy (small → large fallback)
- June's RAG enrichments and future Graph RAG
- CS workflow lifecycle: ingest → approve → retrieve → use → measure → improve

---

## Embedding architecture — cascade strategy

### Confirmed by June (2026-04-24)

Both models are OpenAI. The strategy avoids paying the 6.5× cost premium of `text-embedding-3-large` on every request.

**Step 1 — ASCII pre-check (Python, free, no API call)**
Before embedding, scan the incoming email for non-ASCII characters (Chinese, Cyrillic, Arabic, etc.).
If non-ASCII detected → skip Step 2, go directly to Step 3.

```python
def has_non_ascii(text: str) -> bool:
    return any(ord(c) > 127 for c in text)
```

**Step 2 — Small model first pass (~80% of queries)**
- Embed email with `text-embedding-3-small`
- Search `kb_chunk_embeddings` (small index)
- Check best similarity score
- If score ≥ 0.7 → return results, done

**Step 3 — Large model fallback (~20% of queries)**
Triggered by:
- Non-ASCII detected (pre-check), OR
- Small model similarity < 0.7 (low confidence)

- Embed email with `text-embedding-3-large` (MRL-truncated dimension, same as stored)
- Search `kb_chunk_embeddings_large` (large index)
- Return results

**Why this works:**
Standard typed English → small model handles it well, high similarity, cheap.
Mixed-language, OCR/scanned text, dense technical content, non-ASCII → small model struggles with ambiguity → large model resolves it.

**MRL (Matryoshka Representation Learning):**
OpenAI's `text-embedding-3-large` natively produces 3072-dim vectors. MRL allows you to request a truncated dimension (e.g. 1024) that retains most of the semantic quality at a fraction of the storage cost. Pass `dimensions=1024` (or 512) to the API — the returned vector is already the right size.

### Model and dimension table

| Table | Model | Dimensions | Cost | Status |
|-------|-------|-----------|------|--------|
| `kb_chunk_embeddings` | `text-embedding-3-small` | 1536 | $0.02/1M tokens | ✅ Confirmed |
| `kb_chunk_embeddings_large` | `text-embedding-3-large` + MRL | **TBD: 512 or 1024** | $0.13/1M tokens | ⚠️ Dimension pending June |

> ⚠️ **One open item before Stage 3b:** June to confirm MRL truncation dimension for `text-embedding-3-large` — 512 or 1024. Once confirmed, `kb_chunk_embeddings_large` and its HNSW index can be created and KB can be embedded with the large model.

**Similarity threshold:** 0.7 is the assumed default for the small → large fallback trigger. Tune after the first 100 live retrievals.

---

## What this schema needs to do

1. Ingest source KB content
2. Clean and canonicalize duplicated / overlapping entries
3. Preserve alternate phrasings for recognition
4. Semantically chunk the canonical answer
5. Embed all retrievable chunks with **both** models (small index + large index)
6. At query time: detect ASCII complexity → route to small or large → cascade if needed
7. Retrieve with structured filters plus lexical and vector search
8. Attach enrichments (guardrails, routing hints, field requirements)
9. Return the best support blocks for draft generation
10. Log what was retrieved per email (retrieval audit)
11. Record human edits back into a feedback queue for KB improvement
12. Track KB change approvals with a full audit trail

---

## Supabase design principles

1. **Canonical answer first** — one stable answer path per support intent
2. **Variants enrich retrieval** — alternate phrasings for matching, not competing records
3. **Semantic chunking after canonicalization** — clean first, chunk second
4. **Filter before retrieval** — narrow by category, store, and approval state before search
5. **Hybrid retrieval is default** — lexical + vector similarity, fused with RRF
6. **Cascade before paying for large** — ASCII check + similarity threshold gate the expensive path
7. **Embeddings are derived artifacts** — generated from chunks, refreshed when content changes
8. **Enrichment is explicit** — routing hints, guardrails, and exception logic in structured tables
9. **Every KB change requires an approval trail** — no entry goes live without a logged approval event
10. **Retrieval is auditable** — every chunk retrieved for a live email is logged with model used
11. **Human feedback closes the loop** — MAJOR_EDIT and REWRITE outcomes feed back into the KB

---

## CS workflow cycle

```
KB SOURCE (GDrive CANONICAL files)
        ↓
    kb_sources              [ingest raw content]
        ↓
kb_canonical_entries        [clean, dedupe, canonicalize — T0 answer]
        ↓
  kb_query_variants         [store alternate phrasings]
        ↓
  kb_semantic_chunks        [chunk canonical answers by type]
        ↓
  [embed ALL chunks with BOTH models]
        ↓
kb_chunk_embeddings         kb_chunk_embeddings_large
(small, 1536)               (large + MRL, TBD dims)
        ↓                           ↓
        ————————————————————————————
                    ↓
           [LIVE EMAIL ARRIVES]
                    ↓
           ASCII pre-check (Python)
          /                     \
    ASCII clean             Non-ASCII found
         ↓                       ↓
  small model query     large model query directly
         ↓
  similarity ≥ 0.7?
     /        \
   YES          NO
    ↓            ↓
  done      large model
            fallback query
                ↓
        kb_retrieval_log    [log model used, rank, score]
                ↓
    [DRAFT CREATED → BigQuery draft_log]
                ↓
     [HUMAN SENDS OR EDITS]
                ↓
    [Reconciler → accuracy_log]
                ↓
      feedback_queue        [MAJOR_EDIT + REWRITE cases]
                ↓
    [Human approves improved answer]
                ↓
      kb_approval_log       [approval logged]
                ↓
    [KB updated → re-chunk → re-embed both indexes → cycle continues]
```

---

## Extensions and helper trigger

```sql
create extension if not exists pgcrypto;
create extension if not exists vector;
```

```sql
create or replace function set_updated_at()
returns trigger language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;
```

---

## Core schema

### 1. `kb_sources`
Raw ingest boundary.

```sql
create table kb_sources (
  id             uuid primary key default gen_random_uuid(),
  source_system  text not null,
  external_id    text,
  source_uri     text,
  title          text,
  raw_text       text,
  raw_payload    jsonb not null default '{}'::jsonb,
  source_hash    text,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),

  constraint kb_sources_source_system_chk
    check (source_system in ('gdrive', 'sheet', 'csv', 'manual', 'import')),

  unique (source_system, external_id)
);

create trigger kb_sources_set_updated_at
before update on kb_sources
for each row execute function set_updated_at();
```

---

### 2. `kb_canonical_entries`
One row per canonical support answer path.

```sql
create table kb_canonical_entries (
  id                      uuid primary key default gen_random_uuid(),
  source_id               uuid references kb_sources(id) on delete set null,

  slug                    text not null unique,
  title                   text not null,

  category                text not null,
  store                   text not null,
  channel_scope           text[] not null default '{}',

  primary_intent          text not null,
  secondary_intent        text,
  sentiment_profile       text,
  escalation_risk         text,

  canonical_question      text not null,
  canonical_answer        text not null,

  intent_cluster          text,
  content_hash            text not null,

  -- CS workflow fields
  policy_source_url       text,
  requires_human_approval boolean not null default false,
  review_due_at           timestamptz,
  last_verified_at        timestamptz,
  approved_by             text,
  approved_at             timestamptz,

  status                  text not null default 'draft',
  created_at              timestamptz not null default now(),
  updated_at              timestamptz not null default now(),

  constraint kb_canonical_entries_category_chk
    check (category in (
      'WARRANTY', 'RETURN', 'OOS', 'WISMO',
      'ORDER_MOD', 'PRODUCT', 'CHARGEBACK', 'ADDRESS'
    )),

  constraint kb_canonical_entries_store_chk
    check (store in ('US', 'INTL', 'BOTH')),

  constraint kb_canonical_entries_status_chk
    check (status in ('draft', 'review', 'approved', 'retired')),

  constraint kb_canonical_entries_channel_scope_chk
    check (
      channel_scope <@ array['email','chat','amazon_us','amazon_ca','amazon_uk','social']::text[]
    )
);

create trigger kb_canonical_entries_set_updated_at
before update on kb_canonical_entries
for each row execute function set_updated_at();
```

Note: `content_language` removed in v8.0. Language detection happens on the incoming email at query time in Python — it is not a property of the KB entry. All KB entries are embedded with both models at ingest.

---

### 3. `kb_query_variants`
Alternate phrasings for lexical retrieval and recognition.

```sql
create table kb_query_variants (
  id                 uuid primary key default gen_random_uuid(),
  canonical_entry_id uuid not null references kb_canonical_entries(id) on delete cascade,

  variant_text       text not null,
  variant_type       text not null default 'customer_query',
  source_system      text,
  variant_hash       text,

  search_vector      tsvector generated always as (
    to_tsvector('english', coalesce(variant_text, ''))
  ) stored,

  created_at         timestamptz not null default now(),

  constraint kb_query_variants_type_chk
    check (variant_type in ('customer_query', 'synonym', 'internal_label', 'search_hint'))
);
```

---

### 4. `kb_semantic_chunks`
Typed semantic retrieval blocks derived from the canonical answer.

```sql
create table kb_semantic_chunks (
  id                 uuid primary key default gen_random_uuid(),
  canonical_entry_id uuid not null references kb_canonical_entries(id) on delete cascade,

  chunk_key          text not null,
  chunk_type         text not null,
  chunk_order        int not null default 0,
  chunk_text         text not null,
  token_count        int,

  is_retrievable     boolean not null default true,
  is_required        boolean not null default false,

  applicability      jsonb not null default '{}'::jsonb,
  content_hash       text not null,

  search_vector      tsvector generated always as (
    to_tsvector('english', coalesce(chunk_text, ''))
  ) stored,

  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now(),

  constraint kb_semantic_chunks_type_chk
    check (chunk_type in (
      'summary', 'policy_rule', 'eligibility_rule', 'required_evidence',
      'agent_action', 'customer_message', 'exception_rule',
      'escalation_condition', 'closure'
    )),

  unique (canonical_entry_id, chunk_key)
);

create trigger kb_semantic_chunks_set_updated_at
before update on kb_semantic_chunks
for each row execute function set_updated_at();
```

---

### 5. `kb_chunk_embeddings`
Primary embedding index. `text-embedding-3-small`, 1536 dims. First-pass retrieval.

```sql
-- ✅ Ready to create.
create table kb_chunk_embeddings (
  id                uuid primary key default gen_random_uuid(),
  semantic_chunk_id uuid not null references kb_semantic_chunks(id) on delete cascade,

  embedding_model   text not null default 'text-embedding-3-small',
  dimensions        int not null default 1536,
  embedding         vector(1536) not null,

  content_hash      text not null,
  created_at        timestamptz not null default now(),

  unique (semantic_chunk_id, content_hash)
);
```

---

### 6. `kb_chunk_embeddings_large`
Fallback embedding index. `text-embedding-3-large` with MRL truncation. Used when small model is not confident or non-ASCII is detected.

```sql
-- ⚠️ DO NOT CREATE until June confirms MRL dimension (512 or 1024).
-- Replace XXXX with confirmed dimension before running.
-- To use MRL: pass dimensions=XXXX to the OpenAI embeddings API call — no post-processing needed.
--
create table kb_chunk_embeddings_large (
  id                uuid primary key default gen_random_uuid(),
  semantic_chunk_id uuid not null references kb_semantic_chunks(id) on delete cascade,

  embedding_model   text not null default 'text-embedding-3-large',
  dimensions        int not null,          -- set to confirmed MRL dimension
  embedding         vector(XXXX) not null, -- replace XXXX before running

  content_hash      text not null,
  created_at        timestamptz not null default now(),

  unique (semantic_chunk_id, content_hash)
);
```

---

### 7. `kb_enrichments`

```sql
create table kb_enrichments (
  id                 uuid primary key default gen_random_uuid(),
  canonical_entry_id uuid not null references kb_canonical_entries(id) on delete cascade,

  enrichment_type    text not null,
  payload            jsonb not null,
  source_system      text,
  source_ref         text,
  created_at         timestamptz not null default now(),

  constraint kb_enrichments_type_chk
    check (enrichment_type in (
      'routing_hint', 'guardrail', 'rerank_signal',
      'exception_rule', 'field_requirement', 'qa_note'
    ))
);
```

---

### 8. `kb_approval_log`

```sql
create table kb_approval_log (
  id                 uuid primary key default gen_random_uuid(),
  canonical_entry_id uuid not null references kb_canonical_entries(id) on delete cascade,

  from_status        text not null,
  to_status          text not null,
  approved_by        text not null,
  notes              text,
  created_at         timestamptz not null default now(),

  constraint kb_approval_log_from_chk check (from_status in ('draft','review','approved','retired')),
  constraint kb_approval_log_to_chk   check (to_status   in ('draft','review','approved','retired'))
);
```

---

### 9. `kb_retrieval_log`
Per-interaction retrieval audit. `embedding_model` field records which cascade path was taken.

```sql
create table kb_retrieval_log (
  id                 uuid primary key default gen_random_uuid(),
  draft_log_id       text not null,
  canonical_entry_id uuid references kb_canonical_entries(id) on delete set null,
  semantic_chunk_id  uuid references kb_semantic_chunks(id) on delete set null,

  retrieval_method   text not null,
  embedding_model    text,
  rank_position      int not null,
  similarity_score   real,
  was_used_in_draft  boolean not null default true,

  created_at         timestamptz not null default now(),

  constraint kb_retrieval_log_method_chk
    check (retrieval_method in ('lexical', 'semantic', 'hybrid')),
  constraint kb_retrieval_log_rank_chk
    check (rank_position between 1 and 10)
);
```

---

### 10. `feedback_queue`

```sql
create table feedback_queue (
  id             uuid primary key default gen_random_uuid(),
  draft_log_id   text not null unique,

  kb_ids_used    uuid[] not null default '{}',
  claude_draft   text not null,
  final_sent     text,
  edit_pct       real,

  primary_intent  text,
  email_category  text,

  status          text not null default 'PENDING_REVIEW',
  reviewed_by     text,
  review_notes    text,

  created_at      timestamptz not null default now(),
  reviewed_at     timestamptz,

  constraint feedback_queue_status_chk
    check (status in ('PENDING_REVIEW', 'PROMOTED', 'SKIPPED', 'ESCALATED'))
);
```

---

### 11. `kb_graph_pairs`

```sql
create table kb_graph_pairs (
  id                uuid primary key default gen_random_uuid(),
  concept_a         text not null,
  concept_b         text not null,
  relationship_type text not null,
  notes             text,
  created_at        timestamptz not null default now()
);
```

---

### 12. `kb_ingestion_runs`

```sql
create table kb_ingestion_runs (
  id                 uuid primary key default gen_random_uuid(),
  run_type           text not null,
  status             text not null,
  records_read       int not null default 0,
  canonical_written  int not null default 0,
  variants_written   int not null default 0,
  chunks_written     int not null default 0,
  embeddings_written int not null default 0,
  error_text         text,
  started_at         timestamptz not null default now(),
  finished_at        timestamptz,

  constraint kb_ingestion_runs_type_chk
    check (run_type in ('source_sync','dedupe','clustering','chunking','embed','refresh')),
  constraint kb_ingestion_runs_status_chk
    check (status in ('running','succeeded','failed','partial'))
);
```

---

## Index plan

```sql
-- kb_canonical_entries
create index kb_canonical_entries_category_idx   on kb_canonical_entries (category);
create index kb_canonical_entries_store_idx      on kb_canonical_entries (store);
create index kb_canonical_entries_status_idx     on kb_canonical_entries (status);
create index kb_canonical_entries_intent_idx     on kb_canonical_entries (primary_intent);
create index kb_canonical_entries_review_due_idx on kb_canonical_entries (review_due_at)
  where review_due_at is not null;

-- kb_query_variants
create index kb_query_variants_entry_idx  on kb_query_variants (canonical_entry_id);
create index kb_query_variants_search_idx on kb_query_variants using gin (search_vector);

-- kb_semantic_chunks
create index kb_semantic_chunks_entry_idx       on kb_semantic_chunks (canonical_entry_id, chunk_order);
create index kb_semantic_chunks_retrievable_idx on kb_semantic_chunks (is_retrievable);
create index kb_semantic_chunks_search_idx      on kb_semantic_chunks using gin (search_vector);

-- kb_enrichments / kb_approval_log
create index kb_enrichments_entry_idx  on kb_enrichments  (canonical_entry_id);
create index kb_approval_log_entry_idx on kb_approval_log (canonical_entry_id);

-- kb_retrieval_log / feedback_queue
create index kb_retrieval_log_draft_idx  on kb_retrieval_log (draft_log_id);
create index kb_retrieval_log_entry_idx  on kb_retrieval_log (canonical_entry_id);
create index feedback_queue_status_idx   on feedback_queue  (status);

-- ✅ Vector index — primary (small model, 1536)
create index kb_chunk_embeddings_hnsw_idx
  on kb_chunk_embeddings
  using hnsw (embedding vector_cosine_ops);

-- ⚠️ Vector index — large model (MRL). Create after kb_chunk_embeddings_large is confirmed.
-- create index kb_chunk_embeddings_large_hnsw_idx
--   on kb_chunk_embeddings_large
--   using hnsw (embedding vector_cosine_ops);
```

---

## Supabase RPC plan

The cascade decision (small vs. large) lives in Python (`catalyst_semantic_retriever.py`), not in Postgres. Postgres has two separate semantic search functions — one per embedding table. Python calls one or both depending on the cascade outcome.

### 1. Lexical retrieval (language-agnostic)

```sql
create or replace function kb_search_lexical(
  query_text      text,
  filter_category text,
  filter_store    text default null,
  match_count     int  default 10
)
returns table (canonical_entry_id uuid, semantic_chunk_id uuid, rank_score real)
language sql stable
as $$
  with q as (select websearch_to_tsquery('english', query_text) as tsq),
  variant_hits as (
    select v.canonical_entry_id, null::uuid, ts_rank_cd(v.search_vector, q.tsq)
    from kb_query_variants v
    join kb_canonical_entries e on e.id = v.canonical_entry_id
    cross join q
    where e.status = 'approved'
      and e.category = filter_category
      and (filter_store is null or e.store in (filter_store, 'BOTH'))
      and v.search_vector @@ q.tsq
  ),
  chunk_hits as (
    select c.canonical_entry_id, c.id, ts_rank_cd(c.search_vector, q.tsq)
    from kb_semantic_chunks c
    join kb_canonical_entries e on e.id = c.canonical_entry_id
    cross join q
    where e.status = 'approved'
      and e.category = filter_category
      and (filter_store is null or e.store in (filter_store, 'BOTH'))
      and c.is_retrievable = true
      and c.search_vector @@ q.tsq
  )
  select * from (select * from variant_hits union all select * from chunk_hits) x
  order by rank_score desc limit match_count;
$$;
```

### 2. Semantic retrieval — small model (first pass)

```sql
create or replace function kb_search_semantic(
  query_embedding vector(1536),
  filter_category text,
  filter_store    text default null,
  match_count     int  default 10
)
returns table (canonical_entry_id uuid, semantic_chunk_id uuid, similarity double precision)
language sql stable
as $$
  select c.canonical_entry_id, c.id,
         1 - (e.embedding <=> query_embedding)
  from kb_chunk_embeddings e
  join kb_semantic_chunks c on c.id = e.semantic_chunk_id
  join kb_canonical_entries k on k.id = c.canonical_entry_id
  where k.status = 'approved'
    and k.category = filter_category
    and (filter_store is null or k.store in (filter_store, 'BOTH'))
    and c.is_retrievable = true
  order by e.embedding <=> query_embedding
  limit match_count;
$$;
```

### 3. Semantic retrieval — large model (fallback)

```sql
-- ⚠️ Replace vector(XXXX) with confirmed MRL dimension before creating.
create or replace function kb_search_semantic_large(
  query_embedding vector(XXXX),
  filter_category text,
  filter_store    text default null,
  match_count     int  default 10
)
returns table (canonical_entry_id uuid, semantic_chunk_id uuid, similarity double precision)
language sql stable
as $$
  select c.canonical_entry_id, c.id,
         1 - (e.embedding <=> query_embedding)
  from kb_chunk_embeddings_large e
  join kb_semantic_chunks c on c.id = e.semantic_chunk_id
  join kb_canonical_entries k on k.id = c.canonical_entry_id
  where k.status = 'approved'
    and k.category = filter_category
    and (filter_store is null or k.store in (filter_store, 'BOTH'))
    and c.is_retrievable = true
  order by e.embedding <=> query_embedding
  limit match_count;
$$;
```

### 4. Hybrid fusion RPC — small model

```sql
create or replace function kb_search_rrf(
  query_text      text,
  query_embedding vector(1536),
  filter_category text,
  filter_store    text default null,
  lexical_k       int  default 20,
  semantic_k      int  default 20,
  final_k         int  default 3,
  rrf_k           int  default 60
)
returns table (canonical_entry_id uuid, semantic_chunk_id uuid, fused_score double precision)
language sql stable
as $$
  with l as (
    select canonical_entry_id, semantic_chunk_id,
           row_number() over (order by rank_score desc) as rnk
    from kb_search_lexical(query_text, filter_category, filter_store, lexical_k)
  ),
  s as (
    select canonical_entry_id, semantic_chunk_id,
           row_number() over (order by similarity desc) as rnk
    from kb_search_semantic(query_embedding, filter_category, filter_store, semantic_k)
  ),
  combined as (
    select
      coalesce(l.canonical_entry_id, s.canonical_entry_id),
      coalesce(l.semantic_chunk_id,  s.semantic_chunk_id),
      coalesce(1.0/(rrf_k+l.rnk),0.0) + coalesce(1.0/(rrf_k+s.rnk),0.0) as fused_score
    from l full outer join s
      on  l.canonical_entry_id = s.canonical_entry_id
      and coalesce(l.semantic_chunk_id,'00000000-0000-0000-0000-000000000000'::uuid)
        = coalesce(s.semantic_chunk_id,'00000000-0000-0000-0000-000000000000'::uuid)
  )
  select * from combined order by fused_score desc limit final_k;
$$;
```

### 5. Hybrid fusion RPC — large model fallback
Mirror of `kb_search_rrf` calling `kb_search_semantic_large`. Create after MRL dimension confirmed.

---

## Cascade logic (Python — `catalyst_semantic_retriever.py`)

This lives in the application layer, not in Postgres.

```python
SIMILARITY_THRESHOLD = 0.7  # tune after first 100 live retrievals

def retrieve(email_text, category, store):
    # Step 1: free ASCII check
    if has_non_ascii(email_text):
        return retrieve_large(email_text, category, store)

    # Step 2: small model first pass
    results = retrieve_small(email_text, category, store)
    best_score = results[0]["similarity"] if results else 0.0

    # Step 3: fallback if low confidence
    if best_score < SIMILARITY_THRESHOLD:
        return retrieve_large(email_text, category, store)

    return results
```

---

## Ingestion sequence

1. Load KB source files into `kb_sources`
2. Hash entries and remove exact duplicates
3. Cluster semantically similar entries
4. Create one canonical T0 answer in `kb_canonical_entries` (status = `draft`)
5. Store alternate phrasings in `kb_query_variants`
6. Semantically chunk the canonical answer into `kb_semantic_chunks`
7. Embed ALL retrievable chunks with **both** models:
   - → `kb_chunk_embeddings` via `text-embedding-3-small` (1536 dims)
   - → `kb_chunk_embeddings_large` via `text-embedding-3-large` + MRL (TBD dims) ⚠️ pending dimension
8. Load June's improvements into `kb_enrichments`
9. Human reviews → log in `kb_approval_log` → status → `approved`
   - Set `approved_by`, `approved_at`, `review_due_at` (`approved_at + 90 days`)
10. Optionally seed concept links into `kb_graph_pairs`
11. Log every pass in `kb_ingestion_runs`

---

## Semantic chunking guidance

- `summary` — one-sentence answer overview
- `policy_rule` — what the policy says
- `eligibility_rule` — who qualifies, what conditions apply
- `required_evidence` — what the customer must provide
- `agent_action` — what the CS agent does next
- `customer_message` — approved language for the reply
- `exception_rule` — edge cases and overrides
- `escalation_condition` — when to escalate to human
- `closure` — how the reply closes

---

## Supabase security stance

- RLS enabled on all tables
- All tables: service role only — no public client reads
- Retrieval RPCs: backend only
- `feedback_queue` and `kb_approval_log`: HITL review via internal tooling

---

## Recommended build order

### Stage 1 — canonical layer ✅ ready
`kb_sources`, `kb_canonical_entries`, `kb_query_variants`, `kb_approval_log`, `kb_ingestion_runs`

### Stage 2 — semantic chunk layer ✅ ready
`kb_semantic_chunks`

### Stage 3a — primary retrieval (small model) ✅ ready
`kb_chunk_embeddings` (1536), lexical + primary HNSW index, `kb_search_lexical`, `kb_search_semantic`, `kb_search_rrf`, `kb_retrieval_log`

### Stage 3b — fallback retrieval (large model) ⚠️ blocked on MRL dimension
`kb_chunk_embeddings_large` (XXXX), large HNSW index, `kb_search_semantic_large`, `kb_search_rrf_large`

### Stage 4 — feedback and enrichment
`kb_enrichments`, `feedback_queue`, `kb_graph_pairs`

---

## One open item

| Item | What's needed | Who |
|------|--------------|-----|
| MRL truncation dimension for `text-embedding-3-large` | 512 or 1024 — pick one. This sets the vector column size for `kb_chunk_embeddings_large` and all large-model RPCs. Can't be changed after data is stored. | June |

Everything else is unblocked.
