import subprocess
import urllib.request
import json
import re
import os

REPO = "achadar839-creator/LegendCoderAI"

def get_git_token():
    # 1. एनवायरनमेंट वेरिएबल चेक
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    # 2. gh cli चेक
    try:
        res = subprocess.run(["gh", "auth", "token"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    # 3. git credentials स्टोर चेक
    try:
        res = subprocess.run(["git", "config", "--get", "user.password"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None

def main():
    print("🔍 [Ultron Sniper v2] रन स्टेटस स्कैन कर रहा है...")
    token = get_git_token()
    
    headers = {"User-Agent": "UltronAgent/2.0"}
    if token:
        headers["Authorization"] = f"token {token}"
        print("🔑 गिटहब टोकन डिटेक्ट हो गया!")
    else:
        print("⚠️ बिना टोकन के पब्लिक एपीआई मोड में चल रहा है...")

    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=1"
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            latest = data["workflow_runs"][0]
            run_id = latest["id"]
            jobs_url = latest["jobs_url"]
            print(f"📡 रन ID: #{run_id} | स्थिति: {latest['status']} | परिणाम: {latest.get('conclusion')}")

        req_jobs = urllib.request.Request(jobs_url, headers=headers)
        with urllib.request.urlopen(req_jobs) as j_resp:
            j_data = json.loads(j_resp.read().decode('utf-8'))
            job = j_data["jobs"][0]
            job_id = job["id"]

        # अगर gh cli मौजूद है तो सीधे उससे लॉग ले लो
        try:
            gh_run = subprocess.run(["gh", "run", "view", "--job", str(job_id), "--log-failed"], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if gh_run.returncode == 0 and gh_run.stdout.strip():
                print("\n🎯 [GH CLI से निकला असली एरर]:")
                print("="*50)
                print(gh_run.stdout[-2500:])
                print("="*50)
                return
        except Exception:
            pass

        # API से डायरेक्ट लॉग
        log_url = f"https://api.github.com/repos/{REPO}/actions/jobs/{job_id}/logs"
        req_log = urllib.request.Request(log_url, headers=headers)
        with urllib.request.urlopen(req_log) as l_resp:
            raw_logs = l_resp.read().decode('utf-8', errors='ignore').splitlines()

        print("\n🧠 [Ultron Analyzer] बिल्ड फ़ेलियर का हिस्सा:")
        print("="*50)
        target_idx = -1
        for i, line in enumerate(raw_logs):
            if "Buildozer failed to execute the last command" in line:
                target_idx = i
                break

        if target_idx != -1:
            start = max(0, target_idx - 35)
            for line in raw_logs[start:target_idx]:
                clean = re.sub(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s*', '', line)
                print(clean)
        else:
            for line in raw_logs[-35:]:
                print(re.sub(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s*', '', line))
        print("="*50)

    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"❌ 403 Forbidden: गिटहब ने लॉग ब्लॉक किया।")
            print("👉 तुरंत फिक्स: टर्मक्स में 'gh auth login' चलाएं या टोकन सेट करें: export GITHUB_TOKEN=your_pat_token")
        else:
            print(f"❌ HTTP Error: {e}")
    except Exception as e:
        print(f"❌ एरर: {e}")

if __name__ == "__main__":
    main()
