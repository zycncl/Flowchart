from flask import Flask, request, jsonify, send_from_directory
import json
import os

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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
