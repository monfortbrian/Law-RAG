"""
RAG Engine - search + LLM with citations
Temperature: 0.1 (factual, no hallucination)
"""

import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

CHROMA = os.path.join(PROJECT_ROOT, "chroma_db")
COLLECTION = "rwanda_laws"
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.1
TOP_K = 6

oai = OpenAI()

SYSTEM = """You are a legal assistant specializing in Rwandan law. You help citizens and professionals understand their legal rights and obligations.

RULES:
1. ONLY answer based on the legal articles provided below. Never invent law.
2. ALWAYS cite specific article numbers (e.g. "Article 142, Penal Code").
3. When multiple articles apply, explain how they work together.
4. If the articles don't cover the question, say: "This is not covered by the laws in my current database (Constitution, Penal Code, Labor Law). Please consult a legal professional."
5. Use clear language a non-lawyer can understand.
6. State penalties clearly when applicable.
7. Mention exceptions and conditions when they exist.

FORMAT:
Start with a direct answer (2-3 sentences).
Then explain the legal reasoning with article citations.
End with a list of all articles referenced."""

_col = None

def _get_col():
    global _col
    if _col is None:
        _col = chromadb.PersistentClient(path=CHROMA).get_collection(COLLECTION)
    return _col


def _embed(text):
    return oai.embeddings.create(model=EMBED_MODEL, input=[text]).data[0].embedding


def search(query, law_filter="all", top_k=TOP_K):
    col = _get_col()
    emb = _embed(query)
    where = {"law_key": law_filter} if law_filter != "all" else None
    r = col.query(query_embeddings=[emb], n_results=top_k, where=where)
    return [{
        "id": r["ids"][0][i],
        "content": r["documents"][0][i],
        "metadata": r["metadatas"][0][i],
    } for i in range(len(r["ids"][0]))]


def _context(articles):
    parts = []
    for i, a in enumerate(articles, 1):
        m = a["metadata"]
        parts.append(
            f"[Article {i}]\n"
            f"Law: {m['short_name']}\n"
            f"Chapter: {m['chapter']}\n"
            f"Section: {m['section']}\n"
            f"Reference: {m['article_number']}\n"
            f"Title: {m['article_title']}\n\n"
            f"{a['content']}\n"
        )
    return "\n---\n".join(parts)


def query_law(question, law_filter="all"):
    articles = search(question, law_filter)
    if not articles:
        return {
            "answer": "No relevant articles found. Try rephrasing your question.",
            "cited_articles": [], "query": question, "law_filter": law_filter,
        }

    resp = oai.chat.completions.create(
        model=LLM_MODEL, temperature=TEMPERATURE, max_tokens=1500,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"LEGAL ARTICLES:\n\n{_context(articles)}\n\n---\n\nQUESTION: {question}"},
        ],
    )
    return {
        "answer": resp.choices[0].message.content,
        "cited_articles": articles,
        "query": question,
        "law_filter": law_filter,
    }
