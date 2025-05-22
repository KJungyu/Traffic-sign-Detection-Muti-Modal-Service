from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import cv2
import os
import threading
import time

app = Flask(__name__)
CORS(app)

# ----------------------------
# 웹캠 설정 (0번 카메라)
# ----------------------------
cap = cv2.VideoCapture(0)
latest_result = None  # 가장 최근 감지 결과

# ----------------------------
# 가짜 YOLO + VLM + TTS 감지 함수 (프레임마다)
# ----------------------------
def fake_detect_frame():
    global latest_result
    while True:
        success, frame = cap.read()
        if not success:
            continue

        # 실제 YOLO/BLIP2 대신 더미 감지 결과 설정
        latest_result = {
            "label": "주정차 금지",
            "description": "이 표지판은 주정차 금지 구역을 나타냅니다.",
            "actionTip": "이 구역에는 정차할 수 없습니다.",
            "audioUrl": "http://localhost:5001/static/tts-output.mp3"
        }
        time.sleep(3)  # 3초마다 감지 시뮬레이션

# 감지 쓰레드 실행
threading.Thread(target=fake_detect_frame, daemon=True).start()

# ----------------------------
# 실시간 영상 스트리밍
# ----------------------------
@app.route('/video-stream')
def video_stream():
    def generate():
        while True:
            success, frame = cap.read()
            if not success:
                continue
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ----------------------------
# 감지된 표지판 결과 반환 (React가 3초마다 요청)
# ----------------------------
@app.route('/api/detect-latest', methods=['GET'])
def detect_latest():
    if latest_result:
        return jsonify(latest_result)
    return jsonify({})

if __name__ == '__main__':
    os.makedirs("static", exist_ok=True)
    app.run(host='0.0.0.0', port=5001)
