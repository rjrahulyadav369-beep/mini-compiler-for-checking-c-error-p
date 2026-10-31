const DEFAULT_CODE = `#include <stdio.h>

int main() {
    int a = 10;
    int b = 20;
    int sum = a + b;
    printf("%d\\n", sum);
    return 0;
}`;

const KEYWORDS = new Set([
  'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
  'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
  'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof',
  'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
  'volatile', 'while', 'include', 'define', 'stdio', 'h', 'main', 'printf', 'scanf'
]);

const OPERATORS = new Set(['=', '+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=', '&&', '||', '!', '&', '|']);

function tokenizeCode(code) {
  const tokens = [];
  if (!code) return tokens;

  const lines = code.split('\n');
  lines.forEach((line, index) => {
    const matches = line.matchAll(/"(?:\\.|[^"\\])*"|\b[a-zA-Z_]\w*\b|\d+|==|!=|<=|>=|&&|\|\||[=+\-*/%<>(){};!&|,\[\].]/g);

    for (const match of matches) {
      const token = match[0];
      if (!token.trim()) continue;

      let tokenType = 'other';

      if (KEYWORDS.has(token)) tokenType = 'keyword';
      else if (/^[A-Za-z_]\w*$/.test(token)) tokenType = 'identifier';
      else if (/^\d+$/.test(token)) tokenType = 'number';
      else if (token.startsWith('"')) tokenType = 'string';
      else if (OPERATORS.has(token)) tokenType = 'operator';
      else if [';', '(', ')', '{', '}', '[', ']', ',', '.'].includes(token) tokenType = 'symbol';

      tokens.push({ token, type: tokenType, line: index + 1 });
    }
  });

  return tokens;
}

function analyzeCode(code) {
  const text = (code || '').trim();

  if (!text) {
    return {
      status: 'No input',
      summary: 'Waiting for code input.',
      issues: ['Please paste or upload C code to check.'],
      tokens: [],
      score: 0,
    };
  }

  const issues = [];
  const lines = text.split('\n');

  lines.forEach((line, idx) => {
    const stripped = line.trim();
    if (!stripped || stripped.startsWith('#')) return;
    if (stripped.endsWith('{') || stripped.endsWith('}')) return;
    if (/(?:if|for|while|else|switch|do)\b.*/.test(stripped)) return;
    if (stripped.startsWith('return ')) return;
    if (stripped.endsWith(';')) return;
    if ((stripped.includes('printf') || stripped.includes('scanf')) && stripped.endsWith(')')) return;
    issues.push(`Line ${idx + 1}: Check statement termination or the function syntax.`);
  });

  if (/\b[0-9][A-Za-z_][A-Za-z0-9_]*\b/.test(text)) {
    issues.push('Invalid identifier format detected.');
  }

  if (!text.includes('main')) {
    issues.push('Missing main() function — required as the C program entry point.');
  }

  if (text.includes('main') && !text.includes('return 0;')) {
    issues.push('main() should return a value, usually return 0;.');
  }

  if (text.toLowerCase().includes('printf') && !text.includes('(')) {
    issues.push('printf is used without parentheses.');
  }

  if (text.toLowerCase().includes('for(') || text.toLowerCase().includes('while(')) {
    issues.push('Loop condition should be reviewed for valid syntax and braces.');
  }

  const tokens = tokenizeCode(text);
  const score = Math.max(0, 100 - issues.length * 18);

  if (!issues.length) {
    return {
      status: 'Healthy',
      summary: 'Code looks structurally valid and ready to compile.',
      issues: ['No syntax issues detected in the current sample.'],
      tokens,
      score,
    };
  }

  return {
    status: 'Needs attention',
    summary: 'The compiler found a few issues that should be reviewed.',
    issues,
    tokens,
    score,
  };
}

function renderResult(result) {
  const statusBadge = document.getElementById('statusBadge');
  const summaryText = document.getElementById('summaryText');
  const issueList = document.getElementById('issueList');
  const tokenTableBody = document.getElementById('tokenTableBody');

  if (statusBadge) statusBadge.textContent = result.status;
  if (summaryText) summaryText.textContent = result.summary;

  if (issueList) {
    issueList.innerHTML = '';
    result.issues.forEach((issue) => {
      const item = document.createElement('li');
      item.textContent = issue;
      issueList.appendChild(item);
    });
  }

  if (tokenTableBody) {
    tokenTableBody.innerHTML = '';
    if (!result.tokens.length) {
      tokenTableBody.innerHTML = '<tr><td colspan="3" class="empty-state">No tokens available.</td></tr>';
    } else {
      result.tokens.slice(0, 20).forEach((token) => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${token.token}</td>
          <td>${token.type}</td>
          <td>${token.line}</td>
        `;
        tokenTableBody.appendChild(row);
      });
    }
  }

  const tokenStat = document.getElementById('tokenStat');
  const issueStat = document.getElementById('issueStat');
  const healthStat = document.getElementById('healthStat');

  if (tokenStat) tokenStat.textContent = result.tokens.length;
  if (issueStat) issueStat.textContent = result.issues.length;
  if (healthStat) healthStat.textContent = result.status;
}

function updateFromCode(code) {
  const result = analyzeCode(code);
  renderResult(result);
}

document.addEventListener('DOMContentLoaded', () => {
  const codeInput = document.getElementById('codeInput');
  const fileInput = document.getElementById('fileInput');

  if (codeInput) {
    codeInput.value = DEFAULT_CODE;
    updateFromCode(DEFAULT_CODE);
  }

  document.getElementById('analyzeBtn')?.addEventListener('click', () => {
    updateFromCode(codeInput.value);
  });

  document.getElementById('heroAnalyzeBtn')?.addEventListener('click', () => {
    updateFromCode(codeInput.value);
  });

  document.getElementById('launchBtn')?.addEventListener('click', () => {
    document.getElementById('workspace')?.scrollIntoView({ behavior: 'smooth' });
  });

  document.getElementById('heroSampleBtn')?.addEventListener('click', () => {
    if (codeInput) {
      codeInput.value = DEFAULT_CODE;
      updateFromCode(DEFAULT_CODE);
    }
  });

  document.getElementById('clearBtn')?.addEventListener('click', () => {
    if (codeInput) {
      codeInput.value = '';
      updateFromCode('');
    }
  });

  fileInput?.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      if (codeInput) {
        codeInput.value = reader.result || '';
        updateFromCode(codeInput.value);
      }
    };
    reader.readAsText(file);
  });
});
