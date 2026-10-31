from __future__ import annotations

import re

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Mini Compiler Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_CODE = '''#include <stdio.h>
int main() {
    int a = 10;
    int b = 20;
    int sum = a + b;
    printf("%d\\n", sum);
    return 0;
}'''

KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "int", "long", "register", "return", "short", "signed", "sizeof",
    "static", "struct", "switch", "typedef", "union", "unsigned", "void",
    "volatile", "while", "include", "define", "stdio", "h", "main",
    "printf", "scanf"
}

OPERATORS = {"=", "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||", "!", "&", "|"}


def tokenize_code(code: str):
    tokens = []
    for line_number, line in enumerate((code or "").splitlines(), start=1):
        for match in re.finditer(r'"(?:\\.|[^"\\])*"|\b[a-zA-Z_]\w*\b|\d+|==|!=|<=|>=|&&|\|\||[=+\-*/%<>(){};!&|,\[\].]','', line):
            token = match.group(0)
            if not token.strip():
                continue
            if token in KEYWORDS:
                token_type = "keyword"
            elif re.fullmatch(r"[A-Za-z_]\w*", token):
                token_type = "identifier"
            elif re.fullmatch(r"\d+", token):
                token_type = "number"
            elif token.startswith('"') or token.startswith("'"):
                token_type = "string"
            elif token in OPERATORS:
                token_type = "operator"
            elif token in {";", "(", ")", "{", "}", "[", "]", ",", "."}:
                token_type = "symbol"
            else:
                token_type = "other"
            tokens.append({"token": token, "type": token_type, "line": line_number})
    return tokens


