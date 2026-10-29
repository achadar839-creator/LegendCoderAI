import os
import importlib.util
import sys
import urllib.request

def load_cosmic_plugin(plugin_name, plugin_url=None):
    """
    यह फंक्शन इंटरनेट से नए फीचर्स (Plugins) को डाउनलोड करता है
    और बिना ऐप को रीस्टार्ट किए उन्हें कॉस्मिक कोडर के दिमाग में लोड कर देता है।
    """
    plugin_dir = "plugins"
    # अगर प्लगइन फोल्डर नहीं है, तो उसे बना लें
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
        
    plugin_path = os.path.join(plugin_dir, f"{plugin_name}.py")
    
    # अगर URL दिया है और प्लगइन मौजूद नहीं है, तो उसे डाउनलोड करें
    if plugin_url and not os.path.exists(plugin_path):
        print(f"[{plugin_name}] डाउनलोड हो रहा है...")
        try:
            urllib.request.urlretrieve(plugin_url, plugin_path)
        except Exception as e:
            return {"status": "error", "message": f"डाउनलोड फेल: {str(e)}"}
            
    # डाउनलोड हो जाने के बाद, कोड को ऐप में डायनामिकली इंजेक्ट (Inject) करना
    if os.path.exists(plugin_path):
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            return {"status": "success", "message": f"प्लगइन '{plugin_name}' सफलतापूर्वक चालू हो गया!"}
        except Exception as e:
            return {"status": "crash", "message": f"प्लगइन लोड करने में एरर: {str(e)}"}
    else:
        return {"status": "not_found", "message": "प्लगइन फाइल नहीं मिली!"}
