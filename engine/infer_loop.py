import time
import subprocess
import re
from engine.sentinel import CISentinel
from engine.artifact_downloader import ArtifactSiphon

class InferLoop:
    def __init__(self):
        self.sentinel = CISentinel()
        self.siphon = ArtifactSiphon()
        self.max_retries = 3 # सेफ्टी के लिए अधिकतम 3 बार खुद को फिक्स करने की कोशिश करेगा

    def ai_heal_error(self, error_log):
        print("\n🧠 [Infer AI] एरर का विश्लेषण कर रहा है...")
        with open("buildozer.spec", "r", encoding="utf-8") as f:
            spec = f.read()

        fixed = False
        # Rule 1: SDK/NDK Mismatch Rule
        if "minsdk argument does not match" in error_log or "allow-minsdk-ndkapi-mismatch" in error_log:
            print("💡 [Infer AI] Minsdk mismatch डिटेक्ट हुआ! NDK API 24 पर लॉक कर रहा हूँ...")
            spec = re.sub(r'^#?\s*android\.ndk_api\s*=.*', 'android.ndk_api = 24', spec, flags=re.MULTILINE)
            spec = re.sub(r'^#?\s*android\.minapi\s*=.*', 'android.minapi = 24', spec, flags=re.MULTILINE)
            fixed = True

        # Rule 2: Dependency Mismatch
        elif "Didn't find any valid dependency graphs" in error_log:
            print("💡 [Infer AI] Dependency graph एरर! sdl2 बूटस्ट्रैप सेट कर रहा हूँ...")
            spec = re.sub(r'^#?\s*p4a\.bootstrap\s*=.*', 'p4a.bootstrap = sdl2', spec, flags=re.MULTILINE)
            fixed = True

        # (भविष्य में यहाँ आपका लोकल Ollama/Llama-3 मॉडल जुड़ेगा जो किसी भी अनजाने एरर को खुद पढ़ेगा)

        if fixed:
            with open("buildozer.spec", "w", encoding="utf-8") as f:
                f.write(spec)
            return True
        else:
            print("⚠️ [Infer AI] यह एक नया एरर है! (डीप AI एनालिसिस की जरूरत है)")
            return False

    def start_autonomous_loop(self):
        # सबसे पहले मौजूदा पेंच (minsdk) को फिक्स करके पुश करना
        self.ai_heal_error("minsdk argument does not match")
        try:
            subprocess.run(["git", "add", "buildozer.spec"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "commit", "-m", "Infer Auto-Heal: Synchronize API 24"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "push", "origin", "main"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("📤 [Infer] इनिशियल फिक्स गिटहब पर भेज दिया गया है!")
        except Exception:
            pass # अगर पहले से पुश्ड होगा तो इग्नोर करे

        for attempt in range(1, self.max_retries + 1):
            print(f"\n🔄 [Infer Loop] साइकिल #{attempt} - गिटहब बिल्ड की लाइव निगरानी शुरू...")
            
            def print_status(msg):
                print(f"   -> {msg}       ", end="\r")
            
            result = self.sentinel.watch_build_until_finish(callback_status=print_status)
            
            if result.get("conclusion") == "success":
                print("\n🟢 [Infer] मिशन सक्सेसफुल! ग्रीन टिक आ गया!")
                print("📥 [Infer Siphon] APK डाउनलोड कर रहा है...")
                apk_path = self.siphon.download_latest_apk(result["id"])
                print(f"\n🎉 [COMPLETE] आपका नया ऐप यहाँ सेव है: {apk_path}")
                break
            else:
                print("\n🔴 [Infer] बिल्ड फेल हुआ! एरर स्नाइपर एक्टिवेट...")
                error_log = self.sentinel.extract_failure_root_cause(result["id"])
                print("🎯 [एरर]:\n", error_log)
                
                healed = self.ai_heal_error(error_log)
                if healed:
                    print("🚀 [Infer] एरर फिक्स कर दिया गया! नया कोड गिटहब पर पुश कर रहा है...")
                    subprocess.run(["git", "add", "buildozer.spec"], check=True)
                    subprocess.run(["git", "commit", "-m", f"Infer Auto-Heal Loop: Attempt {attempt}"], check=True)
                    subprocess.run(["git", "push", "origin", "main"], check=True)
                    print("⏳ गिटहब एक्शन रिस्टार्ट होने का इंतज़ार (15 सेकंड)...")
                    time.sleep(15)
                else:
                    print("🛑 [Infer] यह एरर अभी के रूल्स से बाहर है। कृपया इसे मैन्युअली चेक करें।")
                    break

if __name__ == "__main__":
    loop = InferLoop()
    loop.start_autonomous_loop()
