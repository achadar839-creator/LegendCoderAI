import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .policy import ExecutionPolicy


class AutonomousTaskEngine:

    def __init__(self, root=None):
        self.root = Path(root or Path(__file__).resolve().parents[2])
        self.task_dir = self.root / "workspace" / "tasks"
        self.log_dir = self.root / "logs" / "tasks"

        self.task_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def timestamp(self):
        return datetime.now(timezone.utc).isoformat()

    def create_task(self, instruction):
        instruction = str(instruction).strip()

        if not instruction:
            raise ValueError("Task instruction cannot be empty.")

        task_id = uuid.uuid4().hex[:12]

        steps = [
            {"id": 1, "name": "Understand task", "action": "analyze"},
            {"id": 2, "name": "Inspect project", "action": "scan"},
            {"id": 3, "name": "Prepare execution plan", "action": "analyze"},
            {"id": 4, "name": "Prepare code changes", "action": "write"},
            {"id": 5, "name": "Build and test", "action": "test"},
            {"id": 6, "name": "Verify results", "action": "validate"},
            {"id": 7, "name": "Generate final report", "action": "write"},
        ]

        task = {
            "task_id": task_id,
            "instruction": instruction,
            "status": "PLANNED",
            "created_at": self.timestamp(),
            "updated_at": self.timestamp(),
            "platform": "cross_platform",
            "autonomous_mode": True,
            "completed_steps": [],
            "failed_steps": [],
            "approval_queue": [],
            "steps": steps,
            "repair_attempts": 0,
            "max_repair_attempts": 3
        }

        self.save(task)
        self.log(task_id, "TASK_CREATED", "Task successfully created.")

        return task

    def save(self, task):
        task["updated_at"] = self.timestamp()

        path = self.task_dir / f"{task['task_id']}.json"
        path.write_text(
            json.dumps(task, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

    def load(self, task_id):
        path = self.task_dir / f"{task_id}.json"

        if not path.exists():
            raise FileNotFoundError("Task not found.")

        return json.loads(path.read_text(encoding="utf-8"))

    def authorize(self, task, action):
        decision = ExecutionPolicy.decision(action)

        if decision["approval_required"]:
            task["approval_queue"].append({
                "action": action,
                "risk": decision["risk"],
                "status": "WAITING_FOR_APPROVAL"
            })

            self.log(
                task["task_id"],
                "APPROVAL_REQUIRED",
                f"Action blocked: {action}"
            )
        else:
            self.log(
                task["task_id"],
                "ACTION_AUTHORIZED",
                f"Action permitted: {action}"
            )

        self.save(task)
        return decision

    def complete_step(self, task_id, step_id, evidence):
        task = self.load(task_id)

        step = next(
            (item for item in task["steps"] if item["id"] == step_id),
            None
        )

        if step is None:
            raise ValueError("Invalid step ID.")

        if not evidence:
            raise ValueError("Verification evidence is required.")

        task["completed_steps"].append({
            "step_id": step_id,
            "name": step["name"],
            "evidence": str(evidence),
            "completed_at": self.timestamp()
        })

        task["status"] = "IN_PROGRESS"

        if len(task["completed_steps"]) == len(task["steps"]):
            task["status"] = "COMPLETED"

        self.save(task)
        self.log(task_id, "STEP_COMPLETED", step["name"])

        return task

    def log(self, task_id, event, details):
        path = self.log_dir / f"{task_id}.jsonl"

        entry = {
            "time": self.timestamp(),
            "event": event,
            "details": details
        }

        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")
