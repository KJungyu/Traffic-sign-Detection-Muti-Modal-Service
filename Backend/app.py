# ✅ 수정된 Flask app.py (AVI → MP4 변환 포함)
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import requests
import os
import uuid
from dotenv import load_dotenv
import subprocess
import time
import subprocess

# 환경 변수 로딩
load_dotenv()

# Flask 초기화
app = Flask(__name__)
CORS(app)

# 환경 설정
BASE_DIR = "/home/dsc/work/dsc_react/flask_whisper_api"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "upload")
RESULT_FOLDER = os.path.join(BASE_DIR, "results")
IMAGE_RESULT_DIR = os.path.join(RESULT_FOLDER, "inference", "predict")
VIDEO_RESULT_DIR = os.path.join(RESULT_FOLDER, "predict_video")


FFMPEG_PATH = "/home/dsc/work/dsc_react/flask_whisper_api/ffmpeg-7.0.2-amd64-static/ffmpeg"


# 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_RESULT_DIR, exist_ok=True)
os.makedirs(VIDEO_RESULT_DIR, exist_ok=True)

# 모델 로드
model = YOLO(os.path.join(BASE_DIR, "best.pt"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def convert_avi_to_mp4(input_path, output_path):
    """FFmpeg를 사용하여 AVI를 MP4로 변환"""
    try:
        cmd = [
            FFMPEG_PATH,
            '-i', input_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-y',
            output_path
        ]
        
        print(f"🔄 FFmpeg 변환 시작: {input_path} → {output_path}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ FFmpeg 변환 성공")
            return True
        else:
            print(f"❌ FFmpeg 변환 실패: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg 변환 시간 초과")
        return False
    except FileNotFoundError:
        print("❌ FFmpeg 실행 파일을 찾을 수 없습니다. 경로를 확인하세요.")
        return False
    except Exception as e:
        print(f"❌ FFmpeg 변환 중 예외 발생: {str(e)}")
        return False


# Whisper STT
@app.route('/stt', methods=['POST'])
def stt():
    file = request.files.get('audio')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    files = {'file': (file.filename, file.stream, file.mimetype)}
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}
    data = {'model': 'whisper-1'}

    response = requests.post(
        'https://api.openai.com/v1/audio/transcriptions',
        headers=headers, data=data, files=files
    )

    if response.status_code == 200:
        return jsonify({'text': response.json()['text']})
    return jsonify({'error': 'STT 실패', 'detail': response.text}), 500

# YOLO 이미지 추론
@app.route('/detect', methods=['POST'])
def detect_yolo():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': '파일이 없습니다'}), 400

    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    results = model.predict(
        source=filepath,
        save=True,
        project=os.path.join(RESULT_FOLDER, 'inference'),
        name='predict',
        conf=0.1,
        iou=0.45,
        imgsz=(640, 640),
        verbose=True,
        exist_ok=True
    )

    saved_files = os.listdir(IMAGE_RESULT_DIR)
    saved_files.sort(key=lambda f: os.path.getmtime(os.path.join(IMAGE_RESULT_DIR, f)), reverse=True)
    result_image = next((f for f in saved_files if f.endswith('.jpg') or f.endswith('.png')), None)
    if not result_image:
        return jsonify({'error': '결과 이미지 없음'}), 500

    return jsonify({'result_image_url': f'http://localhost:5000/result/{result_image}'})

# YOLO 영상 추론 (AVI → MP4 변환 포함)
@app.route('/detect_video', methods=['POST'])
def detect_yolo_video():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': '파일이 없습니다'}), 400

    print(f"📹 받은 파일: {file.filename}")
    
    # 고유 ID로 파일명 생성
    unique_id = uuid.uuid4().hex
    filename = f"{unique_id}.mp4"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    print(f"📁 파일 저장 경로: {filepath}")

    try:
        # YOLO 추론 실행
        print("🔄 YOLO 추론 시작...")
        results = model.predict(
            source=filepath,
            save=True,
            project=VIDEO_RESULT_DIR,
            name='predict',
            conf=0.1,
            iou=0.45,
            exist_ok=True,
            verbose=True,
            vid_stride=1
        )
        print("✅ YOLO 추론 완료")

        # 결과 폴더 확인
        predict_folder = os.path.join(VIDEO_RESULT_DIR, 'predict')
        print(f"🔍 결과 폴더 경로: {predict_folder}")
        
        if not os.path.exists(predict_folder):
            print("❌ predict 폴더가 존재하지 않음")
            return jsonify({'error': 'predict 폴더가 생성되지 않았습니다'}), 500

        # 모든 비디오 파일 형식 찾기
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        saved_files = [f for f in os.listdir(predict_folder) 
                      if any(f.lower().endswith(ext) for ext in video_extensions)]
        
        print(f"📂 저장된 파일들: {saved_files}")
        
        if not saved_files:
            print("❌ 결과 영상 파일이 없음")
            all_files = os.listdir(predict_folder)
            print(f"🔍 폴더 내 모든 파일: {all_files}")
            return jsonify({'error': '결과 영상이 생성되지 않았습니다'}), 500

        # 가장 최신 파일 선택
        saved_files.sort(key=lambda f: os.path.getmtime(os.path.join(predict_folder, f)), reverse=True)
        result_video = saved_files[0]
        
        print(f"✅ 결과 영상: {result_video}")
        
        # AVI 파일인 경우 MP4로 변환 시도
        final_video = result_video
        if result_video.lower().endswith('.avi'):
            print("🔄 AVI 파일 감지됨, MP4로 변환 시도 중...")
            
            avi_path = os.path.join(predict_folder, result_video)
            mp4_filename = result_video.replace('.avi', '.mp4')
            mp4_path = os.path.join(predict_folder, mp4_filename)
            
            if convert_avi_to_mp4(avi_path, mp4_path):
                final_video = mp4_filename
                print(f"✅ MP4 변환 완료: {final_video}")
            else:
                print("⚠️ MP4 변환 실패, 원본 AVI 파일 사용")
        
        # 결과 URL 반환
        result_url = f'http://localhost:5000/result_video/{final_video}'
        print(f"🌐 결과 URL: {result_url}")
        
        return jsonify({
            'result_video_url': result_url,
            'message': '영상 분석이 완료되었습니다',
            'filename': final_video,
            'original_format': result_video.split('.')[-1] if '.' in result_video else 'unknown'
        })

    except Exception as e:
        print(f"❌ YOLO 추론 중 오류: {str(e)}")
        return jsonify({'error': f'YOLO 추론 실패: {str(e)}'}), 500

# 정적 파일 제공
@app.route('/result/<filename>')
def serve_result(filename):
    return send_from_directory(IMAGE_RESULT_DIR, filename)

# 비디오 파일 제공 (Range Request 지원)
@app.route('/result_video/<filename>')
def serve_result_video(filename):
    print(f"📹 영상 파일 요청: {filename}")
    video_path = os.path.join(VIDEO_RESULT_DIR, 'predict', filename)
    print(f"📁 영상 파일 경로: {video_path}")
    
    if os.path.exists(video_path):
        print("✅ 파일 존재함, 전송 시작")
        
        # 파일 확장자에 따른 MIME 타입 설정
        if filename.lower().endswith('.mp4'):
            mime_type = 'video/mp4'
        elif filename.lower().endswith('.avi'):
            mime_type = 'video/avi'
        elif filename.lower().endswith('.webm'):
            mime_type = 'video/webm'
        else:
            mime_type = 'video/mp4'  # 기본값
        
        response = send_from_directory(os.path.join(VIDEO_RESULT_DIR, 'predict'), filename)
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Type'] = mime_type
        response.headers['Cache-Control'] = 'no-cache'
        return response
    else:
        print("❌ 파일이 존재하지 않음")
        return jsonify({'error': '파일을 찾을 수 없습니다'}), 404

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
