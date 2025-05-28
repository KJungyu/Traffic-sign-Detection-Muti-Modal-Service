from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route('/stt', methods=['POST'])
def stt():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({'error': 'No audio file uploaded'}), 400

    files = {
        'file': (audio_file.filename, audio_file.stream, audio_file.mimetype),
    }
    data = {'model': 'whisper-1'}
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}

    response = requests.post(
        'https://api.openai.com/v1/audio/transcriptions',
        headers=headers,
        data=data,
        files=files
    )

    if response.status_code == 200:
        return jsonify({'text': response.json()['text']})
    else:
        return jsonify({'error': 'STT 실패', 'detail': response.text}), 500

if __name__ == '__main__':
    app.run(debug=True)
