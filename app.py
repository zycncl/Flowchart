from flask import Flask, request, jsonify, send_from_directory
import json
import os
from google import genai
from google.genai import types

app = Flask(__name__, static_folder="static")

SAVE_PATH = 'flowcharts/'
os.makedirs(SAVE_PATH, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    with open(os.path.join(SAVE_PATH, 'flow1.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"message": "Kaydedildi"})

@app.route('/load', methods=['GET'])
def load():
    file_path = os.path.join(SAVE_PATH, 'flow1.json')
    if os.path.exists(file_path):
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Dosya bulunamadı"}), 404

response_text = response.text.strip()
        
        # --- EKSTRA GÜVENLİK KONTROLÜ ---
        # Eğer Gemini inatla markdown ```json ... ``` blokları eklediyse temizle
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        flow_data = json.loads(response_text)
        return jsonify(flow_data)
    try:
        # Google GenAI istemcisini başlatıyoruz
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        ... PROMPT ICERIGI BURADA ...
        """

        # Gemini 2.5 Flash ile yanıt üretiyoruz
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        response_text = response.text.strip()
        
        # --- EKSTRA GÜVENLİK KONTROLÜ (HİZALAMAYA DİKKAT) ---
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        flow_data = json.loads(response_text)
        return jsonify(flow_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
