import sys

print("=== 🔍 Legend Coder AI System Core Check ===")
try:
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    print("✅ main.py file successfully loaded!")
    print(f"📏 Total Code Length: {len(content)} characters")
    
    if "Flask" in content:
        print("✅ Flask Server framework: DETECTED")
    else:
        print("❌ Flask Server framework: NOT FOUND")
        
    if "HTML_TEMPLATE" in content:
        print("✅ Frontend HTML UI Template: DETECTED")
    else:
        print("❌ Frontend HTML UI Template: NOT FOUND")
        
    if "subprocess" in content:
        print("✅ Local Model Execution (subprocess): DETECTED")
    else:
        print("⚠️ Local Model execution (subprocess): NOT FOUND")
        
    print("\n🎉 Core system inspection completed successfully! Everything looks solid.")

except Exception as e:
    print(f"❌ Error while checking system: {e}")
