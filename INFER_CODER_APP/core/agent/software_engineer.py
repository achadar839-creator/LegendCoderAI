import ast
import json
from pathlib import Path

from core.ai.offline_runtime import OfflineAIRuntime
from core.brain.intelligent_planner import IntelligentPlanner
from core.executor.controller import AutonomousExecutor


class SoftwareEngineer:
    def __init__(self, root=None):
        self.root = Path(root or Path(__file__).resolve().parents[2]).resolve()
        self.ai = OfflineAIRuntime(self.root)
        self.planner = IntelligentPlanner(self.root)
        self.executor = AutonomousExecutor(self.root)

    def status(self):
        info = self.ai.status()
        return {"agent": "INFER CODER SOFTWARE ENGINEER", "ai": info,
                "workspace": str(self.executor.workspace), "ready": info["ready"]}

    @staticmethod
    def extract_json(response):
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            if text.rstrip().endswith("```"):
                text = text.rstrip()[:-3]
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end < start:
            raise ValueError("AI did not return JSON.")
        result = json.loads(text[start:end + 1])
        if not isinstance(result, dict):
            raise ValueError("AI response must be a JSON object.")
        return result

    def run(self, instruction):
        instruction = str(instruction).strip()
        if not instruction:
            raise ValueError("Task instruction is empty.")
        if not self.ai.status()["ready"]:
            raise RuntimeError("Offline AI is not ready.")

        task = self.executor.run_task(instruction)
        task_id = task["task_id"]
        context = self.executor.engine.load(task_id).get("execution_context", {})
        plan = self.planner.create_plan(instruction, task_id, context)

        prompt = f"""You are INFER CODER, an offline software engineer.
TASK: {instruction}
PROJECT FILES: {json.dumps(context.get("project_scan", {}).get("files", [])[:80])}
PLAN: {json.dumps(plan.get("steps", []), ensure_ascii=False)}

Return only JSON:
{{"summary":"short summary","files":[{{"path":"file.py","content":"complete content"}}],"tests":["suggested test"]}}
Rules: files must be workspace-relative; never use ../ or absolute paths;
provide complete content; do not claim tests were run; do not modify outside workspace.
"""
        result = self.extract_json(self.ai.generate(prompt, max_tokens=1400, timeout=300))
        files = result.get("files", [])
        if not isinstance(files, list):
            raise ValueError("AI files must be a list.")

        written = []
        for item in files:
            if not isinstance(item, dict):
                raise ValueError("Invalid file entry.")
            path, content = str(item.get("path", "")).strip(), item.get("content")
            if not path or not isinstance(content, str):
                raise ValueError("Invalid file path or content.")
            target = self.executor.safe_path(path)
            if target.suffix.lower() == ".py":
                ast.parse(content, filename=path)
            outcome = self.executor.execute("write_workspace", path=path, content=content)
            written.append(outcome["result"])

        data = self.executor.engine.load(task_id)
        data["status"] = "CODE_GENERATED" if written else "AI_RESPONSE_READY"
        data["ai_summary"] = str(result.get("summary", ""))
        data["generated_files"] = written
        data["suggested_tests"] = result.get("tests", [])
        self.executor.engine.save(data)
        return {"task_id": task_id, "status": data["status"],
                "summary": data["ai_summary"], "generated_files": written,
                "suggested_tests": data["suggested_tests"]}
