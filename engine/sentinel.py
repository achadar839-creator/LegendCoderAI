import urllib.request
import json
import time
import os
import re
import subprocess

class CISentinel:
    def __init__(self, repo="achadar839-creator/LegendCoderAI"):
        self.repo = repo
        self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.headers = {"User-Agent": "InferSentinel/2.0"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def get_latest_run(self):
        url = f"https://api.github.com/repos/{self.repo}/actions/runs?per_page=1"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                runs = data.get("workflow_runs", [])
                return runs[0] if runs else None
        except Exception as e:
            return {"error": str(e)}

    def watch_build_until_finish(self, callback_status=None, poll_interval=15, timeout=900):
        start_time = time.time()
        print("🛰️ [Sentinel] GitHub Actions की लाइव निगरानी शुरू...")
        while time.time() - start_time < timeout:
            run = self.get_latest_run()
            if not run or "error" in run:
                time.sleep(poll_interval)
                continue
            status = run.get("status")
            conclusion = run.get("conclusion")
            run_id = run.get("id")
            if callback_status:
                callback_status(f"Run #{run_id} - Status: {status}")
            if status == "completed":
                print(f"🏁 [Sentinel] बिल्ड खत्म हुआ! परिणाम: {conclusion}")
                return {"id": run_id, "conclusion": conclusion, "run": run}
            time.sleep(poll_interval)
        return {"error": "Timeout exceeded"}

    def extract_failure_root_cause(self, run_id):
        # अब यह सीधे GH CLI का उपयोग करेगा, कोई 403 एरर नहीं आएगा!
        try:
            res = subprocess.run(["gh", "run", "view", str(run_id), "--log"], stdout=subprocess.PIPE, text=True, errors="ignore")
            lines = res.stdout.splitlines()
            
            start_env = -1
            for i, line in enumerate(lines):
                if 'Buildozer failed to execute the last command' in line:
                    j = i
                    while j >= 0 and ('# ' in lines[j] or '#\t' in lines[j]):
                        j -= 1
                    start_env = j
                    break
                    
            if start_env != -1:
                snippet = []
                for l in lines[max(0, start_env - 40):start_env + 1]:
                    snippet.append(re.sub(r'^\S+\s+\S+\s+\d{4}-\d{2}-\d{2}T\S+\s*', '', l))
                return "\n".join(snippet)
            else:
                snippet = []
                for l in lines:
                    if any(k in l.lower() for k in ["error:", "fatal error:", "exception:"]):
                        snippet.append(re.sub(r'^\S+\s+\S+\s+\d{4}-\d{2}-\d{2}T\S+\s*', '', l))
                return "\n".join(snippet[-20:]) if snippet else "Could not isolate error."
        except Exception as e:
            return f"CLI Log extraction error: {e}"
