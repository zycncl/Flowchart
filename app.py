from flask import Flask, request, jsonify, send_from_directory
import json
import os
from google import genai
from google.genai import types

app = Flask(__name__, static_folder="static")

SAVE_PATH = 'flowcharts/'
os.makedirs(SAVE_PATH, exist_ok=True)

# Sabit Prompt Şablonu (Hata riskini sıfırlamak için fonksiyon dışına aldık)
PROMPT_TEMPLATE = """
Sana gelen iş akışı metnini Drawflow kütüphanesinin tanıdığı JSON yapısına dönüştür.
Süreç Metni: "{user_text}"

Kullanabileceğin düğüm (node) türleri, html içerikleri ve kuralları şunlardır:
1. 'Başlangıç': html: '<div class="node-box style-start" contenteditable="true" spellcheck="false">Metin</div>', inputs: 0, outputs: 1, class: ''
2. 'Bitiş': html: '<div class="node-box style-end" contenteditable="true" spellcheck="false">Metin</div>', inputs: 1, outputs: 0, class: ''
3. 'Görev': html: '<div class="node-box style-task" contenteditable="true" spellcheck="false">Metin</div>', inputs: 1, outputs: 1, class: ''
4. 'Karar': html: '<div class="diamond-wrap"><div class="diamond"></div><div class="diamond-label" contenteditable="true" spellcheck="false">Metin</div><div class="evet-label">Evet</div><div class="hayir-label">Hayır</div></div>', inputs: 1, outputs: 2, class: 'decision'

Notlar:
- Her düğümün (node) benzersiz bir sayısal "id" değeri olmalıdır (Örn: "1", "2").
- "pos_x" ve "pos_y" koordinatlarını akış soldan sağa düzgün ilerleyecek şekilde hesapla (Örn: ardışık düğümler arasında x ekseninde en az 250px-300px mesafe bırak, y eksenini dengeli tut).
- Karar (decision) düğümünün 2 çıktısı (outputs) vardır. output_1 'Evet' (sağ köşe), output_2 'Hayır' (alt köşe) bağlantısıdır. Bağlantıları buna göre kur.
- Çıktı formatı SADECE saf ve geçerli bir JSON olmalıdır. Başında veya sonunda açıklama, ```json kodu blokları içermemelidir.

İşte uyman gereken Drawflow JSON şablonu:
{
  "drawflow": {
    "Home": {
      "data": {
        "1": {
          "id": 1,
          "name": "Başlangıç",
          "data": {},
          "class": "",
          "html": "<div class=\\"node-box style-start\\" contenteditable=\\"true\\" spellcheck=\\"false\\">Başlangıç</div>",
          "inputs": {},
          "outputs": { "output_1": { "connections": [ { "node": "2", "output": "input_1" } ] } },
          "pos_x": 100,
          "pos_y": 200
        },
        "2": {
          "id": 2,
          "name": "Görev",
          "data": {},
          "class": "",
          "html": "<div class=\\"node-box style-task\\" contenteditable=\\"true\\" spellcheck=\\"false\\">Müdür Onayı</div>",
          "inputs": { "input_1": { "connections": [ { "node": "1", "input": "output_1" } ] } },
          "outputs": { "output_1": { "connections": [] } },
          "pos_x": 400,
          "pos_y": 200
        }
      }
    }
  }
}
"""

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

# --- GEMINI API ENTEGRASYONU ---
@app.route('/ai-generate', methods=['POST'])
def ai_generate():
    data = request.get_json()
    user_text = data.get('text', '')
    
    if not user_text:
        return jsonify({"error": "Metin boş olamaz"}), 400

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY bulunamadı. Lütfen Render Environment ayarlarına ekleyin."}), 500

    try:
        client = genai.Client(api_key=api_key)
        
        # Metni şablona güvenli bir şekilde yerleştiriyoruz
        prompt = PROMPT_TEMPLATE.replace("{user_text}", user_text)

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        response_text = response.text.strip()
        
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        flow_data = json.loads(response_text)
        return jsonify(flow_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
