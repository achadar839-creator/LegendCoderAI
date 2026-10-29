import subprocess
import json
import re
import os
import sys

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def get_latest_failed_log():
    out, _, code = run_cmd("gh run list --limit 1 --json databaseId,conclusion,status")
    if code != 0 or not out:
        return None, None
    runs = json.loads(out)
    if not runs:
        return None, None
    run = runs[0]
    run_id = run.get("databaseId")
    conclusion = run.get("conclusion")
    status = run.get("status")

    if status == "in_progress":
        return "IN_PROGRESS", run_id
    if conclusion != "failure":
        return conclusion, run_id

    log_out, _, _ = run_cmd(f"gh run view {run_id} --log-failed")
    return log_out, run_id

def fix_spec_duplicates():
    spec_path = "buildozer.spec"
    if not os.path.exists(spec_path):
        return False
    with open(spec_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    seen_keys = set()
    cleaned = []
    modified = False

    for line in lines:
        stripped = line.strip()
        m = re.match(r"^([a-zA-Z0-9_\.]+)\s*=", stripped)
        if m:
            key = m.group(1)
            if key in seen_keys:
                modified = True
                continue
            seen_keys.add(key)
        cleaned.append(line)

    if modified:
        with open(spec_path, "w", encoding="utf-8") as f:
            f.writelines(cleaned)
    return modified

def fix_spec_concatenated_lines():
    spec_path = "buildozer.spec"
    if not os.path.exists(spec_path):
        return False
    with open(spec_path, "r", encoding="utf-8") as f:
        text = f.read()

    new_text = re.sub(r'(android\.api\s*=\s*\d+)(android\.[a-zA-Z0-9_]+)', r'\1\n\2', text)
    if new_text != text:
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        return True
    return False

def fix_docker_and_ppa_in_workflow():
    wf_path = ".github/workflows/build.yml"
    if not os.path.exists(wf_path):
        return False
    with open(wf_path, "r", encoding="utf-8") as f:
        wf = f.read()

    if "ArtemSBulgakov" in wf or "ppa:openjdk-r/ppa" in wf or "resolute" in wf:
        clean_wf = """name: Build Android APK

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

    - name: Install Buildozer & Cython
      run: |
        python -m pip install --upgrade pip
        pip install --upgrade "Cython<3.0" buildozer virtualenv

    - name: Build APK with Buildozer
      run: |
        buildozer -v android debug

    - name: Upload Finished APK
      uses: actions/upload-artifact@v4
      with:
        name: LegendBrowser-APK
        path: bin/*.apk
"""
        with open(wf_path, "w", encoding="utf-8") as f:
            f.write(clean_wf)
        return True
    return False

def fix_missing_dependencies(log_text):
    spec_path = "buildozer.spec"
    if not os.path.exists(spec_path):
        return False
    modified = False

    # Cython 3 vs Cython < 3.0 incompatibility
    if "Cython" in log_text and ("compile" in log_text or "legacy-install-failure" in log_text):
        wf_path = ".github/workflows/build.yml"
        if os.path.exists(wf_path):
            with open(wf_path, "r", encoding="utf-8") as f:
                wf = f.read()
            if "Cython<3.0" not in wf:
                wf = re.sub(r'pip install.*buildozer.*', 'pip install --upgrade "Cython<3.0" buildozer virtualenv', wf)
                with open(wf_path, "w", encoding="utf-8") as f:
                    f.write(wf)
                modified = True

    return modified

def auto_heal():
    log_data, run_id = get_latest_failed_log()
    if log_data == "IN_PROGRESS":
        print(f"⏳ रन ID {run_id} अभी चल रहा है... इंतज़ार करें।")
        return False
    elif log_data == "success":
        print(f"🎉 रन ID {run_id} पहले ही सफल हो चुका है! APK तैयार है।")
        return False
    elif log_data is None:
        print("⚠️ कोई फेल्ड रन या गिटहब लॉग नहीं मिला।")
        return False

    print(f"🚨 फेल्ड रन ID: {run_id} मिला। एरर का विश्लेषण शुरू...")
    fixes_applied = []

    # 1. डुप्लीकेट कीज चेक
    if "DuplicateOptionError" in log_data or fix_spec_duplicates():
        fixes_applied.append("buildozer.spec से डुप्लीकेट विकल्प हटाए गए")

    # 2. चिपकी हुई सिंटैक्स लाइनें
    if "Failed to find package platforms;" in log_data or fix_spec_concatenated_lines():
        fixes_applied.append("buildozer.spec में चिपकी हुई लाइन्स अलग की गईं")

    # 3. Docker / PPA 404 क्रैश
    if "ppa:openjdk-r/ppa" in log_data or "resolute Release" in log_data or fix_docker_and_ppa_in_workflow():
        fixes_applied.append("वर्कफ़्लो से टूटा हुआ डॉकर हटाकर नेटिव Ubuntu 22.04 + Java 17 लगाया गया")

    # 4. मिसिंग लाइब्रेरीज़ या Cython एरर
    if fix_missing_dependencies(log_data):
        fixes_applied.append("डिपेंडेंसी व Cython पिनिंग दुरुस्त की गई")

    if not fixes_applied:
        # अगर कोई ज्ञात पैटर्न मैच न हुआ हो तो भी स्पेक और वर्कफ़्लो को क्लीन फॉर्मेट में रीसेट करें
        if fix_spec_duplicates() or fix_spec_concatenated_lines():
            fixes_applied.append("सामान्य स्पेक क्लीनअप लागू किया गया")

    if fixes_applied:
        print("\n🛠️ लागू किए गए फिक्स:")
        for fix in fixes_applied:
            print(f"  • {fix}")

        commit_msg = "Auto-Heal: " + "; ".join(fixes_applied)
        run_cmd("git add buildozer.spec .github/workflows/build.yml")
        run_cmd(f'git commit -m "{commit_msg}"')
        _, _, push_code = run_cmd("git push origin main")
        if push_code == 0:
            print(f"\n🚀 [सफलता] कोड खुद ठीक करके गिटहब पर पुश कर दिया गया है!")
            return True
        else:
            print("❌ पुश करने में विफलता आई। नेटवर्क या गिट क्रेडेंशियल्स जांचें।")
            return False
    else:
        print("⚠️ कोई स्वचालित सुधार लागू नहीं हो सका। लॉग्स की मैन्युअल समीक्षा करें।")
        return False

if __name__ == "__main__":
    auto_heal()
