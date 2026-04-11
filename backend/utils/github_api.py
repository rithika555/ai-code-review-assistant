import requests
import base64
from typing import Optional, List, Dict
import re


REVIEWABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".cc", ".cxx",
    ".c", ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".kts",
    ".scala", ".r", ".R"
}

MAX_FILE_SIZE = 100_000  # 100KB


def build_headers(token: Optional[str] = None) -> dict:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def parse_repo_url(url: str) -> tuple[str, str]:
    patterns = [
        r"github\.com/([^/]+)/([^/\?#]+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            owner = m.group(1)
            repo = m.group(2).rstrip(".git")
            return owner, repo
    raise ValueError(f"Cannot parse GitHub repository URL: {url}")


def parse_pr_url(url: str) -> tuple[str, str, int]:
    m = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if m:
        return m.group(1), m.group(2).rstrip(".git"), int(m.group(3))
    raise ValueError(f"Cannot parse GitHub PR URL: {url}")


def fetch_repo_files(
    owner: str, repo: str, token: Optional[str] = None, path: str = ""
) -> List[Dict]:
    headers = build_headers(token)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    files = []
    for item in resp.json():
        if item["type"] == "file":
            ext = "." + item["name"].rsplit(".", 1)[-1] if "." in item["name"] else ""
            if ext in REVIEWABLE_EXTENSIONS and item.get("size", 0) < MAX_FILE_SIZE:
                content = fetch_raw_file(item["download_url"])
                if content:
                    files.append(
                        {
                            "filename": item["path"],
                            "content": content,
                            "size": item.get("size", 0),
                        }
                    )
        elif item["type"] == "dir":
            files.extend(fetch_repo_files(owner, repo, token, item["path"]))

    return files


def fetch_raw_file(url: str, token: Optional[str] = None) -> Optional[str]:
    try:
        headers = build_headers(token)
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def fetch_file_via_api(
    owner: str, repo: str, path: str, token: Optional[str] = None
) -> Optional[str]:
    headers = build_headers(token)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("encoding") == "base64":
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return data.get("content", "")
    except Exception:
        return None


def fetch_pr_files(
    owner: str, repo: str, pr_number: int, token: Optional[str] = None
) -> List[Dict]:
    headers = build_headers(token)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    files = []
    for item in resp.json():
        filename = item.get("filename", "")
        ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""
        if ext not in REVIEWABLE_EXTENSIONS:
            continue
        patch = item.get("patch", "")
        raw_url = item.get("raw_url", "")
        content = ""
        if raw_url:
            content = fetch_raw_file(raw_url, token) or ""
        if not content and patch:
            lines = [l[1:] for l in patch.split("\n") if not l.startswith("-") and not l.startswith("@@")]
            content = "\n".join(lines)
        if content:
            files.append({"filename": filename, "content": content, "patch": patch})

    return files


def fetch_pr_metadata(
    owner: str, repo: str, pr_number: int, token: Optional[str] = None
) -> dict:
    headers = build_headers(token)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return {
        "title": data.get("title", ""),
        "description": data.get("body", ""),
        "author": data.get("user", {}).get("login", ""),
        "base_branch": data.get("base", {}).get("ref", ""),
        "head_branch": data.get("head", {}).get("ref", ""),
        "state": data.get("state", ""),
        "changed_files": data.get("changed_files", 0),
        "additions": data.get("additions", 0),
        "deletions": data.get("deletions", 0),
    }