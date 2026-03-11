/**
 * script.js
 * Client-side logic for the AI Code Review Assistant dashboard.
 * Handles tab switching, API calls, and dynamic rendering of results.
 */

const API_BASE = "http://127.0.0.1:8000";

// ─────────────────────────────────────────────
// Utility Helpers
// ─────────────────────────────────────────────

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function scoreClass(score) {
  if (score >= 80) return "score-high";
  if (score >= 65) return "score-medium";
  if (score >= 40) return "score-low";
  return "score-bad";
}

function scoreBarColor(score) {
  if (score >= 80) return "var(--green)";
  if (score >= 65) return "var(--yellow)";
  if (score >= 40) return "var(--orange)";
  return "var(--red)";
}

function sevIcon(severity) {
  const icons = { critical: "🔴", bug: "🟠", warning: "🟡", info: "🔵" };
  return icons[severity] || "⚪";
}

function riskDot(risk) {
  const dots = { Clean: "🟢", Low: "🔵", Medium: "🟡", High: "🔴" };
  return dots[risk] || "⚪";
}

// ─────────────────────────────────────────────
// Tab Switching
// ─────────────────────────────────────────────

$$(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    $$(".tab-btn").forEach(b => b.classList.remove("active"));
    $$(".panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    $(`#panel-${btn.dataset.tab}`).classList.add("active");
  });
});

// ─────────────────────────────────────────────
// Suggestion Card Builder
// ─────────────────────────────────────────────

function buildSuggestionCard(s, index) {
  const lineInfo = s.line ? `Line ${s.line}` : "";
  const exFix = s.example_fix
    ? `<div class="card-section">
        <div class="card-section-label"><span>💡</span> Example Fix</div>
        <pre class="card-code">${escapeHtml(s.example_fix)}</pre>
       </div>`
    : "";
  const benefit = s.benefit
    ? `<div class="card-section">
        <div class="card-section-label"><span>✅</span> Benefit</div>
        <div class="card-benefit">${escapeHtml(s.benefit)}</div>
       </div>`
    : "";

  return `
    <div class="suggestion-card" id="card-${index}" style="animation-delay: ${index * 0.05}s">
      <div class="card-header" onclick="toggleCard('card-${index}')">
        <div class="card-header-left">
          <span class="sev-badge sev-${s.severity}">${sevIcon(s.severity)} ${escapeHtml(s.severity)}</span>
          <span class="card-type">${escapeHtml(s.type)}</span>
        </div>
        ${lineInfo ? `<span class="card-line">${lineInfo}</span>` : ""}
        <span class="card-toggle">▾</span>
      </div>
      <div class="card-body">
        <div class="card-section">
          <div class="card-section-label"><span>⚠️</span> Issue</div>
          <div class="card-message">${escapeHtml(s.message)}</div>
        </div>
        <div class="card-section">
          <div class="card-section-label"><span>🔧</span> Fix</div>
          <div class="card-fix">${escapeHtml(s.fix)}</div>
        </div>
        ${exFix}
        ${benefit}
      </div>
    </div>`;
}

function toggleCard(id) {
  const card = document.getElementById(id);
  if (card) card.classList.toggle("open");
}

// ─────────────────────────────────────────────
// Summary Banner Builder
// ─────────────────────────────────────────────

function buildSummary({ language, quality_score, risk_level, total_issues }) {
  return `
    <div class="summary-grid">
      <div class="summary-card">
        <div class="summary-label">Language</div>
        <div class="summary-value" style="font-size:1.2rem; color: var(--accent)">${escapeHtml(language)}</div>
      </div>
      <div class="summary-card">
        <div class="summary-label">Quality Score</div>
        <div class="summary-value ${scoreClass(quality_score)}">${quality_score}</div>
        <div class="score-bar-wrapper">
          <div class="score-bar-fill" style="width: 0%; background: ${scoreBarColor(quality_score)}"
               data-target="${quality_score}"></div>
        </div>
        <div class="summary-sub">out of 100</div>
      </div>
      <div class="summary-card">
        <div class="summary-label">Risk Level</div>
        <div class="summary-value" style="font-size:1.1rem">
          <span class="risk-badge risk-${risk_level}">${riskDot(risk_level)} ${escapeHtml(risk_level)}</span>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-label">Issues Found</div>
        <div class="summary-value ${total_issues > 0 ? "score-bad" : "score-high"}">${total_issues}</div>
        <div class="summary-sub">${total_issues === 0 ? "no issues 🎉" : "need attention"}</div>
      </div>
    </div>`;
}

function animateScoreBars() {
  $$(".score-bar-fill").forEach(bar => {
    const target = parseInt(bar.dataset.target, 10);
    requestAnimationFrame(() => {
      setTimeout(() => { bar.style.width = `${target}%`; }, 80);
    });
  });
}

// ─────────────────────────────────────────────
// Code Review — Paste Tab
// ─────────────────────────────────────────────

const reviewBtn   = $("#btn-review");
const codeInput   = $("#code-input");
const reviewOut   = $("#review-output");