def analyze_code(code: str):
    text = (code or "").strip()
    if not text:
        return {
            "status": "No input",
            "summary": "Waiting for code input.",
            "issues": ["Please paste or upload C code to check."],
            "tokens": [],
            "confidence": 0,
        }

    issues = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.endswith("{") or stripped.endswith("}"):
            continue
        if re.fullmatch(r"(?:if|for|while|else|switch|do)\b.*", stripped):
            continue
        if stripped.startswith("return "):
            continue
        if stripped.endswith(";"):
            continue
        if stripped.endswith(")") and "printf" in stripped:
            continue
        if stripped.endswith(")") and "scanf" in stripped:
            continue
        issues.append(f"Line {idx}: Missing semicolon or statement terminator.")

    if re.search(r"\b[0-9][A-Za-z_][A-Za-z0-9_]*\b", text):
        issues.append("Invalid identifier format detected.")

    if "main" not in text:
        issues.append("Missing main() function — required for a C program entry point.")

    if "main" in text and "return 0;" not in text:
        issues.append("main() should return a value, usually return 0;.")

    if "printf" in text.lower() and "(" not in text:
        issues.append("printf is being used without parentheses.")

    if "for(" in text.lower() or "while(" in text.lower():
        issues.append("Loop condition should be reviewed for valid syntax and braces.")

    tokens = tokenize_code(text)
    quality_score = max(0, 100 - (len(issues) * 18))

    if not issues:
        return {
            "status": "Healthy",
            "summary": "Code looks structurally valid and ready to compile.",
            "issues": ["No syntax issues detected in the current sample."],
            "tokens": tokens,
            "confidence": quality_score,
        }

    return {
        "status": "Needs attention",
        "summary": "The compiler found a few issues that should be reviewed.",
        "issues": issues,
        "tokens": tokens,
        "confidence": quality_score,
    }


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #f5f7ff 0%, #edf4ff 100%);
            font-family: 'Inter', sans-serif;
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .topbar {
            background: rgba(17, 24, 39, 0.96);
            border-radius: 22px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
            margin-bottom: 1.25rem;
            color: white;
        }

        .brand-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .brand-wrap {
            display: flex;
            align-items: center;
            gap: 0.9rem;
        }

        .brand-mark {
            width: 3rem;
            height: 3rem;
            border-radius: 16px;
            display: grid;
            place-items: center;
            font-weight: 800;
            font-size: 1.2rem;
            background: linear-gradient(135deg, #4f8cff, #7f5af0);
            color: white;
            box-shadow: 0 12px 26px rgba(79, 140, 255, 0.35);
        }

        .eyebrow {
            margin: 0;
            color: #9bb7ff;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .title {
            margin: 0.2rem 0 0 0;
            font-size: clamp(1.6rem, 2vw, 2.3rem);
            font-weight: 800;
        }

        .subtitle {
            margin: 0;
            color: #dfeafe;
            font-size: 0.95rem;
        }

        .summary-card, .panel-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 20px;
            padding: 1.1rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.04);
            backdrop-filter: blur(8px);
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            background: #eaf7ee;
            color: #0c8b4f;
        }

        .metric-box {
            background: linear-gradient(135deg, #eff6ff, #ffffff);
            border: 1px solid #dbeafe;
            border-radius: 18px;
            padding: 1rem;
            height: 100%;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 0.4rem;
        }

        .highlight-box {
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: linear-gradient(135deg, #f8fafc, #eef6ff);
            border: 1px solid #dfeafe;
        }

        .stTextArea textarea,
        .stSelectbox > div,
        .stDataFrame,
        .stButton > button {
            border-radius: 16px !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            color: white;
            border: none;
            font-weight: 700;
            padding: 0.65rem 1rem;
            box-shadow: 0 14px 24px rgba(37, 99, 235, 0.25);
        }

        .stButton > button:hover {
            filter: brightness(1.05);
        }

        div[data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.96);
            color: white;
        }

        div[data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #38bdf8, #2563eb);
            box-shadow: none;
        }

        h3 {
            margin-top: 0;
        }

        .token-table {
            border-radius: 14px;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "source_code" not in st.session_state:
    st.session_state.source_code = DEFAULT_CODE

st.markdown(
    """
    <div class="topbar">
        <div class="brand-row">
            <div class="brand-wrap">
                <div class="brand-mark">C</div>
                <div>
                    <p class="eyebrow">Compiler Design Lab</p>
                    <h1 class="title">Mini Compiler Dashboard</h1>
                </div>
            </div>
            <p class="subtitle">Linting, token checks, and issue detection for C code.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Compiler Console")
    st.caption("Paste, upload, and validate C source code in real time.")

    if st.button("Load sample", use_container_width=True):
        st.session_state.source_code = DEFAULT_CODE

    if st.button("Clear editor", use_container_width=True):
        st.session_state.source_code = ""

    uploaded_file = st.file_uploader("Upload a .c file", type=["c"], help="Choose a C source file to inspect.")
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.session_state.source_code = text

    source_code = st.text_area("C source code", key="source_code", height=360)

    if st.button("Analyze code", use_container_width=True):
        st.session_state.result = analyze_code(source_code)

    if "result" not in st.session_state:
        st.session_state.result = analyze_code(source_code)

st.subheader("Project overview")
intro_col, status_col = st.columns([2, 1])
with intro_col:
    st.markdown(
        """
        <div class="summary-card">
            <p style="margin: 0 0 0.5rem; color: #475569; font-weight: 600;">Overview</p>
            <div style="font-size: 1.05rem; line-height: 1.7; color: #0f172a;">
                This project is designed to review C programs for common lexical and syntax issues,
                give users a more polished dashboard experience, and highlight problems in a simple,
                readable format for students and developers.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with status_col:
    result = st.session_state.result
    st.markdown(
        f"""
        <div class="summary-card">
            <p style="margin: 0 0 0.5rem; color: #475569; font-weight: 600;">Status</p>
            <div class="status-pill">{result['status']}</div>
            <div style="margin-top: 0.8rem; font-size: 1.2rem; font-weight: 700; color: #0f172a;">{result['confidence']}% confidence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-label">Tokens</div>
            <div class="metric-value">0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col2:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-label">Issues</div>
            <div class="metric-value">0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric_col3:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-label">Health</div>
            <div class="metric-value">-</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

result = st.session_state.result
analysis_tokens = result["tokens"]
issue_count = len(result["issues"])

token_df = pd.DataFrame(analysis_tokens)[["token", "type", "line"]]
if token_df.empty:
    token_df = pd.DataFrame(columns=["token", "type", "line"])

st.markdown("### Quick analysis")
left_panel, right_panel = st.columns([1.7, 1])

with left_panel:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.write(result["summary"])
    st.table(token_df.head(20))
    st.markdown("</div>", unsafe_allow_html=True)

with right_panel:
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.write("### Analysis result")
    for item in result["issues"]:
        st.markdown(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("### Source preview")
st.code(source_code if source_code else "// Waiting for source input...", language="c")

st.markdown("### Additional notes")
st.markdown(
    """
    - LEX/FLEX handles token generation for keywords and identifiers.
    - YACC/Bison validates grammatical structure for valid C programs.
    - The interface is designed to be clearer, cleaner, and more user-friendly for lab demos.
    """
)

# Inject the final metric values after we know the result.
metric_html = f"""
<script>
    const cards = document.querySelectorAll('.metric-value');
    if (cards.length >= 3) {{
        cards[0].textContent = '{len(analysis_tokens)}';
        cards[1].textContent = '{issue_count}';
        cards[2].textContent = '{result["status"]}';
    }}
</script>
"""

st.markdown(metric_html, unsafe_allow_html=True)
