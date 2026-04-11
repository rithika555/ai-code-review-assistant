from backend.reviewers.base_reviewer import BaseReviewer


class KotlinReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("Kotlin")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior Kotlin/Android engineer with expertise in null safety, "
            "coroutines, Flow, Jetpack Compose patterns, Android security, "
            "sealed classes, extension functions, and idiomatic Kotlin style."
        )