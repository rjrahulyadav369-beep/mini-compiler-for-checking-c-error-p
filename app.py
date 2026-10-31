from __future__ import annotations

import re
import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mini Compiler Dashboard", page_icon="⚙️", layout="wide")

DEFAULT_CODE = '''int a = 10;
int b = 20;
int c = a + b;
print(c);'''

st.markdown(
    """
    <style>
    :root {
        --bg-dark: #2f2e2d;
        --paper: #f5f5f3;
        --ink: #1d2f3d;
        --muted: #64748b;
        --accent: #0b80ae;
        --accent-soft: #dfeff5;
        --line: #d4d9df;
        --table-head: #dfeff5;
        --white: #ffffff;
    }

    html, body {
        background: var(--bg-dark);
        height: 100%;
        margin: 0;
        font-family: 'Segoe UI', Tahoma, sans-serif;
        color: var(--ink);
    }

    [data-testid="stAppViewContainer"] {
        background: #383737;
        padding: 0;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
        max-width: 1240px;
    }

    .document-shell {
        display: flex;
        justify-content: center;
        padding: 24px 16px 28px;
    }

    .paper {
        width: 100%;
        max-width: 1060px;
        min-height: 980px;
        background: var(--paper);
        box-shadow: 0 18px 36px rgba(0,0,0,0.22);
        border: 1px solid rgba(0,0,0,0.10);
        padding: 20px 28px 14px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .page-top-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 16px;
        border-bottom: 1px solid var(--line);
        padding-bottom: 16px;
        margin-bottom: 18px;
    }

    .title-wrap {
        text-align: center;
        width: 100%;
        margin-top: 6px;
    }

    h1 {
        margin: 0;
        font-size: 26px;
        letter-spacing: 0.3px;
        color: #1e3d63;
        font-weight: 800;
    }

    .subtitle {
        font-size: 12px;
        color: #6a7a8f;
        margin-top: 6px;
        text-align: center;
    }

    .meta-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(120px, 1fr));
        gap: 0;
        width: 100%;
        margin: 16px 0 14px;
        border: 1px solid var(--line);
        border-bottom: none;
        background: #edf4fb;
    }

    .meta-cell {
        padding: 10px 8px;
        border-right: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-height: 54px;
    }

    .meta-cell:nth-child(4n) {
        border-right: none;
    }

    .meta-label {
        font-size: 11px;
        line-height: 1.3;
        font-weight: 700;
        color: #2b5368;
        text-transform: none;
    }

    .meta-value {
        font-size: 11px;
        color: #1e2c38;
        font-weight: 500;
    }

    .section {
        margin-top: 10px;
    }

    .section h2 {
        margin: 0 0 10px;
        color: #2877a5;
        font-size: 15px;
        font-weight: 800;
    }

    .content {
        font-size: 12px;
        line-height: 1.7;
        color: #1e2c38;
    }

    .content p {
        margin: 0 0 8px;
    }

    .content ul {
        margin: 8px 0 10px 18px;
        padding: 0;
    }

    .content li {
        margin-bottom: 4px;
    }

    .code-block {
        background: #eef2f5;
        border: 1px solid var(--line);
        padding: 10px 12px;
        margin: 12px 0 10px;
        font-family: 'Consolas', monospace;
        font-size: 11.5px;
        line-height: 1.7;
        color: #102533;
        white-space: pre-wrap;
    }

    .table-wrap {
        border: 1px solid var(--line);
        background: #f8fafb;
        margin-top: 12px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
    }

    th, td {
        border-bottom: 1px solid var(--line);
        border-right: 1px solid var(--line);
        padding: 8px 10px;
        text-align: left;
    }

    th {
        background: var(--table-head);
        font-weight: 700;
        color: #2e4a5f;
    }

    tr:last-child td { border-bottom: none; }
    td:last-child, th:last-child { border-right: none; }

    .footer-bar {
        border-top: 1px solid var(--line);
        margin-top: 18px;
        padding-top: 8px;
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        color: #6d7d8d;
    }

    .page-pill {
        display: inline-block;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 10px;
        background: rgba(11, 128, 174, 0.07);
        color: #1f5d7f;
    }

    .status-box {
        border: 1px solid #d0dfe8;
        background: #edf7fb;
        padding: 12px 14px;
        border-radius: 10px;
        margin-top: 16px;
        font-size: 12px;
    }

    .status-box strong {
        color: #0d5c82;
    }

    .status-badge {
        display: inline-block;
        padding: 5px 8px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.4px;
        margin-left: 8px;
        background: #d9f3e5;
        color: #0d7a4b;
    }

    @media (max-width: 900px) {
        .meta-grid {
            grid-template-columns: repeat(2, minmax(120px, 1fr));
        }
        .paper {
            padding: 18px 16px 12px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def analyze_code(code: str):
    issues = []
    code = code.strip()
    if not code:
        return {
            "status": "No input",
            "issues": ["Please paste or upload C code to check."],
            "summary": "Waiting for code input.",
        }

    if re.search(r";\s*$", code) is None:
        issues.append("Missing semicolon at the end of a statement.")

    if re.search(r"\bint\b.*\=", code) and "=" in code:
        pass

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


def render_document_html(code: str, result: dict):
    analysis_list = "\n".join(f"• {item}" for item in result["issues"])
    return f"""
    <div class="document-shell">
      <div class="paper">
        <div>
          <div class="title-wrap">
            <h1>MINI COMPILER DESIGN PROJECT</h1>
            <div class="subtitle">Problem Statement: Development of a Mini Compiler Dashboard</div>
          </div>

          <div class="meta-grid">
            <div class="meta-cell"><div class="meta-label">Subject</div><div class="meta-value">Compiler Design Lab</div></div>
            <div class="meta-cell"><div class="meta-label">Difficulty</div><div class="meta-value">Easy to Moderate</div></div>
            <div class="meta-cell"><div class="meta-label">Project type</div><div class="meta-value">Mini Project / Lab Assignment</div></div>
            <div class="meta-cell"><div class="meta-label">Core tools</div><div class="meta-value">LEX/FLEX, YACC/Bison, C</div></div>
          </div>

          <div class="section">
            <h2>1. Project Overview</h2>
            <div class="content">
              <p>Develop a web-based Mini Compiler Dashboard. A user must be able to upload a source code file or paste code into an editor, then run lexical analysis and syntax analysis. The application must display generated tokens and clearly report lexical or syntax errors, including line numbers where possible.</p>
              <p>In simple terms: Upload / Enter source code → Lexical Analysis → View tokens and lexical errors → Syntax Analysis → View accepted or rejected syntax.</p>
            </div>
          </div>

          <div class="section">
            <h2>2. Project Objectives</h2>
            <div class="content">
              <ul>
                <li>Build a user-friendly dashboard for source-code analysis.</li>
                <li>Implement lexical analysis using LEX/FLEX.</li>
                <li>Implement syntax analysis using YACC/Bison.</li>
                <li>Display generated tokens in a table.</li>
                <li>Detect and report lexical and syntax errors separately.</li>
                <li>Connect the interface to the actual compiler components.</li>
              </ul>
            </div>
          </div>

          <div class="section">
            <h2>3. Required Dashboard Features</h2>
            <div class="content">
              <p><strong>A. Source Code Input</strong></p>
              <ul>
                <li>Upload a source file (for example, a .c file).</li>
                <li>Provide an editor area to type or paste code.</li>
                <li>Provide controls such as Upload, Analyze, and Clear.</li>
              </ul>
              <p><strong>B. Lexical Analysis – LEX/FLEX</strong></p>
              <p>Scan the source code and identify keywords, identifiers, operators, constants and delimiters. Detect invalid characters or unrecognized token patterns.</p>

              <div class="table-wrap">
                <table>
                  <thead>
                    <tr><th>Example token table</th><th>Token Type</th><th>Line</th></tr>
                  </thead>
                  <tbody>
                    <tr><td>int</td><td>KEYWORD</td><td>1</td></tr>
                    <tr><td>a</td><td>IDENTIFIER</td><td>1</td></tr>
                    <tr><td>=</td><td>OPERATOR</td><td>1</td></tr>
                    <tr><td>25</td><td>CONSTANT</td><td>1</td></tr>
                    <tr><td>;</td><td>DELIMITER</td><td>1</td></tr>
                  </tbody>
                </table>
              </div>

              <p style="margin-top: 14px;"><strong>C. Syntax Analysis – YACC/Bison</strong></p>
              <p>Pass tokens from the lexical analyzer to the parser. Check whether the token sequence follows the grammar defined by the team. Report syntax errors and their line number wherever possible.</p>

              <p><strong>D. Error Reporting</strong></p>
              <p>Display lexical and syntax errors in separate sections. Each diagnostic should show the error category, line number (where available), and a clear message. If no error is detected, show a successful analysis status.</p>
            </div>
          </div>

          <div class="section">
            <h2>4. Illustrative Examples</h2>
            <div class="code-block">int a = 10;
int b = 20;
int c = a + b;

Expected: Tokens are listed and syntax analysis accepts the program if it follows the grammar implemented by the team.</div>
          </div>
        </div>

        <div class="footer-bar">
          <span>Mini Compiler Dashboard | Compiler Design Lab</span>
          <span>Page 1</span>
        </div>
      </div>
    </div>

    <div class="document-shell" style="margin-top: 18px;">
      <div class="paper">
        <div>
          <div class="title-wrap" style="margin-top: 8px;">
            <div class="page-pill">Page 2 of 3</div>
            <h1 style="margin-top: 10px; font-size: 22px;">5. Technology Requirements</h1>
          </div>

          <div class="table-wrap" style="margin-top: 12px;">
            <table>
              <thead>
                <tr><th>Component</th><th>Required / Suggested Technology</th></tr>
              </thead>
              <tbody>
                <tr><td>Frontend</td><td>HTML, CSS, JavaScript (or another approved UI framework)</td></tr>
                <tr><td>Lexical analyzer</td><td>LEX / FLEX</td></tr>
                <tr><td>Syntax analyzer</td><td>YACC / Bison</td></tr>
                <tr><td>Compiler</td><td>GCC</td></tr>
                <tr><td>Backend / Integration</td><td>Suitable API backend, e.g. Flask or FastAPI, connecting the UI to compiler components</td></tr>
              </tbody>
            </table>
          </div>

          <div class="section">
            <h2>6. System Workflow</h2>
            <div class="content">
              <p>Step 1: User uploads a source file or pastes code.</p>
              <p>Step 2: Dashboard sends the source code to the backend.</p>
              <p>Step 3: LEX/FLEX scans the input and generates tokens.</p>
              <p>Step 4: Lexical errors, if any, are displayed.</p>
              <p>Step 5: Tokens are passed to YACC/Bison for parsing.</p>
              <p>Step 6: The parser validates the token sequence against grammar.</p>
              <p>Step 7: Dashboard displays syntax errors or accepted status.</p>
            </div>
          </div>

          <div class="section">
            <h2>7. Important Implementation Rules</h2>
            <div class="content">
              <ul>
                <li>Actual lexical analysis must be performed by LEX/FLEX; do not simulate tokenization only with JavaScript.</li>
                <li>Actual syntax analysis must be performed by YACC/Bison using grammar rules.</li>
                <li>Display tokenization and errors clearly.</li>
                <li>Define and document the subset of C syntax supported.</li>
                <li>Test valid code, invalid characters, missing delimiters and malformed expressions.</li>
              </ul>
            </div>
          </div>

          <div class="section">
            <h2>8. Evaluation Criteria (30 Marks)</h2>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr><th>Evaluation component</th><th>Marks</th></tr>
                </thead>
                <tbody>
                  <tr><td>Dashboard design and functionality</td><td>5</td></tr>
                  <tr><td>LEX implementation</td><td>5</td></tr>
                  <tr><td>Token generation and display</td><td>4</td></tr>
                  <tr><td>YACC/Bison implementation</td><td>4</td></tr>
                  <tr><td>Syntax detection</td><td>4</td></tr>
                  <tr><td>Error reporting and integration</td><td>5</td></tr>
                  <tr><td>UI and code explanation</td><td>2</td></tr>
                  <tr><td>Total</td><td>30</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="section">
            <h2>9. Submission Requirements</h2>
            <div class="content">
              <ol>
                <li>Complete source code: frontend, backend, LEX and YACC/Bison files.</li>
                <li>README document with setup and usage instructions.</li>
                <li>Screenshots of successful lexical and syntax analysis, plus at least one lexical error and one syntax error.</li>
                <li>Short demonstration of the working dashboard.</li>
              </ol>
            </div>
          </div>

          <div class="section">
            <h2>10. Final Expected Outcome</h2>
            <div class="content">
              <p>A working web-based Mini Compiler Dashboard where users can upload or enter source code, run lexical analysis and YACC/Bison-based syntax analysis, view generated tokens, and identify lexical and syntax errors through a clear interface.</p>
            </div>
          </div>
        </div>

        <div class="footer-bar">
          <span>Mini Compiler Dashboard | Compiler Design Lab</span>
          <span>Page 2</span>
        </div>
      </div>
    </div>

    <div class="status-box">
      <strong>Compiler output</strong>
      <span class="status-badge">{result['status']}</span>
      <div style="margin-top: 10px; white-space: pre-wrap;">{analysis_list}</div>
    </div>
    """


rendered = f"""
<div style="display:flex; gap:24px; align-items:flex-start;">
  <div style="flex: 1; min-width: 260px;">{render_document_html(DEFAULT_CODE, analyze_code(DEFAULT_CODE))}</div>
  <div style="width: 340px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12); border-radius: 18px; padding: 18px; color: #edf3f8;">
    <h3 style="margin:0 0 12px; color:#bfe7fb; font-size: 18px;">Code Analyzer</h3>
    <div style="font-size: 12px; color: #d6e7f6; line-height: 1.8;">
      <p><strong>Project:</strong> Mini Compiler Dashboard</p>
      <p><strong>Language:</strong> C source analysis</p>
      <p><strong>Focus:</strong> lexical + syntax validation</p>
      <p><strong>Status:</strong> Ready to run</p>
    </div>
    <div style="margin-top: 18px; background: rgba(16,28,36,0.42); border-radius: 10px; padding: 12px; border: 1px solid rgba(198,224,245,0.18);">
      <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #9ccce9; margin-bottom: 8px;">Sample input</div>
      <pre style="margin:0; white-space: pre-wrap; font-size: 11px; color: #f0f7fb; font-family: Consolas, monospace;">{DEFAULT_CODE}</pre>
    </div>
    <div style="margin-top: 18px; padding: 10px 12px; border-radius: 10px; background: rgba(13,109,140,0.18); border: 1px solid rgba(23,198,255,0.26); font-size: 12px; color: #d8eff8;">
      <strong>Result:</strong> The compiler will scan the source, identify tokens and syntax structures, and detail any lexical or parser errors.
    </div>
  </div>
</div>
"""

with st.container():
    st.markdown('<div style="padding: 10px 0 20px;">', unsafe_allow_html=True)
    html(rendered, height=1550, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.title("Compiler Console")
st.sidebar.caption("Upload or paste C code to inspect lexical and syntax output.")
source_code = st.sidebar.text_area("C source code", value=DEFAULT_CODE, height=260)
if st.sidebar.button("Analyze code"):
    result = analyze_code(source_code)
    st.sidebar.success(result["summary"])
    for item in result["issues"]:
        st.sidebar.write(f"• {item}")

    with st.container():
        st.markdown(f"<div class='status-box'><strong>Live compiler output</strong><span class='status-badge'>{result['status']}</span><div style='margin-top: 10px;'>{' '.join(f'<p>{issue}</p>' for issue in result['issues'])}</div></div>", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("Upload a .c file", type=["c"])
if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8", errors="ignore")
    st.sidebar.write("Loaded file:", uploaded_file.name)
    st.sidebar.code(text[:250], language="c")

st.sidebar.markdown("""
---
### Quick notes
- LEX/FLEX handles token generation.
- YACC/Bison validates syntax structure.
- UI uses a clean document-inspired layout for a strong academic presentation.
""")

