from backend.reviewers.base_reviewer import BaseReviewer


class CSharpReviewer(BaseReviewer):
    def __init__(self):
        super().__init__("C#")

    def get_language_prompt(self) -> str:
        return (
            "You are a senior C# and .NET engineer with expertise in async/await patterns, "
            "LINQ performance, Entity Framework N+1 issues, dependency injection, "
            "nullable reference types, and ASP.NET Core security best practices."
        )