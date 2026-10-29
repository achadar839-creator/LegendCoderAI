import os
import subprocess
from engine.sentinel import CISentinel
from engine.artifact_downloader import ArtifactSiphon

class InferCortex:
    def __init__(self, repo="achadar839-creator/LegendCoderAI"):
        self.repo = repo
        self.sentinel = CISentinel(repo)
        self.siphon = ArtifactSiphon(repo)

    def execute_autonomous_pipeline(self, prompt, target_file="main.py"):
        print(f"\n🧠 [Infer Cortex] नया टास्क प्राप्त हुआ: '{prompt}'")
        
        # 1. कोड जनरेशन का सिमुलेशन / हुक (qwen2.5-coder इंजन यहाँ जुड़ता है)
        print("⚡ [Phase 1] कोड आर्किटेक्टिंग और लोकल सिंटैक्स एनालिसिस...")
        
        # 2. ऑटोमैटिक गिट कमिट और पुश
        print("🚀 [Phase 2] गिट पैकेजिंग और GitHub रिमोट पर डिप्लॉयमेंट...")
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Infer Auto-Build: {prompt[:30]}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("📤 [Phase 2] कोड सफलतापूर्वक GitHub पर पुश हो गया!")
        except Exception as e:
            print(f"⚠️ गिट पुश में समस्या या कोई नया बदलाव नहीं था: {e}")

        # 3. बैकग्राउंड सेंटिनल को एक्टिवेट करना
        print("🛰️ [Phase 3] सेंटिनल सर्विलांस एक्टिवेट...")
        result = self.sentinel.watch_build_until_finish()
        
        if result.get("conclusion") == "success":
            print("🟢 [Phase 4] ग्रीन टिक आ गया! अब APK सीधे फोन में खींचा जा रहा है...")
            apk_path = self.siphon.download_latest_apk(result["id"])
            if apk_path:
                print(f"🎉 [MISSION COMPLETE] आपका नया ऐप इंस्टॉल के लिए तैयार है: {apk_path}")
                return {"status": "SUCCESS", "apk": apk_path}
        else:
            print("🔴 [Phase 4] बिल्ड फ़ेल हुआ! सेंटिनल ऑटो-स्नाइपर एक्टिवेट...")
            error_root = self.sentinel.extract_failure_root_cause(result["id"])
            print("🎯 [असली वजह]:")
            print(error_root)
            return {"status": "FAILED", "error": error_root}

if __name__ == "__main__":
    cortex = InferCortex()
    print("🤖 Infer Cortex सिस्टम पूरी तरह इनिशियलाइज़ हो चुका है!")
