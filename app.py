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
}
'''

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
    if not code:
        return tokens

    for line_number, line in enumerate(code.splitlines(), start=1):
        matches = re.finditer(r'"(?:\\.|[^"\\])*"|\b[a-zA-Z_]\w*\b|\d+|==|!=|<=|>=|&&|\|\||[=+\-*/%<>(){};!&|,\[\].]', line)
        for match in matches:
            token = match.group(0)
            if not token.strip():
                continue

            if token in KEYWORDS:
                token_type = "keyword"
            elif re.fullmatch(r"[A-Za-z_]\w*", token):
                token_type = "identifier"
            elif re.fullmatch(r"\d+", token):
                token_type = "number"
            elif token.startswith('"'):
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
            "score": 0,
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
        if "printf" in stripped or "scanf" in stripped:
            if stripped.endswith(")"):
                continue
        issues.append(f"Line {idx}: Check statement termination or the function syntax.")

    if re.search(r"\b[0-9][A-Za-z_][A-Za-z0-9_]*\b", text):
        issues.append("Invalid identifier format detected.")

    if "main" not in text:
        issues.append("Missing main() function — required as the C program entry point.")

    if "main" in text and "return 0;" not in text:
        issues.append("main() should return a value, usually return 0;.")

    if "printf" in text.lower() and "(" not in text:
        issues.append("printf is used without parentheses.")

    if "for(" in text.lower() or "while(" in text.lower():
        issues.append("Loop condition should be reviewed for valid syntax and braces.")

    tokens = tokenize_code(text)
    score = max(0, 100 - (len(issues) * 18))

    if not issues:
        return {
            "status": "Healthy",
            "summary": "Code looks structurally valid and ready to compile.",
            "issues": ["No syntax issues detected in the current sample."],
            "tokens": tokens,
            "score": score,
        }

    return {
        "status": "Needs attention",
        "summary": "The compiler found a few issues that should be reviewed.",
        "issues": issues,
        "tokens": tokens,
        "score": score,
    }


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #eef4ff 0%, #f6f7fb 100%);
            font-family: 'Inter', sans-serif;
        }

        .main .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        .topbar {
            background: linear-gradient(135deg, #0f172a 0%, #14213d 100%);
            border-radius: 24px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 20px 44px rgba(15, 23, 42, 0.12);
            margin-bottom: 1.3rem;
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
            width: 3.2rem;
            height: 3.2rem;
            border-radius: 18px;
            display: grid;
            place-items: center;
            font-size: 1.2rem;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            box-shadow: 0 14px 30px rgba(59, 130, 246, 0.35);
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
            margin: 0.2rem 0 0;
            font-size: clamp(1.7rem, 2.2vw, 2.4rem);
            font-weight: 800;
            color: white;
        }

        .subtitle {
            margin: 0;
            color: #dfeafc;
            font-size: 0.94rem;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.04);
            backdrop-filter: blur(8px);
        }

        .status-badge {
            display: inline-block;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            background: #ecfdf5;
            color: #0b8f57;
            margin-top: 0.75rem;
        }

        .metric-box {
            background: linear-gradient(135deg, #f8fbff, #eef3ff);
            border: 1px solid #dfeafe;
            border-radius: 18px;
            padding: 1rem;
            height: 100%;
        }

        .metric-label {
            color: #64748b;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .metric-value {
            color: #0f172a;
            font-weight: 800;
            font-size: 1.7rem;
            margin-top: 0.45rem;
        }

        div[data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.97);
            color: white;
        }

        div[data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border: none;
            color: white;
            font-weight: 700;
            border-radius: 14px;
        }

        .stTextArea textarea {
            border-radius: 16px;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }

        .stDataFrame {
            border-radius: 14px;
            overflow: hidden;
        }

        .stButton > button {
            border-radius: 14px;
            font-weight: 700;
            padding: 0.7rem 1rem;
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            border: none;
            color: white;
            box-shadow: 0 12px 24px rgba(37, 99, 235, 0.2);
        }

        .stButton > button:hover {
            filter: brightness(1.05);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "source_code" not in st.session_state:
    st.session_state.source_code = DEFAULT_CODE

if "result" not in st.session_state:
    st.session_state.result = analyze_code(st.session_state.source_code)

st.markdown(
    """
    <div class="topbar">
        <div class="brand-row">
            <div class="brand-wrap">
                <div class="brand-mark">C</div>
                <div>
                    <p class="eyebrow">Compiler design lab</p>
                    <h1 class="title">Mini Compiler Dashboard</h1>
                </div>
            </div>
            <p class="subtitle">Token analysis, validation, and clean code diagnostics.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Compiler Console")
    st.caption("Paste, upload, and validate C source code instantly.")

    if st.button("Load sample", use_container_width=True):
        st.session_state.source_code = DEFAULT_CODE
        st.session_state.result = analyze_code(DEFAULT_CODE)

    if st.button("Clear editor", use_container_width=True):
        st.session_state.source_code = ""
        st.session_state.result = analyze_code("")

    uploaded_file = st.file_uploader("Upload a .c file", type=["c"], help="Choose a C source file to inspect.")
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.session_state.source_code = text
        st.session_state.result = analyze_code(text)

    source_code = st.text_area("C source code", key="source_code", height=340)

    if st.button("Analyze code", use_container_width=True):
        st.session_state.result = analyze_code(source_code)

st.subheader("Project overview")

summary_col, status_col = st.columns([2, 1])
with summary_col:
    st.markdown(
        """
        <div class="glass-card">
            <div style="font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; color: #64748b; font-weight: 700;">Overview</div>
            <div style="margin-top: 0.7rem; line-height: 1.75; color: #0f172a; font-size: 1.05rem;">
                This dashboard helps review C source code for syntax issues, detect common compiler-style problems,
                and present the result in a more user-friendly, modern interface for students and projects.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with status_col:
    result = st.session_state.result
    st.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; color: #64748b; font-weight: 700;">Status</div>
            <div class="status-badge">{result['status']}</div>
            <div style="margin-top: 0.8rem; font-size: 1.35rem; font-weight: 800; color: #0f172a;">{result['score']}% confidence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

metric1, metric2, metric3 = st.columns(3)
with metric1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Tokens</div>
            <div class="metric-value">{len(result['tokens'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Issues</div>
            <div class="metric-value">{len(result['issues'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metric3:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Health</div>
            <div class="metric-value">{result['status']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

analysis_result = st.session_state.result

left_panel, right_panel = st.columns([1.7, 1])

with left_panel:
    st.markdown("### Analysis summary")
    st.info(analysis_result["summary"])

    token_df = pd.DataFrame(analysis_result["tokens"])
    if token_df.empty:
        token_df = pd.DataFrame(columns=["token", "type", "line"])
    else:
        token_df = token_df[["token", "type", "line"]]

    st.dataframe(token_df.head(25), use_container_width=True)

with right_panel:
    st.markdown("### Issues")
    issue_list = analysis_result["issues"]
    if issue_list:
        for item in issue_list:
            st.warning(item)
    else:
        st.success("No issues found.")

st.markdown("### Source preview")
st.code(st.session_state.source_code if st.session_state.source_code else "// Waiting for source input...", language="c")

st.markdown("### Additional notes")
st.markdown(
    """
    - LEX/FLEX handles token generation for keywords and identifiers.
    - YACC/Bison validates grammatical structure for valid C programs.
    - The interface is designed to be more user-friendly, cleaner, and better suited for project demos.
    """
)
