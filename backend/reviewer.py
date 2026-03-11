"""
reviewer.py
Core code analysis engine for the AI Code Review Assistant.
Performs static analysis on Python source code and returns structured suggestions.
"""

import re
import ast
from typing import Optional


# ─────────────────────────────────────────────
# Language Detection
# ─────────────────────────────────────────────

def detect_language(code: str, filename: Optional[str] = None) -> str:
    """Detect the programming language of the provided code snippet."""
    if filename:
        ext_map = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".java": "Java", ".cpp": "C++", ".c": "C",
            ".rb": "Ruby", ".go": "Go", ".rs": "Rust", ".php": "PHP",
        }
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang

    python_keywords = ["def ", "import ", "class ", "elif ", "None", "True", "False", "print(", "self."]
    js_keywords = ["const ", "let ", "var ", "function ", "=>", "console.log", "require(", "module.exports"]

    python_score = sum(1 for kw in python_keywords if kw in code)
    js_score = sum(1 for kw in js_keywords if kw in code)

    if python_score >= js_score:
        return "Python"
    elif js_score > 0:
        return "JavaScript"
    return "Unknown"


# ─────────────────────────────────────────────
# AST-Based Python Analysis
# ─────────────────────────────────────────────

def analyze_python_ast(code: str) -> list[dict]:
    """Use Python's AST module to detect structural code issues."""
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        issues.append({
            "type": "Syntax Error",
            "severity": "critical",
            "line": e.lineno,
            "message": f"Syntax error: {e.msg}",
            "fix": "Fix the syntax error before proceeding.",
            "example_fix": "",
            "benefit": "Code cannot run with syntax errors."
        })
        return issues

    for node in ast.walk(tree):
        # Check for bare except
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append({
                "type": "Broad Exception Handling",
                "severity": "warning",
                "line": getattr(node, "lineno", None),
                "message": "Bare `except:` clause catches all exceptions including system exits.",
                "fix": "Catch specific exception types (e.g., `except ValueError:`).",
                "example_fix": "try:\n    risky_call()\nexcept ValueError as e:\n    handle(e)",
                "benefit": "Prevents masking of unexpected errors and improves debuggability."
            })

        # Check for mutable default arguments
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    issues.append({
                        "type": "Mutable Default Argument",
                        "severity": "bug",
                        "line": node.lineno,
                        "message": f"Function `{node.name}` uses a mutable default argument (list/dict/set).",
                        "fix": "Use `None` as the default and initialise inside the function body.",
                        "example_fix": f"def {node.name}(items=None):\n    if items is None:\n        items = []",
                        "benefit": "Avoids shared state bugs that are very hard to trace."
                    })

        # Check for missing docstrings on functions/classes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
                issues.append({
                    "type": "Missing Docstring",
                    "severity": "info",
                    "line": node.lineno,
                    "message": f"`{node.name}` is missing a docstring.",
                    "fix": "Add a docstring describing purpose, parameters, and return values.",
                    "example_fix": f'def {node.name}(...):\n    """Brief description of what this does."""\n    ...',
                    "benefit": "Improves code readability and helps auto-generated documentation."
                })

        # Check for print statements in non-trivial code (code smell)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                issues.append({
                    "type": "Debug Print Statement",
                    "severity": "info",
                    "line": getattr(node, "lineno", None),
                    "message": "Found a `print()` statement — consider using `logging` instead.",
                    "fix": "Replace `print()` with Python's `logging` module.",
                    "example_fix": "import logging\nlogging.info('Your message here')",
                    "benefit": "Logging provides levels, timestamps, and is configurable per environment."
                })

        # Detect use of eval()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "eval":
                issues.append({
                    "type": "Dangerous eval() Usage",
                    "severity": "critical",
                    "line": getattr(node, "lineno", None),
                    "message": "`eval()` can execute arbitrary code and is a critical security risk.",
                    "fix": "Avoid `eval()`. Use `ast.literal_eval()` for safe parsing of literals.",
                    "example_fix": "import ast\nresult = ast.literal_eval(user_input)",
                    "benefit": "Eliminates remote code execution vulnerabilities."
                })

    return issues


# ─────────────────────────────────────────────
# Regex-Based Pattern Analysis
# ─────────────────────────────────────────────

