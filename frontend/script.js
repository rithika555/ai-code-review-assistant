const API_BASE = "http://127.0.0.1:8000";

const LANGUAGES = [
  "Python","JavaScript","TypeScript","Java","C++","C","C#",
  "Go","Rust","PHP","Ruby","Swift","Kotlin","Scala","R"
];

const SCAN_MESSAGES = [
  "Parsing abstract syntax tree...",
  "Running vulnerability pattern matching...",
  "Analyzing algorithmic complexity...",
  "Checking security boundaries...",
  "Evaluating architecture patterns...",
  "Cross-referencing best practices...",
  "Generating improvement vectors...",
  "Compiling threat assessment...",
];

let reviewCount = 0;

// ── BOOT SEQUENCE ─────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  runBoot();
  initCanvas();
  renderLangChips();
  setupTabs();
  setupLineNumbers();
  setupButtons();
});

function runBoot() {
  const bar = document.getElementById("boot-bar");
  const status = document.getElementById("boot-status");
  const screen = document.getElementById("boot-screen");
  const app = document.getElementById("app");

  const messages = [
    [0,  "INITIALIZING NEURAL MODULES..."],
    [20, "LOADING LANGUAGE ANALYZERS..."],
    [45, "CALIBRATING THREAT MATRIX..."],
    [65, "CONNECTING TO REVIEW ENGINE..."],
    [85, "RUNNING SELF-DIAGNOSTICS..."],
    [100,"SYSTEM READY"],
  ];

  let i = 0;
  const tick = () => {
    if (i >= messages.length) {
      setTimeout(() => {
        screen.classList.add("gone");
        app.classList.add("visible");
      }, 400);
      return;
    }
    const [pct, msg] = messages[i++];
    bar.style.width = pct + "%";
    status.textContent = msg;
    setTimeout(tick, 320);
  };
  setTimeout(tick, 200);
}

