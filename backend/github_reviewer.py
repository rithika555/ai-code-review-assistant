"""
github_reviewer.py
GitHub integration layer for the AI Code Review Assistant.
Fetches repository file trees and source code via the GitHub REST API,
then passes each file through the core reviewer engine.
"""

import re
import requests
from typing import Optional
from backend.reviewer import review_code


# ─────────────────────────────────────────────
# URL Parsing
# ─────────────────────────────────────────────

def parse_github_url(url: str) -> tuple[str, str]:
    """
    Extract owner and repo name from a GitHub URL.

    Supports formats:
      - https://github.com/owner/repo
      - https://github.com/owner/repo.git
      - github.com/owner/repo

    Returns:
        (owner, repo) tuple

    Raises:
        ValueError if the URL cannot be parsed.
    """
    url = url.strip().rstrip("/").replace(".git", "")
    pattern = r"(?:https?://)?github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(
            f"Could not parse GitHub URL: '{url}'. "
            "Expected format: https://github.com/owner/repo"
        )
    return match.group(1), match.group(2)


# ─────────────────────────────────────────────
# GitHub API Helpers
# ─────────────────────────────────────────────

GITHUB_API = "https://api.github.com"
SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".cpp", ".c", ".rs"}
MAX_FILE_SIZE_BYTES = 100_000   # Skip files larger than 100 KB
MAX_FILES_TO_REVIEW = 10        # Cap to avoid rate limiting


def _headers(token: Optional[str] = None) -> dict:
    """Build request headers, optionally with a GitHub token."""
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def fetch_repo_tree(owner: str, repo: str, token: Optional[str] = None) -> list[dict]:
    """
    Fetch the full file tree of a GitHub repository using the Git Trees API.

    Returns:
        List of file objects with 'path', 'size', 'url' keys.

    Raises:
        RuntimeError on API errors.
    """
    # First, get the default branch SHA
    repo_url = f"{GITHUB_API}/repos/{owner}/{repo}"
    repo_resp = requests.get(repo_url, headers=_headers(token), timeout=10)

    if repo_resp.status_code == 404:
        raise RuntimeError(f"Repository '{owner}/{repo}' not found. Check the URL and ensure it is public.")
    if repo_resp.status_code == 403:
        raise RuntimeError("GitHub API rate limit exceeded. Provide a GitHub token to increase limits.")
    if repo_resp.status_code != 200:
        raise RuntimeError(f"GitHub API error {repo_resp.status_code}: {repo_resp.text}")

    repo_data = repo_resp.json()
    default_branch = repo_data.get("default_branch", "main")

    # Fetch the recursive file tree
    tree_url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    tree_resp = requests.get(tree_url, headers=_headers(token), timeout=15)

    if tree_resp.status_code != 200:
        raise RuntimeError(f"Could not fetch repository tree: {tree_resp.status_code}")

    tree_data = tree_resp.json()
    files = [
        item for item in tree_data.get("tree", [])
        if item.get("type") == "blob"
        and any(item["path"].endswith(ext) for ext in SUPPORTED_EXTENSIONS)
        and item.get("size", 0) <= MAX_FILE_SIZE_BYTES
    ]
    return files


def fetch_file_content(owner: str, repo: str, path: str, token: Optional[str] = None) -> str:
    """
    Fetch raw file content from GitHub.

    Returns:
        File content as a string, or empty string on failure.
    """
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
    resp = requests.get(raw_url, headers=_headers(token), timeout=10)
    if resp.status_code == 200:
        return resp.text
    return ""


# ─────────────────────────────────────────────
# Public Entry Point
# ─────────────────────────────────────────────

def review_github_repo(repo_url: str, token: Optional[str] = None) -> dict:
    """
    Main entry point for GitHub repository review.

    Fetches all supported source files (up to MAX_FILES_TO_REVIEW),
    runs the code reviewer on each, and returns an aggregated result.

    Args:
        repo_url: Full GitHub repository URL.
        token:    Optional GitHub personal access token for higher rate limits.

    Returns:
        dict with keys: owner, repo, files_reviewed, overall_score, overall_risk,
                        total_issues, file_results
    """
    owner, repo = parse_github_url(repo_url)
    files = fetch_repo_tree(owner, repo, token)

    if not files:
        return {
            "owner": owner,
            "repo": repo,
            "files_reviewed": 0,
            "overall_score": 100,
            "overall_risk": "Clean",
            "total_issues": 0,
            "file_results": [],
            "message": "No supported source files found in this repository.",
        }

    # Prioritise Python files, then others
    python_files = [f for f in files if f["path"].endswith(".py")]
    other_files = [f for f in files if not f["path"].endswith(".py")]
    ordered_files = (python_files + other_files)[:MAX_FILES_TO_REVIEW]

    file_results = []
    all_scores = []
    all_issues = []

    for file_meta in ordered_files:
        path = file_meta["path"]
        content = fetch_file_content(owner, repo, path, token)
        if not content.strip():
            continue

        result = review_code(content, filename=path)
        result["file"] = path
        file_results.append(result)
        all_scores.append(result["quality_score"])
        all_issues.extend(result["suggestions"])

    if not all_scores:
        overall_score = 100
    else:
        overall_score = round(sum(all_scores) / len(all_scores))

    # Overall risk: take the worst risk level found
    risk_priority = {"High": 3, "Medium": 2, "Low": 1, "Clean": 0}
    if file_results:
        overall_risk = max(
            (r["risk_level"] for r in file_results),
            key=lambda r: risk_priority.get(r, 0),
        )
    else:
        overall_risk = "Clean"

    return {
        "owner": owner,
        "repo": repo,
        "files_reviewed": len(file_results),
        "overall_score": overall_score,
        "overall_risk": overall_risk,
        "total_issues": len(all_issues),
        "file_results": file_results,
    }