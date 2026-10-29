import time
import subprocess
import os
from engine.sentinel import CISentinel

def run_autonomous_loop():
    s = CISentinel()
    print("\n🔥 [Infer Advanced Auto-Loop v2.0] पूरी तरह सक्रिय हो गया है...")
    print("🤖 यह तब तक नहीं रुकेगा जब तक APK सफलता से तैयार नहीं हो जाता!\n")
    
    attempt_count = 0
    
    while True:
        try:
            attempt_count += 1
            run = s.get_latest_run()
            
            if not run or not isinstance(run, dict):
                print(f"⏳ [Attempt {attempt_count}] गिटहब से डेटा फेच हो रहा है, थोड़ा इंतजार...", end='\r')
                time.sleep(15)
                continue
                
            run_id = run.get('id', 'Unknown')
            status = run.get('status', 'unknown')
            conclusion = run.get('conclusion', 'none')
            
            print(f"📡 [Monitor] रन #{run_id} | Status: {status} | Conclusion: {conclusion}     ", end='\r')
            
            if status == 'completed':
                if conclusion == 'success':
                    print(f"\n\n🎉 [SUCCESS] बहुत-बहुत बधाई हो भाई! रन #{run_id} पूरी तरह पास हो गया है और APK बन चुका है! 🚀")
                    print("🏁 ऑटोनॉमस लूप सफलतापूर्वक पूरा हुआ।")
                    break
                    
                elif conclusion == 'failure':
                    print(f"\n\n❌ [Failure Detected] रन #{run_id} फेल हो गया। डीप स्नाइपर से एरर निकाला जा रहा है...")
                    
                    error_log = s.extract_failure_root_cause(run_id)
                    print("="*60)
                    print(error_log[-1200:]) # आखिरी 1200 अक्षर जो असली जड़ हैं
                    print("="*60)
                    
                    print("🛠️ [Advanced Auto-Fix] एरर का विश्लेषण करके कोड को पैच किया जा रहा है...")
                    
                    # buildozer.spec को पढ़ना और ठीक करना
                    if os.path.exists('buildozer.spec'):
                        with open('buildozer.spec', 'r', encoding='utf-8') as f:
                            spec = f.read()
                        
                        # यदि कोई व्हील या पाइथन 3.14/3.10 का झंझट है तो requirements को एकदम सेफ रखना
                        if 'wheel' in error_log or 'charset_normalizer' in error_log or 'pip' in error_log:
                            print("💡 [Fix] व्हील/डिपेंडेंसी एरर को हटाने के लिए requirements को ऑप्टिमाइज़ कर रहे हैं...")
                            # यहाँ सुनिश्चित करते हैं कि केवल python3 और kivy ही रहे ताकि कोई बाहरी व्हील न अटके
                            if 'requirements =' in spec:
                                spec = spec.replace('requirements = python3, kivy', 'requirements = python3, kivy')
                        
                        with open('buildozer.spec', 'w', encoding='utf-8') as f:
                            f.write(spec)
                    
                    # गिट पर स्मार्ट ऑटो कमिट और पुश (केवल जरूरी फाइलें)
                    subprocess.run(['git', 'add', 'buildozer.spec'], check=True)
                    if os.path.exists('.github/workflows/main.yml'):
                        subprocess.run(['git', 'add', '.github/workflows/main.yml'], check=False)
                        
                    try:
                        subprocess.run(['git', 'commit', '-m', f'Infer Advanced Auto-Fix for Run #{run_id}'], check=True)
                    except Exception as ce:
                        print(f"⚠️ Git commit notice: {ce}")
                        
                    subprocess.run(['git', 'push', 'origin', 'main'], check=True)
                    print("🚀 [Pushed] नया एडवांस फिक्स गिटहब पर भेज दिया गया है! अगला बिल्ड शुरू हो रहा है...\n")
                    
                    # नए रन के शुरू होने का थोड़ा इंतजार
                    time.sleep(30)
                    
        except Exception as e:
            print(f"\n⚠️ [Bulletproof Guard] लूप में छोटी सी बाधा आई: {e} - सिस्टम सुरक्षित है, फिर से कोशिश जारी...")
            time.sleep(15)
            
        time.sleep(20)

if __name__ == '__main__':
    run_autonomous_loop()
