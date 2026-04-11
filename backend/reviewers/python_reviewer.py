from backend.reviewers.base_reviewer import BaseReviewer


class PythonReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("Python")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior Python engineer with deep expertise in Pythonic code, "
            "PEP 8 standards, security (OWASP), async patterns, type hints, "
            "and performance optimization using profiling and algorithmic complexity analysis."
        )