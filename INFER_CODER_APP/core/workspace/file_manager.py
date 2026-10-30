from pathlib import Path
from datetime import datetime
import shutil


class WorkspaceManager:

    def __init__(self, workspace="workspace"):
        self.root = Path(workspace).resolve()
        self.backups = self.root / "backups"
        self.root.mkdir(parents=True, exist_ok=True)
        self.backups.mkdir(parents=True, exist_ok=True)

    def safe_path(self, filename):
        target = (self.root / filename).resolve()

        if not target.is_relative_to(self.root):
            raise PermissionError("Access outside workspace denied")

        if target == self.backups or self.backups in target.parents:
            raise PermissionError("Direct backup access denied")

        return target

    def list_files(self):
        return [
            str(path.relative_to(self.root))
            for path in self.root.rglob("*")
            if path.is_file()
            and self.backups not in path.parents
        ]

    def read_file(self, filename):
        target = self.safe_path(filename)

        if not target.is_file():
            raise FileNotFoundError(filename)

        if target.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("File exceeds 2 MB read limit")

        return target.read_text(encoding="utf-8")

    def write_file(self, filename, content, approved=False):
        if not approved:
            raise PermissionError("User approval required")

        target = self.safe_path(filename)

        if not isinstance(content, str):
            raise TypeError("Content must be text")

        if len(content.encode("utf-8")) > 2 * 1024 * 1024:
            raise ValueError("File exceeds 2 MB write limit")

        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            backup_name = f"{timestamp}_{target.name}"
            shutil.copy2(target, self.backups / backup_name)

        target.write_text(content, encoding="utf-8")

        return str(target)


if __name__ == "__main__":
    manager = WorkspaceManager()

    print("===== INFER FILE MANAGER =====")
    print("WORKSPACE:", manager.root)
    print("EXISTING FILES:", manager.list_files())

    test_file = manager.write_file(
        "engine_test.txt",
        "INFER CODER File Manager is working.",
        approved=True
    )

    print("TEST FILE CREATED:", test_file)
    print("TEST CONTENT:", manager.read_file("engine_test.txt"))

    try:
        manager.safe_path("../outside.txt")
    except PermissionError:
        print("PATH SECURITY: PASSED")

    print("===== FILE MANAGER ONLINE =====")
