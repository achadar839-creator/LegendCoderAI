import json
import shutil
import subprocess
from pathlib import Path


class ModelManager:
    def __init__(self, root=None):
        self.root = Path(
            root or Path(__file__).resolve().parents[2]
        ).resolve()

        self.model_dir = self.root / "models"
        self.config_file = self.root / "config" / "offline_ai.json"
        self.catalog_file = self.root / "config" / "model_catalog.json"

        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.catalog = {
            "lite": {
                "name": "Qwen2.5-Coder 1.5B Q4",
                "size": "940 MB",
                "ram_gb": 3,
                "file": "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
                "url": "https://huggingface.co/bartowski/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf"
            },
            "standard": {
                "name": "Standard Coding Model",
                "size": "2-4 GB",
                "ram_gb": 6,
                "file": "",
                "url": ""
            },
            "advanced": {
                "name": "Advanced Coding Model",
                "size": "4-8 GB",
                "ram_gb": 10,
                "file": "",
                "url": ""
            },
            "ultra": {
                "name": "Ultra Coding Model",
                "size": "8 GB+",
                "ram_gb": 16,
                "file": "",
                "url": ""
            }
        }

        if not self.catalog_file.exists():
            self.catalog_file.write_text(
                json.dumps(self.catalog, indent=4),
                encoding="utf-8"
            )

    def device_info(self):
        ram_gb = 0

        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        ram_gb = int(line.split()[1]) / 1048576
                        break
        except OSError:
            pass

        storage = shutil.disk_usage(self.root)

        return {
            "ram_gb": round(ram_gb, 2),
            "free_storage_gb": round(
                storage.free / (1024 ** 3), 2
            )
        }

    def available_models(self):
        result = []

        for tier, item in self.catalog.items():
            filename = item["file"]
            path = self.model_dir / filename if filename else None

            result.append({
                "tier": tier,
                "name": item["name"],
                "size": item["size"],
                "installed": bool(path and path.is_file()),
                "recommended": (
                    self.device_info()["ram_gb"] >= item["ram_gb"]
                )
            })

        return result

    def select_model(self, tier):
        if tier not in self.catalog:
            raise ValueError("Unknown model tier.")

        item = self.catalog[tier]
        if not item["file"]:
            raise NotImplementedError(
                "This tier needs a verified model download entry."
            )

        model_path = self.model_dir / item["file"]

        if not model_path.is_file():
            raise FileNotFoundError("Selected model is not downloaded.")

        config = json.loads(self.config_file.read_text())

        config["model_file"] = str(model_path.relative_to(self.root))
        config["context_size"] = 2048 if tier == "lite" else 4096
        config["threads"] = 3
        config["gpu_layers"] = 0

        self.config_file.write_text(
            json.dumps(config, indent=4),
            encoding="utf-8"
        )

        return model_path

    def download_model(self, tier):
        if tier not in self.catalog:
            raise ValueError("Unknown model tier.")

        item = self.catalog[tier]

        if not item["url"] or not item["file"]:
            raise NotImplementedError(
                "No verified download source configured for this tier."
            )

        info = self.device_info()
        if info["free_storage_gb"] < 2:
            raise RuntimeError("Insufficient free storage.")

        destination = self.model_dir / item["file"]

        subprocess.run([
            "wget", "-c", "-O", str(destination), item["url"]
        ], check=True)

        return destination
