from flask import Flask, render_template_string, request, jsonify
import os
import subprocess
from engine.legend_core import LegendEngine

app = Flask(__name__)
ai_engine = LegendEngine(model="deepseek-coder")

# outputs फोल्डर सुनिश्चित करना
os.makedirs("outputs", exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legend Coder AI + GitHub</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: monospace; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        .header { background-color: #1f1f1f; padding: 15px; text-align: center; font-size: 18px; font-weight: bold; color: #00e676; border-bottom: 1px solid #333; }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { padding: 12px; border-radius: 8px; max-width: 85%; white-space: pre-wrap; word-wrap: break-word; line-height: 1.4; }
        .user { background-color: #004d40; align-self: flex-end; color: #fff; }
        .ai { background-color: #262626; align-self: flex-start; border: 1px solid #444; color: #00e676; }
        .controls { background-color: #1f1f1f; padding: 10px; display: flex; flex-direction: column; gap: 8px; border-top: 1px solid #333; }
        input, textarea, button { padding: 10px; border-radius: 5px; border: 1px solid #444; background-color: #2b2b2b; color: #fff; font-family: monospace; }
        .btn-row { display: flex; gap: 8px; }
        button { flex: 1; background-color: #00e676; color: #000; font-weight: bold; cursor: pointer; border: none; }
        button.git-btn { background-color: #ff9100; }
    </style>
</head>
<body>
    <div class="header">⚡ Legend Coder AI (DeepSeek Engine)</div>
    <div class="chat-box" id="chatBox">
        <div class="message ai">नमस्ते अजय! Legend Coder AI तैयार है। अपना प्रॉम्प्ट और फाइल का नाम लिखें।</div>
    </div>
    <div class="controls">
        <input type="text" id="filename" placeholder="फाइल का नाम (जैसे: app.py)" value="output.py">
        <textarea id="prompt" rows="2" placeholder="यहाँ बताएं क्या कोड बनाना है..."></textarea>
        <div class="btn-row">
            <button onclick="generateCode()">⚙️ कोड बनाएं</button>
            <button class="git-btn" onclick="gitPush()">🚀 GitHub Push</button>
        </div>
    </div>

    <script>
        async function generateCode() {
            const promptInput = document.getElementById('prompt');
            const filenameInput = document.getElementById('filename');
            const chatBox = document.getElementById('chatBox');

            const prompt = promptInput.value.trim();
            const filename = filenameInput.value.trim() || 'output.py';
            if (!prompt) return;

            chatBox.innerHTML += `<div class="message user">📄 <b>${filename}</b>: ${prompt}</div>`;
            promptInput.value = '';
            chatBox.innerHTML += `<div class="message ai" id="loading">⏳ AI कोड लिख रहा है...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt, filename })
                });
                const data = await response.json();
                document.getElementById('loading').remove();
                chatBox.innerHTML += `<div class="message ai">${data.reply}</div>`;
            } catch (err) {
                document.getElementById('loading').remove();
                chatBox.innerHTML += `<div class="message ai">एरर: सर्वर से कनेक्ट नहीं हो पाया!</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function gitPush() {
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML += `<div class="message user">🚀 GitHub पर पुश किया जा रहा है...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/git-push', { method: 'POST' });
                const data = await response.json();
                chatBox.innerHTML += `<div class="message ai">${data.reply}</div>`;
            } catch (err) {
                chatBox.innerHTML += `<div class="message ai">एरर: गिटहब पुश फेल हो गया!</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    prompt = data.get('prompt', '')
    filename = os.path.basename(data.get('filename', 'output.py'))
    save_path = os.path.join("outputs", filename)

    ai_response = ai_engine.query_ai(prompt)
    if "Ollama Connection Error" in ai_response:
        code_content = f"# [Offline Fallback Mode - Ollama Not Running]\n# Prompt: {prompt}\n\ndef main():\n    print('Hello Ajay! Start Ollama in Termux for live DeepSeek AI generation.')\n\nif __name__ == '__main__':\n    main()\n"
        status_note = f"⚠️ नोट: {ai_response}\n(अभी बेसिक टेम्पलेट जनरेट किया गया है)"
    else:
        code_content = ai_response
        status_note = "✅ DeepSeek AI द्वारा कोड जनरेट किया गया!"

    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        file_msg = f"फाइल 'outputs/{filename}' में सेव हो गई है!"
    except Exception as e:
        file_msg = f"फाइल सेव एरर: {str(e)}"

    return jsonify({"reply": f"{status_note}\n📁 {file_msg}\n\n{code_content}"})

@app.route('/git-push', methods=['POST'])
def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "Auto-update from Legend Coder AI"], check=False, capture_output=True, text=True)
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=True)
        return jsonify({"reply": "धमाका! कोड सफलतापूर्वक आपके GitHub रिपॉजिटरी पर पुश हो गया है! 🚀🔥"})
    except FileNotFoundError:
        return jsonify({"reply": "⚠️ नोट: Android APK के अंदर इनबिल्ट Git बाइनरी नहीं होती। गिट पुश फीचर Termux सर्वर मोड में काम करेगा।"})
    except subprocess.CalledProcessError as e:
        return jsonify({"reply": f"गिट एरर: {e.stderr or 'रिपॉजिटरी कनेक्शन चेक करें।'}"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
