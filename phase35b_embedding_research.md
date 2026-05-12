# Phase 3.5b — Embedding Model Research
**Prepared By:** Theresa
**Updated:** April 10, 2026
**Purpose:** Pre-design research across all platforms before building the multi-model KB ingestion system

---

## Summary

Catalyst operates across two channel types:

**CS / Live Chat:** Gmail (email), Vanchat, tawk.to, tinytalk.ai, clickconnector.io — all confirmed OpenAI. One `embedding_openai_small` column covers the entire CS stack.

**Social:** Instagram, Facebook, TikTok, Pinterest, LinkedIn — managed via Replient (closed platform). Replient uses OpenAI/Anthropic/Gemini internally but is not externally feedable via embeddings. It is configured through brand guidelines in their UI. No BQ embedding column needed for social.

Platforms with distinct models requiring their own column: Amazon (Titan V2), Shopify (Nomic — confirmed), and LLaMA (open source fallback). Vimeo uses OpenAI so it falls into the existing OpenAI column.

The native embedding models of Instagram (Meta), TikTok (ByteDance Monolith), and Pinterest (PinSage) are fully proprietary and cannot be fed from our KB. For Catalyst's purposes these don't matter — Replient is the intermediary and its model is what drives retrieval for all social responses.

---

## Full Platform Breakdown

| Platform | Embedding Model | Dimensions | RAG Method | Notes |
|---|---|---|---|---|
| **OpenAI / ChatGPT** | text-embedding-3-small / text-embedding-3-large | 1536 / 3072 | Hybrid | Industry standard. Covers most CS platforms. |
| **Amazon** | Titan Text Embeddings V2 | 256, 384, or 1024 (configurable) | Hybrid BM25 + semantic (Kendra GenAI Index) | Used in Amazon seller tools and product search. |
| **Shopify** | Nomic (confirmed by June Lai) | Unknown | Vector search | Confirmed by June Lai, April 2026. |
| **Twitter / X (Grok)** | grok-embedding-small | Not disclosed | Hybrid: inverted index + vector + RRF | xAI Collections API supports document upload. |
| **tawk.to** ⭐ | OpenAI text-embedding-3 | 1536 / 3072 | RAG + KB | Catalyst active channel. Uses OpenAI APIs. Apollo AI Bot. Falls into OpenAI column. |
| **Vanchat** ⭐ | OpenAI (confirmed by support — exact model unspecified) | 1536 / 3072 | Unknown | Uses "OpenAI ChatGPT models for different use cases" per support response Apr 9. Likely text-embedding-3 family. Follow-up needed on RAG method. |
| **Replient** ⭐ | OpenAI + Anthropic + Google Gemini (internal) | N/A | Closed platform — not externally feedable via embeddings | Catalyst active channel. AI-powered community management — automates social comment responses. Configured via brand guidelines and approved responses in their UI, not via embedding injection. No BQ column needed. |
| **Instagram** ⭐ | Meta proprietary + ImageBind | Unknown | Semantic + visual (FAISS) | Catalyst active channel. Responses handled via Replient — Replient's model is what matters here, not Meta's native model. |
| **Facebook** ⭐ | Meta proprietary + ImageBind | Unknown | Semantic + visual (FAISS) | Catalyst active channel. Responses handled via Replient. Same as Instagram. |
| **TikTok** ⭐ | Monolith (ByteDance proprietary) | Unknown | Real-time, no traditional RAG | Catalyst active channel. Responses handled via Replient. Cannot feed external KB to TikTok directly. |
| **Pinterest** ⭐ | PinSage (proprietary GCN, 256D) | 256 | Graph-based recommendation | Catalyst active channel. Responses handled via Replient. PinSage is for recommendations — not externally feedable for CS responses. |
| **LinkedIn** ⭐ | Proprietary BERT-based (89M params) | 50 | Hybrid | Catalyst active channel (presence only — does not sell on LinkedIn). Responses handled via Replient. |
| **Vimeo** ⭐ | OpenAI + Google Vertex AI | 1536 | RAG + transcript-based search | Catalyst active channel. Uses OpenAI embeddings — falls into same column as email/Vanchat. |
| **tinytalk.ai** ⭐ | OpenAI GPT-3 / GPT-4 / GPT-4o | 1536 / 3072 | RAG + KB (PDF upload supported) | Catalyst active channel. AI chatbot with KB feeding. Falls into OpenAI column. |
| **clickconnector.io** ⭐ | OpenAI (Magic Assistant) | 1536 / 3072 | RAG + KB integration | Catalyst active channel. Omnichannel support inbox. Falls into OpenAI column. |
| **stamped.io** ⭐ | StampedIQ (proprietary) | Unknown | No — analyzes existing reviews only | Catalyst active channel. Review sentiment analysis. Not feedable — no embedding column needed. |
| **justreview.co** ⭐ | Proprietary AI | Unknown | No — analyzes collected reviews only | Catalyst active channel. Review collection + authenticity verification. Not feedable — no embedding column needed. |
| **Zendesk** | OpenAI text-embedding-3 | 1536 / 3072 | Vector search + RAG | Industry reference only — not used by Catalyst. Partners with OpenAI since 2023. |
| **Intercom (Fin)** | BGE-Large-EN-v1.5 + multilingual-E5-base (fine-tuned) | ~768 | Hybrid semantic + custom reranking | Industry reference only — not used by Catalyst. Powered by Anthropic Claude. |
| **Gorgias** | OpenAI text-embedding-3 | 1536 / 3072 | RAG + KB | Industry reference only — not used by Catalyst. GPT-4o + Shopify integration. |
| **Freshdesk (Freddy AI)** | Azure OpenAI | 1536 / 3072 | KB integration + RAG | Industry reference only — not used by Catalyst. Azure OpenAI powered. |

