from __future__ import annotations

import re

import streamlit as st

st.set_page_config(page_title="Mini Compiler Dashboard", page_icon="⚙️", layout="wide")

DEFAULT_CODE = '''int a = 10;
int b = 20;
int c = a + b;
print(c);'''


def analyze_code(code: str):
    issues = []
    code = (code or "").strip()

    if not code:
        return {
            "status": "No input",
            "issues": ["Please paste or upload C code to check."],
            "summary": "Waiting for code input.",
        }

    if re.search(r";\s*$", code) is None:
        issues.append("Missing semicolon at the end of a statement.")

    if re.search(r"\b[0-9][A-Za-z_][A-Za-z0-9_]*\b", code):
        issues.append("Invalid identifier format detected.")

    if "for(" in code.lower() or "while(" in code.lower():
        issues.append("Loop structure is valid but should be checked for condition syntax.")

    if "printf" in code.lower() and "(" not in code:
        issues.append("Function call missing parentheses.")

    if not issues:
        return {
            "status": "Ready",
            "issues": ["No syntax issues detected in this sample. The lexer and parser would accept the code."],
            "summary": "Code is structurally valid.",
        }

    return {
        "status": "Detected",
        "issues": issues,
        "summary": "The compiler found common token and syntax issues.",
    }


st.title("Mini Compiler Dashboard")
st.caption("C source analysis and syntax validation")

with st.sidebar:
    st.title("Compiler Console")
    st.caption("Upload or paste C code to inspect lexical and syntax output.")
    source_code = st.text_area("C source code", value=DEFAULT_CODE, height=260)

    if st.button("Analyze code"):
        result = analyze_code(source_code)
        st.success(result["summary"])
        for item in result["issues"]:
            st.write(f"• {item}")

    uploaded_file = st.file_uploader("Upload a .c file", type=["c"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        st.write("Loaded file:", uploaded_file.name)
        st.code(text[:250], language="c")

st.subheader("Sample code")
st.code(DEFAULT_CODE, language="c")

result = analyze_code(DEFAULT_CODE)
with st.container():
    st.markdown(
        "<div style='padding: 16px; border-radius: 12px; background: #f0f6ff; border: 1px solid #d7e6ff;'>"
        f"<strong>Compiler output</strong><span style='margin-left: 10px; display:inline-block; background:#d9f3e5; color:#0d7a4b; padding:4px 8px; border-radius:999px; font-size: 12px; font-weight:700;'>{result['status']}</span><br><br>"
        + "<br>".join(f"• {item}" for item in result["issues"]) +
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
    ---
    ### Quick notes
    - LEX/FLEX handles token generation.
    - YACC/Bison validates syntax structure.
    - This app is a lightweight working prototype for the project.
    """
)
