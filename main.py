from flask import Flask, render_template_string, request, jsonify
import os
import subprocess

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legend Coder AI + GitHub</title>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: monospace; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background: #1e1e1e; padding: 12px; text-align: center; font-size: 16px; border-bottom: 1px solid #333; color: #00ff66; font-weight: bold; display: flex; justify-content: space-between; align-items: center; padding-left: 15px; padding-right: 15px;}
        .github-status { font-size: 12px; background: #2b2b2b; padding: 4px 8px; border-radius: 4px; color: #ffaa00; }
        #chat-box { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .message { padding: 12px 16px; border-radius: 8px; max-width: 85%; word-wrap: break-word; line-height: 1.5; font-size: 14px; }
        .user { background: #2b2b2b; color: #fff; align-self: flex-end; border: 1px solid #444; }
        .ai { background: #1e1e1e; color: #00ff66; align-self: flex-start; border: 1px solid #333; white-space: pre-wrap; }
        #input-area { display: flex; flex-direction: column; padding: 10px; background: #1e1e1e; border-top: 1px solid #333; gap: 8px; }
        .input-row { display: flex; gap: 8px; }
        textarea { flex: 1; background: #2b2b2b; color: #fff; border: 1px solid #444; padding: 10px; border-radius: 5px; resize: none; height: 40px; font-family: monospace; }
        button { background: #00ff66; color: #000; border: none; padding: 0 15px; border-radius: 5px; font-weight: bold; cursor: pointer; }
        button.git-btn { background: #ffaa00; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <header>
        <span>Legend Coder AI</span>
        <span class="github-status">GitHub Ready</span>
    </header>
    <div id="chat-box">
        <div class="message ai">नमस्ते अजय भाई! लीजेंड कोडर तैयार है। जो कोड चाहिए यहाँ लिखो, और सीधे GitHub पर पुश करने के लिए नीचे दिए बटन का इस्तेमाल करो!</div>
    </div>
    <div id="input-area">
        <div class="input-row">
            <textarea id="file-name" placeholder="फाइल का नाम (যেমন: script.py)" rows="1" style="flex: 0.4;"></textarea>
            <textarea id="user-input" placeholder="यहाँ अपना कोडिंग कमांड टाइप करें..." rows="1"></textarea>
        </div>
        <div class="input-row">
            <button onclick="sendMessage()" style="flex: 1; padding: 10px;">कोड जनरेट करें</button>
            <button class="git-btn" onclick="pushToGitHub()" style="flex: 1; padding: 10px;">GitHub पर पुश करें 🚀</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const inputField = document.getElementById('user-input');
            const fileNameField = document.getElementById('file-name');
            const chatBox = document.getElementById('chat-box');
            const text = inputField.value.trim();
            const filename = fileNameField.value.trim() || "output.py";

            if(!text) return;

            chatBox.innerHTML += `<div class="message user">फाइल: ${filename}<br>${text}</div>`;
            inputField.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const aiMsgId = 'ai-' + Date.now();
            chatBox.innerHTML += `<div class="message ai" id="${aiMsgId}">कोड लिखा जा रहा है और फाइल बन रही है...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text, filename: filename})
                });
                const data = await response.json();
                document.getElementById(aiMsgId).innerText = data.reply;
            } catch (err) {
                document.getElementById(aiMsgId).innerText = "एरर: कुछ गड़बड़ हो गई भाई!";
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function pushToGitHub() {
            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<div class="message ai">GitHub पर पुश किया जा रहा है...</div>`;
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
    data = request.json
    prompt = data.get('prompt', '')
    filename = data.get('filename', 'output.py')
    
    code_content = f"# Generated for: {prompt}\nprint('Hello Ajay, Code executed successfully!')\n"
    
    with open(filename, 'w') as f:
        f.write(code_content)
        
    return jsonify({"reply": f"सफलतापूर्वक फाइल '{filename}' बन गई है और लोकल सेव हो गई है!\n\n{code_content}"})

@app.route('/git-push', methods=['POST'])
def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-update from Legend Coder AI"], check=True)
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, check=True)
        return jsonify({"reply": "धमाका! कोड सफलतापूर्वक आपके GitHub रिपॉजिटरी पर पुश हो गया है! 🚀🔥"})
    except subprocess.CalledProcessError as e:
        return jsonify({"reply": f"गिट एरर: {e.stderr or 'रिपॉजिटरी कनेक्शन चेक करें।'}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
