# Rwanda Law RAG

RAG-powered legal assistant for Rwandan law. Ask questions in plain language, get answers with exact article citations from the Constitution, Penal Code, and Labor Law.

**Live demo:** [your-app.streamlit.app](https://your-app.streamlit.app)

## What it does

- Searches 568 legal articles across 3 Rwandan laws
- Returns answers with specific article citations
- Retrieves 6 relevant articles per query for multi-article legal reasoning
- Detects non-legal questions and responds appropriately

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
Question → OpenAI Embedding → ChromaDB (top 6) → GPT-4o-mini → Cited answer
```

The Penal Code and Labor Law PDFs have 3-column layouts (Kinyarwanda | English | French). The extraction script uses coordinate-based clipping to extract only the English middle column.

## Laws covered

- **Constitution of Rwanda (2003, revised 2015)** - fundamental rights, governance, judiciary
- **Penal Code (Law No. 68/2018)** - criminal offences and penalties
- **Labor Law (Law No. 66/2018)** - employment contracts, termination, working conditions
