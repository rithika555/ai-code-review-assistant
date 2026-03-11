"""
main.py
FastAPI application entry point for the AI Code Review Assistant.

Run with:
    uvicorn backend.main:app --reload

Endpoints:
    POST /review          — Review a pasted code snippet
    POST /review-github   — Review all files in a GitHub repository
    GET  /health          — Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from backend.reviewer import review_code
from backend.github_reviewer import review_github_repo


# ─────────────────────────────────────────────
# App Initialisation
# ─────────────────────────────────────────────

app = FastAPI(
    title="AI Code Review Assistant",
    description="Intelligent code review for Python projects with GitHub integration.",
    version="1.0.0",
)

# Allow requests from the frontend (served from file:// or localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Request / Response Schemas
# ─────────────────────────────────────────────

class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to review")
    filename: Optional[str] = Field(None, description="Optional filename for language detection")


class GitHubReviewRequest(BaseModel):
    repo_url: str = Field(..., description="Full GitHub repository URL")
    token: Optional[str] = Field(None, description="Optional GitHub personal access token")


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/health", tags=["Utility"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "service": "AI Code Review Assistant"}


@app.post("/review", tags=["Code Review"])
def review_code_endpoint(request: CodeReviewRequest):
    """
    Analyse a code snippet and return structured review results.

    Returns:
        language, quality_score, risk_level, total_issues, suggestions
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    try:
        result = review_code(request.code, filename=request.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return result


@app.post("/review-github", tags=["GitHub Review"])
def review_github_endpoint(request: GitHubReviewRequest):
    """
    Fetch and analyse all source files in a GitHub repository.

    Returns:
        owner, repo, files_reviewed, overall_score, overall_risk,
        total_issues, file_results
    """
    if not request.repo_url.strip():
        raise HTTPException(status_code=400, detail="Repository URL cannot be empty.")

    try:
        result = review_github_repo(request.repo_url, token=request.token)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub review failed: {str(e)}")

    return result