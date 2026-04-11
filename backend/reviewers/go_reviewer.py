from backend.reviewers.base_reviewer import BaseReviewer


class GoReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("Go")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior Go engineer with expertise in goroutine safety, channel patterns, "
            "race conditions, error handling idioms, interface design, context propagation, "
            "memory escaping to heap, and Go security best practices."
        )