import datetime
import json
import os

print("🧠 [Infer Engine]: Action Controller Initializing with Dynamic PIN Sync...")

CONFIG_PATH = os.path.expanduser("~/LegendCoderAI/engine/pin_config.json")

class InferActionBrain:
    def __init__(self):
        pass

    def get_current_pin(self):
        """वर्तमान पिन को सुरक्षित रूप से पढ़ना"""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return str(data.get("pin", "1234")).strip()
            except Exception:
                pass
        return "1234"

    def authorize_system_unlock(self):
        """इनफ़र द्वारा पिन का उपयोग करके लॉक स्क्रीन को खोलना"""
        from engine.lock_overlay import lock_manager
        current_pin = self.get_current_pin()
        lock_manager.pin = current_pin
        lock_manager.auto_bypass()
        print(f"🤖 [Infer Brain]: वर्तमान पिन ({current_pin}) प्रमाणित हुआ। लॉक स्क्रीन हटाई गई।")
        return True

    def parse_command(self, text):
        cmd = text.strip().lower()

        # 1. समय (Time) - हेडलेस मोड
        if any(w in cmd for w in ["टाइम", "समय", "time"]):
            now = datetime.datetime.now()
            t_str = now.strftime("%I बजकर %M मिनट")
            return {
                "action": "speak",
                "data": f"अभी {t_str} हो रहे हैं।",
                "need_screen": False
            }

        # 2. बैटरी (Battery) - हेडलेस मोड
        elif any(w in cmd for w in ["बैटरी", "चार्ज", "battery"]):
            return {
                "action": "speak",
                "data": "बैटरी 75 प्रतिशत के आसपास है।",
                "need_screen": False
            }

        # 3. गाना / म्यूज़िक (Music) - इनफ़र पिन से लॉक खोलेगा
        elif any(w in cmd for w in ["गाना", "म्यूजिक", "song", "play"]):
            self.authorize_system_unlock()
            return {
                "action": "launch_app",
                "data": "ब्राउज़र में बैकग्राउंड म्यूजिक शुरू किया जा रहा है।",
                "need_screen": True
            }

        # 4. ब्राउज़र / सर्च (Browser) - इनफ़र पिन से लॉक खोलेगा
        elif any(w in cmd for w in ["ब्राउज़र", "सर्च", "browser", "खोजो"]):
            self.authorize_system_unlock()
            return {
                "action": "launch_browser",
                "data": "ब्राउज़र खोला जा रहा है।",
                "need_screen": True
            }

        # 5. सीधा 'फोन खोलो' बोलना
        elif any(w in cmd for w in ["अनलॉक", "खोलो", "स्क्रीन खोलो", "unlock"]):
            self.authorize_system_unlock()
            return {
                "action": "unlock_only",
                "data": "फोन अनलॉक कर दिया गया है।",
                "need_screen": True
            }

        else:
            return {
                "action": "speak",
                "data": "आदेश प्राप्त हुआ, प्रक्रिया जारी है।",
                "need_screen": False
            }

infer_brain = InferActionBrain()
