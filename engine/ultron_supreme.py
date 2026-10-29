import subprocess
import json
import re
import os
import time

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def get_run_status():
    out, _, _ = run_cmd("gh run list --limit 1 --json databaseId,status,conclusion")
    if not out: return None
    try:
        return json.loads(out)[0]
    except:
        return None

def heal_error(log):
    fixes = []
    
    # 1. Duplicate Option Error in buildozer.spec
    if "DuplicateOptionError" in log or "already exists" in log:
        with open("buildozer.spec", "r") as f: spec = f.read()
        spec = re.sub(r'(android\.api\s*=\s*\d+)(android\.[a-zA-Z0-9_]+)', r'\1\n\2', spec)
        lines = spec.splitlines()
        seen, new_lines = set(), []
        for line in lines:
            m = re.match(r"^([a-zA-Z0-9_\.]+)\s*=", line.strip())
            if m:
                k = m.group(1)
                if k in seen: continue
                seen.add(k)
            new_lines.append(line)
        with open("buildozer.spec", "w") as f: f.write("\n".join(new_lines) + "\n")
        fixes.append("DuplicateOptionError फिक्स किया")

    # 2. Cython C-Compiler Error
    if "Cython" in log or "fatal error:" in log or "command 'gcc' failed" in log:
        with open(".github/workflows/build.yml", "r") as f: wf = f.read()
        if "Cython==0.29.36" not in wf:
            wf = re.sub(r'pip install.*buildozer.*', 'pip install "Cython==0.29.36" virtualenv\n        pip install buildozer', wf)
            with open(".github/workflows/build.yml", "w") as f: f.write(wf)
            fixes.append("Cython वर्जन 0.29.36 पर लॉक किया")

    # 3. Missing Python Module (Requirements)
    match = re.search(r"ModuleNotFoundError: No module named '(.+?)'", log)
    if match:
        module = match.group(1)
        with open("buildozer.spec", "r") as f: spec = f.read()
        if module not in spec:
            spec = re.sub(r'(requirements\s*=.*)', r'\1, ' + module, spec)
            with open("buildozer.spec", "w") as f: f.write(spec)
            fixes.append(f"मिसिंग मॉड्यूल '{module}' को requirements में जोड़ा")

    return fixes

def ultron_loop():
    print("="*60)
    print("🧠 [ULTRON SUPREME] अखंड ऑटोनोमस लूप चालू हो गया है!")
    print("🎯 लक्ष्य: जब तक हरा निशान (Success) और APK नहीं मिलता, यह नहीं रुकेगा।")
    print("="*60)
    
    last_failed_id = None

    while True:
        run_info = get_run_status()
        if not run_info:
            print("⚠️ गिटहब से संपर्क टूटा, 15 सेकंड में दोबारा कोशिश कर रहा हूँ...")
            time.sleep(15)
            continue
            
        run_id = run_info.get("databaseId")
        status = run_info.get("status")
        conclusion = run_info.get("conclusion")

        if status in ["in_progress", "queued"]:
            print(f"⏳ [RUN: {run_id}] सर्वर पर बिल्ड चल रहा है... इंतज़ार जारी।", end="\r")
            time.sleep(20)
            continue

        if conclusion == "success":
            print(f"\n🎉 [विजय!] बिल्ड {run_id} 100% सक्सेसफुल! हरा निशान आ गया।")
            print("📥 सीधे फोन में APK डाउनलोड किया जा रहा है...")
            run_cmd("gh run download --name LegendBrowser-APK")
            print("✅ [MISSION ACCOMPLISHED] APK आपके फोल्डर में आ चुका है!")
            break

        if conclusion == "failure":
            if run_id == last_failed_id:
                # एक ही रन को बार-बार स्कैन न करे
                time.sleep(20)
                continue
                
            print(f"\n🚨 लाल निशान (Failure) मिला! रन ID: {run_id}")
            print("🔍 लॉग्स डाउनलोड करके एरर स्कैन किया जा रहा है...")
            log_out, _, _ = run_cmd(f"gh run view {run_id} --log-failed")
            
            fixes = heal_error(log_out)
            
            run_cmd("git add -A")
            out, _, _ = run_cmd("git status -s")
            
            if out.strip() and fixes:
                print(f"🛠️ इन्फ़र ने ये फिक्स लागू किए: {', '.join(fixes)}")
                run_cmd(f'git commit -m "Ultron-Supreme Auto-Fix: {fixes[0]}"')
                print("📤 गिटहब पर नया कोड पुश किया जा रहा है...")
                _, _, push_code = run_cmd("git push origin main")
                if push_code == 0:
                    print("🚀 फिक्स सफलता से गिटहब पर भेज दिया गया! नया रन चालू हो गया है।\n")
                    last_failed_id = run_id
                else:
                    print("❌ पुश में नेटवर्क एरर।")
            else:
                print("⚠️ [चेतावनी] एक ऐसा नया एरर मिला है जो इन्फ़र की डिक्शनरी से बाहर है!")
                print("👇 कृपया यह लॉग चंदन भाई को दिखाएँ (लूप रोककर मैनुअल मदद लें):")
                print("\n".join(log_out.splitlines()[-15:]))
                break
                
        time.sleep(20)

if __name__ == "__main__":
    ultron_loop()
