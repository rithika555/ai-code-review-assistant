<div align="center">

<img src="https://img.shields.io/badge/AI-Powered-blueviolet?style=for-the-badge&logo=openai&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/15%20Languages-Supported-3b82f6?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Custom%20AI-Ready-a855f7?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-Active-10b981?style=for-the-badge"/>

# ⬡ CodeSentinel — AI Code Review Engine

**A production-grade, AI-powered code review system that performs deep contextual analysis across 15 programming languages simultaneously — detecting security vulnerabilities, performance bottlenecks, architecture flaws, and maintainability issues in seconds.**

> Built with a modular, pluggable AI engine architecture — designed today to run on external inference APIs, and engineered to seamlessly integrate a fully custom-trained AI model in the future.

[Features](#-features) · [Architecture](#-architecture) · [Setup](#-getting-started) · [API](#-api-reference) · [Languages](#-supported-languages)

</div>

---

## 🧠 What is CodeSentinel?

CodeSentinel is a full-stack AI code review assistant that goes far beyond traditional linting. At its core is the **AIReviewEngine** — a modular, swappable inference layer that performs human-level code analysis, the kind of feedback you'd expect from a senior engineer with deep expertise in each language.

The system supports **15 programming languages out of the box**, each with its own dedicated reviewer module containing language-specific expert knowledge. Whether you paste a snippet, point it at a GitHub repository, or feed it a pull request URL, CodeSentinel returns a fully structured, actionable review in seconds.

### 🔮 Vision

CodeSentinel is architected with the future in mind. The `AIReviewEngine` class is a clean abstraction layer — meaning the underlying model can be swapped without touching any other part of the system. The long-term goal is to train and deploy a **fully custom AI model** fine-tuned specifically on code review data, replacing any external dependency entirely and making CodeSentinel a fully self-contained, proprietary intelligence platform.

---

## ✨ Features

- 🔍 **Deep Multi-Language Analysis** — Reviews code in 15 languages simultaneously with language-specific expert context
- 🔒 **Security Vulnerability Detection** — SQL injection, XSS, CSRF, buffer overflows, hardcoded secrets, and more
- ⚡ **Performance Analysis** — Identifies O(n²) complexity, memory leaks, inefficient loops, and algorithmic issues
- 🏗️ **Architecture Review** — SOLID violations, poor separation of concerns, design pattern misuse
- 🧩 **Maintainability Scoring** — Code readability, naming conventions, duplication, and complexity
- 📊 **Structured Output** — Every review returns a quality score (0–100), risk level, and actionable suggestions
- 🌐 **GitHub Integration** — Scan entire repositories or specific pull requests via GitHub API
- 🔌 **Pluggable AI Engine** — Swap the underlying model with zero changes to the rest of the system
- 🖥️ **3D Holographic Dashboard** — Spatial computing UI with real CSS 3D depth and glassmorphism

---

## 🗂️ Supported Languages

CodeSentinel ships with **15 individual reviewer modules**, each containing deep, language-specific expert prompts and knowledge:

| Language | Reviewer Module | Specializations |
|----------|----------------|-----------------|
| 🐍 Python | `python_reviewer.py` | PEP 8, async patterns, type hints, security |
| 🌐 JavaScript | `javascript_reviewer.py` | ES2023+, XSS, event loop, Node.js security |
| 🔷 TypeScript | `typescript_reviewer.py` | Strict typing, generics, utility types, guards |
| ☕ Java | `java_reviewer.py` | JVM, Spring security, concurrency, serialization |
| ⚙️ C++ | `cpp_reviewer.py` | RAII, smart pointers, undefined behavior, memory |
| 🔧 C | `c_reviewer.py` | Buffer overflows, pointer safety, MISRA compliance |
| 🔵 C# | `csharp_reviewer.py` | async/await, LINQ, Entity Framework, .NET security |
| 🐹 Go | `go_reviewer.py` | Goroutines, race conditions, error handling, context |
| 🦀 Rust | `rust_reviewer.py` | Ownership, lifetimes, unsafe blocks, trait design |
| 🐘 PHP | `php_reviewer.py` | SQL injection, XSS, modern PHP 8.x, session security |
| 💎 Ruby | `ruby_reviewer.py` | Rails security, metaprogramming, N+1 queries |
| 🍎 Swift | `swift_reviewer.py` | ARC, retain cycles, optionals, Swift concurrency |
| 🟠 Kotlin | `kotlin_reviewer.py` | Null safety, coroutines, Flow, Jetpack patterns |
| 🎯 Scala | `scala_reviewer.py` | Functional patterns, Cats/ZIO, Spark performance |
| 📊 R | `r_reviewer.py` | Vectorization, tidyverse, memory efficiency |

---

## 📐 Architecture

```
ai-code-review-assistant/
├── backend/
│   ├── main.py                    # FastAPI — POST /review, /review_repo, /review_pr
│   ├── language_detector.py       # Extension + heuristic auto-detection (15 languages)
│   ├── github_reviewer.py         # GitHub repo and PR orchestration
│   ├── reviewers/
│   │   ├── base_reviewer.py       # ★ AIReviewEngine — pluggable inference abstraction
│   │   ├── python_reviewer.py
│   │   ├── javascript_reviewer.py
│   │   ├── typescript_reviewer.py
│   │   ├── java_reviewer.py
│   │   ├── cpp_reviewer.py
│   │   ├── c_reviewer.py
│   │   ├── csharp_reviewer.py
│   │   ├── go_reviewer.py
│   │   ├── rust_reviewer.py
│   │   ├── php_reviewer.py
│   │   ├── ruby_reviewer.py
│   │   ├── swift_reviewer.py
│   │   ├── kotlin_reviewer.py
│   │   ├── scala_reviewer.py
│   │   └── r_reviewer.py
│   ├── services/
│   │   └── analysis_service.py    # Routes code to correct reviewer, retry logic
│   └── utils/
│       └── github_api.py          # GitHub API helpers
└── frontend/
    ├── index.html                 # 3-panel spatial dashboard
    ├── style.css                  # 3D glassmorphism design system
    └── script.js                  # API calls and rendering
```

### Data Flow

```
User Input
    ↓
Language Auto-Detection (extension + heuristics)
    ↓
Language-Specific Reviewer Module (expert context)
    ↓
AIReviewEngine (pluggable inference layer)
    ↓
Structured JSON Parser (with robust error recovery)
    ↓
Frontend Dashboard (Score · Risk · Suggestions · Metrics)
```

### The AIReviewEngine — Pluggable by Design

The `AIReviewEngine` class in `base_reviewer.py` is the single point of contact between CodeSentinel and any AI model. It exposes three clean methods:

- `build_analysis_prompt()` — constructs the language-aware review prompt
- `run()` — executes inference against any model endpoint
- `parse_output()` — parses and validates the structured JSON response

**To swap the AI model**, only the `run()` method needs to change. The rest of the system — all 15 reviewers, the analysis service, the GitHub integration, and the frontend — remain completely untouched. This makes CodeSentinel ready to plug in a fully custom-trained model the moment it's available.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com) *(no credit card required)*
- A [GitHub Personal Access Token](https://github.com/settings/tokens) *(optional, for repo/PR scanning)*

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-code-review-assistant.git
cd ai-code-review-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Create a .env file in the project root:
echo "GROQ_API_KEY=your_groq_key_here" > .env

# 4. Start the server
uvicorn backend.main:app --reload

# 5. Open the dashboard
# Navigate to http://localhost:8000
```

---

## 📡 API Reference

### `POST /review` — Review a code snippet

```json
{
  "code": "def get_user(id):\n    return db.execute(f'SELECT * FROM users WHERE id={id}')",
  "filename": "user.py"
}
```

**Response:**
```json
{
  "language": "Python",
  "score": 32,
  "risk": "Critical",
  "ai_explanation": "Detected SQL injection vulnerability and missing error handling.",
  "suggestions": [
    {
      "issue": "SQL Injection via f-string query construction",
      "suggestion": "Use parameterized queries to separate data from SQL logic.",
      "example": "db.execute('SELECT * FROM users WHERE id = %s', (id,))",
      "benefit": "Eliminates SQL injection attack vector completely."
    }
  ]
}
```

### `POST /review_repo` — Scan a GitHub repository

```json
{
  "repo_url": "https://github.com/owner/repository",
  "github_token": "ghp_optional_for_private_repos"
}
```

### `POST /review_pr` — Review a pull request

```json
{
  "pr_url": "https://github.com/owner/repository/pull/42",
  "github_token": "ghp_your_token"
}
```

### `GET /health` — Server status

---

## ⚙️ Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for AI inference | ✅ Yes |
| `GITHUB_TOKEN` | GitHub token for private repos and higher rate limits | ❌ Optional |

---

## 🔒 Security & Privacy

- No code is stored or logged — every review is completely stateless
- API keys are loaded from environment variables only, never hardcoded
- GitHub tokens are passed per-request and never persisted
- All review data stays local to your machine

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Python 3.10+ |
| AI Inference | Groq API — llama-3.1-8b-instant *(swappable)* |
| GitHub Integration | GitHub REST API v3 |
| Frontend | Vanilla HTML / CSS / JavaScript |
| UI Design | CSS 3D Transforms, Glassmorphism, Spatial Computing Aesthetic |

---

## 🗺️ Roadmap

- [x] 15-language support with individual reviewer modules
- [x] GitHub repository scanning
- [x] GitHub pull request review
- [x] Pluggable AIReviewEngine abstraction
- [x] 3D holographic dashboard
- [ ] Custom fine-tuned AI model (in development)
- [ ] VS Code extension
- [ ] CI/CD pipeline integration
- [ ] Team dashboard with review history

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

**Built for engineers who take code quality seriously.**

⬡ CodeSentinel — *Analyze. Detect. Improve.*

</div>
