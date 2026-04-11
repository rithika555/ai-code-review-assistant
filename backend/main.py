from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from backend.services.analysis_service import AnalysisService
from backend.github_reviewer import GitHubReviewer

app = FastAPI(title="AI Code Review Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analysis_service = AnalysisService()
github_reviewer = GitHubReviewer()


class CodeReviewRequest(BaseModel):
    code: str
    filename: Optional[str] = None


class RepoReviewRequest(BaseModel):
    repo_url: str
    github_token: Optional[str] = None


class PRReviewRequest(BaseModel):
    pr_url: str
    github_token: Optional[str] = None


@app.post("/review")
async def review_code(request: CodeReviewRequest):
    try:
        print(f"[DEBUG] /review called, code length: {len(request.code)}")
        print(f"[DEBUG] GROQ_API_KEY set: {bool(os.environ.get('GROQ_API_KEY'))}")
        result = await analysis_service.analyze_code(request.code, request.filename)
        print(f"[DEBUG] Success — language: {result.get('language')}, score: {result.get('score')}")
        return result
    except Exception as e:
        print(f"[ERROR] /review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review_repo")
async def review_repo(request: RepoReviewRequest):
    try:
        results = await github_reviewer.review_repository(
            request.repo_url, request.github_token
        )
        return results
    except Exception as e:
        print(f"[ERROR] /review_repo failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review_pr")
async def review_pr(request: PRReviewRequest):
    try:
        results = await github_reviewer.review_pull_request(
            request.pr_url, request.github_token
        )
        return results
    except Exception as e:
        print(f"[ERROR] /review_pr failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "groq_key_set": bool(os.environ.get("GROQ_API_KEY")),
    }


frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))