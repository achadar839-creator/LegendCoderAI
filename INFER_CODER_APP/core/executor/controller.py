import ast
import json
import shutil
import time
from pathlib import Path

from core.autonomy.task_engine import AutonomousTaskEngine
from core.autonomy.policy import ExecutionPolicy


class AutonomousExecutor:

    def __init__(self, root=None):
        self.root = Path(root or Path(__file__).resolve().parents[2]).resolve()
        self.engine = AutonomousTaskEngine(self.root)
        self.workspace = (self.root / "workspace").resolve()
        self.backups = self.workspace / "backups"
        self.backups.mkdir(parents=True, exist_ok=True)

        self.actions = {
            "scan_project": self.scan_project,
            "list_workspace": self.list_workspace,
            "read_workspace": self.read_workspace,
            "write_workspace": self.write_workspace,
            "validate_python": self.validate_python,
        }

    def safe_path(self, relative_path):
        target = (self.workspace / relative_path).resolve()

        if target != self.workspace and self.workspace not in target.parents:
            raise PermissionError("Path outside workspace is blocked.")

        return target

    def scan_project(self):
        extensions = {
            ".py", ".kt", ".java", ".cpp", ".c", ".cs",
            ".js", ".ts", ".html", ".css", ".json",
            ".xml", ".yaml", ".yml", ".swift", ".go",
            ".rs", ".dart", ".sh", ".md"
        }

        ignored = {
            ".git", ".gradle", "__pycache__",
            "node_modules", ".venv", "venv", "build", "dist"
        }

        files = []

        for path in self.root.rglob("*"):
            if any(part in ignored for part in path.parts):
                continue

            if path.is_file() and path.suffix.lower() in extensions:
                files.append(str(path.relative_to(self.root)))

        return {
            "file_count": len(files),
            "files": files[:500]
        }

    def list_workspace(self):
        files = []

        for path in self.workspace.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(self.workspace)))

        return {"file_count": len(files), "files": files[:300]}

    def read_workspace(self, path):
        target = self.safe_path(path)

        if not target.is_file():
            raise FileNotFoundError("Workspace file not found.")

        if target.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("File exceeds 2 MB limit.")

        return {"path": str(target), "content": target.read_text(encoding="utf-8")}

    def write_workspace(self, path, content):
        target = self.safe_path(path)

        if len(content.encode("utf-8")) > 2 * 1024 * 1024:
            raise ValueError("Content exceeds 2 MB limit.")

        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            backup = self.backups / f"{int(time.time() * 1000)}_{target.name}"
            shutil.copy2(target, backup)

        temp = target.with_name(target.name + ".tmp")
        temp.write_text(content, encoding="utf-8")
        temp.replace(target)

        return {
            "written": True,
            "path": str(target.relative_to(self.workspace)),
            "backup_created": target.exists()
        }

    def validate_python(self, path):
        target = self.safe_path(path)

        if target.suffix != ".py" or not target.is_file():
            raise ValueError("A Python file inside workspace is required.")

        source = target.read_text(encoding="utf-8")
        ast.parse(source, filename=str(target))

        return {"valid": True, "path": str(target.relative_to(self.workspace))}

    def execute(self, action, **arguments):
        if action not in self.actions:
            raise PermissionError(f"Action not available: {action}")

        policy_action = {
            "scan_project": "scan",
            "list_workspace": "inspect",
            "read_workspace": "read",
            "write_workspace": "write",
            "validate_python": "validate",
        }[action]

        decision = ExecutionPolicy.decision(policy_action)

        if not decision["allowed"]:
            raise PermissionError("Action requires approval.")

        result = self.actions[action](**arguments)

        return {
            "status": "SUCCESS",
            "action": action,
            "result": result
        }

    def run_task(self, instruction):
        task = self.engine.create_task(instruction)
        task_id = task["task_id"]

        self.engine.log(task_id, "EXECUTOR_STARTED", "Execution controller started.")

        try:
            scan = self.execute("scan_project")
            self.engine.log(
                task_id, "PROJECT_SCANNED",
                f"Files discovered: {scan['result']['file_count']}"
            )

            workspace = self.execute("list_workspace")
            self.engine.log(
                task_id, "WORKSPACE_INSPECTED",
                f"Files found: {workspace['result']['file_count']}"
            )

            task = self.engine.load(task_id)
            task["status"] = "READY_FOR_AI_PLANNING"
            task["execution_context"] = {
                "project_scan": scan["result"],
                "workspace": workspace["result"]
            }

            self.engine.save(task)
            self.engine.log(
                task_id, "CONTEXT_READY",
                "Project context collected for intelligent planning."
            )

            return {
                "task_id": task_id,
                "status": task["status"],
                "project_files": scan["result"]["file_count"],
                "workspace_files": workspace["result"]["file_count"]
            }

        except Exception as error:
            task = self.engine.load(task_id)
            task["status"] = "FAILED"
            task["error"] = str(error)
            self.engine.save(task)
            self.engine.log(task_id, "EXECUTION_FAILED", str(error))
            raise
