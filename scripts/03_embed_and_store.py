"""
==========================================================
STEP 3 - Embed + store in ChromaDB (FIXED: duplicate IDs)
==========================================================
RUN:  python scripts/03_embed_and_store.py
==========================================================
"""

import json
import os
import shutil
from collections import Counter
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PROCESSED = "data/processed"
CHROMA = "chroma_db"
COLLECTION = "rwanda_laws"
MODEL = "text-embedding-3-small"
BATCH = 50

client = OpenAI()


def embed(texts):
    r = client.embeddings.create(model=MODEL, input=texts)
    return [x.embedding for x in r.data]


def deduplicate_ids(chunks):
    """
    Some articles appear twice (e.g. Article 82 spanning pages).
    This makes every ID unique by appending _2, _3 etc.
    """
    seen = Counter()
    for c in chunks:
        orig = c["id"]
        seen[orig] += 1
        if seen[orig] > 1:
            c["id"] = f"{orig}_{seen[orig]}"

    fixed = sum(1 for v in seen.values() if v > 1)
    if fixed:
        print(f"  Fixed {fixed} duplicate article IDs")
    return chunks


def main():
    print("=" * 60)
    print("STEP 3: Embed and store in ChromaDB")
    print("=" * 60)

    # Load all chunks
    all_chunks = []
    for fn in sorted(os.listdir(PROCESSED)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(PROCESSED, fn), encoding="utf-8") as f:
            chunks = json.load(f)
            all_chunks.extend(chunks)
            print(f"  {fn}: {len(chunks)} chunks")

    if not all_chunks:
        print("No chunks found. Run step 2 first!")
        return

    print(f"\n  Total: {len(all_chunks)} chunks")

    # FIX DUPLICATE IDS
    all_chunks = deduplicate_ids(all_chunks)

    # Verify all unique
    all_ids = [c["id"] for c in all_chunks]
    dupes = [x for x, cnt in Counter(all_ids).items() if cnt > 1]
    if dupes:
        print(f"  ERROR still have duplicates: {dupes}")
        return
    print(f"  All {len(all_ids)} IDs are unique - good!")

    # Estimate cost
    chars = sum(len(c["embedding_text"]) for c in all_chunks)
    est = (chars / 4 / 1_000_000) * 0.02
    print(f"  Estimated embedding cost: ${est:.4f}")

    # Delete old ChromaDB completely
    if os.path.exists(CHROMA):
        shutil.rmtree(CHROMA)
        print(f"  Deleted old chroma_db folder")

    # Create fresh ChromaDB
    db = chromadb.PersistentClient(path=CHROMA)
    col = db.create_collection(COLLECTION)
    print(f"  Created fresh collection: {COLLECTION}")

    # Embed + store
    print(f"\nEmbedding and storing...")
    for i in range(0, len(all_chunks), BATCH):
        batch = all_chunks[i: i + BATCH]

        ids = [c["id"] for c in batch]
        docs = [c["content"] for c in batch]
        texts = [c["embedding_text"] for c in batch]
        metas = [
            {
                "law_key": c["law_key"],
                "law_name": c["law_name"],
                "short_name": c["short_name"],
                "chapter": c["chapter"],
                "section": c["section"],
                "article_number": c["article_number"],
                "article_title": c["article_title"],
                "full_citation": c["full_citation"],
            }
            for c in batch
        ]

        embeddings = embed(texts)
        col.add(ids=ids, embeddings=embeddings,
                documents=docs, metadatas=metas)

        done = min(i + BATCH, len(all_chunks))
        print(f"  {done}/{len(all_chunks)}")

    print(f"\nStored: {col.count()} documents")

    # Quick test searches
    print("\nTest searches:")
    for q in ["rights of arrested person", "penalty for theft", "annual leave days"]:
        emb = embed([q])
        r = col.query(query_embeddings=emb, n_results=3)
        print(f"\n  Q: '{q}'")
        for j, m in enumerate(r["metadatas"][0]):
            print(f"    {j+1}. {m['article_number']} ({m['short_name']})")

    print(f"\n{'=' * 60}")
    print(f"Done! {col.count()} articles in ChromaDB")
    print(f"Next: python scripts/04_test_rag.py")


if __name__ == "__main__":
    main()
