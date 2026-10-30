import json
from datetime import datetime, timezone
from pathlib import Path


class IntelligentPlanner:

    def __init__(self, root=None):
        self.root = Path(root or Path(__file__).resolve().parents[2])
        self.plan_dir = self.root / "logs" / "plans"
        self.plan_dir.mkdir(parents=True, exist_ok=True)

    def analyze_intent(self, instruction):
        text = instruction.lower()

        categories = []

        patterns = {
            "create": ["create", "build", "develop", "make", "बनाओ", "बनाना"],
            "debug": ["debug", "fix", "repair", "error", "crash", "ठीक"],
            "modify": ["modify", "change", "update", "edit", "बदलना"],
            "analyze": ["analyze", "inspect", "review", "check", "जांच"],
            "test": ["test", "testing", "validate", "verify", "टेस्ट"],
            "research": ["research", "find", "search", "compare", "खोज"]
        }

        for category, keywords in patterns.items():
            if any(word in text for word in keywords):
                categories.append(category)

        return categories or ["general"]

    def select_steps(self, categories):
        steps = [
            "Understand user requirements",
            "Inspect existing project architecture",
            "Identify relevant files and dependencies",
            "Create a detailed execution plan"
        ]

        if "create" in categories:
            steps += [
                "Design required components",
                "Generate implementation",
                "Integrate new components"
            ]

        if "modify" in categories:
            steps += [
                "Identify existing implementation",
                "Prepare minimal code changes",
                "Preserve existing functionality"
            ]

        if "debug" in categories:
            steps += [
                "Collect error information",
                "Locate the root cause",
                "Prepare a repair",
                "Recheck the affected components"
            ]

        if "analyze" in categories:
            steps += [
                "Analyze architecture and source code",
                "Identify risks and improvements"
            ]

        if "test" in categories:
            steps += [
                "Prepare test cases",
                "Execute available tests",
                "Verify test results"
            ]

        if "research" in categories:
            steps += [
                "Identify required technical information",
                "Evaluate available solutions",
                "Record findings"
            ]

        steps += [
            "Run validation",
            "Review possible regressions",
            "Generate final evidence-based report"
        ]

        return steps

    def create_plan(self, instruction, task_id, context=None):
        categories = self.analyze_intent(instruction)
        steps = self.select_steps(categories)

        plan = {
            "task_id": task_id,
            "instruction": instruction,
            "categories": categories,
            "status": "PLANNED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "project_context": context or {},
            "steps": [
                {
                    "step_id": index + 1,
                    "description": description,
                    "status": "PENDING"
                }
                for index, description in enumerate(steps)
            ]
        }

        output = self.plan_dir / f"{task_id}_plan.json"
        output.write_text(
            json.dumps(plan, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

        return plan
