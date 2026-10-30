import os
import json
import threading
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

ROOT = Path(__file__).resolve().parent
Window.clearcolor = (0.025, 0.035, 0.065, 1)


class InferCoderApp(App):
    def build(self):
        self.title = "INFER CODER"
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        title = Label(
            text="[b]INFER CODER[/b]\n[i]INFINITY CORE • AI SOFTWARE ENGINEER[/i]",
            markup=True, font_size="22sp", size_hint_y=None, height=dp(85),
            color=(0, 0.9, 1, 1)
        )
        root.add_widget(title)

        self.status = Label(
            text="SYSTEM ONLINE • APK INITIALIZED",
            size_hint_y=None, height=dp(40),
            color=(0.2, 1, 0.6, 1)
        )
        root.add_widget(self.status)

        self.input = TextInput(
            hint_text="Describe the software task...",
            multiline=True, size_hint_y=None, height=dp(120),
            background_color=(0.08, 0.1, 0.15, 1),
            foreground_color=(1, 1, 1, 1)
        )
        root.add_widget(self.input)

        btn = Button(
            text="⚡  START AI TASK",
            size_hint_y=None, height=dp(52),
            background_normal="", background_color=(0, 0.45, 0.65, 1)
        )
        btn.bind(on_release=self.start_task)
        root.add_widget(btn)

        scroll = ScrollView()
        self.output = Label(
            text="INFER CODER READY.\nEnter a task to begin.",
            size_hint_y=None, halign="left", valign="top",
            color=(0.85, 0.9, 1, 1)
        )
        self.output.bind(
            texture_size=lambda obj, size: setattr(obj, "height", size[1])
        )
        self.output.bind(width=lambda obj, width: setattr(obj, "text_size", (width, None)))
        scroll.add_widget(self.output)
        root.add_widget(scroll)

        return root

    def start_task(self, *_):
        task = self.input.text.strip()
        if not task:
            self.status.text = "Please enter a task."
            return

        self.status.text = "PROCESSING..."
        self.output.text = "Inspecting task and initializing AI engine..."

        threading.Thread(target=self.process_task, args=(task,), daemon=True).start()

    def process_task(self, task):
        try:
            from core.agent.software_engineer import SoftwareEngineer
            engineer = SoftwareEngineer(str(ROOT))
            result = engineer.run(task)
            message = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        except Exception as exc:
            message = "CORE STATUS: INITIALIZED\nAI EXECUTION: NOT AVAILABLE\n\n" + str(exc)

        Clock.schedule_once(lambda dt: self.show_result(message), 0)

    def show_result(self, message):
        self.output.text = message
        self.status.text = "TASK FINISHED • CHECK OUTPUT"


if __name__ == "__main__":
    InferCoderApp().run()
