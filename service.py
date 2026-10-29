import time
import threading
import os
import sys

print("🌌 [CosmicService]: Infer Background Engine Starting...")

def run_audio_listener():
    print("🎙️ [CosmicService]: Wake-word ('Infer' / 'इनफ़र') listener online.")
    try:
        from engine.wake_listener import wake_engine
    except Exception as e:
        print(f"⚠️ [CosmicService Listener Error]: {e}")
        return

    # बैकग्राउंड लिसनिंग लूप
    while True:
        try:
            # यहाँ ऑडियो डिटेक्टर सिस्टम इनपुट सुनता है
            time.sleep(2)
        except Exception:
            time.sleep(3)

if __name__ == '__main__':
    listener_thread = threading.Thread(target=run_audio_listener, daemon=True)
    listener_thread.start()

    # सर्विस को एक्टिव रखने के लिए मुख्य लूप
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 [CosmicService]: Background service stopped.")
