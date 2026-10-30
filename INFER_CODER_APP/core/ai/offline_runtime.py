import json
import shutil
import subprocess
from pathlib import Path


class OfflineAIRuntime:

    def __init__(self, root=None):
        self.root = Path(
            root or Path(__file__).resolve().parents[2]
        ).resolve()

        self.config_file = self.root / "config" / "offline_ai.json"
        self.model_dir = self.root / "models"

        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.config = {
            "mode": "offline",
            "provider": "llama_cpp_cli",
            "model_file": "",
            "context_size": 2048,
            "threads": 3,
            "gpu_layers": 0,
            "internet_required": False,
            "paid_api_required": False
        }

        if self.config_file.exists():
            saved = json.loads(
                self.config_file.read_text(encoding="utf-8")
            )
            self.config.update(saved)

        self.cli = shutil.which("llama-cli")

    def find_model(self):
        configured = self.config.get("model_file", "")

        if configured:
            path = Path(configured)

            if not path.is_absolute():
                path = self.root / path

            if path.is_file() and path.suffix == ".gguf":
                return path.resolve()

        models = sorted(self.model_dir.glob("*.gguf"))
        return models[0].resolve() if models else None

    def status(self):
        model = self.find_model()

        return {
            "mode": "OFFLINE",
            "runtime_installed": self.cli is not None,
            "model_available": model is not None,
            "model": model.name if model else None,
            "ready": bool(self.cli and model),
            "internet_required": False,
            "paid_api_required": False
        }

    def generate(self, instruction, max_tokens=256, timeout=300):
        if not self.cli:
            raise RuntimeError("llama-cli is not installed.")

        model = self.find_model()

        if model is None:
            raise FileNotFoundError("No GGUF model found.")

        instruction = str(instruction).strip()

        if not instruction:
            raise ValueError("Instruction cannot be empty.")

        prompt = (
            "You are INFER CODER, an offline software engineering AI.\n"
            "Understand the user's task carefully.\n"
            "Give practical, accurate coding solutions.\n"
            "Never claim that code was executed or tested unless verified.\n\n"
            f"USER TASK:\n{instruction}\n\n"
            "INFER CODER RESPONSE:\n"
        )

        command = [
            self.cli,
            "-m", str(model),
            "-c", str(int(self.config.get("context_size", 2048))),
            "-t", str(int(self.config.get("threads", 3))),
            "-n", str(int(max_tokens)),
            "-p", prompt,
            "--no-display-prompt",
            "--no-conversation"
        ]

        result = subprocess.run(
            command,
            cwd=str(self.root),
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            raise RuntimeError(
                "AI generation failed:\n" + result.stderr[-3000:]
            )

        answer = result.stdout.strip()

        if not answer:
            answer = result.stderr.strip()

        if not answer:
            raise RuntimeError("AI returned an empty response.")

        return answer

    def save_config(self):
        self.config_file.write_text(
            json.dumps(self.config, indent=4),
            encoding="utf-8"
        )
