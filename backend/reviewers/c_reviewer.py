from backend.reviewers.base_reviewer import BaseReviewer


class CReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("C")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior C systems programmer with expertise in memory management, "
            "pointer arithmetic, buffer overflows, stack/heap vulnerabilities, "
            "undefined behavior, MISRA C compliance, and secure coding standards."
        )