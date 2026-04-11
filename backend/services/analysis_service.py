import asyncio
from typing import Optional
from backend.language_detector import detect_language
from backend.reviewers.python_reviewer import PythonReviewer
from backend.reviewers.javascript_reviewer import JavaScriptReviewer
from backend.reviewers.typescript_reviewer import TypeScriptReviewer
from backend.reviewers.java_reviewer import JavaReviewer
from backend.reviewers.cpp_reviewer import CppReviewer
from backend.reviewers.c_reviewer import CReviewer
from backend.reviewers.csharp_reviewer import CSharpReviewer
from backend.reviewers.go_reviewer import GoReviewer
from backend.reviewers.rust_reviewer import RustReviewer
from backend.reviewers.php_reviewer import PhpReviewer
from backend.reviewers.ruby_reviewer import RubyReviewer
from backend.reviewers.swift_reviewer import SwiftReviewer
from backend.reviewers.kotlin_reviewer import KotlinReviewer
from backend.reviewers.scala_reviewer import ScalaReviewer
from backend.reviewers.r_reviewer import RReviewer
from backend.reviewers.base_reviewer import BaseReviewer


REVIEWER_MAP = {
    "Python": PythonReviewer,
    "JavaScript": JavaScriptReviewer,
    "TypeScript": TypeScriptReviewer,
    "Java": JavaReviewer,
    "C++": CppReviewer,
    "C": CReviewer,
    "C#": CSharpReviewer,
    "Go": GoReviewer,
    "Rust": RustReviewer,
    "PHP": PhpReviewer,
    "Ruby": RubyReviewer,
    "Swift": SwiftReviewer,
    "Kotlin": KotlinReviewer,
    "Scala": ScalaReviewer,
    "R": RReviewer,
}

ERROR_KEYWORDS = ["engine error", "error analyzing", "check your groq", "encountered an error"]

# Delay between each file to avoid Groq rate limits (seconds)
FILE_DELAY = 4


def _is_error_result(result: dict) -> bool:
    explanation = result.get("ai_explanation", "").lower()
    suggestions = result.get("suggestions", [])
    if any(kw in explanation for kw in ERROR_KEYWORDS):
        return True
    if len(suggestions) == 1:
        issue = suggestions[0].get("issue", "").lower()
        suggestion = suggestions[0].get("suggestion", "").lower()
        if "engine error" in issue or "groq_api_key" in suggestion:
            return True
    return False


class AnalysisService:
    def __init__(self):
        self._reviewers = {}

    def _get_reviewer(self, language: str):
        if language not in self._reviewers:
            reviewer_class = REVIEWER_MAP.get(language)
            if reviewer_class:
                self._reviewers[language] = reviewer_class()
            else:
                self._reviewers[language] = BaseReviewer(language)
        return self._reviewers[language]

    async def analyze_code(self, code: str, filename: Optional[str] = None) -> dict:
        language = detect_language(code, filename)
        reviewer = self._get_reviewer(language)
        # Try up to 3 times with delay between retries
        for attempt in range(3):
            if attempt > 0:
                wait = attempt * 5
                print(f"[WAIT] Waiting {wait}s before retry {attempt}...")
                await asyncio.sleep(wait)
            result = await reviewer.review(code)
            result["filename"] = filename or "unknown"
            if not _is_error_result(result):
                return result
            print(f"[RETRY] Attempt {attempt + 1} failed for {filename}")
        return result

    async def analyze_multiple(self, files: list[dict]) -> list[dict]:
        results = []
        for i, file_info in enumerate(files):
            code = file_info.get("content", "")
            filename = file_info.get("filename", "")
            if not code.strip():
                continue

            # Wait between files to respect rate limits
            if i > 0:
                print(f"[WAIT] Waiting {FILE_DELAY}s before next file...")
                await asyncio.sleep(FILE_DELAY)

            try:
                result = await self.analyze_code(code, filename)
                if not _is_error_result(result):
                    results.append(result)
                    print(f"[OK] {filename} — score: {result.get('score')}")
                else:
                    print(f"[SKIP] {filename} — engine error after retries")
            except Exception as e:
                print(f"[SKIP] {filename} — exception: {e}")
                continue

        return results