from backend.reviewers.base_reviewer import BaseReviewer


class TypeScriptReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("TypeScript")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior TypeScript engineer specializing in strict typing, "
            "generics, utility types, discriminated unions, type guards, "
            "structural typing pitfalls, and advanced TypeScript compiler configurations."
        )