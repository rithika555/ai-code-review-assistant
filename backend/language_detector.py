import re
from typing import Optional

EXTENSION_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".scala": "Scala",
    ".r": "R",
    ".R": "R",
}

HEURISTICS = {
    "Python": [
        r"^\s*def\s+\w+\s*\(",
        r"^\s*import\s+\w+",
        r"^\s*from\s+\w+\s+import",
        r"^\s*class\s+\w+.*:",
        r"print\s*\(",
        r"^\s*#.*$",
        r"if\s+__name__\s*==\s*['\"]__main__['\"]",
    ],
    "JavaScript": [
        r"^\s*const\s+\w+\s*=",
        r"^\s*let\s+\w+\s*=",
        r"^\s*var\s+\w+\s*=",
        r"console\.log\s*\(",
        r"^\s*function\s+\w+\s*\(",
        r"=>\s*\{",
        r"require\s*\(",
        r"module\.exports",
    ],
    "TypeScript": [
        r":\s*(string|number|boolean|any|void|never|unknown)",
        r"interface\s+\w+\s*\{",
        r"type\s+\w+\s*=",
        r"<[A-Z]\w*>",
        r"as\s+(string|number|boolean|any)",
        r"readonly\s+\w+",
    ],
    "Java": [
        r"public\s+class\s+\w+",
        r"public\s+static\s+void\s+main",
        r"System\.out\.println",
        r"import\s+java\.",
        r"@Override",
        r"private\s+\w+\s+\w+;",
    ],
    "C++": [
        r"#include\s*<\w+>",
        r"std::",
        r"cout\s*<<",
        r"cin\s*>>",
        r"::\w+",
        r"template\s*<",
    ],
    "C": [
        r"#include\s*<stdio\.h>",
        r"printf\s*\(",
        r"scanf\s*\(",
        r"int\s+main\s*\(",
        r"malloc\s*\(",
        r"free\s*\(",
    ],
    "C#": [
        r"using\s+System",
        r"namespace\s+\w+",
        r"Console\.WriteLine",
        r"public\s+class\s+\w+\s*:",
        r"\.NET",
        r"var\s+\w+\s*=\s*new",
    ],
    "Go": [
        r"^package\s+\w+",
        r"^import\s+\(",
        r"func\s+\w+\s*\(",
        r"fmt\.Println",
        r":=",
        r"goroutine",
    ],
    "Rust": [
        r"fn\s+main\s*\(\)",
        r"let\s+mut\s+\w+",
        r"println!\s*\(",
        r"use\s+std::",
        r"->\s*\w+",
        r"impl\s+\w+",
    ],
    "PHP": [
        r"<\?php",
        r"\$\w+\s*=",
        r"echo\s+",
        r"->",
        r"function\s+\w+\s*\(",
        r"array\s*\(",
    ],
    "Ruby": [
        r"^\s*def\s+\w+",
        r"puts\s+",
        r"\.each\s+do",
        r"require\s+['\"]",
        r"attr_accessor",
        r"end$",
    ],
    "Swift": [
        r"import\s+UIKit",
        r"import\s+Foundation",
        r"var\s+\w+:\s*\w+",
        r"let\s+\w+:\s*\w+",
        r"func\s+\w+\s*\(",
        r"print\s*\(",
    ],
    "Kotlin": [
        r"fun\s+main\s*\(",
        r"fun\s+\w+\s*\(",
        r"val\s+\w+\s*=",
        r"var\s+\w+\s*=",
        r"println\s*\(",
        r"data\s+class",
    ],
    "Scala": [
        r"object\s+\w+",
        r"def\s+\w+\s*:",
        r"val\s+\w+\s*:",
        r"import\s+scala\.",
        r"extends\s+App",
        r"println\s*\(",
    ],
    "R": [
        r"<-",
        r"library\s*\(",
        r"c\s*\(",
        r"data\.frame\s*\(",
        r"ggplot\s*\(",
        r"print\s*\(",
    ],
}


def detect_language(code: str, filename: Optional[str] = None) -> str:
    if filename:
        for ext, lang in EXTENSION_MAP.items():
            if filename.endswith(ext):
                return lang

    scores = {lang: 0 for lang in HEURISTICS}
    for lang, patterns in HEURISTICS.items():
        for pattern in patterns:
            if re.search(pattern, code, re.MULTILINE):
                scores[lang] += 1

    best_lang = max(scores, key=scores.get)
    if scores[best_lang] > 0:
        return best_lang

    return "Unknown"


def get_supported_languages():
    return list(HEURISTICS.keys())