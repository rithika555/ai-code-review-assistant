from backend.reviewers.base_reviewer import BaseReviewer


class RReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("R")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior R data scientist with expertise in vectorization over loops, "
            "tidyverse best practices, memory efficiency for large datasets, "
            "reproducibility, package security, and statistical code correctness."
        )