"""
==========================================================
STEP 4 - Test the full RAG pipeline
==========================================================

Runs real questions and shows answers + cited articles.
Verify answers make sense before launching the web app.

RUN:  python scripts/04_test_rag.py
==========================================================
"""

from app.rag_engine import query_law, search
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("=" * 60)
    print("🏛️  STEP 4: Test RAG Pipeline")
    print("=" * 60)

    tests = [
        {
            "q": "What are my rights if I am arrested?",
            "f": "all",
            "why": "Should cite Constitution articles on rights of accused",
        },
        {
            "q": "What is the penalty for theft in Rwanda?",
            "f": "penal_code",
            "why": "Should cite Penal Code with specific penalties",
        },
        {
            "q": "Can my employer terminate my contract without notice?",
            "f": "labor_law",
            "why": "Should cite Labor Law on termination + notice periods",
        },
        {
            "q": "My boss fired me and refused to pay my last salary",
            "f": "all",
            "why": "CROSS-LAW - should pull from Labor Law (termination + wages) and maybe Constitution",
        },
        {
            "q": "How to make a chocolate cake?",
            "f": "all",
            "why": "NOT IN LAW - should say 'not covered', proving no hallucination",
        },
    ]

    for i, t in enumerate(tests, 1):
        print(f"\n{'━' * 60}")
        print(f"TEST {i}: {t['q']}")
        print(f"Filter: {t['f']} | Expect: {t['why']}")
        print(f"{'━' * 60}")

        result = query_law(t["q"], t["f"])

        # Answer (truncated)
        ans = result["answer"]
        if len(ans) > 500:
            ans = ans[:500] + "\n..."
        print(f"\n📝 ANSWER:\n{ans}")

        # Sources
        print(f"\n📎 SOURCES:")
        for a in result["cited_articles"]:
            m = a["metadata"]
            print(
                f"   • {m['article_number']} ({m['short_name']}) - {m['article_title'][:50]}")

    print(f"\n{'=' * 60}")
    print(f"✅ All tests done!")
    print(f"\n🚀 Launch web app:  streamlit run app/app.py")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
