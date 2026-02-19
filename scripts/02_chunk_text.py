"""
==========================================================
STEP 2 - Chunk into article-level pieces
==========================================================

WHY BY ARTICLE?
  → Perfect citations (always know exact Article number)
  → Clean boundaries (no mid-sentence cuts)
  → Articles are natural legal units

SKIPS: Preamble text, TOC entries, empty articles, non-English chunks

Each chunk carries metadata:
  law_name, chapter, section, article_number, full_citation

RUN:  python scripts/02_chunk_text.py
==========================================================
"""

import json
import os
import re

RAW = "data/raw_text"
OUT = "data/processed"

# ── Sections to SKIP (not useful for RAG) ──
SKIP_PATTERNS = [
    r"^preamble",
    r"^table of contents",
    r"^ishakiro",
    r"^table des matières",
    r"^preambule",
]


def is_skipable_title(title: str) -> bool:
    t = title.lower().strip()
    return any(re.match(p, t) for p in SKIP_PATTERNS)


EN_WORDS = frozenset({
    "the", "and", "of", "to", "in", "a", "is", "for", "shall", "any",
    "person", "who", "with", "upon", "by", "or", "not", "be", "this",
    "law", "an", "has", "are", "from", "may", "such", "under", "article",
    "court", "offence", "penalty", "imprisonment", "guilty", "employee",
    "employer", "contract", "right", "rights", "state", "republic",
    "rwanda", "convicted", "liable", "fine", "unless", "where", "that",
    "which", "every", "no", "been", "their", "its", "into", "than",
    "more", "less", "years", "days", "months", "his", "her", "she", "he",
})


def looks_english(text: str) -> bool:
    words = text.lower().split()[:40]
    hits = sum(1 for w in words if w in EN_WORDS)
    return hits >= 3 or len(words) <= 5


def chunk_law(raw_text, law_key, law_name, short_name):
    chunks = []
    chapter = ""
    section = ""
    art_num = None
    art_title = ""
    art_lines = []

    re_ch = re.compile(
        r"^(?:CHAPTER|Chapter)\s+([IVXLCDM]+|\d+)\s*[:\.\s]*(.*)", re.I)
    re_sc = re.compile(r"^(?:Section|SECTION)\s+(\w+)\s*[:\.\s]*(.*)", re.I)
    re_ar = re.compile(
        r"^(?:Article|ARTICLE)\s+(One|\d+)\s*[:\.\s]*(.*)", re.I)

    def flush():
        nonlocal art_num, art_title, art_lines
        if art_num is None or not art_lines:
            return

        content = "\n".join(art_lines).strip()
        if len(content) < 15:
            return
        if not looks_english(content):
            return
        if is_skipable_title(art_title):
            return

        embed = (
            f"[{short_name}] [{chapter}] [{section}] "
            f"[Article {art_num}: {art_title}] {content}"
        )
        chunks.append({
            "id": f"{law_key}_art_{art_num}",
            "law_key": law_key,
            "law_name": law_name,
            "short_name": short_name,
            "chapter": chapter,
            "section": section,
            "article_number": f"Article {art_num}",
            "article_title": art_title.strip(),
            "content": content,
            "full_citation": f"Article {art_num}, {law_name}",
            "embedding_text": embed,
        })

    for line in raw_text.split("\n"):
        line = line.strip()

        m = re_ch.match(line)
        if m:
            chapter = f"Chapter {m.group(1)}: {m.group(2).strip()}"
            continue

        m = re_sc.match(line)
        if m:
            section = f"Section {m.group(1)}: {m.group(2).strip()}"
            continue

        m = re_ar.match(line)
        if m:
            flush()
            art_num = m.group(1)
            art_title = m.group(2).strip()
            art_lines = []
            continue

        if art_num is not None and line:
            art_lines.append(line)

    flush()
    return chunks


def split_long(chunks, max_words=500):
    out = []
    for c in chunks:
        words = c["content"].split()
        if len(words) <= max_words:
            out.append(c)
            continue

        sents = re.split(r"(?<=\.)\s+", c["content"])
        parts, cur, cur_len = [], [], 0

        for s in sents:
            sl = len(s.split())
            if cur_len + sl > max_words and cur:
                parts.append(" ".join(cur))
                cur, cur_len = [], 0
            cur.append(s)
            cur_len += sl
        if cur:
            parts.append(" ".join(cur))

        for i, pt in enumerate(parts):
            nc = c.copy()
            nc["id"] = f"{c['id']}_p{i+1}"
            nc["content"] = pt
            nc["article_title"] = f"{c['article_title']} (Part {i+1}/{len(parts)})"
            nc["embedding_text"] = (
                f"[{c['short_name']}] [{c['chapter']}] [{c['section']}] "
                f"[{c['article_number']}: {c['article_title']}] {pt}"
            )
            out.append(nc)
    return out


def main():
    print("=" * 60)
    print("🏛️  STEP 2: Chunk into articles")
    print("=" * 60)

    if not os.path.exists(RAW):
        print("❌ Run step 1 first!")
        return

    os.makedirs(OUT, exist_ok=True)
    total = 0

    for fn in sorted(os.listdir(RAW)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(RAW, fn), encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n📋 {data['short_name']}")
        chunks = chunk_law(data["raw_text"], data["law_key"],
                           data["law_name"], data["short_name"])
        print(f"   Articles: {len(chunks)}")

        chunks = split_long(chunks)
        print(f"   After split: {len(chunks)}")

        if chunks:
            avg = sum(len(c["content"].split()) for c in chunks) / len(chunks)
            print(f"   Avg words: {avg:.0f}")
            for c in chunks[:3]:
                print(
                    f"   → {c['article_number']}: {c['content'][:70].replace(chr(10), ' ')}...")

        path = os.path.join(OUT, fn)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        total += len(chunks)
        print(f"   ✅ → {path}")

    print(f"\n{'=' * 60}")
    print(f"📊 Total chunks: {total}")
    print(f"👉 Next: python scripts/03_embed_and_store.py")


if __name__ == "__main__":
    main()
