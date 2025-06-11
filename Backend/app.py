from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import requests
import os
import uuid
from dotenv import load_dotenv
import subprocess
import shutil
import glob
import json
from datetime import datetime
import cv2
import threading
import time
import numpy as np

load_dotenv()

app = Flask(__name__)
CORS(app)

BASE_DIR = "C:/Users/a6351/OneDrive/Desktop/dsc_react/flask_whisper_api"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "upload")
RESULT_FOLDER = os.path.join(BASE_DIR, "results")
IMAGE_RESULT_DIR = os.path.join(RESULT_FOLDER, "predict")
VIDEO_RESULT_DIR = os.path.join(RESULT_FOLDER, "predict_video")
SNAPSHOT_DIR = os.path.join(BASE_DIR, "stt_triggered_dataset")


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_RESULT_DIR, exist_ok=True)
os.makedirs(VIDEO_RESULT_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


model = YOLO(os.path.join(BASE_DIR, "best.pt"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


recording_sessions = {}

def convert_avi_to_mp4(input_path, output_path):
    try:
        cmd = ['ffmpeg', '-i', input_path, '-c:v', 'libx264', '-c:a', 'aac', '-y', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0
    except Exception:
        return False

def draw_bounding_boxes(image, results):
    if results and len(results) > 0:
        boxes = results[0].boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy.cpu().numpy()[0].astype(int)
                conf = float(box.conf.cpu().numpy()[0])
                cls = int(box.cls.cpu().numpy()[0])
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"Class {cls}: {conf:.2f}"
                cv2.putText(image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return image

@app.route('/detect_frame', methods=['POST'])
def detect_frame():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No frame uploaded'}), 400

    # 이미지를 OpenCV로 읽기
    file_bytes = file.read()
    np_arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # YOLO 예측
    results = model.predict(img, conf=0.2, iou=0.4, verbose=False)

    detections = []
    if results and len(results) > 0:
        boxes = results[0].boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy.cpu().numpy()[0].astype(int)
                label_idx = int(box.cls.cpu().numpy()[0])
                conf = float(box.conf.cpu().numpy()[0])
                # 필요한 클래스명을 직접 넣으세요 (예시: ['stop sign', ...])
                label = f"Class {label_idx} ({conf:.2f})"
                # [x, y, w, h] 형태로 반환 (프론트에서 bbox 사용)
                bbox = [int(x1), int(y1), int(x2-x1), int(y2-y1)]
                detections.append({'label': label, 'bbox': bbox})

    return jsonify({'detections': detections})


@app.route('/stt', methods=['POST'])
def stt():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    files = {'file': (file.filename, file.stream, file.mimetype)}
    headers = {'Authorization': f'Bearer {OPENAI_API_KEY}'}
    data = {'model': 'whisper-1'}
    response = requests.post('https://api.openai.com/v1/audio/transcriptions', headers=headers, data=data, files=files)
    if response.status_code == 200:
        return jsonify({'text': response.json()['text']})
    return jsonify({'error': 'STT 실패', 'detail': response.text}), 500

@app.route('/start_recording', methods=['POST'])
def start_recording():
    session_id = request.json.get('session_id', str(uuid.uuid4()))
    video_start_time = request.json.get('video_current_time', 0)
    recording_sessions[session_id] = {
        'start_time': time.time(),
        'frames': [],
        'active': True,
        'video_start_time': float(video_start_time)
    }
    print(f"Recording started for session: {session_id} (video_start_time={video_start_time})")
    return jsonify({'session_id': session_id, 'message': '녹음이 시작되었습니다'})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    session_id = request.json.get('session_id')
    video_end_time = request.json.get('video_current_time', 0)
    if session_id not in recording_sessions:
        return jsonify({'error': '유효하지 않은 세션입니다'}), 400
    session = recording_sessions[session_id]
    session['active'] = False
    session['end_time'] = time.time()
    session['video_end_time'] = float(video_end_time) if video_end_time is not None else 0
    saved_count = save_recording_frames(session_id)
    del recording_sessions[session_id]
    print(f"Recording stopped for session: {session_id}, saved {saved_count} frames")
    return jsonify({
        'message': f'녹음이 종료되었습니다. {saved_count}개의 프레임이 저장되었습니다',
        'saved_frames': saved_count
    })


def save_recording_frames(session_id):
    session = recording_sessions.get(session_id)
    if not session:
        print(f"[ERROR] save_recording_frames: No session for {session_id}")
        return 0

    video_start_time = float(session.get('video_start_time', 0))
    video_end_time = float(session.get('video_end_time', 0))
    print(f"[INFO] save_recording_frames: session_id={session_id}, video_start_time={video_start_time}, video_end_time={video_end_time}")

    annotated_frames_dir = os.path.join(VIDEO_RESULT_DIR, "predict", "annotated_frames")
    labels_dir = os.path.join(VIDEO_RESULT_DIR, "predict", "labels")
    if not os.path.exists(annotated_frames_dir) or not os.path.exists(labels_dir):
        print(f"[ERROR] save_recording_frames: annotated_frames_dir or labels_dir not found")
        return 0

    timestamps_path = os.path.join(VIDEO_RESULT_DIR, "predict", "frames", "frame_timestamps.json")
    if not os.path.exists(timestamps_path):
        print(f"[ERROR] save_recording_frames: frame_timestamps.json not found")
        return 0
    with open(timestamps_path, "r") as f:
        frame_timestamps = json.load(f)
    print(f"[INFO] frame_timestamps loaded: {len(frame_timestamps)} frames")
    if frame_timestamps:
        print(f"[INFO] first frame time: {frame_timestamps[0]['video_time']}, last frame time: {frame_timestamps[-1]['video_time']}")
        print(f"[INFO] example video times: {[ft['video_time'] for ft in frame_timestamps[:5]]} ... {[ft['video_time'] for ft in frame_timestamps[-5:]]}")

    saved_count = 0
    for ts in frame_timestamps:
        vt = float(ts["video_time"])
        if video_start_time <= vt <= video_end_time:
            annotated_filename = ts["frame_filename"].replace("frame_", "annotated_frame_")
            print(f"[SAVE] annotated {annotated_filename} (video_time={vt}) in range [{video_start_time}, {video_end_time}]")
            frame_file = os.path.join(annotated_frames_dir, annotated_filename)
            label_file = os.path.join(labels_dir, ts["frame_filename"].replace(".jpg", ".txt"))
            new_id = f"{session_id}_{saved_count:04d}"
            shutil.copy(frame_file, os.path.join(SNAPSHOT_DIR, f"{new_id}.jpg"))
            if os.path.exists(label_file):
                shutil.copy(label_file, os.path.join(SNAPSHOT_DIR, f"{new_id}.txt"))
            else:
                with open(os.path.join(SNAPSHOT_DIR, f"{new_id}.txt"), "w") as f:
                    f.write("")
            saved_count += 1

    

    if saved_count == 0:
        print(f"[WARN] No frames matched the time range. Please check video_start_time/video_end_time and video playback status.")

    
    metadata = {
        "session_id": session_id,
        "recording_video_start": video_start_time,
        "recording_video_end": video_end_time,  
        "saved_frames": saved_count,
        "timestamp": datetime.now().isoformat()
    }
    metadata_path = os.path.join(SNAPSHOT_DIR, f"{session_id}_session_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"[INFO] save_recording_frames: {saved_count} frames saved to {SNAPSHOT_DIR}")
    return saved_count


@app.route('/detect_video', methods=['POST'])
def detect_yolo_video():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': '파일이 없습니다'}), 400
    unique_id = uuid.uuid4().hex
    filename = f"{unique_id}.mp4"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    try:
        frames_dir = os.path.join(VIDEO_RESULT_DIR, 'predict', 'frames')
        labels_dir = os.path.join(VIDEO_RESULT_DIR, 'predict', 'labels')
        annotated_frames_dir = os.path.join(VIDEO_RESULT_DIR, 'predict', 'annotated_frames')
        os.makedirs(frames_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)
        os.makedirs(annotated_frames_dir, exist_ok=True)
        
        results = model.predict(
            source=filepath,
            save=True,
            save_txt=True,
            project=VIDEO_RESULT_DIR,
            name='predict',
            conf=0.1,
            iou=0.45,
            exist_ok=True,
            verbose=True,
            vid_stride=1
        )
        cap = cv2.VideoCapture(filepath)
        frame_count = 0
        frame_timestamps = []
        print("Starting frame extraction and analysis...")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_time_in_video = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            frame_timestamps.append({
                "frame_number": frame_count,
                "frame_filename": f"frame_{frame_count:06d}.jpg",
                "video_time": frame_time_in_video
            })
            original_frame_filename = f"frame_{frame_count:06d}.jpg"
            original_frame_path = os.path.join(frames_dir, original_frame_filename)
            cv2.imwrite(original_frame_path, frame)
            frame_results = model.predict(frame, conf=0.1, iou=0.45, verbose=False)
            annotated_frame = frame.copy()
            annotated_frame = draw_bounding_boxes(annotated_frame, frame_results)
            annotated_frame_filename = f"annotated_frame_{frame_count:06d}.jpg"
            annotated_frame_path = os.path.join(annotated_frames_dir, annotated_frame_filename)
            cv2.imwrite(annotated_frame_path, annotated_frame)
            label_filename = f"frame_{frame_count:06d}.txt"
            label_path = os.path.join(labels_dir, label_filename)
            with open(label_path, 'w') as f:
                if frame_results and len(frame_results) > 0:
                    boxes = frame_results[0].boxes
                    if boxes is not None:
                        for box in boxes:
                            cls = int(box.cls.cpu().numpy()[0])
                            x, y, w, h = box.xywhn.cpu().numpy()[0]
                            f.write(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames...")
        cap.release()
        with open(os.path.join(frames_dir, "frame_timestamps.json"), "w") as f:
            json.dump(frame_timestamps, f)
        print(f"Extracted {frame_count} frames to {frames_dir}")
        print(f"Generated {frame_count} annotated frames to {annotated_frames_dir}")
        print(f"Generated {frame_count} label files to {labels_dir}")
        predict_folder = os.path.join(VIDEO_RESULT_DIR, 'predict')
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        saved_files = [f for f in os.listdir(predict_folder) if any(f.lower().endswith(ext) for ext in video_extensions)]
        saved_files.sort(key=lambda f: os.path.getmtime(os.path.join(predict_folder, f)), reverse=True)
        result_video = saved_files[0] if saved_files else None
        final_video = result_video
        if result_video and result_video.lower().endswith('.avi'):
            avi_path = os.path.join(predict_folder, result_video)
            mp4_filename = result_video.replace('.avi', '.mp4')
            mp4_path = os.path.join(predict_folder, mp4_filename)
            if convert_avi_to_mp4(avi_path, mp4_path):
                final_video = mp4_filename
        result_url = f'http://localhost:5000/result_video/{final_video}'
        return jsonify({
            'result_video_url': result_url,
            'message': '영상 분석이 완료되었습니다',
            'filename': final_video,
            'frames_extracted': frame_count,
            'frames_with_annotations': frame_count
        })
    except Exception as e:
        print(f"Error in detect_video: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'YOLO 추론 실패: {str(e)}'}), 500

@app.route('/trigger_snapshot', methods=['POST'])
def trigger_snapshot():
    try:
        annotated_frames_dir = os.path.join(VIDEO_RESULT_DIR, "predict", "annotated_frames")
        labels_dir = os.path.join(VIDEO_RESULT_DIR, "predict", "labels")
        if not os.path.exists(annotated_frames_dir):
            return jsonify({"error": "분석된 프레임이 없습니다. 먼저 영상을 분석해주세요."}), 404
        image_files = sorted(glob.glob(os.path.join(annotated_frames_dir, "*.jpg")), key=os.path.getmtime, reverse=True)
        if not image_files:
            return jsonify({"error": "추출된 프레임이 없습니다."}), 404
        import random
        selected_image = random.choice(image_files)
        image_basename = os.path.basename(selected_image).replace("annotated_", "").replace("frame_", "frame_")
        frame_number = image_basename.split('_')[1].split('.')[0]
        corresponding_label = os.path.join(labels_dir, f"frame_{frame_number}.txt")
        new_id = uuid.uuid4().hex
        target_image_path = os.path.join(SNAPSHOT_DIR, f"{new_id}.jpg")
        shutil.copy(selected_image, target_image_path)
        target_label_path = os.path.join(SNAPSHOT_DIR, f"{new_id}.txt")
        if os.path.exists(corresponding_label):
            shutil.copy(corresponding_label, target_label_path)
        else:
            with open(target_label_path, 'w') as f:
                f.write("")
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "image_file": f"{new_id}.jpg",
            "label_file": f"{new_id}.txt",
            "source_image": selected_image,
            "source_label": corresponding_label if os.path.exists(corresponding_label) else None,
            "frame_number": frame_number,
            "type": "single_snapshot"
        }
        metadata_path = os.path.join(SNAPSHOT_DIR, f"{new_id}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return jsonify({
            "message": "STT 시점 프레임 저장 완료", 
            "image": f"{new_id}.jpg", 
            "label": f"{new_id}.txt",
            "metadata": f"{new_id}_metadata.json",
            "timestamp": metadata["timestamp"],
            "frame_number": frame_number
        })
    except Exception as e:
        print(f"Error in trigger_snapshot: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"스냅샷 저장 중 오류 발생: {str(e)}"}), 500

@app.route('/result_video/<filename>')
def serve_result_video(filename):
    video_path = os.path.join(VIDEO_RESULT_DIR, 'predict', filename)
    if os.path.exists(video_path):
        return send_from_directory(os.path.join(VIDEO_RESULT_DIR, 'predict'), filename)
    else:
        return jsonify({'error': '파일을 찾을 수 없습니다'}), 404

@app.route('/debug/folders', methods=['GET'])
def debug_folders():
    try:
        predict_folder = os.path.join(VIDEO_RESULT_DIR, "predict")
        debug_info = {
            "predict_folder": predict_folder,
            "predict_folder_exists": os.path.exists(predict_folder),
            "contents": []
        }
        if os.path.exists(predict_folder):
            for item in os.listdir(predict_folder):
                item_path = os.path.join(predict_folder, item)
                item_info = {
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "path": item_path
                }
                if os.path.isdir(item_path):
                    try:
                        item_info["contents"] = os.listdir(item_path)[:10]
                    except:
                        item_info["contents"] = "접근 불가"
                debug_info["contents"].append(item_info)
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
