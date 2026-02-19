"""
==========================================================
STEP 1 - Extract English text from your 3 law PDFs
==========================================================

Constitution:  full English → extract everything
Penal Code:    3 columns (Kinyarwanda | ENGLISH | French) → middle column only
Labor Law:     3 columns (Kinyarwanda | ENGLISH | French) → middle column only

RUN:  python scripts/01_extract_pdf.py
==========================================================
"""

import fitz  # PyMuPDF
import json
import os
import re

PDF_DIR = "data/pdfs"
OUT_DIR = "data/raw_text"

LAWS = {
    "constitution": {
        "file": "constitution.pdf",
        "name": "Constitution of the Republic of Rwanda of 2003, Revised in 2015",
        "short": "Constitution",
        "layout": "single",
    },
    "penal_code": {
        "file": "penal_code.pdf",
        "name": "Law Nº 68/2018 of 30/08/2018 Determining Offences and Penalties in General",
        "short": "Penal Code",
        "layout": "three_column",
    },
    "labor_law": {
        "file": "labor_law.pdf",
        "name": "Law Nº 66/2018 of 30/08/2018 Regulating Labour in Rwanda",
        "short": "Labor Law",
        "layout": "three_column",
    },
}


def middle_column(page):
    """Extract ONLY the middle third (English) from a 3-column page."""
    w = page.rect.width
    h = page.rect.height
    # margins to avoid bleed from neighboring columns
    # ↑ increase to 10-15 if you see French/Kinyarwanda leaking in
    margin = 8
    clip = fitz.Rect(w / 3 + margin, 0, 2 * w / 3 - margin, h)
    return page.get_text("text", clip=clip).strip()


def full_page(page):
    """Extract all text from a single-language page."""
    return page.get_text("text").strip()


def clean(text):
    text = re.sub(r"Official Gazette.*?\d{4}\s*\d*", "", text, flags=re.I)
    text = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def is_toc_or_preamble(text):
    """
    Detect Table of Contents / Preamble pages to SKIP.
    These don't contain actionable legal content.
    """
    lower = text.lower()
    # TOC indicators
    if "table of contents" in lower or "ishakiro" in lower or "table des matières" in lower:
        return True
    # Page is mostly dots/periods (TOC formatting)
    if text.count(".") > 50 and text.count("Article") < 2:
        return True
    return False


def process(key, info):
    path = os.path.join(PDF_DIR, info["file"])
    if not os.path.exists(path):
        print(f"  ⚠️  MISSING: {path}")
        return None

    doc = fitz.open(path)
    extract = middle_column if info["layout"] == "three_column" else full_page

    print(f"  📄 {info['short']}: {len(doc)} pages [{info['layout']}]")

    all_text = ""
    pages = []
    skipped = 0

    for i in range(len(doc)):
        raw = extract(doc[i])
        txt = clean(raw)

        if not txt:
            continue

        # Skip TOC and preamble pages
        if is_toc_or_preamble(txt):
            skipped += 1
            continue

        all_text += txt + "\n\n"
        pages.append({"page": i + 1, "text": txt})

    doc.close()

    arts = len(re.findall(r"Article\s+\d+", all_text, re.I))
    print(
        f"  📊 {len(all_text):,} chars | {arts} articles | {skipped} TOC/preamble pages skipped")
    print(f"  📝 Preview: {all_text[:120].replace(chr(10), ' ')}...")

    return {
        "law_key": key,
        "law_name": info["name"],
        "short_name": info["short"],
        "total_pages": len(pages),
        "article_count": arts,
        "raw_text": all_text,
    }


def main():
    print("=" * 60)
    print("🏛️  STEP 1: PDF → English text")
    print("=" * 60)

    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    for k, v in LAWS.items():
        p = os.path.join(PDF_DIR, v["file"])
        print(f"  {'✅' if os.path.exists(p) else '❌'} {v['file']}")

    total = 0
    for k, v in LAWS.items():
        print(f"\n{'─' * 50}")
        r = process(k, v)
        if r:
            out = os.path.join(OUT_DIR, f"{k}.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(r, f, ensure_ascii=False, indent=2)
            total += r["article_count"]
            print(f"  ✅ → {out}")

    print(f"\n{'=' * 60}")
    print(f"📊 Total articles: {total}")
    print(f"👉 Next: python scripts/02_chunk_text.py")


if __name__ == "__main__":
    main()
