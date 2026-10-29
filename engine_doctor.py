import sys
import os

sys.path.append('.')

print("="*40)
print("🔍 COSMIC CODER: ENGINE DOCTOR RUNNING...")
print("="*40)

modules = [
    ("Voice Core", "engine.voice_core"),
    ("Live Sandbox", "engine.live_sandbox"),
    ("Plugin Manager", "engine.plugin_manager"),
    ("Self Healing", "engine.self_healing")
]

failed = False

for name, mod in modules:
    try:
        __import__(mod)
        print(f"✅ {name}: 100% OK & Safe")
    except Exception as e:
        print(f"❌ {name}: FAILED! एरर मिला -> {e}")
        failed = True

print("="*40)
if not failed:
    print("🎉 नतीजा: सारे इंजन बिल्कुल स्वस्थ और दुरुस्त हैं!")
else:
    print("⚠️ चेतावनी: कुछ इंजनों में ऊपर दिए गए एरर को ठीक करना होगा।")
print("="*40)
