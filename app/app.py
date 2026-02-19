"""
Rwanda Law RAG - Web Interface
streamlit run app/app.py
"""

from rag_engine import query_law
import streamlit as st
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".."))


st.set_page_config(page_title="Rwanda Law AI",
                   page_icon="⚖️", layout="centered")

# ── Dark theme colors ──
C = dict(
    bg="#0f1117", card="#1e2130", border="#2d3348",
    text="#e2e8f0", text2="#94a3b8", muted="#64748b", heading="#f1f5f9",
    accent="#22c55e",
    input_bg="#1a1d29", input_border="#3b4252",
    tag_bg="#1e2235", tag_border="#2d3348", tag_text="#94a3b8",
    cite_bg="#1e2235", cite_text="#94a3b8",
    warn_bg="#422006", warn_border="#854d0e", warn_title="#fbbf24", warn_body="#fcd34d",
    btn_bg="#3b82f6", btn_text="#ffffff",
    qbtn_text="#94a3b8", qbtn_border="#2d3348", qbtn_hover="#1e2235",
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600;700&family=DM+Sans:wght@400;500;600&display=swap');

/* ── Base ── */
.stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    background-color: {C['bg']} !important;
    color: {C['text']} !important;
}}
.main > div {{ max-width: 820px; margin: 0 auto; }}
#MainMenu, footer, .stDeployButton, div[data-testid="stToolbar"] {{ visibility: hidden; display: none; }}

