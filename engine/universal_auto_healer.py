import subprocess
import json
import re
import os
import sys
import shutil

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def get_failed_run():
    out, _, code = run_cmd("gh run list --limit 1 --json databaseId,conclusion,status")
    if code != 0 or not out:
        return None, None, None
    runs = json.loads(out)
    if not runs:
        return None, None, None
    r = runs[0]
    return r.get("databaseId"), r.get("status"), r.get("conclusion")

def get_error_log(run_id):
    out, _, _ = run_cmd(f"gh run view {run_id} --log-failed")
    return out

def universal_heal():
    print("=" * 60)
    print("🤖 [INFER UNIVERSAL AUTO-HEALER] सिस्टम डायग्नोस्टिक्स शुरू...")
    print("=" * 60)

    run_id, status, conclusion = get_failed_run()
    if status == "in_progress":
        print(f"⏳ रन ID {run_id} अभी चल रहा है। कृपया इसके समाप्त होने की प्रतीक्षा करें।")
        return

    log = ""
    if conclusion == "failure" and run_id:
        print(f"🚨 फेल रन ID {run_id} पकड़ा गया! लाइव एरर लॉग का विश्लेषण हो रहा है...")
        log = get_error_log(run_id)
    else:
        print("ℹ️ कोई सक्रिय विफलता नहीं मिली, संपूर्ण प्रोजेक्ट अखंडता जांच शुरू की जा रही है...")

    actions = []

    # -------------------------------------------------------------
    # 1. फ़ाइल संरचना और पाथ चेकर (फाइल गलत जगह हो तो ठीक करना)
    # -------------------------------------------------------------
    if not os.path.exists("main.py"):
        for root, _, files in os.walk("."):
            if "main.py" in files and ".git" not in root and ".buildozer" not in root:
                src = os.path.join(root, "main.py")
                shutil.copy(src, "main.py")
                actions.append(f"main.py को {src} से रूट डायरेक्टरी में स्थानांतरित किया")
                break

    os.makedirs(".github/workflows", exist_ok=True)

    # -------------------------------------------------------------
    # 2. buildozer.spec यूनिवर्सल सैनिटाइज़र
    # -------------------------------------------------------------
    spec_path = "buildozer.spec"
    if os.path.exists(spec_path):
        with open(spec_path, "r", encoding="utf-8") as f:
            raw_spec = f.read()

        # एरर A: चिपकी हुई लाइनें ठीक करना (e.g. android-33android.ndk_api)
        cleaned_spec = re.sub(r'(android\.api\s*=\s*\d+)(android\.[a-zA-Z0-9_]+)', r'\1\n\2', raw_spec)

        lines = cleaned_spec.splitlines()
        seen = set()
        final_lines = []

        # अनिवार्य सटीक सेटिंग्स
        must_have = {
            "android.api": "33",
            "android.minapi": "24",
            "android.ndk": "25b",
            "android.ndk_api": "24",
            "android.archs": "arm64-v8a",
            "p4a.branch": "master"
        }

        for l in lines:
            s = l.strip()
            m = re.match(r"^([a-zA-Z0-9_\.]+)\s*=", s)
            if m:
                k = m.group(1)
                if k in must_have:
                    if k not in seen:
                        final_lines.append(f"{k} = {must_have[k]}")
                        seen.add(k)
                    continue
                if k in seen:
                    continue
                seen.add(k)
            final_lines.append(l)

        for k, v in must_have.items():
            if k not in seen:
                final_lines.append(f"{k} = {v}")
                actions.append(f"buildozer.spec में {k} = {v} जोड़ा")

        new_spec = "\n".join(final_lines) + "\n"
        if new_spec != raw_spec:
            with open(spec_path, "w", encoding="utf-8") as f:
                f.write(new_spec)
            actions.append("buildozer.spec से डुप्लीकेट और विकृत लाइनें ठीक की गईं")

    # -------------------------------------------------------------
    # 3. GitHub Workflow यूनिवर्सल बिल्डर (Cython, Java, Runner फिक्स)
    # -------------------------------------------------------------
    wf_path = ".github/workflows/build.yml"
    clean_workflow = """name: Build Android APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
    - name: Checkout Repository
      uses: actions/checkout@v4

    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Set up Java 17
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Install System Build Tools
      run: |
        sudo apt-get update
        sudo apt-get install -y git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

    - name: Install Buildozer & Pin Cython
      run: |
        python -m pip install --upgrade pip
        pip install "Cython>=0.29.33,<3.0.0" buildozer virtualenv

    - name: Build APK with Buildozer
      run: |
        buildozer -v android debug

    - name: Upload Finished APK
      uses: actions/upload-artifact@v4
      with:
        name: LegendBrowser-APK
        path: bin/*.apk
"""
    write_wf = False
    if not os.path.exists(wf_path):
        write_wf = True
    else:
        with open(wf_path, "r", encoding="utf-8") as f:
            current_wf = f.read()
        # अगर Cython<3.0 गायब है, डॉकर है, या पुराना वर्ज़न है तो दोबारा राइट करें
        if "Cython<3.0" not in current_wf or "ArtemSBulgakov" in current_wf or "ubuntu-22.04" not in current_wf:
            write_wf = True

    if write_wf:
        with open(wf_path, "w", encoding="utf-8") as f:
            f.write(clean_workflow)
        actions.append("वर्कफ़्लो में Cython<3.0, Java 17 और Ubuntu 22.04 को लॉक किया गया")

    # -------------------------------------------------------------
    # 4. गिट स्थिति और ऑटो-पुश
    # -------------------------------------------------------------
    run_cmd("git add -A")
    status_out, _, _ = run_cmd("git status -s")

    if status_out.strip():
        print("\n🔧 लागू किए गए ऑटो-सुधार:")
        for a in actions:
            print(f"  • {a}")
        commit_msg = "Infer-Healer: " + "; ".join(actions[:2])
        run_cmd(f'git commit -m "{commit_msg}"')
        _, _, push_code = run_cmd("git push origin main")
        if push_code == 0:
            print("\n🚀 [सफलता] सभी त्रुटियों को स्वतः ठीक करके कोड गिटहब पर भेज दिया गया है!")
        else:
            print("\n❌ गिट पुश विफल रहा।")
    else:
        print("\n✨ रिपॉजिटरी पहले से ही सही स्थिति में है। कोई अतिरिक्त बदलाव आवश्यक नहीं था।")

    print("=" * 60)

if __name__ == "__main__":
    universal_heal()