PYTHON_PATTERNS = [
    {
        "pattern": r"password\s*=\s*['\"].+['\"]",
        "type": "Hardcoded Password",
        "severity": "critical",
        "message": "A password appears to be hardcoded in plain text.",
        "fix": "Use environment variables or a secrets manager.",
        "example_fix": "import os\npassword = os.getenv('DB_PASSWORD')",
        "benefit": "Prevents credential leaks if code is shared or version-controlled."
    },
    {
        "pattern": r"(api_key|secret_key|token)\s*=\s*['\"].+['\"]",
        "type": "Hardcoded Secret",
        "severity": "critical",
        "message": "A secret key or API token appears hardcoded.",
        "fix": "Load secrets from environment variables or a `.env` file.",
        "example_fix": "import os\napi_key = os.getenv('API_KEY')",
        "benefit": "Protects secrets from exposure in version control."
    },
    {
        "pattern": r"except\s+Exception\s+as",
        "type": "Overly Broad Exception",
        "severity": "warning",
        "message": "Catching the base `Exception` class is too broad.",
        "fix": "Catch specific exception types relevant to the operation.",
        "example_fix": "except (ValueError, KeyError) as e:\n    handle(e)",
        "benefit": "Ensures unexpected errors surface rather than being silently swallowed."
    },
    {
        "pattern": r"import \*",
        "type": "Wildcard Import",
        "severity": "warning",
        "message": "Wildcard imports (`from x import *`) pollute the namespace.",
        "fix": "Import only the specific names you need.",
        "example_fix": "from module import SpecificClass, specific_function",
        "benefit": "Avoids name collisions and makes dependencies explicit."
    },
    {
        "pattern": r"TODO|FIXME|HACK|XXX",
        "type": "Unresolved TODO / FIXME",
        "severity": "info",
        "message": "There are unresolved TODO or FIXME comments in the code.",
        "fix": "Track these as proper issues in your project tracker.",
        "example_fix": "# GitHub Issue #42: Refactor this section",
        "benefit": "Keeps the codebase clean and tasks properly tracked."
    },
    {
        "pattern": r"^\s{0,}(if __name__\s*==\s*['\"]__main__['\"])",
        "type": "Missing main guard",
        "severity": "info",
        "message": "Code outside a `if __name__ == '__main__':` guard runs on import.",
        "fix": "Wrap script-level code in a main guard.",
        "example_fix": "if __name__ == '__main__':\n    main()",
        "benefit": "Prevents unintended execution when the module is imported."
    },
    {
        "pattern": r"open\([^)]+\)(?!\s+as)",
        "type": "File Not Closed (Context Manager)",
        "severity": "warning",
        "message": "File opened without a `with` statement — may not be closed on error.",
        "fix": "Use `with open(...) as f:` to ensure the file is always closed.",
        "example_fix": "with open('file.txt', 'r') as f:\n    data = f.read()",
        "benefit": "Prevents resource leaks and guarantees file closure even on exceptions."
    },
    {
        "pattern": r"==\s*True|==\s*False|==\s*None",
        "type": "Non-Idiomatic Comparison",
        "severity": "info",
        "message": "Comparing with `== True`, `== False`, or `== None` is not Pythonic.",
        "fix": "Use `is True`, `is False`, `is None` or just the truthiness directly.",
        "example_fix": "if result is None:\n    ...\nif flag:\n    ...",
        "benefit": "Improves readability and follows PEP 8 style guidelines."
    },
]


def analyze_patterns(code: str) -> list[dict]:
    """Run regex pattern matching against code to find common anti-patterns."""
    issues = []
    seen_types = set()
    lines = code.split("\n")

    for rule in PYTHON_PATTERNS:
        for i, line in enumerate(lines, start=1):
            if re.search(rule["pattern"], line, re.IGNORECASE):
                if rule["type"] not in seen_types:
                    seen_types.add(rule["type"])
                    issues.append({
                        "type": rule["type"],
                        "severity": rule["severity"],
                        "line": i,
                        "message": rule["message"],
                        "fix": rule["fix"],
                        "example_fix": rule["example_fix"],
                        "benefit": rule["benefit"],
                    })
    return issues


# ─────────────────────────────────────────────
# Complexity & Quality Metrics
# ─────────────────────────────────────────────

def compute_quality_score(code: str, issues: list[dict]) -> int:
    """
    Compute a 0–100 quality score based on:
    - Issue severity counts
    - Code length ratio
    - Comment coverage
    """
    score = 100
    deductions = {"critical": 20, "bug": 15, "warning": 8, "info": 3}

    for issue in issues:
        sev = issue.get("severity", "info")
        score -= deductions.get(sev, 3)

    lines = [l for l in code.split("\n") if l.strip()]
    comment_lines = [l for l in lines if l.strip().startswith("#")]
    if len(lines) > 10 and len(comment_lines) / len(lines) < 0.05:
        score -= 5  # penalise low comment ratio

    # Penalise very long functions (rough heuristic)
    if code.count("def ") > 0:
        avg_lines_per_func = len(lines) / code.count("def ")
        if avg_lines_per_func > 40:
            score -= 5

    return max(0, min(100, score))


def compute_risk_level(score: int, issues: list[dict]) -> str:
    """Determine overall risk level from score and critical issue count."""
    critical_count = sum(1 for i in issues if i.get("severity") == "critical")
    if critical_count >= 2 or score < 40:
        return "High"
    if critical_count == 1 or score < 65:
        return "Medium"
    if score < 80:
        return "Low"
    return "Clean"


# ─────────────────────────────────────────────
# Public Entry Point
# ─────────────────────────────────────────────

def review_code(code: str, filename: Optional[str] = None) -> dict:
    """
    Main entry point. Analyses the provided source code and returns a
    structured review result.

    Returns:
        dict with keys: language, quality_score, risk_level, suggestions
    """
    language = detect_language(code, filename)
    suggestions = []

    if language == "Python":
        ast_issues = analyze_python_ast(code)
        pattern_issues = analyze_patterns(code)
        # Deduplicate by type
        seen = set()
        for issue in ast_issues + pattern_issues:
            key = issue["type"]
            if key not in seen:
                seen.add(key)
                suggestions.append(issue)
    else:
        suggestions.append({
            "type": "Language Not Fully Supported",
            "severity": "info",
            "line": None,
            "message": f"Deep analysis is currently optimised for Python. Detected: {language}.",
            "fix": "Submit Python code for full analysis.",
            "example_fix": "",
            "benefit": "Python analysis includes AST-level bug detection and security checks."
        })

    quality_score = compute_quality_score(code, suggestions)
    risk_level = compute_risk_level(quality_score, suggestions)

    return {
        "language": language,
        "quality_score": quality_score,
        "risk_level": risk_level,
        "total_issues": len(suggestions),
        "suggestions": suggestions,
    }