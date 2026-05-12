-- =============================================================
-- CATALYST CS — KB Retrieval Schema v8.0
-- Date: 2026-04-24
--
-- Cascade embedding strategy:
--   Primary:  text-embedding-3-small  → vector(1536)  [~80% of queries]
--   Fallback: text-embedding-3-large + MRL → vector(1024) [~20% — non-ASCII or low confidence]
--
-- ⚠️ Large model dimension (1024) assumed — confirm MRL dim before Stage 3b.
--
-- Cascade logic lives in Python (catalyst_semantic_retriever.py):
--   1. ASCII pre-check (free) → non-ASCII → skip to large
--   2. Small model first pass → similarity ≥ 0.7 → done
--   3. similarity < 0.7 → fallback to large
-- =============================================================


-- -------------------------------------------------------------
-- EXTENSIONS
-- -------------------------------------------------------------

create extension if not exists pgcrypto;
create extension if not exists vector;


-- -------------------------------------------------------------
-- HELPER TRIGGER
-- -------------------------------------------------------------

create or replace function set_updated_at()
returns trigger language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;


-- =============================================================
-- STAGE 1 — CANONICAL LAYER
-- =============================================================

-- -------------------------------------------------------------
-- kb_sources
-- Raw ingest boundary. One row per source file/document.
-- -------------------------------------------------------------

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


-- -------------------------------------------------------------
-- kb_canonical_entries
-- One row per canonical support answer path (T0 answer).
-- -------------------------------------------------------------

create table kb_canonical_entries (
  id                      uuid primary key default gen_random_uuid(),
  source_id               uuid references kb_sources(id) on delete set null,

  slug                    text not null unique,
  title                   text not null,

  -- Classification
  category                text not null,
  store                   text not null,
  channel_scope           text[] not null default '{}',

  -- Intent and tone
  primary_intent          text not null,
  secondary_intent        text,
  sentiment_profile       text,
  escalation_risk         text,

  -- Content
  canonical_question      text not null,
  canonical_answer        text not null,
  intent_cluster          text,
  content_hash            text not null,

  -- CS workflow fields
  policy_source_url       text,                        -- link to authoritative policy page
  requires_human_approval boolean not null default false,
  review_due_at           timestamptz,                 -- set to approved_at + 90 days
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


-- -------------------------------------------------------------
-- kb_query_variants
-- Alternate phrasings for lexical retrieval.
-- "50 ways to ask, 1 answer."
-- -------------------------------------------------------------

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


-- -------------------------------------------------------------
-- kb_approval_log
-- HITL audit trail for every KB status transition.
-- -------------------------------------------------------------

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


-- -------------------------------------------------------------
-- kb_ingestion_runs
-- Audit trail for every ingest / embed / refresh job.
-- -------------------------------------------------------------

create table kb_ingestion_runs (
  id                 uuid primary key default gen_random_uuid(),
  run_type           text not null,
  status             text not null,
  records_read       int  not null default 0,
  canonical_written  int  not null default 0,
  variants_written   int  not null default 0,
  chunks_written     int  not null default 0,
  embeddings_written int  not null default 0,
  error_text         text,
  started_at         timestamptz not null default now(),
  finished_at        timestamptz,

  constraint kb_ingestion_runs_type_chk
    check (run_type in ('source_sync','dedupe','clustering','chunking','embed','refresh')),
  constraint kb_ingestion_runs_status_chk
    check (status in ('running','succeeded','failed','partial'))
);


-- =============================================================
-- STAGE 2 — SEMANTIC CHUNK LAYER
-- =============================================================

-- -------------------------------------------------------------
-- kb_semantic_chunks
-- Typed retrieval blocks derived from the canonical answer.
-- Chunking happens after canonicalization.
-- -------------------------------------------------------------

create table kb_semantic_chunks (
  id                 uuid primary key default gen_random_uuid(),
  canonical_entry_id uuid not null references kb_canonical_entries(id) on delete cascade,

  chunk_key          text not null,
  chunk_type         text not null,
  chunk_order        int  not null default 0,
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
      'summary',
      'policy_rule',
      'eligibility_rule',
      'required_evidence',
      'agent_action',
      'customer_message',
      'exception_rule',
      'escalation_condition',
      'closure'
    )),

  unique (canonical_entry_id, chunk_key)
);

create trigger kb_semantic_chunks_set_updated_at
  before update on kb_semantic_chunks
  for each row execute function set_updated_at();


-- =============================================================
-- STAGE 3a — PRIMARY RETRIEVAL (small model, English, ~80%)
-- =============================================================

-- -------------------------------------------------------------
-- kb_chunk_embeddings
-- text-embedding-3-small, 1536 dims. First-pass retrieval.
-- -------------------------------------------------------------

