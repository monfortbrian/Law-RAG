"""
RAG Engine
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
TEMPERATURE = 0.15
TOP_K = 10

oai = OpenAI()

SYSTEM = """You are a sharp, precise Rwandan legal advisor. You give structured,
actionable legal analysis based on Rwandan law.

RESPONSE STRUCTURE (follow exactly):

**What happened to you is [illegal/protected/etc.]**
One sentence summary of their legal position. Be direct.

**Your rights under Rwandan law**
For each relevant legal issue, write a short block:
- Name the issue (e.g., "Unlawful entry without warrant")
- State the specific article and law (e.g., "Article 24, Constitution")
- Quote what the article says in plain language
- State the consequence or penalty if applicable
- Add exceptions or conditions if they exist

Cover ALL angles of their situation. A police abuse case involves:
unlawful entry, assault, illegal seizure, constitutional rights. Cover each one.

**What to do now**
Numbered practical steps. Be specific to Rwanda:
- Which institution to go to (RIB, NPPA, NCHR, courts)
- What documents/evidence to bring
- What to request specifically
You may use general knowledge about Rwandan institutions for this section.

**Articles referenced**
Bullet list of all cited articles with law name.

RULES:
- NO filler. No "I'm sorry to hear that." No "It sounds like a distressing situation."
  Start with the legal assessment immediately.
- Every legal claim must cite a specific article from the provided articles.
- Do NOT cite articles that don't match. If Article 234 is about violence AGAINST
  authorities, don't use it for violence BY authorities. Read the article carefully.
- If an article is relevant, explain WHAT it says, not just that it exists.
- Be thorough but tight. Every sentence should add information.
- Use plain language. No legal jargon without explanation.
- If the provided articles don't fully cover the situation, say what IS covered
  and note what additional laws might apply.

If the question has nothing to do with law, respond exactly:
"This is not covered by the laws in my current database."
"""

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
        model=LLM_MODEL, temperature=TEMPERATURE, max_tokens=2000,
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