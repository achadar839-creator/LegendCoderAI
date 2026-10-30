import ast
import json
from pathlib import Path

class CodeAnalyzer:

    def analyze(self, project_path):
        root = Path(project_path).expanduser().resolve()

        if not root.is_dir():
            raise ValueError("Invalid project directory")

        report = {
            "project": root.name,
            "total_files": 0,
            "total_lines": 0,
            "empty_files": [],
            "syntax_errors": [],
            "todo_items": [],
            "analyzed_files": []
        }

        ignored = {
            ".git", ".gradle", "__pycache__",
            "node_modules", "build", "dist",
            ".venv", "venv"
        }

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if any(part in ignored for part in path.parts):
                continue

            report["total_files"] += 1

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="replace"
                )
            except OSError:
                continue

            lines = content.splitlines()
            report["total_lines"] += len(lines)

            relative = str(path.relative_to(root))

            report["analyzed_files"].append({
                "file": relative,
                "lines": len(lines)
            })

            if not content.strip():
                report["empty_files"].append(relative)

            for number, line in enumerate(lines, 1):
                upper = line.upper()

                if "TODO" in upper or "FIXME" in upper:
                    report["todo_items"].append({
                        "file": relative,
                        "line": number,
                        "text": line.strip()[:200]
                    })

            if path.suffix.lower() == ".py":
                try:
                    ast.parse(content, filename=relative)
                except SyntaxError as error:
                    report["syntax_errors"].append({
                        "file": relative,
                        "line": error.lineno,
                        "error": error.msg
                    })

        return report


if __name__ == "__main__":
    analyzer = CodeAnalyzer()
    result = analyzer.analyze(".")

    output = Path("logs/analysis_report.json")
    output.parent.mkdir(exist_ok=True)

    output.write_text(
        json.dumps(result, indent=4),
        encoding="utf-8"
    )

    print("===== CODE ANALYSIS =====")
    print("PROJECT:", result["project"])
    print("TOTAL FILES:", result["total_files"])
    print("TOTAL LINES:", result["total_lines"])
    print("EMPTY FILES:", len(result["empty_files"]))
    print("SYNTAX ERRORS:", len(result["syntax_errors"]))
    print("TODO ITEMS:", len(result["todo_items"]))
    print("REPORT:", output)
    print("===== ANALYSIS COMPLETED =====")
