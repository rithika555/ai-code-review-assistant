import json
import re
import os
import asyncio
import requests
from concurrent.futures import ThreadPoolExecutor

REVIEW_SCHEMA = {
    "language": "string",
    "score": "integer (0-100)",
    "risk": "Low | Medium | High | Critical",
    "ai_explanation": "string",
    "suggestions": [
        {
            "issue": "string",
            "suggestion": "string",
            "example": "string with code",
            "benefit": "string",
        }
    ],
}

_executor = ThreadPoolExecutor(max_workers=4)


class AIReviewEngine:
    """
    Internal AI Review Engine responsible for:
      - Contextual code analysis
      - Architecture suggestions
      - Security issue detection
      - Performance improvements
    """

    def __init__(self):
        self._api_key = os.environ.get("GROQ_API_KEY")
        self._endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self._model = "llama-3.1-8b-instant"

    def build_analysis_prompt(self, code: str, language: str, expert_context: str) -> str:
        schema_str = json.dumps(REVIEW_SCHEMA, indent=2)
        return f"""{expert_context}

Perform a deep, expert-level code review of the following {language} code.

Analyze for:
1. Security vulnerabilities (SQL injection, XSS, buffer overflows, etc.)
2. Performance issues (inefficient algorithms, unnecessary loops, memory leaks)
3. Architecture and design problems (SOLID violations, poor separation of concerns)
4. Code maintainability (naming, complexity, duplication)
5. Best practices specific to {language}
6. Potential bugs and edge cases

Return ONLY a valid JSON object matching this exact schema:
{schema_str}

STRICT RULES — failure to follow these will break the output:
- score must be an integer from 0 to 100
- risk must be exactly one of: "Low", "Medium", "High", "Critical"
- provide 3-5 concrete, actionable suggestions
- All string values must be on a single line — NO newlines inside strings
- In the example field, use semicolons instead of newlines to separate lines of code
- Do NOT use backslashes in any string values
- Do NOT wrap output in markdown, backticks, or any extra text
- Output raw JSON only, nothing else

Code to review:
```
{code[:3000]}
```"""

    def _call_api(self, prompt: str) -> str:
        """Synchronous API call — runs in thread pool."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2048,
        }
        response = requests.post(
            self._endpoint, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    async def run(self, prompt: str) -> str:
        """Run API call in thread pool so it doesn't block the event loop."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._call_api, prompt)

    def parse_output(self, raw: str) -> dict:
        """Parse and clean structured JSON output from the engine."""
        # Strip markdown code fences
        raw = re.sub(r"^```json\s*", "", raw.strip())
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        raw = raw.strip()

        # Try direct parse first
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Fix invalid escape sequences and control chars inside JSON strings
        def fix_string(m):
            s = m.group(0)
            valid_escapes = {'"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u'}
            result = []
            i = 0
            while i < len(s):
                c = s[i]
                if c == '\\' and i + 1 < len(s):
                    nc = s[i + 1]
                    if nc in valid_escapes:
                        result.append(c)
                        result.append(nc)
                        i += 2
                    else:
                        # Drop invalid backslash, keep character
                        result.append(nc)
                        i += 2
                elif c == '\n':
                    result.append('\\n')
                    i += 1
                elif c == '\r':
                    result.append('\\r')
                    i += 1
                elif c == '\t':
                    result.append('\\t')
                    i += 1
                else:
                    result.append(c)
                    i += 1
            return ''.join(result)

        try:
            fixed = re.sub(r'"(?:[^"\\]|\\.)*"', fix_string, raw, flags=re.DOTALL)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # Last resort — extract JSON object manually
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        raise json.JSONDecodeError("Could not parse response", raw, 0)


class BaseReviewer:
    def __init__(self, language: str):
        self.language = language
        self._engine = AIReviewEngine()

    def get_language_prompt(self) -> str:
        return f"You are an expert {self.language} code reviewer."

    async def review(self, code: str) -> dict:
        expert_context = self.get_language_prompt()
        prompt = self._engine.build_analysis_prompt(code, self.language, expert_context)
        try:
            print(f"[ENGINE] Sending to Groq API for {self.language} review...")
            raw = await self._engine.run(prompt)
            print(f"[ENGINE] Got response, parsing...")
            result = self._engine.parse_output(raw)
            result["language"] = self.language
            print(f"[ENGINE] Parsed successfully!")
            return self._normalize(result)
        except json.JSONDecodeError as e:
            print(f"[ENGINE] JSON parse error: {e}")
            return self._fallback_response(str(e))
        except Exception as e:
            print(f"[ENGINE] Error: {e}")
            return self._fallback_response(str(e))

    def _normalize(self, result: dict) -> dict:
        return {
            "language": result.get("language", self.language),
            "score": max(0, min(100, int(result.get("score", 50)))),
            "risk": result.get("risk", "Medium"),
            "ai_explanation": result.get("ai_explanation", ""),
            "suggestions": [
                {
                    "issue": s.get("issue", ""),
                    "suggestion": s.get("suggestion", ""),
                    "example": s.get("example", ""),
                    "benefit": s.get("benefit", ""),
                }
                for s in result.get("suggestions", [])
            ],
        }

    def _fallback_response(self, error: str) -> dict:
        return {
            "language": self.language,
            "score": 50,
            "risk": "Medium",
            "ai_explanation": f"Review engine encountered an error: {error}",
            "suggestions": [
                {
                    "issue": "Engine error",
                    "suggestion": "Please check your GROQ_API_KEY and try again.",
                    "example": "",
                    "benefit": "Reliable code review output",
                }
            ],
        }