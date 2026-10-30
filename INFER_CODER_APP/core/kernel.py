import json
import platform
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent

class InferCore:

    def __init__(self):
        self.name = "INFER CODER"
        self.config_path = ROOT / "config" / "settings.json"
        self.settings = self.load_settings()

    def load_settings(self):
        with open(self.config_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def system_status(self):
        return {
            "name": self.name,
            "version": self.settings["version"],
            "python": platform.python_version(),
            "system": platform.system(),
            "machine": platform.machine(),
            "status": "ONLINE",
            "time": datetime.now().isoformat(timespec="seconds")
        }

    def start(self):
        print("=" * 40)
        print("       INFER CODER CORE")
        print("=" * 40)

        for key, value in self.system_status().items():
            print(f"{key.upper():12}: {value}")

        print("=" * 40)
        print("CORE INITIALIZED SUCCESSFULLY")

if __name__ == "__main__":
    InferCore().start()