---

## Proposed Multi-Model Column Schema (Draft)

Based on the research, the minimum actionable columns for Catalyst's KB ingestion are:

| Column Name | Covers | Cost | Status |
|---|---|---|---|
| `embedding_openai_small` | Gmail (email), Vanchat, tawk.to, tinytalk.ai, clickconnector.io, Vimeo, ChatGPT | Paid API | Ready |
| `embedding_amazon_titan` | Amazon seller tools, Kendra, product search | AWS Bedrock | Ready — needs AWS Bedrock credentials |
| `embedding_nomic` | Shopify | Free (open source) | Confirmed |
| `embedding_llama` | Open source fallback, Facebook/Instagram proxy | Free (local) | Ready |
| `embedding_model_notes` | Per-row notes on T0 word or platform-specific adjustments | — | Metadata column |

**Note on social channels:**
Catalyst's social channels (Instagram, Facebook, TikTok, Pinterest, LinkedIn) are managed through Replient. Replient is a closed community management platform — it uses OpenAI, Anthropic, and Google Gemini internally but is not externally feedable via embeddings. It is configured through brand guidelines in their UI. No BQ embedding column is needed for social.

**Platforms where native embedding feeding is not possible:**
- TikTok — Monolith is fully proprietary, no external KB ingestion
- Meta/Instagram — proprietary ImageBind, not externally feedable
- Pinterest — PinSage is recommendation-only, not CS-feedable
- LinkedIn — proprietary 50D model, cannot replicate (Catalyst has presence only, does not sell)

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
Closed community management platform. Uses OpenAI, Anthropic, and Google Gemini for reply generation internally. Not feedable via external embeddings — configured via brand guidelines in their UI. No open questions on embedding model.

### Shopify
Confirmed: uses Nomic embedding model.

---

## Key Design Principle (per June, April 8 Ops Call)

> "Rather than rebuild for every platform, build the ingestion once across all models. Add a column per model in BigQuery. When you update one answer, it rolls out across all platforms. When you retrieve, you just switch the column. That way you never get lost in translation between platforms."

One canonical answer. Multiple embeddings stored at ingestion. Retrieval selects by platform column. T0 word captured per model where applicable.

---

*Research compiled: April 9, 2026*
*Next step: June to review schema and confirm scope of social channels (Replient vs. custom build) before any code is written.*
