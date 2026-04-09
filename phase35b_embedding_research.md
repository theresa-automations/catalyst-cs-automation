# Phase 3.5b — Embedding Model Research
**Prepared By:** Theresa
**Updated:** April 9, 2026
**Purpose:** Pre-design research across all platforms before building the multi-model KB ingestion system

---

## Summary

Catalyst's active platforms (Vanchat, tawk.to, email/Gmail) all use OpenAI text-embedding-3. This means **one OpenAI column covers the entire active CS stack** — not a separate column per tool. Industry reference platforms (Zendesk, Gorgias, Freshdesk, Intercom) also use OpenAI, confirming this as the dominant standard.

Platforms with truly distinct models that need their own column are: Amazon (Titan V2), Shopify (Nomic — pending confirmation), Meta/Instagram (proprietary), and LLaMA (open source, free fallback).

TikTok, LinkedIn, and Meta use fully proprietary systems that do not accept external embeddings — those are research reference only and cannot be fed from our KB. Catalyst does not sell on LinkedIn.

---

## Full Platform Breakdown

| Platform | Embedding Model | Dimensions | RAG Method | Notes |
|---|---|---|---|---|
| **OpenAI / ChatGPT** | text-embedding-3-small / text-embedding-3-large | 1536 / 3072 | Hybrid | Industry standard. Covers most CS platforms. |
| **Amazon** | Titan Text Embeddings V2 | 256, 384, or 1024 (configurable) | Hybrid BM25 + semantic (Kendra GenAI Index) | Used in Amazon seller tools and product search. |
| **Shopify** | Nomic (per June — unconfirmed in public docs) | Unknown | Vector search | Needs direct confirmation from Shopify or Vanchat. |
| **Facebook / Instagram** | Meta proprietary + ImageBind (multimodal) | Unknown | Semantic + visual (FAISS) | Proprietary. Not externally feedable. |
| **TikTok** | Monolith (ByteDance proprietary) | Unknown | Real-time embedding, no traditional RAG | Fully proprietary. Cannot feed external KB data. |
| **Twitter / X (Grok)** | grok-embedding-small | Not disclosed | Hybrid: inverted index + vector + RRF | xAI Collections API supports document upload. |
| **LinkedIn** | Proprietary BERT-based (6-layer, 89M params) | 50 | Hybrid | Proprietary. Cannot replicate externally. |
| **tawk.to** | OpenAI text-embedding-3 | 1536 / 3072 | RAG + KB | Uses OpenAI APIs. Apollo AI Bot. |
| **Vanchat** ⭐ | OpenAI (confirmed by support — exact model unspecified) | 1536 / 3072 | Unknown | Uses "OpenAI ChatGPT models for different use cases" per support response Apr 9. Likely text-embedding-3 family. Follow-up needed on RAG method. |
| **Replient** ⭐ | Undisclosed | Unknown | Historical embeddings + ML | Needs direct outreach. See open questions below. |
| **Zendesk** | OpenAI text-embedding-3 | 1536 / 3072 | Vector search + RAG | Industry reference only — not used by Catalyst. Partners with OpenAI since 2023. |
| **Intercom (Fin)** | BGE-Large-EN-v1.5 + multilingual-E5-base (fine-tuned) | ~768 | Hybrid semantic + custom reranking | Industry reference only — not used by Catalyst. Powered by Anthropic Claude. |
| **Gorgias** | OpenAI text-embedding-3 | 1536 / 3072 | RAG + KB | Industry reference only — not used by Catalyst. GPT-4o + Shopify integration. |
| **Freshdesk (Freddy AI)** | Azure OpenAI | 1536 / 3072 | KB integration + RAG | Industry reference only — not used by Catalyst. Azure OpenAI powered. |

---

## Proposed Multi-Model Column Schema (Draft)

Based on the research, the minimum actionable columns for Catalyst's KB ingestion are:

| Column Name | Covers | Cost | Status |
|---|---|---|---|
| `embedding_openai_small` | ChatGPT, tawk.to, Vanchat, Gmail (email) | Paid API | Ready |
| `embedding_amazon_titan` | Amazon seller tools, Kendra, product search | AWS Bedrock | Ready |
| `embedding_nomic` | Shopify (pending confirmation) | Free (open source) | Pending confirmation |
| `embedding_llama` | Meta open source, free fallback, Facebook/Instagram proxy | Free (local) | Ready |
| `embedding_model_notes` | Per-row notes on T0 word or platform-specific adjustments | — | Metadata column |

**Platforms where feeding is not possible (reference only):**
- TikTok — fully proprietary real-time system, no external data ingestion
- Meta/Instagram — proprietary, not externally feedable
- LinkedIn — proprietary 50-dimension model, cannot replicate externally (Catalyst does not sell on LinkedIn)

---

## Open Questions Before Schema Can Be Finalized

### Vanchat
**Confirmed:** Uses OpenAI models (per support response, April 9, 2026). Exact model unspecified.
**Still needed:**
1. Which OpenAI embedding model specifically? (text-embedding-3-small or large?)
2. What RAG retrieval method — hybrid (keyword + semantic) or semantic only?
3. What data sources does the AI index? (KB articles, product pages, chat history?)
4. If we feed you a knowledge base, what format do you accept and what chunking do you recommend?

### Replient
1. What embedding model powers your AI comment response system?
2. Is the model OpenAI-based, or proprietary to Replient?
3. Can we feed a curated knowledge base to improve response accuracy? If so, what format?

### Shopify
1. Can you confirm the embedding model used by Shopify Sidekick / semantic search?
2. Is it Nomic Embed, or a different model?

---

## Key Design Principle (per June, April 8 Ops Call)

> "Rather than rebuild for every platform, build the ingestion once across all models. Add a column per model in BigQuery. When you update one answer, it rolls out across all platforms. When you retrieve, you just switch the column. That way you never get lost in translation between platforms."

One canonical answer. Multiple embeddings stored at ingestion. Retrieval selects by platform column. T0 word captured per model where applicable.

---

*Research compiled: April 9, 2026*
*Next step: Confirm Vanchat + Shopify models, then finalize schema with June before any code is written.*
