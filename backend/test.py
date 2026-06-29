# # Run this to see what's available
# import google.generativeai as genai
# genai.configure(api_key="AIzaSyDndS9sRpuOlbbyHAAx6JuY4ORqIHaauUc")
# for model in genai.list_models():
#     if 'generateContent' in model.supported_generation_methods:
#         print(model.name)



# test_tesseract.py
import pytesseract
import subprocess

# Try to find tesseract
try:
    # Check if tesseract is in PATH
    result = subprocess.run(['tesseract', '--version'], 
                          capture_output=True, 
                          text=True)
    print("✅ Tesseract found in PATH")
    print(result.stdout[:200])
except FileNotFoundError:
    print("❌ Tesseract NOT found in PATH")
    
    # Try common installation paths
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    
    for path in common_paths:
        import os
        if os.path.exists(path):
            print(f"✅ Found Tesseract at: {path}")
            # Set it for pytesseract
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Set pytesseract to use: {path}")
            break
    else:
        print("❌ Tesseract not found. Please install it.")