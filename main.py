import os
import sys
import datetime

# ------------------------------------------------------------
# 1. Kivy सुरक्षित आयात (Android APK में GUI, Termux में CLI)
# ------------------------------------------------------------
try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.metrics import dp, sp
    from kivy.core.window import Window
    from kivy.graphics import Color, RoundedRectangle, Line
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.widget import Widget
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

# ------------------------------------------------------------
# 2. आपका असली बैकएंड इंजन (Lock, Action Controller, Pin Sync)
# ------------------------------------------------------------
from engine.lock_overlay import lock_manager
from engine.action_controller import infer_brain

APP_NAME = "INFER AI × COSMIC CODER"

# ------------------------------------------------------------
# 3. फ्यूचरिस्टिक नियॉन विजेट्स (ChatGPT का स्टाइल + आपका कोड)
# ------------------------------------------------------------
if KIVY_AVAILABLE:
    BG = (0.02, 0.03, 0.06, 1)          # गहरा Obsidian Black
    PANEL = (0.05, 0.07, 0.12, 0.95)     # Cyberpunk Glass Panel
    CYAN = (0.0, 0.9, 1.0, 1)            # Electric Neon Cyan
    VIOLET = (0.6, 0.3, 1.0, 1)          # Neon Violet
    GREEN = (0.1, 1.0, 0.5, 1)           # Emerald Green
    WHITE = (0.95, 0.95, 1.0, 1)
    MUTED = (0.5, 0.6, 0.7, 1)

    Window.clearcolor = BG

    def make_label(text="", size=14, color=WHITE, halign="left", bold=False):
        lbl = Label(text=text, font_size=sp(size), color=color, halign=halign, bold=bold)
        lbl.bind(size=lambda w, v: setattr(w, "text_size", v))
        return lbl

    class NeonPanel(BoxLayout):
        def __init__(self, border_color=CYAN, radius=16, **kwargs):
            super().__init__(**kwargs)
            self.padding = dp(14)
            self.spacing = dp(10)
            with self.canvas.before:
                Color(*PANEL)
                self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
                Color(*border_color)
                self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(radius)), width=1.1)
            self.bind(pos=self._redraw, size=self._redraw)

        def _redraw(self, *_):
            self.bg.pos = self.pos
            self.bg.size = self.size
            self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(16))

    class NeonButton(Button):
        def __init__(self, accent=CYAN, **kwargs):
            super().__init__(**kwargs)
            self.background_normal = ""
            self.background_color = (0, 0, 0, 0)
            self.color = accent
            self.bold = True
            self.font_size = sp(14)
            with self.canvas.before:
                Color(accent[0], accent[1], accent[2], 0.12)
                self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
                Color(*accent)
                self.outline = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)), width=1.0)
            self.bind(pos=self._redraw, size=self._redraw)

        def _redraw(self, *_):
            self.bg.pos = self.pos
            self.bg.size = self.size
            self.outline.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))

    # --- स्क्रीन 1: फ्यूचरिस्टिक लॉक स्क्रीन (Infer Guard) ---
    class LockScreenUI(BoxLayout):
        def __init__(self, app, **kwargs):
            super().__init__(orientation="vertical", spacing=dp(12), padding=dp(20), **kwargs)
            self.app = app

            # हेडर व डिजिटल क्लॉक
            self.add_widget(make_label("INFER AI // SECURITY SHIELD", size=14, color=CYAN, bold=True))
            self.lbl_clock = make_label("--:--", size=48, color=WHITE, halign="center", bold=True)
            self.add_widget(self.lbl_clock)

            self.lbl_status = make_label("🔒 सिस्टम लॉक है", size=15, color=MUTED, halign="center")
            self.add_widget(self.lbl_status)

            # क्विक की बटन
            self.btn_key = NeonButton(text="🔑 क्विक पिन दर्ज करें", accent=CYAN, size_hint_y=None, height=dp(48))
            self.btn_key.bind(on_release=self.show_pad)
            self.add_widget(self.btn_key)

            # पिनपैड (शुरुआत में छुपा हुआ)
            self.pad = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(180))
            for b in ["1","2","3","4","5","6","7","8","9","C","0","OK"]:
                btn = NeonButton(text=b, accent=VIOLET if b in ["C","OK"] else CYAN)
                btn.bind(on_release=self.press_pad)
                self.pad.add_widget(btn)

            Clock.schedule_interval(self.tick, 1.0)
            Clock.schedule_interval(self.check_auto_unlock, 0.4)

        def tick(self, _):
            self.lbl_clock.text = datetime.datetime.now().strftime("%I:%M %p")

        def show_pad(self, _):
            lock_manager.tap_key_icon()
            if self.btn_key in self.children:
                self.remove_widget(self.btn_key)
            if self.pad not in self.children:
                self.add_widget(self.pad)
            self.lbl_status.text = "पिन दर्ज करें:"

        def press_pad(self, instance):
            v = instance.text
            if v == "C":
                lock_manager.clear_digits()
                self.lbl_status.text = "पिन साफ़ हुआ"
            elif v == "OK":
                res = lock_manager.submit_pin()
                self.handle_res(res)
            else:
                res = lock_manager.enter_digit(v)
                self.lbl_status.text = f"पिन: {'*' * len(lock_manager.current_digits)}"
                if res.get("unlocked"):
                    self.handle_res(res)

        def handle_res(self, res):
            if res.get("unlocked"):
                self.lbl_status.text = "🔓 एक्सेस स्वीकृत! होम स्क्रीन लोड हो रही है..."
                self.lbl_status.color = GREEN
                Clock.schedule_once(lambda _: self.app.open_main_hub(), 0.3)
            else:
                self.lbl_status.text = "❌ गलत पिन"
                self.lbl_status.color = (1, 0.3, 0.3, 1)

        def check_auto_unlock(self, _):
            if not lock_manager.is_active and "स्वीकृत" not in self.lbl_status.text:
                self.lbl_status.text = "⚡ इनफ़र द्वारा ऑटो-अनलॉक"
                self.lbl_status.color = GREEN
                Clock.schedule_once(lambda _: self.app.open_main_hub(), 0.3)

    # --- स्क्रीन 2: फ्यूचरिस्टिक होम / कोडिंग हब (Cosmic Coder & Infer Core) ---
    class DashboardUI(BoxLayout):
        def __init__(self, app, **kwargs):
            super().__init__(orientation="vertical", spacing=dp(10), padding=dp(14), **kwargs)
            self.app = app

            # टॉप बार
            top = BoxLayout(size_hint_y=None, height=dp(36))
            top.add_widget(make_label("COSMIC CODER // INFER CORE", size=16, color=CYAN, bold=True))
            btn_lock = NeonButton(text="🔒 LOCK", accent=(1, 0.3, 0.3, 1), size_hint_x=0.25)
            btn_lock.bind(on_release=lambda _: self.app.lock_system())
            top.add_widget(btn_lock)
            self.add_widget(top)

            scroll = ScrollView(do_scroll_x=False)
            content = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
            content.bind(minimum_height=content.setter("height"))

            # 1. Infer AI पैनल
            ai_panel = NeonPanel(border_color=CYAN, size_hint_y=None, height=dp(110))
            ai_panel.add_widget(make_label("🎙️ INFER ASSISTANT [ONLINE]", size=13, color=CYAN, bold=True))
            self.lbl_ai_resp = make_label("बोलिए: 'इनफ़र टाइम', 'गाना चलाओ' या टेक्स्ट लिखें...", size=12, color=MUTED)
            ai_panel.add_widget(self.lbl_ai_resp)
            content.add_widget(ai_panel)

            # 2. Cosmic Coder वर्कस्पेस
            coder_panel = NeonPanel(border_color=VIOLET, size_hint_y=None, height=dp(320))
            coder_panel.add_widget(make_label("⌘ COSMIC CODER WORKSPACE", size=14, color=VIOLET, bold=True))

            self.txt_file = TextInput(text="script.py", multiline=False, size_hint_y=None, height=dp(38), background_color=(0.08, 0.1, 0.16, 1), foreground_color=WHITE)
            coder_panel.add_widget(self.txt_file)

            self.txt_prompt = TextInput(hint_text="कोडिंग प्रॉम्प्ट लिखें (उदा. Create a Python calculator)...", multiline=True, size_hint_y=None, height=dp(70), background_color=(0.08, 0.1, 0.16, 1), foreground_color=WHITE)
            coder_panel.add_widget(self.txt_prompt)

            self.txt_editor = TextInput(text="# Cosmic Coder Ready\nprint('System Online')\n", multiline=True, size_hint_y=None, height=dp(110), background_color=(0.08, 0.1, 0.16, 1), foreground_color=WHITE)
            coder_panel.add_widget(self.txt_editor)

            btns = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(8))
            btn_save = NeonButton(text="💾 SAVE", accent=GREEN)
            btn_run = NeonButton(text="⚡ RUN SCRIPT", accent=CYAN)
            btns.add_widget(btn_save)
            btns.add_widget(btn_run)
            coder_panel.add_widget(btns)
            content.add_widget(coder_panel)

            scroll.add_widget(content)
            self.add_widget(scroll)

    class InferNexusApp(App):
        def build(self):
            self.sm = ScreenManager(transition=FadeTransition(duration=0.2))
            
            self.sc_lock = Screen(name="lock")
            self.sc_lock.add_widget(LockScreenUI(self))
            
            self.sc_dash = Screen(name="dash")
            self.sc_dash.add_widget(DashboardUI(self))

            self.sm.add_widget(self.sc_lock)
            self.sm.add_widget(self.sc_dash)
            return self.sm

        def open_main_hub(self):
            self.sm.current = "dash"

        def lock_system(self):
            lock_manager.trigger_overlay()
            self.sm.current = "lock"

# ------------------------------------------------------------
# 4. Termux CLI मोड (बिना किसी क्रैश के सुरक्षित टेस्ट)
# ------------------------------------------------------------
def run_cli_mode():
    print()
    print("=" * 48)
    print(" 🚀 INFER AI × COSMIC CODER (CLI ENGINE)")
    print("=" * 48)
    print(f"🔒 वर्तमान सिस्टम पिन: {lock_manager.pin}")
    print("⚙️ आर्किटेक्चर: हाइब्रिड (Termux CLI + Android Kivy GUI)")
    print("✨ स्टेटस: इंजन पूरी तरह सिंक और रेडी है।")
    print("=" * 48)
    print()

if __name__ == '__main__':
    if KIVY_AVAILABLE:
        InferNexusApp().run()
    else:
        run_cli_mode()
