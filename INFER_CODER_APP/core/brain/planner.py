import json
from datetime import datetime
from pathlib import Path


class InferBrain:

    def __init__(self):
        self.name = "INFER AI BRAIN"
        self.categories = {
            "create": ["create", "make", "build", "बनाओ", "बनाना"],
            "debug": ["error", "bug", "fix", "debug", "गलती", "ठीक"],
            "analyze": ["analyze", "inspect", "scan", "जांच", "विश्लेषण"],
            "modify": ["change", "update", "modify", "बदलना", "बदलो"],
            "test": ["test", "testing", "verify", "टेस्ट", "जांचो"]
        }

    def understand(self, instruction):
        text = instruction.lower()

        detected = []

        for category, keywords in self.categories.items():
            if any(word in text for word in keywords):
                detected.append(category)

        if not detected:
            detected = ["general"]

        return {
            "instruction": instruction,
            "categories": detected,
            "language": "Hindi/English",
            "received_at": datetime.now().isoformat()
        }

    def create_plan(self, instruction):
        understanding = self.understand(instruction)

        steps = [
            "Understand user requirements",
            "Inspect existing project structure",
            "Identify required files and technologies",
            "Prepare implementation plan",
            "Implement changes after approval",
            "Run relevant tests",
            "Verify results and report status"
        ]

        return {
            "engine": self.name,
            "task": understanding,
            "steps": steps,
            "execution_enabled": False,
            "approval_required": True,
            "status": "PLAN_CREATED"
        }

    def save_plan(self, plan):
        output = Path("logs/brain_plan.json")
        output.parent.mkdir(exist_ok=True)

        output.write_text(
            json.dumps(plan, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

        return output


if __name__ == "__main__":
    brain = InferBrain()

    instruction = input("INFER CODER COMMAND: ").strip()

    if not instruction:
        print("No instruction received.")
    else:
        plan = brain.create_plan(instruction)
        output = brain.save_plan(plan)

        print("\n===== INFER AI BRAIN =====")
        print("TASK:", plan["task"]["instruction"])
        print("CATEGORY:", plan["task"]["categories"])
        print("\n===== EXECUTION PLAN =====")

        for number, step in enumerate(plan["steps"], 1):
            print(f"{number}. {step}")

        print("\nSTATUS:", plan["status"])
        print("APPROVAL REQUIRED:", plan["approval_required"])
        print("SAVED:", output)