/* ── Typography ── */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown strong,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] strong {{
    color: {C['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}

/* ── Header ── */
.header {{ text-align: center; padding: 2rem 0 1.2rem; border-bottom: 1px solid {C['border']}; margin-bottom: 1.5rem; }}
.header h1 {{
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 2rem; font-weight: 700; color: {C['heading']};
    margin: 0 0 0.4rem; letter-spacing: -0.02em;
}}
.header .sub {{ color: {C['text2']}; font-size: 0.9rem; margin: 0 0 1rem; font-family: 'DM Sans', sans-serif; }}
.tags {{ display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }}
.tag {{
    font-family: 'DM Sans', sans-serif; font-size: 0.72rem; font-weight: 500;
    padding: 4px 14px; border-radius: 20px;
    border: 1px solid {C['tag_border']}; color: {C['tag_text']}; background: {C['tag_bg']};
}}

/* ── Inputs ── */
textarea, input, [data-testid="stTextArea"] textarea {{
    background-color: {C['input_bg']} !important; color: {C['text']} !important;
    border: 1px solid {C['input_border']} !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    outline: none !important; box-shadow: none !important;
}}
textarea:focus, [data-testid="stTextArea"] textarea:focus {{
    border-color: {C['input_border']} !important;
    outline: none !important; box-shadow: none !important;
}}
textarea::placeholder {{ color: {C['muted']} !important; }}
[data-baseweb="textarea"], [data-baseweb="textarea"]:focus-within,
div[data-baseweb="textarea"] {{
    border-color: {C['input_border']} !important; box-shadow: none !important;
}}

/* ── Select ── */
[data-baseweb="select"], [data-baseweb="select"] > div,
[data-baseweb="select"] > div > div, [data-baseweb="select"] span {{
    background-color: {C['input_bg']} !important;
    color: {C['text']} !important;
    border-color: {C['input_border']} !important;
}}
[data-baseweb="select"] svg {{ fill: {C['text2']} !important; }}
[data-baseweb="popover"] > div, [data-baseweb="menu"], [role="listbox"] {{
    background-color: {C['card']} !important; border: 1px solid {C['border']} !important;
}}
[role="option"] {{ color: {C['text']} !important; background: {C['card']} !important; }}
[role="option"]:hover {{ background: {C['tag_bg']} !important; }}

/* ── Search button ── */
.search-btn .stButton > button,
.search-btn .stButton > button p {{
    background: {C['btn_bg']} !important; color: {C['btn_text']} !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.92rem !important;
    letter-spacing: 0.01em;
}}
.search-btn .stButton > button:hover {{
    opacity: 0.9;
}}

/* ── Example buttons ── */
.q-btn .stButton > button {{
    background: transparent !important; color: {C['qbtn_text']} !important;
    border: 1px solid {C['qbtn_border']} !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important; font-size: 0.84rem !important;
    text-align: left !important; padding: 10px 16px !important;
}}
.q-btn .stButton > button p {{ color: {C['qbtn_text']} !important; }}
.q-btn .stButton > button:hover {{
    background: {C['qbtn_hover']} !important;
    border-color: {C['text2']} !important;
}}

/* ── Answer ── */
.answer-card {{
    background: {C['card']}; border: 1px solid {C['border']};
    border-radius: 10px; padding: 22px 26px; margin: 18px 0;
}}
.answer-card p, .answer-card li, .answer-card span, .answer-card em {{
    color: {C['text']} !important; font-size: 0.95rem; line-height: 1.7;
    font-family: 'DM Sans', sans-serif;
}}
.answer-card strong {{ color: {C['heading']} !important; }}
.answer-label {{
    font-family: 'DM Sans', sans-serif; font-size: 0.68rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em; color: {C['accent']}; margin-bottom: 12px;
}}

/* ── Not covered ── */
.not-covered {{
    background: {C['warn_bg']}; border: 1px solid {C['warn_border']};
    border-radius: 10px; padding: 24px; margin: 18px 0; text-align: center;
}}
.not-covered .nc-t {{
    font-family: 'DM Sans', sans-serif; font-size: 1rem; font-weight: 600;
    color: {C['warn_title']}; margin-bottom: 8px;
}}
.not-covered .nc-b {{
    font-family: 'DM Sans', sans-serif; font-size: 0.88rem;
    color: {C['warn_body']}; line-height: 1.6;
}}

/* ── Sources ── */
.src-h {{
    font-family: 'Source Serif 4', Georgia, serif; font-size: 1.1rem;
    font-weight: 600; color: {C['heading']}; margin: 1.8rem 0 0.3rem;
}}
.src-sub {{ font-family: 'DM Sans', sans-serif; font-size: 0.76rem; color: {C['muted']}; margin-bottom: 1rem; }}

/* ── Expanders ── */
[data-testid="stExpander"] {{
    border: 1px solid {C['border']} !important; border-radius: 8px !important;
    margin-bottom: 8px !important; background: {C['card']} !important;
}}
[data-testid="stExpander"] summary {{ background: {C['card']} !important; }}
[data-testid="stExpander"] summary span, [data-testid="stExpander"] summary p {{
    color: {C['text']} !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important;
}}
[data-testid="stExpander"] svg {{ fill: {C['text2']} !important; }}
[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{ background: {C['card']} !important; }}

.meta-row {{ font-family: 'DM Sans', sans-serif; font-size: 0.82rem; color: {C['text2']}; padding: 3px 0; }}
.meta-label {{ font-weight: 600; color: {C['text']}; }}
.meta-cite {{
    font-family: 'DM Sans', sans-serif; font-size: 0.8rem; background: {C['cite_bg']};
    padding: 6px 12px; border-radius: 6px; color: {C['cite_text']};
    margin: 8px 0 14px; display: inline-block; border: 1px solid {C['border']};
}}
.art-body {{
    font-family: 'Source Serif 4', Georgia, serif; font-size: 0.9rem;
    line-height: 1.7; color: {C['text']}; padding-top: 12px;
    border-top: 1px solid {C['border']}; margin-top: 4px;
}}

/* ── Footer ── */
.disc {{
    font-family: 'DM Sans', sans-serif; font-size: 0.8rem; color: {C['warn_body']};
    background: {C['warn_bg']}; border: 1px solid {C['warn_border']};
    border-radius: 8px; padding: 14px 18px; margin-top: 2rem; line-height: 1.5;
}}
.foot {{
    text-align: center; padding: 1.2rem 0 0.5rem;
    border-top: 1px solid {C['border']}; margin-top: 1.5rem;
}}
.foot p {{ font-family: 'DM Sans', sans-serif; font-size: 0.72rem; color: {C['muted']}; margin: 2px 0; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──

def clean_ch(raw):
    if not raw:
        return ""
    c = re.sub(r"^Chapter\s+[IVXLCDM\d]+\s*:\s*", "", raw, flags=re.I).strip()
    for f in ["Chapitre", "Infractions", "Dispositions", "Sous-section", "d'ordre", "d'entrave"]:
        if f.lower() in c.lower():
            return ""
    return c


def clean_sc(raw):
    if not raw:
        return ""
    c = re.sub(r"^Section\s+\w+\s*:\s*", "", raw, flags=re.I).strip()
    for f in ["infractions", "première", "premiere", "dispositions", "d'entrave", "d'ordre", "contre", "l'action", "portant"]:
        if f in c.lower():
            return ""
    return c


def is_not_covered(txt):
    lo = txt.lower()
    return any(x in lo for x in [
        "not covered", "not fully covered", "not addressed", "does not cover",
        "consult a legal professional", "outside the scope", "beyond the scope",
    ])


# ── Header ──

st.markdown(f"""
<div class="header">
    <h1>Rwanda Law RAG</h1>
    <p class="sub">Legal information with article-level citations</p>
    <div class="tags">
        <span class="tag">Constitution (2015)</span>
        <span class="tag">Penal Code (2018)</span>
        <span class="tag">Labor Law (2018)</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Controls ──

fmap = {"All Laws": "all", "Constitution": "constitution",
        "Penal Code": "penal_code", "Labor Law": "labor_law"}
law_filter = fmap[st.selectbox(
    "Filter", list(fmap), label_visibility="collapsed")]

q = st.text_area("q", placeholder="Describe your situation or ask a legal question...",
                 height=80, label_visibility="collapsed")

st.markdown('<div class="search-btn">', unsafe_allow_html=True)
go = st.button("Search", use_container_width=True, key="search_main")
st.markdown('</div>', unsafe_allow_html=True)


# ── Examples ──

if not q or not go:
    if "auto_q" not in st.session_state:
        st.markdown("**Common questions:**")
        for ex in [
            "What are my rights if I am arrested?",
            "What is the penalty for theft in Rwanda?",
            "Can my employer terminate my contract without notice?",
            "What does the Constitution say about freedom of expression?",
            "My employer fired me and refused to pay my last salary",
            "What protections exist for children in the workplace?",
        ]:

            if st.button(ex, key=ex):
                st.session_state["auto_q"] = ex
                st.rerun()


if "auto_q" in st.session_state:
    q = st.session_state.pop("auto_q")
    go = True


# ── Results ──

if q and go:
    with st.spinner("Searching..."):
        result = query_law(q.strip(), law_filter)
    answer = result["answer"]

    if is_not_covered(answer):
        st.markdown("""
        <div class="not-covered">
            <div class="nc-t">Not found in current database</div>
            <div class="nc-b">
                Your question is not covered by the laws currently available
                (Constitution, Penal Code, Labor Law).<br><br>
                Try rephrasing with specific legal terms, or consult a qualified legal professional.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
        st.markdown('<div class="answer-label">Answer</div>',
                    unsafe_allow_html=True)
        st.markdown(answer)
        st.markdown('</div>', unsafe_allow_html=True)

        if result["cited_articles"]:
            st.markdown('<p class="src-h">Source Articles</p>',
                        unsafe_allow_html=True)
            st.markdown(
                '<p class="src-sub">Expand to read the full legal text</p>', unsafe_allow_html=True)

            for art in result["cited_articles"]:
                m = art["metadata"]
                ch = clean_ch(m.get("chapter", ""))
                sc = clean_sc(m.get("section", ""))
                ti = m.get("article_title", "")
                label = f"{m['article_number']}  |  {m['short_name']}"
                if ti:
                    label += f"  |  {ti[:55]}"

                with st.expander(label):
                    html = ""
                    if ch:
                        html += f'<div class="meta-row"><span class="meta-label">Chapter:</span> {ch}</div>'
                    if sc:
                        html += f'<div class="meta-row"><span class="meta-label">Section:</span> {sc}</div>'
                    html += f'<div class="meta-cite">{m["full_citation"]}</div>'
                    st.markdown(html, unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="art-body">{art["content"]}</div>', unsafe_allow_html=True)


# ── Footer ──

st.markdown("""
<div class="disc">
    This tool provides legal information, not legal advice.
    Always consult a qualified lawyer for specific legal matters.
</div>
<div class="foot">
    <p>Knowledge base: Constitution of Rwanda (2015), Penal Code (2018), Labor Law (2018)</p>
    <p>Rwanda Law RAG</p>
</div>
""", unsafe_allow_html=True)
