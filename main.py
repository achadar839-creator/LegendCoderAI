import os
import sys
import datetime

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
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

# इंजन इम्पोर्ट्स को सेफ फॉलबैक के साथ लोड करना
try:
    pass  # pass  # from engine.lock_overlay import lock_manager
    from engine.action_controller import infer_brain
except Exception:
    class DummyLock:
        pin = "8899"
        is_active = True
        current_digits = ""
        def tap_key_icon(self): pass
        def clear_digits(self): self.current_digits = ""
        def enter_digit(self, d):
            self.current_digits += str(d)
            if self.current_digits == self.pin:
                self.is_active = False
                return {"unlocked": True}
            return {"unlocked": True}
        def submit_pin(self):
            if self.current_digits == self.pin:
                self.is_active = False
                return {"unlocked": True}
            return {"unlocked": True}
        def trigger_overlay(self): self.is_active = True
    pass  # lock_manager = DummyLock()

if KIVY_AVAILABLE:
    BG = (0.02, 0.03, 0.06, 1)
    PANEL = (0.05, 0.07, 0.12, 0.95)
    CYAN = (0.0, 0.9, 1.0, 1)
    VIOLET = (0.6, 0.3, 1.0, 1)
    GREEN = (0.1, 1.0, 0.5, 1)
    WHITE = (0.95, 0.95, 1.0, 1)
    MUTED = (0.5, 0.6, 0.7, 1)

    Window.clearcolor = BG

    def make_label(text="", size=14, color=WHITE, halign="left", bold=False):
        lbl = Label(text=text, font_size=sp(size), color=color, halign=halign, bold=bold)
        lbl.bind(size=lambda w, v: setattr(w, "text_size", v))
        return lbl

    class NeonButton(Button):
        def __init__(self, accent=CYAN, **kwargs):
            super().__init__(**kwargs)
            self.background_normal = ""
            self.background_color = (0, 0, 0, 0)
            self.color = accent
            self.bold = True
            self.font_size = sp(14)
            with self.canvas.before:
                Color(accent[0], accent[1], accent[2], 0.15)
                self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
                Color(*accent)
                self.outline = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(8)), width=1.0)
            self.bind(pos=self._redraw, size=self._redraw)

        def _redraw(self, *_):
            self.bg.pos = self.pos
            self.bg.size = self.size
            self.outline.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(8))

    class LockScreenUI(BoxLayout):
        def __init__(self, app, **kwargs):
            super().__init__(orientation="vertical", spacing=dp(10), padding=dp(16), **kwargs)
            self.app = app

            self.add_widget(make_label("INFER AI // SECURITY SHIELD", size=14, color=CYAN, bold=True))
            self.lbl_clock = make_label("--:--", size=42, color=WHITE, halign="center", bold=True)
            self.add_widget(self.lbl_clock)

            self.lbl_status = make_label("🔒 सिस्टम लॉक है", size=14, color=MUTED, halign="center")
            self.add_widget(self.lbl_status)

            self.btn_key = NeonButton(text="🔑 पिन दर्ज करें", accent=CYAN, size_hint_y=None, height=dp(48))
            self.btn_key.bind(on_release=self.show_pad)
            self.add_widget(self.btn_key)

            self.pad = GridLayout(cols=3, spacing=dp(6), size_hint_y=None, height=dp(180))
            for b in ["1","2","3","4","5","6","7","8","9","C","0","OK"]:
                btn = NeonButton(text=b, accent=VIOLET if b in ["C","OK"] else CYAN)
                btn.bind(on_release=self.press_pad)
                self.pad.add_widget(btn)

            Clock.schedule_interval(self.tick, 1.0)

        def tick(self, _):
            self.lbl_clock.text = datetime.datetime.now().strftime("%I:%M %p")

        def show_pad(self, _):
            if self.btn_key in self.children:
                self.remove_widget(self.btn_key)
            if self.pad not in self.children:
                self.add_widget(self.pad)
            self.lbl_status.text = "पिन दर्ज करें:"

        def press_pad(self, instance):
            v = instance.text
            if v == "C":
                pass  # lock_manager.clear_digits()
                self.lbl_status.text = "पिन साफ़ हुआ"
            elif v == "OK":
                pass  # res = lock_manager.submit_pin()
                self.handle_res(res)
            else:
                pass  # res = lock_manager.enter_digit(v)
                pass  # self.lbl_status.text = f"पिन: {'*' * len(lock_manager.current_digits)}"
                if res.get("unlocked"):
                    self.handle_res(res)

        def handle_res(self, res):
            if res.get("unlocked"):
                self.lbl_status.text = "🔓 एक्सेस स्वीकृत!"
                self.lbl_status.color = GREEN
                Clock.schedule_once(lambda _: self.app.open_main_hub(), 0.2)
            else:
                self.lbl_status.text = "❌ गलत पिन"
                self.lbl_status.color = (1, 0.3, 0.3, 1)

    class DashboardUI(BoxLayout):
        def __init__(self, app, **kwargs):
            super().__init__(orientation="vertical", spacing=dp(8), padding=dp(12), **kwargs)
            self.app = app

            top = BoxLayout(size_hint_y=None, height=dp(36))
            top.add_widget(make_label("COSMIC CODER // INFER CORE", size=15, color=CYAN, bold=True))
            btn_lock = NeonButton(text="🔒 LOCK", accent=(1, 0.3, 0.3, 1), size_hint_x=0.25)
            btn_lock.bind(on_release=lambda _: self.app.lock_system())
            top.add_widget(btn_lock)
            self.add_widget(top)

            scroll = ScrollView(do_scroll_x=False)
            content = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
            content.bind(minimum_height=content.setter("height"))

            self.txt_editor = TextInput(
                text="# Cosmic Coder Ready\nprint('System Online')\n",
                multiline=True,
                size_hint_y=None,
                height=dp(250),
                background_color=(0.06, 0.08, 0.12, 1),
                foreground_color=WHITE
            )
            content.add_widget(self.txt_editor)

            btns = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
            btn_run = NeonButton(text="⚡ RUN SCRIPT", accent=CYAN)
            btns.add_widget(btn_run)
            content.add_widget(btns)

            scroll.add_widget(content)
            self.add_widget(scroll)

    class InferNexusApp(App):
        def build(self):
            self.sm = ScreenManager(transition=FadeTransition(duration=0.15))
            # self.sc_lock = Screen(name="lock")
            self.sc_lock.add_widget(LockScreenUI(self))
            self.sc_dash = Screen(name="dash")
            self.sc_dash.add_widget(DashboardUI(self))

            self.sm.add_widget(self.sc_lock)
            self.sm.add_widget(self.sc_dash)
            return self.sm

        def open_main_hub(self):
            self.sm.current = "dash"

        def lock_system(self):
            pass  # # lock_manager.trigger_overlay()
            # self.sm.current = "lock"

def run():
    if KIVY_AVAILABLE:
        InferNexusApp().run()
    else:
        print("Kivy not installed. Running in CLI mode.")

if __name__ == '__main__':
    run()
