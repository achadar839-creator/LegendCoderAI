# Voice-to-Code & Chat Engine: Cosmic Coder Safe Audio Bridge

# Safe imports to prevent Android APK native crash
try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

def init_tts():
    if not HAS_TTS:
        return None
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        voices = engine.getProperty('voices')
        for voice in voices:
            if "en" in voice.id.lower() or "zira" in voice.id.lower() or "guy" in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        return engine
    except Exception as e:
        print(f"[TTS Init Notice]: {e}")
        return None

def speak(text):
    """कॉस्मिक कोडर की आवाज़ (अगर सिस्टम सपोर्ट करे, वरना सेफ प्रिंट)"""
    engine = init_tts()
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
            return
        except Exception as e:
            print(f"[TTS Run Error]: {e}")
    print(f"🤖 [Cosmic Voice Out]: {text}")

def listen_and_converse(mode="code"):
    """यूजर की आवाज़ सुनना (APK मोड में सुरक्षित फॉलबैक)"""
    welcome_msg = (
        "Cosmic Core online. What shall we build in the universe today?"
        if mode == "code"
        else "Cosmic Core listening. Tell me, what's on your mind?"
    )
    print(f"🌌 {welcome_msg}")
    speak(welcome_msg)

    if not HAS_SR:
        return {
            "status": "fallback",
            "message": "Voice input module running in mobile text fallback mode."
        }

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎙️ Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        print("⚡ Processing your voice...")
        text = recognizer.recognize_google(audio, language="hi-IN")
        return {"status": "success", "input_text": text}
    except Exception as e:
        return {"status": "error", "message": str(e)}
