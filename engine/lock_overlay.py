import sys
import os
import json

CONFIG_PATH = os.path.expanduser("~/LegendCoderAI/engine/pin_config.json")

print("🛡️ [Infer Lock]: Advanced Overlay Engine (Dynamic PIN) Initialized...")

class LockScreenManager:
    def __init__(self):
        self.pin = self.load_pin()
        self.is_active = True
        self.show_keypad = False
        self.current_digits = ""

    def load_pin(self):
        """फ़ाइल से सेव किया हुआ पिन लोड करना"""
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return str(data.get("pin", "1234")).strip()
            except Exception:
                pass
        return "1234"

    def set_new_pin(self, new_pin):
        """नया पिन सेट और सेव करना"""
        clean_pin = str(new_pin).strip()
        if len(clean_pin) >= 4 and clean_pin.isdigit():
            self.pin = clean_pin
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"pin": self.pin}, f)
            print(f"🔐 [Infer Lock]: नया पिन सफलतापूर्वक सेट हो गया: {self.pin}")
            return True, "नया पिन सेव हो गया।"
        return False, "पिन कम से कम 4 अंकों का होना चाहिए।"

    def trigger_overlay(self):
        self.is_active = True
        self.show_keypad = False
        self.current_digits = ""
        return {"is_active": True, "show_keypad": False}

    def tap_key_icon(self):
        self.show_keypad = True
        return {"show_keypad": True}

    def enter_digit(self, digit):
        if not self.show_keypad:
            self.show_keypad = True
        
        self.current_digits += str(digit).strip()
        
        if len(self.current_digits) >= len(self.pin):
            return self.submit_pin()
        return {"unlocked": False, "length": len(self.current_digits)}

    def clear_digits(self):
        self.current_digits = ""
        return {"current": ""}

    def submit_pin(self):
        if self.current_digits == self.pin:
            self.is_active = False
            self.show_keypad = False
            self.current_digits = ""
            print("🔓 [Infer Lock]: PIN Matched! Access Granted.")
            return {"unlocked": True, "message": "सफलतापूर्वक अनलॉक हो गया।"}
        else:
            self.current_digits = ""
            print("❌ [Infer Lock]: Wrong PIN entered.")
            return {"unlocked": False, "message": "गलत पिन। पुनः प्रयास करें।"}

    def auto_bypass(self):
        self.is_active = False
        self.show_keypad = False
        return True

lock_manager = LockScreenManager()
