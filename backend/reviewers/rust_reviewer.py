from backend.reviewers.base_reviewer import BaseReviewer


class RustReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("Rust")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior Rust engineer with deep expertise in ownership, borrowing, "
            "lifetimes, unsafe blocks, trait design, error handling with Result/Option, "
            "async runtimes, and zero-cost abstractions."
        )