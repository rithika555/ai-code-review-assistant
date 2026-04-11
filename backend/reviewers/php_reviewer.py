from backend.reviewers.base_reviewer import BaseReviewer


class PhpReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("PHP")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior PHP engineer with expertise in SQL injection, XSS, CSRF, "
            "modern PHP 8.x features, type declarations, Composer dependency management, "
            "Laravel/Symfony security patterns, and secure session handling."
        )