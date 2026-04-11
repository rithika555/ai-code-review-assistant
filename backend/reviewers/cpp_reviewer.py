from backend.reviewers.base_reviewer import BaseReviewer


class CppReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("C++")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior C++ engineer specializing in modern C++17/20, RAII, "
            "smart pointers, undefined behavior, buffer overflows, use-after-free, "
            "template metaprogramming, move semantics, and memory safety."
        )