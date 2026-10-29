import subprocess

def run_and_heal(code_string):
    """
    यह फंक्शन कोड को रन करता है। अगर कोड क्रैश होता है, 
    तो यह एरर को पकड़कर वापस AI को हीलिंग (Healing) के लिए भेजता है।
    """
    try:
        # कोड को एक सुरक्षित सैंडबॉक्स (subprocess) में रन करना
        result = subprocess.run(
            ['python3', '-c', code_string],
            capture_output=True, 
            text=True, 
            timeout=15
        )
        
        # अगर कोड बिना एरर के चल गया
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout}
        
        # अगर कोड में एरर आया (Syntax, NameError आदि)
        else:
            return {"status": "needs_healing", "error_log": result.stderr}
            
    except Exception as e:
        return {"status": "critical_crash", "error_log": str(e)}
