import os
import subprocess
import tempfile

def execute_live_ui(code_string):
    """
    यह AI के बनाए UI/कोड को एक सुरक्षित टेम्परेरी फाइल में सेव करके रन करता है।
    अगर कोड में इनफिनिट लूप (Infinite loop) हुआ, तो भी मेन ऐप सेफ रहेगा!
    """
    try:
        # एक सुरक्षित टेम्परेरी फाइल बनाना (जो रन होने के बाद खुद मिट जाएगी)
        fd, temp_path = tempfile.mkstemp(suffix=".py", prefix="cosmic_app_")
        with os.fdopen(fd, 'w') as f:
            f.write(code_string)
        
        print(f"🚀 लाइव सैंडबॉक्स एक्टिवेटेड... कोड रन हो रहा है!")
        
        # कोड को एक अलग प्रोसेस में रन करना (20 सेकंड की सख्त लिमिट के साथ)
        result = subprocess.run(
            ['python3', temp_path],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        # काम खत्म होने पर कचरा (फाइल) साफ करना
        os.remove(temp_path)
        
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout}
        else:
            return {"status": "error", "error_log": result.stderr}
            
    except subprocess.TimeoutExpired:
        # अगर कोड हैंग हो जाए, तो सैंडबॉक्स उसे खुद किल कर देगा
        os.remove(temp_path)
        return {"status": "timeout", "error_log": "कोड ने बहुत समय लिया, सैंडबॉक्स ने उसे किल कर दिया!"}
    except Exception as e:
        return {"status": "critical_crash", "error_log": str(e)}