create table kb_chunk_embeddings (
  id                uuid primary key default gen_random_uuid(),
  semantic_chunk_id uuid not null references kb_semantic_chunks(id) on delete cascade,

  embedding_model   text not null default 'text-embedding-3-small',
  dimensions        int  not null default 1536,
  embedding         vector(1536) not null,

  content_hash      text not null,
  created_at        timestamptz not null default now(),

  unique (semantic_chunk_id, content_hash)
);


-- -------------------------------------------------------------
-- kb_retrieval_log
-- Per-interaction retrieval audit.
-- draft_log_id is the external join key to BigQuery draft_log.
-- embedding_model records which cascade path was taken.
-- -------------------------------------------------------------

create table kb_retrieval_log (
  id                 uuid primary key default gen_random_uuid(),
  draft_log_id       text not null,
  canonical_entry_id uuid references kb_canonical_entries(id) on delete set null,
  semantic_chunk_id  uuid references kb_semantic_chunks(id)   on delete set null,

  retrieval_method   text not null,
  embedding_model    text,
  rank_position      int  not null,
  similarity_score   real,
  was_used_in_draft  boolean not null default true,

  created_at         timestamptz not null default now(),

  constraint kb_retrieval_log_method_chk
    check (retrieval_method in ('lexical', 'semantic', 'hybrid')),
  constraint kb_retrieval_log_rank_chk
    check (rank_position between 1 and 10)
);


-- =============================================================
-- STAGE 3b — FALLBACK RETRIEVAL (large model + MRL, ~20%)
-- ⚠️ Dimension assumed 1024. Confirm with June before creating.
-- =============================================================

-- -------------------------------------------------------------
-- kb_chunk_embeddings_large
-- text-embedding-3-large + MRL truncation.
-- Triggered by: non-ASCII input OR small model similarity < 0.7.
-- ⚠️ Replace 1024 if June confirms a different MRL dimension.
-- -------------------------------------------------------------

create table kb_chunk_embeddings_large (
  id                uuid primary key default gen_random_uuid(),
  semantic_chunk_id uuid not null references kb_semantic_chunks(id) on delete cascade,

  embedding_model   text not null default 'text-embedding-3-large',
  dimensions        int  not null default 1024,        -- ⚠️ assumed — confirm MRL dim
  embedding         vector(1024) not null,             -- ⚠️ assumed — confirm MRL dim

  content_hash      text not null,
  created_at        timestamptz not null default now(),

  unique (semantic_chunk_id, content_hash)
);


-- =============================================================
-- STAGE 4 — FEEDBACK AND ENRICHMENT LAYER
-- =============================================================

-- -------------------------------------------------------------
-- kb_enrichments
-- Structured enrichment: routing hints, guardrails, rerank signals.
-- -------------------------------------------------------------

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


-- -------------------------------------------------------------
-- feedback_queue
-- Phase 3.5f self-learning layer.
-- Populated by reconciler when draft scores MAJOR_EDIT or REWRITE.
-- Human reviews weekly; PROMOTED entries are re-embedded.
-- -------------------------------------------------------------

