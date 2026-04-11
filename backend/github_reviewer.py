from typing import Optional
from backend.utils.github_api import (
    parse_repo_url,
    parse_pr_url,
    fetch_repo_files,
    fetch_pr_files,
    fetch_pr_metadata,
)
from backend.services.analysis_service import AnalysisService

MAX_FILES_TO_REVIEW = 5


class GitHubReviewer:
    def __init__(self):
        self.analysis_service = AnalysisService()

    async def review_repository(self, repo_url: str, token: Optional[str] = None) -> dict:
        try:
            owner, repo = parse_repo_url(repo_url)
        except ValueError as e:
            return {"error": str(e)}

        try:
            files = fetch_repo_files(owner, repo, token)
        except Exception as e:
            return {"error": f"Failed to fetch repository: {str(e)}"}

        files = files[:MAX_FILES_TO_REVIEW]

        if not files:
            return {
                "repo": f"{owner}/{repo}",
                "error": "No reviewable source files found in repository.",
                "results": [],
            }

        results = await self.analysis_service.analyze_multiple(files)

        return {
            "repo": f"{owner}/{repo}",
            "total_files": len(results),
            "results": results,
            "summary": self._build_summary(results),
        }

    async def review_pull_request(self, pr_url: str, token: Optional[str] = None) -> dict:
        try:
            owner, repo, pr_number = parse_pr_url(pr_url)
        except ValueError as e:
            return {"error": str(e)}

        try:
            metadata = fetch_pr_metadata(owner, repo, pr_number, token)
            files = fetch_pr_files(owner, repo, pr_number, token)
        except Exception as e:
            return {"error": f"Failed to fetch PR: {str(e)}"}

        files = files[:MAX_FILES_TO_REVIEW]

        if not files:
            return {
                "pr": pr_url,
                "metadata": metadata,
                "error": "No reviewable source files in this PR.",
                "results": [],
            }

        results = await self.analysis_service.analyze_multiple(files)

        return {
            "pr": pr_url,
            "pr_number": pr_number,
            "repo": f"{owner}/{repo}",
            "metadata": metadata,
            "total_files": len(results),
            "results": results,
            "summary": self._build_summary(results),
        }

    def _build_summary(self, results: list) -> dict:
        if not results:
            return {}

        scores = [r.get("score", 0) for r in results if isinstance(r.get("score"), (int, float))]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0

        risk_levels = [r.get("risk", "Unknown") for r in results]
        risk_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Unknown": 0}
        highest_risk = max(risk_levels, key=lambda r: risk_order.get(r, 0))

        languages = list({r.get("language", "Unknown") for r in results})

        total_suggestions = sum(len(r.get("suggestions", [])) for r in results)

        return {
            "average_score": avg_score,
            "highest_risk": highest_risk,
            "languages_detected": languages,
            "total_suggestions": total_suggestions,
            "files_reviewed": len(results),
        }