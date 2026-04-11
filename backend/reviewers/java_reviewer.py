from backend.reviewers.base_reviewer import BaseReviewer


class JavaReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("Java")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior Java engineer with expertise in JVM internals, design patterns, "
            "SOLID principles, Spring Framework security, concurrency, garbage collection, "
            "serialization vulnerabilities, and Java memory model."
        )