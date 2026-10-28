import sys
import json
import urllib.request
import urllib.error

class LegendEngine:
    def __init__(self, model="deepseek-coder"):
        self.model = model
        self.ollama_url = "http://127.0.0.1:11434/api/generate"

    def query_ai(self, prompt):
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        req = urllib.request.Request(
            self.ollama_url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                return res.get("response", "Error: No response from model.")
        except urllib.error.URLError as e:
            return f"Ollama Connection Error: Is Ollama running? ({e.reason})"

if __name__ == "__main__":
    print("LegendCoderAI Core Initialized Successfully!")
