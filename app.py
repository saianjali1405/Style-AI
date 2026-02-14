from flask import Flask, render_template, request, jsonify
import numpy as np
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from groq import Groq
client = Groq(api_key=GROQ_API_KEY)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

model = None
MODEL_ERROR = None
MODEL_PATH = None
CLASS_NAMES = ['Parasitized', 'Uninfected']

print("\n" + "="*70)
print("🔬 MALARIA DETECTION - LOADING MODEL")
print("="*70)

try:
    import tensorflow as tf
    from PIL import Image
    print("✓ TensorFlow imported")
except Exception as e:
    MODEL_ERROR = f"Import failed: {e}"
    print(f"✗ {MODEL_ERROR}")

# ---------------- MODEL LOADING ----------------
if MODEL_ERROR is None:
    current_dir = os.getcwd()
    print(f"✓ Directory: {current_dir}")

    try:
        h5_files = [f for f in os.listdir(current_dir) if f.endswith('.h5')]
        if h5_files:
            MODEL_PATH = os.path.join(current_dir, h5_files[0])
            print(f"✓ Found: {h5_files[0]}")
            model = tf.keras.models.load_model(MODEL_PATH, compile=False)
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            print(f"✓ Loaded! Input: {model.input_shape}, Output: {model.output_shape}")
        else:
            MODEL_ERROR = "No .h5 file found"
            print(f"✗ {MODEL_ERROR}")
    except Exception as e:
        MODEL_ERROR = str(e)
        print(f"✗ {MODEL_ERROR}")

# ---------------- IMAGE PREPROCESS ----------------
def prepare_image(image_file):
    if model is None:
        return None
    try:
        img = Image.open(image_file).convert('RGB')

        # FORCE SIZE FOR MODEL
        img = img.resize((64, 64))   # VERY IMPORTANT

        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        return img_array

    except Exception as e:
        print("Preprocess error:", e)
        return None

# ---------------- HOME ROUTE ----------------
@app.route('/')
def home():
    if os.path.exists('C:/Users/DELL/OneDrive/Desktop/HACK/templates/index.html'):
        return render_template('index.html')
    return f'''<!DOCTYPE html>
<html><head><title>Malaria Detection</title><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Arial;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:20px}}
.container{{max-width:900px;margin:0 auto;background:white;border-radius:20px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.3)}}
h1{{color:#333;margin-bottom:30px;text-align:center}}
.status{{padding:25px;border-radius:12px;margin:25px 0;text-align:center}}
.success{{background:#d4edda;color:#155724;border:2px solid #c3e6cb}}
.error{{background:#f8d7da;color:#721c24;border:2px solid #f5c6cb}}
.icon{{font-size:3rem;margin-bottom:15px}}
</style></head><body>
<div class="container">
<h1>🦠 Malaria Detection System</h1>
<div class="status success"><div class="icon">✅</div><h2>Server Running</h2><p>Port 5000 active</p></div>
<div class="status {'error' if model is None else 'success'}">
<div class="icon">{'❌' if model is None else '✅'}</div>
<h2>Model: {'NOT LOADED' if model is None else 'LOADED'}</h2>
<p>{MODEL_ERROR if MODEL_ERROR else 'Ready!'}</p></div></div></body></html>'''

# ---------------- PREDICT ROUTE ----------------
@app.route('/predict', methods=['POST'])
def predict():

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Empty file'})

    try:
        # ---- You can later add real skin tone detection here ----
        detected_tone = "medium"

        prompt = f"""
You are a fashion stylist AI.
Respond ONLY using this exact template.
Do NOT write paragraphs.
Do NOT explain anything.

DRESS_CODE:
- item
- item

OUTFIT:
- item
- item

SHIRT:
- item

PANT:
- item

SHOES:
- item

HAIRSTYLE:
- item

ACCESSORIES:
- item
- item

COLORS:
- item
- item

SHOPPING_ITEMS:
- Royal Blue Shirt
- Deep Purple Formal
- Emerald Green Shirt
- Black Chelsea Boots
- Burgundy Loafers

Skin tone: {detected_tone}
"""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a fashion stylist AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )

        advice = completion.choices[0].message.content

        return jsonify({
            "success": True,
            "tone": detected_tone,
            "analysis": advice
        })

    except Exception as e:
                         return jsonify({'success': False, 'error': str(e)})


# ---------------- HEALTH ROUTE ----------------
@app.route('/health')
def health():
    return jsonify({'status': 'running', 'model_loaded': model is not None})

# ---------------- RUN SERVER ----------------
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    print("\n" + "="*70)
    print(f"{'✅' if model else '❌'} Model: {'LOADED' if model else 'NOT LOADED'}")
    if model:
        print(f"   Input: {model.input_shape}, Output: {model.output_shape}")
    print(f"🌐 Server: http://127.0.0.1:5000")
    print("="*70 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)