// ── CANVAS BACKGROUND ─────────────────────────────────────────────────────
function initCanvas() {
  const canvas = document.getElementById("bg-canvas");
  const ctx = canvas.getContext("2d");
  let W, H, nodes = [], animId;

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function spawnNodes() {
    nodes = [];
    const count = Math.floor((W * H) / 22000);
    for (let i = 0; i < count; i++) {
      nodes.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
        r: Math.random() * 1.5 + 0.5,
      });
    }
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    // move
    nodes.forEach(n => {
      n.x += n.vx; n.y += n.vy;
      if (n.x < 0) n.x = W; if (n.x > W) n.x = 0;
      if (n.y < 0) n.y = H; if (n.y > H) n.y = 0;
    });
    // edges
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 130) {
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.strokeStyle = `rgba(0,200,255,${0.08 * (1 - dist/130)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    // dots
    nodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(0,200,255,0.35)";
      ctx.fill();
    });
    animId = requestAnimationFrame(draw);
  }

  resize(); spawnNodes(); draw();
  window.addEventListener("resize", () => { resize(); spawnNodes(); });
}

// ── LANG CHIPS ────────────────────────────────────────────────────────────
function renderLangChips() {
  const grid = document.getElementById("lang-grid");
  LANGUAGES.forEach(lang => {
    const chip = document.createElement("div");
    chip.className = "lang-chip";
    chip.textContent = lang;
    grid.appendChild(chip);
  });
}

// ── TABS ──────────────────────────────────────────────────────────────────
function setupTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
    });
  });
}

// ── LINE NUMBERS ──────────────────────────────────────────────────────────
function setupLineNumbers() {
  const ta = document.getElementById("code-input");
  const gutter = document.getElementById("line-numbers");
  ta.addEventListener("input", () => {
    const lines = ta.value.split("\n").length;
    gutter.textContent = Array.from({length: lines}, (_, i) => i + 1).join("\n");
  });
  ta.addEventListener("scroll", () => { gutter.scrollTop = ta.scrollTop; });
}

// ── BUTTONS ───────────────────────────────────────────────────────────────
function setupButtons() {
  document.getElementById("btn-review-code").addEventListener("click", reviewCode);
  document.getElementById("btn-review-repo").addEventListener("click", reviewRepo);
  document.getElementById("btn-review-pr").addEventListener("click", reviewPR);
}

async function reviewCode() {
  const code = document.getElementById("code-input").value.trim();
  const filename = document.getElementById("filename-input").value.trim();
  if (!code) { flashInput("code-input"); return; }
  await runReview(() =>
    fetch(`${API_BASE}/review`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ code, filename: filename || null }),
    }).then(r => r.json())
  , "single");
}

async function reviewRepo() {
  const repo_url = document.getElementById("repo-url").value.trim();
  const github_token = document.getElementById("repo-token").value.trim();
  if (!repo_url) { flashInput("repo-url"); return; }
  await runReview(() =>
    fetch(`${API_BASE}/review_repo`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ repo_url, github_token: github_token || null }),
    }).then(r => r.json())
  , "multi");
}

async function reviewPR() {
  const pr_url = document.getElementById("pr-url").value.trim();
  const github_token = document.getElementById("pr-token").value.trim();
  if (!pr_url) { flashInput("pr-url"); return; }
  await runReview(() =>
    fetch(`${API_BASE}/review_pr`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ pr_url, github_token: github_token || null }),
    }).then(r => r.json())
  , "multi");
}

// ── CORE RUNNER ───────────────────────────────────────────────────────────
async function runReview(fetchFn, mode) {
  setScanning(true);
  clearResults();
  try {
    const data = await fetchFn();
    if (data.error) throw new Error(data.error);
    reviewCount++;
    document.getElementById("stat-reviews").querySelector(".stat-val").textContent = reviewCount;
    if (mode === "single") renderSingle(data);
    else renderMulti(data);
  } catch (err) {
    showError(err.message);
  } finally {
    setScanning(false);
  }
}

// ── RENDER SINGLE ─────────────────────────────────────────────────────────
function renderSingle(data) {
  const suggestions = data.suggestions || [];
  showCards(suggestions);
  updateMetrics(data);
  document.getElementById("issue-counter").textContent =
    suggestions.length + " ISSUE" + (suggestions.length !== 1 ? "S" : "");
}

// ── RENDER MULTI ──────────────────────────────────────────────────────────
function renderMulti(data) {
  const results = data.results || [];
  const container = document.getElementById("cards-container");
  container.classList.remove("hidden");
  document.getElementById("idle-state").classList.add("hidden");

  let total = 0;
  results.forEach((result, ri) => {
    if (!result.suggestions?.length) return;
    const fh = document.createElement("div");
    fh.className = "result-file-header";
    fh.textContent = `▸ ${result.filename || result.language}  ·  SCORE: ${result.score ?? "--"}  ·  RISK: ${result.risk ?? "--"}`;
    container.appendChild(fh);
    result.suggestions.forEach((s, i) => {
      container.appendChild(buildCard(s, i + ri * 10));
      total++;
    });
  });

  document.getElementById("issue-counter").textContent = total + " ISSUES";

  if (data.summary) {
    updateMetrics({
      score: data.summary.average_score,
      risk: data.summary.highest_risk,
      language: (data.summary.languages_detected || []).join(", "),
      ai_explanation: `Scanned ${data.summary.files_reviewed} file(s) across ${(data.summary.languages_detected||[]).join(", ")}. Detected ${data.summary.total_suggestions} total issues.`,
      suggestions: [],
    });
    renderRoster(results);
  }
}

// ── CARDS ─────────────────────────────────────────────────────────────────
function showCards(suggestions) {
  const container = document.getElementById("cards-container");
  container.classList.remove("hidden");
  document.getElementById("idle-state").classList.add("hidden");
  suggestions.forEach((s, i) => container.appendChild(buildCard(s, i)));
}

function buildCard(s, index) {
  const issue = s.issue || "";
  const isSec  = /inject|xss|csrf|overflow|auth|secret|password|vuln|exploit/i.test(issue);
  const isPerf = /performance|loop|memory|complexity|optim|slow|n\+1|leak/i.test(issue);
  const typeClass = isSec ? "type-security" : isPerf ? "type-performance" : "type-default";

  const card = document.createElement("div");
  card.className = "suggestion-card";
  card.style.animationDelay = (index * 70) + "ms";
  card.innerHTML = `
    <div class="card-header" onclick="toggleCard(this)">
      <div class="card-type-bar ${typeClass}"></div>
      <div class="card-issue">${esc(issue)}</div>
      <div class="card-chevron">▼</div>
    </div>
    <div class="card-body" style="display:none">
      ${s.suggestion ? `<div><div class="cb-label">SUGGESTED FIX</div><div class="cb-text">${esc(s.suggestion)}</div></div>` : ""}
      ${s.example    ? `<div><div class="cb-label">EXAMPLE CODE</div><pre class="cb-code">${esc(s.example)}</pre></div>` : ""}
      ${s.benefit    ? `<div><span class="cb-benefit">✓ ${esc(s.benefit)}</span></div>` : ""}
    </div>`;
  return card;
}

// ── METRICS ───────────────────────────────────────────────────────────────
function updateMetrics(data) {
  const score = Math.round(+data.score || 0);
  const risk  = (data.risk || "UNKNOWN").toUpperCase();
  const lang  = data.language || data.detected_language || "--";

  // show live
  document.getElementById("metrics-idle").classList.add("hidden");
  document.getElementById("metrics-live").classList.remove("hidden");

  // header stats
  document.getElementById("stat-lang").textContent = lang.split(",")[0].trim().toUpperCase();
  document.getElementById("stat-risk").textContent = risk;

  // score ring
  document.getElementById("score-number").textContent = score;
  const circ = 351.86;
  document.getElementById("score-arc").style.strokeDashoffset =
    circ - (score / 100) * circ;

  // risk badge
  const badge = document.getElementById("risk-badge");
  const riskText = document.getElementById("risk-text");
  badge.className = "risk-badge " + risk.toLowerCase();
  riskText.textContent = risk + " RISK";

  // bars (derive from score with slight variance)
  const rv = (offset) => Math.min(100, Math.max(0, score + offset));
  setBar("bar-security",  "val-security", rv(-8));
  setBar("bar-perf",      "val-perf",     rv(4));
  setBar("bar-maint",     "val-maint",    rv(6));

  // summary
  document.getElementById("ai-summary-text").textContent =
    data.ai_explanation || "";
}

function setBar(barId, valId, value) {
  setTimeout(() => {
    document.getElementById(barId).style.width = value + "%";
    document.getElementById(valId).textContent = value;
  }, 300);
}

function renderRoster(results) {
  const roster = document.getElementById("file-roster");
  const items  = document.getElementById("roster-items");
  roster.classList.remove("hidden");
  items.innerHTML = results.map((r, i) => `
    <div class="roster-item" onclick="scrollToFile(${i})">
      <span class="roster-name">${esc(r.filename || r.language || "File " + (i+1))}</span>
      <span class="roster-score">${r.score ?? "--"}</span>
    </div>`).join("");
}

// ── SCANNING STATE ────────────────────────────────────────────────────────
let scanInterval;
function setScanning(on) {
  const scanEl  = document.getElementById("scan-state");
  const idleEl  = document.getElementById("idle-state");
  const logEl   = document.getElementById("scan-log");
  const btns    = document.querySelectorAll(".scan-btn");

  if (on) {
    idleEl.classList.add("hidden");
    scanEl.classList.remove("hidden");
    btns.forEach(b => b.disabled = true);
    let mi = 0;
    logEl.textContent = "";
    scanInterval = setInterval(() => {
      logEl.textContent = SCAN_MESSAGES[mi % SCAN_MESSAGES.length];
      mi++;
    }, 900);
  } else {
    clearInterval(scanInterval);
    scanEl.classList.add("hidden");
    btns.forEach(b => b.disabled = false);
  }
}

// ── HELPERS ───────────────────────────────────────────────────────────────
function clearResults() {
  const c = document.getElementById("cards-container");
  c.innerHTML = ""; c.classList.add("hidden");
  document.getElementById("idle-state").classList.remove("hidden");
  document.getElementById("issue-counter").textContent = "";
  document.getElementById("metrics-idle").classList.remove("hidden");
  document.getElementById("metrics-live").classList.add("hidden");
  document.getElementById("file-roster").classList.add("hidden");
  document.getElementById("stat-lang").textContent = "--";
  document.getElementById("stat-risk").textContent = "--";
}

function showError(msg) {
  const c = document.getElementById("cards-container");
  c.classList.remove("hidden");
  document.getElementById("idle-state").classList.add("hidden");
  c.innerHTML = `
    <div class="suggestion-card" style="border-color:rgba(255,51,85,0.3)">
      <div class="card-header">
        <div class="card-type-bar type-security"></div>
        <div class="card-issue">ERROR — ${esc(msg)}</div>
      </div>
    </div>`;
}

function flashInput(id) {
  const el = document.getElementById(id);
  el.style.borderColor = "var(--red)";
  el.style.boxShadow = "0 0 0 3px rgba(255,51,85,0.15)";
  setTimeout(() => { el.style.borderColor = ""; el.style.boxShadow = ""; }, 1200);
}

function toggleCard(header) {
  const body = header.nextElementSibling;
  const chev = header.querySelector(".card-chevron");
  const open = body.style.display !== "none";
  body.style.display = open ? "none" : "flex";
  chev.classList.toggle("open", !open);
}

function scrollToFile(index) {
  const headers = document.querySelectorAll(".result-file-header");
  if (headers[index]) headers[index].scrollIntoView({ behavior: "smooth", block: "start" });
}

function esc(str) {
  return String(str)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

window.toggleCard   = toggleCard;
window.scrollToFile = scrollToFile;