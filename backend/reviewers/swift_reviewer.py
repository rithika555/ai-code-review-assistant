from backend.reviewers.base_reviewer import BaseReviewer


class SwiftReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("Swift")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior Swift/iOS engineer with expertise in ARC memory management, "
            "retain cycles, optionals safety, Swift concurrency (async/await, actors), "
            "Keychain security, and SwiftUI/UIKit best practices."
        )