create table feedback_queue (
  id              uuid primary key default gen_random_uuid(),
  draft_log_id    text not null unique,

  kb_ids_used     uuid[] not null default '{}',
  claude_draft    text   not null,
  final_sent      text,
  edit_pct        real,

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


-- -------------------------------------------------------------
-- kb_graph_pairs
-- Future Graph RAG (Phase 3.5e). Manually seeded concept links.
-- Covers semantically unrelated but contextually linked concepts
-- e.g. AirPods <-> charging, Watch <-> band, packaging <-> shipping.
-- -------------------------------------------------------------

create table kb_graph_pairs (
  id                uuid primary key default gen_random_uuid(),
  concept_a         text not null,
  concept_b         text not null,
  relationship_type text not null,
  notes             text,
  created_at        timestamptz not null default now()
);


-- =============================================================
-- INDEXES
-- =============================================================

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

-- kb_enrichments
create index kb_enrichments_entry_idx  on kb_enrichments  (canonical_entry_id);

-- kb_approval_log
create index kb_approval_log_entry_idx on kb_approval_log (canonical_entry_id);

-- kb_retrieval_log
create index kb_retrieval_log_draft_idx  on kb_retrieval_log (draft_log_id);
create index kb_retrieval_log_entry_idx  on kb_retrieval_log (canonical_entry_id);

-- feedback_queue
create index feedback_queue_status_idx on feedback_queue (status);

-- Vector index — primary (small model, 1536)
create index kb_chunk_embeddings_hnsw_idx
  on kb_chunk_embeddings
  using hnsw (embedding vector_cosine_ops);

-- Vector index — large model (⚠️ assumed 1024 — update if dimension changes)
create index kb_chunk_embeddings_large_hnsw_idx
  on kb_chunk_embeddings_large
  using hnsw (embedding vector_cosine_ops);


-- =============================================================
-- RETRIEVAL RPCs
-- Cascade logic (ASCII check + similarity threshold) lives in
-- Python (catalyst_semantic_retriever.py), not here.
-- These RPCs are called by the retriever depending on cascade outcome.
-- =============================================================

-- -------------------------------------------------------------
-- kb_search_lexical
-- Language-agnostic. Used in both cascade paths.
-- -------------------------------------------------------------

create or replace function kb_search_lexical(
  query_text      text,
  filter_category text,
  filter_store    text default null,
  match_count     int  default 10
)
returns table (canonical_entry_id uuid, semantic_chunk_id uuid, rank_score real)
language sql stable
as $$
  with q as (
    select websearch_to_tsquery('english', query_text) as tsq
  ),
  variant_hits as (
    select v.canonical_entry_id,
           null::uuid             as semantic_chunk_id,
           ts_rank_cd(v.search_vector, q.tsq) as rank_score
    from kb_query_variants v
    join kb_canonical_entries e on e.id = v.canonical_entry_id
    cross join q
    where e.status = 'approved'
      and e.category = filter_category
      and (filter_store is null or e.store in (filter_store, 'BOTH'))
      and v.search_vector @@ q.tsq
  ),
  chunk_hits as (
    select c.canonical_entry_id,
           c.id                   as semantic_chunk_id,
           ts_rank_cd(c.search_vector, q.tsq) as rank_score
    from kb_semantic_chunks c
    join kb_canonical_entries e on e.id = c.canonical_entry_id
    cross join q
    where e.status = 'approved'
      and e.category = filter_category
      and (filter_store is null or e.store in (filter_store, 'BOTH'))
      and c.is_retrievable = true
      and c.search_vector @@ q.tsq
  )
  select * from (
    select * from variant_hits
    union all
    select * from chunk_hits
  ) combined
  order by rank_score desc
  limit match_count;
$$;


-- -------------------------------------------------------------
-- kb_search_semantic
-- Small model first pass. vector(1536).
-- -------------------------------------------------------------

create or replace function kb_search_semantic(
  query_embedding vector(1536),
  filter_category text,
  filter_store    text default null,
  match_count     int  default 10
)
returns table (canonical_entry_id uuid, semantic_chunk_id uuid, similarity double precision)
language sql stable
as $$
  select c.canonical_entry_id,
         c.id                                    as semantic_chunk_id,
         1 - (e.embedding <=> query_embedding)   as similarity
  from kb_chunk_embeddings e
  join kb_semantic_chunks c     on c.id = e.semantic_chunk_id
  join kb_canonical_entries k   on k.id = c.canonical_entry_id
  where k.status = 'approved'
    and k.category = filter_category
    and (filter_store is null or k.store in (filter_store, 'BOTH'))
    and c.is_retrievable = true
  order by e.embedding <=> query_embedding
  limit match_count;
$$;


-- -------------------------------------------------------------
-- kb_search_semantic_large
-- Large model fallback. vector(1024) assumed — update if MRL dim differs.
-- -------------------------------------------------------------

create or replace function kb_search_semantic_large(
  query_embedding vector(1024),             -- ⚠️ assumed — update if MRL dim differs
  filter_category text,
  filter_store    text default null,
  match_count     int  default 10
)
returns table (canonical_entry_id uuid, semantic_chunk_id uuid, similarity double precision)
language sql stable
as $$
  select c.canonical_entry_id,
         c.id                                    as semantic_chunk_id,
         1 - (e.embedding <=> query_embedding)   as similarity
  from kb_chunk_embeddings_large e
  join kb_semantic_chunks c     on c.id = e.semantic_chunk_id
  join kb_canonical_entries k   on k.id = c.canonical_entry_id
  where k.status = 'approved'
    and k.category = filter_category
    and (filter_store is null or k.store in (filter_store, 'BOTH'))
    and c.is_retrievable = true
  order by e.embedding <=> query_embedding
  limit match_count;
$$;


-- -------------------------------------------------------------
-- kb_search_rrf
-- Hybrid fusion (lexical + small model vector) via RRF.
-- For large model hybrid: call kb_search_lexical + kb_search_semantic_large
-- in Python and fuse client-side, or create kb_search_rrf_large mirror.
-- -------------------------------------------------------------

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
      coalesce(l.canonical_entry_id, s.canonical_entry_id) as canonical_entry_id,
      coalesce(l.semantic_chunk_id,  s.semantic_chunk_id)  as semantic_chunk_id,
      coalesce(1.0 / (rrf_k + l.rnk), 0.0) +
      coalesce(1.0 / (rrf_k + s.rnk), 0.0)                as fused_score
    from l
    full outer join s
      on  l.canonical_entry_id = s.canonical_entry_id
      and coalesce(l.semantic_chunk_id, '00000000-0000-0000-0000-000000000000'::uuid)
        = coalesce(s.semantic_chunk_id, '00000000-0000-0000-0000-000000000000'::uuid)
  )
  select canonical_entry_id, semantic_chunk_id, fused_score
  from combined
  order by fused_score desc
  limit final_k;
$$;
