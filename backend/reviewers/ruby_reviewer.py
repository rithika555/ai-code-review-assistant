from backend.reviewers.base_reviewer import BaseReviewer


class RubyReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("Ruby")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior Ruby engineer with expertise in Rails security (mass assignment, "
            "SQL injection), metaprogramming risks, Gem vulnerabilities, idiomatic Ruby patterns, "
            "performance profiling, and N+1 query detection."
        )