import os
from pathlib import Path
from collections import Counter

LANGUAGES = {
    ".py": "Python",
    ".kt": "Kotlin",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "React JSX",
    ".tsx": "React TSX",
    ".html": "HTML",
    ".css": "CSS",
    ".php": "PHP",
    ".rs": "Rust",
    ".go": "Go",
    ".swift": "Swift",
    ".dart": "Dart",
    ".rb": "Ruby",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".xml": "XML",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown"
}

IGNORE_DIRS = {
    ".git", ".gradle", "__pycache__",
    "node_modules", ".venv", "venv",
    "build", "dist"
}

class ProjectScanner:

    def scan(self, project_path):
        root = Path(project_path).expanduser().resolve()

        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid project directory: {root}")

        files = []
        languages = Counter()

        for current, dirs, filenames in os.walk(root):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for filename in filenames:
                path = Path(current) / filename
                files.append(str(path.relative_to(root)))
                languages[LANGUAGES.get(path.suffix.lower(), "Other")] += 1

        return {
            "project": root.name,
            "path": str(root),
            "total_files": len(files),
            "languages": dict(languages),
            "files": files[:500]
        }

if __name__ == "__main__":
    scanner = ProjectScanner()
    result = scanner.scan(".")

    print("===== PROJECT INTELLIGENCE =====")
    print("PROJECT:", result["project"])
    print("TOTAL FILES:", result["total_files"])
    print("LANGUAGES:")

    for language, count in result["languages"].items():
        print(f"  {language}: {count}")

    print("===== SCAN COMPLETED =====")