reviewBtn.addEventListener("click", async () => {
  const code = codeInput.value.trim();
  if (!code) {
    showAlert(reviewOut, "Please paste some code before reviewing.", "error");
    return;
  }

  setLoading(reviewBtn, true);
  reviewOut.innerHTML = "";

  try {
    const resp = await fetch(`${API_BASE}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, filename: "snippet.py" }),
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }

    const data = await resp.json();
    renderCodeReview(data, reviewOut);

  } catch (err) {
    showAlert(reviewOut, `Error: ${err.message}`, "error");
  } finally {
    setLoading(reviewBtn, false);
  }
});

function renderCodeReview(data, container) {
  const summary = buildSummary(data);
  const cards = data.suggestions.length
    ? data.suggestions.map((s, i) => buildSuggestionCard(s, i)).join("")
    : `<div class="state-empty">
         <div class="icon">✅</div>
         <p>No issues found. Your code looks clean!</p>
       </div>`;

  container.innerHTML = `
    ${summary}
    <div class="section-header">
      <div class="section-title">Suggestions (${data.total_issues})</div>
    </div>
    <div class="suggestions-list">${cards}</div>`;

  animateScoreBars();
}

// ─────────────────────────────────────────────
// GitHub Review Tab
// ─────────────────────────────────────────────

const ghBtn    = $("#btn-github");
const ghUrl    = $("#github-url");
const ghToken  = $("#github-token");
const ghOut    = $("#github-output");

ghBtn.addEventListener("click", async () => {
  const repo_url = ghUrl.value.trim();
  const token    = ghToken.value.trim() || null;

  if (!repo_url) {
    showAlert(ghOut, "Please enter a GitHub repository URL.", "error");
    return;
  }

  setLoading(ghBtn, true);
  ghOut.innerHTML = "";

  try {
    const resp = await fetch(`${API_BASE}/review-github`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url, token }),
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }

    const data = await resp.json();
    renderGitHubReview(data, ghOut);

  } catch (err) {
    showAlert(ghOut, `Error: ${err.message}`, "error");
  } finally {
    setLoading(ghBtn, false);
  }
});

function renderGitHubReview(data, container) {
  const repoInfo = `
    <div class="summary-card" style="margin-bottom: 20px; background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 18px;">
      <div class="summary-label">Repository</div>
      <div style="font-size: 1rem; color: var(--accent); font-weight: 600; margin-top: 4px;">
        ${escapeHtml(data.owner)} / ${escapeHtml(data.repo)}
      </div>
      <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 4px;">
        ${data.files_reviewed} file${data.files_reviewed !== 1 ? "s" : ""} reviewed · ${data.total_issues} total issues
      </div>
    </div>`;

  const summary = buildSummary({
    language: "Multi-file",
    quality_score: data.overall_score,
    risk_level: data.overall_risk,
    total_issues: data.total_issues,
  });

  let filesHtml = "";
  if (!data.file_results || data.file_results.length === 0) {
    filesHtml = `<div class="state-empty"><div class="icon">📁</div><p>${data.message || "No files were reviewed."}</p></div>`;
  } else {
    filesHtml = data.file_results.map((file, fi) => buildFileAccordion(file, fi)).join("");
  }

  container.innerHTML = `
    ${repoInfo}
    ${summary}
    <div class="section-header">
      <div class="section-title">File Results (${data.files_reviewed})</div>
    </div>
    ${filesHtml}`;

  animateScoreBars();
}

function buildFileAccordion(file, fi) {
  const cards = file.suggestions && file.suggestions.length
    ? file.suggestions.map((s, si) => buildSuggestionCard(s, `${fi}-${si}`)).join("")
    : `<div class="state-empty" style="padding: 24px 0;">
         <p>✅ No issues found in this file.</p>
       </div>`;

  return `
    <div class="file-accordion" id="file-${fi}">
      <div class="file-accordion-header" onclick="toggleFileAccordion('file-${fi}')">
        <span class="file-icon">📄</span>
        <span class="file-path" title="${escapeHtml(file.file)}">${escapeHtml(file.file)}</span>
        <div class="file-meta">
          <span class="risk-badge risk-${file.risk_level}" style="font-size:0.62rem; padding: 2px 8px;">
            ${riskDot(file.risk_level)} ${escapeHtml(file.risk_level)}
          </span>
          <span style="font-size:0.72rem; color: var(--text-muted)">
            Score: <strong class="${scoreClass(file.quality_score)}">${file.quality_score}</strong>
          </span>
          <span style="font-size:0.72rem; color: var(--text-dim)">${file.total_issues} issues</span>
        </div>
        <span class="card-toggle">▾</span>
      </div>
      <div class="file-accordion-body">
        <div class="suggestions-list mt-16">${cards}</div>
      </div>
    </div>`;
}

function toggleFileAccordion(id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle("open");
}

// ─────────────────────────────────────────────
// UI Helpers
// ─────────────────────────────────────────────

function setLoading(btn, loading) {
  btn.disabled = loading;
  const spinner = btn.querySelector(".spinner");
  const label   = btn.querySelector(".btn-label");
  if (spinner) spinner.classList.toggle("hidden", !loading);
  if (label)   label.textContent = loading ? "Analysing…" : btn.dataset.label;
}

function showAlert(container, message, type = "error") {
  container.innerHTML = `<div class="alert alert-${type}">${escapeHtml(message)}</div>`;
}