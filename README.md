# Rwanda Law RAG

RAG-powered legal assistant for Rwandan law. Ask legal questions in plain language and receive answers grounded in authoritative legal texts, with exact article citations from the Constitution, Penal Code, and Labor Law.

**Live demo:** [law-rag.streamlit.app](https://law-rag.streamlit.app)

## What it does

- Searches 568 legal articles across 3 Rwandan laws
- Returns answers with specific article citations
- Retrieves 6 relevant articles per query for multi-article legal reasoning
- Detects non-legal questions and responds appropriately


## Why Law RAG

General LLMs can answer legal questions, but without access to the relevant legal corpus, they may produce incomplete, outdated, or hallucinated responses. Legal work demands verifiable sources and precise citations.

Law RAG solves this by:

- Grounding every response in an explicit legal knowledge base.
- Retrieving the relevant legal articles first, then generating answers strictly from those sources.
- Ensuring accuracy, traceability, and legal reliability.


### Approach: Retrieval-Augmented Generation (RAG)

1. Retrieval → fetch relevant legal provisions from authoritative laws.
2. Augmentation → structure a prompt with the retrieved articles.
3. Generation → LLM produces the cited legal answer.

Result: answers with article-level provenance.


## Features

🔹Searches 568 legal articles across 3 Rwandan laws.
🔹Returns answers with exact article citations.
🔹Retrieves multiple relevant provisions for multi-article reasoning.
🔹Detects non-legal questions and responds appropriately.


## Laws Covered (Rwanda v1.0)

| Law	                                        Scope
| ------------------------------------------- | ------------------------------------------ |
| Constitution of Rwanda (2003, revised 2015) |	Fundamental rights, governance, judiciary  |
| Penal Code (Law No. 68/2018)                |	Criminal offences and penalties            |
| Labor Law (Law No. 66/2018)	              | Employment relations and conditions        |

> Note: Penal Code and Labor Law PDFs use a 3-column format (Kinyarwanda | English | French).
        The extraction pipeline isolates the English column for indexing.


## Tech stack

| Component  | Technology                    |
| ---------- | ----------------------------- |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB  | ChromaDB (persistent, local)  |
| LLM        | GPT-4o-mini (temperature 0.1) |
| Frontend   | Streamlit                     |
| Chunking   | Article-level with metadata   |

## Architecture

```
User question
   ↓
Embedding
   ↓
ChromaDB retrieval (top-k articles)
   ↓
Prompt augmentation with legal context
   ↓
LLM generation
   ↓
Cited legal answer

```

## Platform Vision

Law RAG is designed as a multi-jurisdiction legal retrieval platform, starting with Rwanda and expanding across Africa.

### Geographic Roadmap

- v1.x — East Africa first batch: Rwanda → Burundi → Kenya
- v2 — Additional African jurisdictions and regional frameworks

### Language Roadmap

- v1.1.0 — French legal corpus support
- v1.2.0 — Local languages per jurisdiction (e.g., Kinyarwanda, Kirundi, Swahili)

### Legal Scope Roadmap

- Additional national codes and statutes
- Sectoral regulations
- Administrative and regulatory law
- Case law (future phase)

## Positioning

Law RAG provides jurisdiction-specific legal AI grounded in authoritative texts, enabling:

- Accurate legal Q&A
- Article-level traceability
- Multilingual legal access
- Cross-country legal retrieval