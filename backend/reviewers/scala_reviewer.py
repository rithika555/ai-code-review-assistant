from backend.reviewers.base_reviewer import BaseReviewer


class ScalaReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("Scala")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior Scala engineer with expertise in functional programming, "
            "immutability, type class patterns, Akka/Cats/ZIO ecosystems, "
            "implicit resolution, Future composition, and Spark performance."
        )