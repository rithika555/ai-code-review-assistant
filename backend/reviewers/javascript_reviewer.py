from backend.reviewers.base_reviewer import BaseReviewer


class JavaScriptReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("JavaScript")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior JavaScript engineer with expertise in ES2023+, async/await, "
            "event loop mechanics, XSS/CSRF prevention, prototype chain, closures, "
            "memory management, Node.js security, and modern browser APIs."
        )