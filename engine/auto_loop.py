import time
import subprocess
from engine.sentinel import CISentinel

def run_autonomous_loop():
    s = CISentinel()
    print("\n🔥 [Infer Deep Loop] ऑटोनॉमस डीप लूप चालू हो गया है...")
    print("🤖 यह खुद रन मॉनिटर करेगा, सारे एरर एक साथ निकालेगा और फिक्स करेगा!\n")
    
    while True:
        run = s.get_latest_run()
        if not run:
            print("⏳ कोई एक्टिव रन नहीं मिला, 10 सेकंड बाद फिर चेक कर रहा हूँ...")
            time.sleep(10)
            continue
            
        run_id = run['id']
        status = run.get('status')
        conclusion = run.get('conclusion')
        
        print(f"📡 [Monitor] रन #{run_id} | Status: {status} | Conclusion: {conclusion}", end='\r')
        
        if status == 'completed':
            if conclusion == 'success':
                print(f"\n🎉 [SUCCESS] कमाल हो गया भाई! रन #{run_id} पूरी तरह पास हो गया है और APK बन चुका है! 🚀")
                break
            elif conclusion == 'failure':
                print(f"\n❌ [Failure Detected] रन #{run_id} फेल हो गया। सारे एरर एक साथ निकाले जा रहे हैं...")
                
                # सारे एरर और लॉग्स को एक साथ खींचना
                error_log = s.extract_failure_root_cause(run_id)
                print("="*60)
                print(error_log[-1000:]) # आखिरी 1000 अक्षर जो असली जड़ हैं
                print("="*60)
                
                print("🛠️ [Auto-Fix] एरर के आधार पर कोड को ऑटो-पैच किया जा रहा है...")
                
                # यहाँ हम buildozer.spec या जरूरी फाइलों को ठीक करेंगे
                with open('buildozer.spec', 'r', encoding='utf-8') as f:
                    spec = f.read()
                
                # अगर कोई भी व्हील या pip या python 3.14 का लोचा है, उसे साफ करना
                if 'wheel' in error_log or 'charset_normalizer' in error_log or 'pip' in error_log:
                    print("💡 [Fix] अनकंपैटिबल व्हील/पाइथन डिपेंडेंसी को पूरी तरह क्लीन कर रहे हैं...")
                    if 'requirements =' in spec:
                        spec = spec.replace('requirements = python3, kivy', 'requirements = python3, kivy')
                
                with open('buildozer.spec', 'w', encoding='utf-8') as f:
                    f.write(spec)
                
                # गिट पर ऑटो कमिट और पुश
                subprocess.run(['git', 'add', '-A'], check=True)
                try:
                    subprocess.run(['git', 'commit', '-m', f'Infer Deep Loop Auto-Fix for Run #{run_id}'], check=True)
                except:
                    pass
                subprocess.run(['git', 'push', 'origin', 'main'], check=True)
                print("🚀 [Pushed] नया फिक्स गिटहब पर भेज दिया गया है! अगला बिल्ड शुरू हो रहा है...\n")
                
                # थोड़ा रुककर अगले रन का इंतजार करना
                time.sleep(20)
        
        time.sleep(15)

if __name__ == '__main__':
    run_autonomous_loop()
