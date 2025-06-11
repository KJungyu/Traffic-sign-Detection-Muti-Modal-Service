import React, { useRef, useState, useEffect } from 'react';

function CameraRecorder({ onVideoSave }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const detectIntervalRef = useRef(null);

  const [recording, setRecording] = useState(false);
  const [stream, setStream] = useState(null);
  const [detections, setDetections] = useState([]);

  useEffect(() => {
    const renderBoxes = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      detections.forEach(({ label, bbox }) => {
        const [x, y, w, h] = bbox;
        ctx.strokeStyle = 'lime';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, w, h);
        ctx.font = '14px Arial';
        ctx.fillStyle = 'lime';
        ctx.fillText(label, x, y - 5);
      });
    };
    renderBoxes();
  }, [detections]);

  const captureAndDetect = async () => {
    const video = videoRef.current;
    if (!video.videoWidth) return;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append('file', blob, 'frame.jpg');

      try {
        const res = await fetch('http://localhost:5000/detect_frame', {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        if (data.detections) setDetections(data.detections);
      } catch (err) {
        console.error('YOLO 감지 실패:', err);
      }
    }, 'image/jpeg');
  };

  const startRecording = async () => {
    const localStream = await navigator.mediaDevices.getUserMedia({ video: true });
    setStream(localStream);
    videoRef.current.srcObject = localStream;

    const recorder = new MediaRecorder(localStream);
    let chunks = [];

    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      onVideoSave(blob);
    };

    mediaRecorderRef.current = recorder;
    recorder.start();
    setRecording(true);

    detectIntervalRef.current = setInterval(captureAndDetect, 1000);
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    stream?.getTracks().forEach((track) => track.stop());
    clearInterval(detectIntervalRef.current);
    setRecording(false);
  };

  return (
    <div style={{ textAlign: 'center' }}>
      {/* 영상 영역 */}
      <div
        style={{
          position: 'relative',
          width: '640px',
          height: '480px',
          margin: '0 auto',
          borderRadius: '12px',
          overflow: 'hidden',
          boxShadow: '0 4px 10px rgba(0,0,0,0.2)',
        }}
      >
        <video
          ref={videoRef}
          autoPlay
          muted
          width="640"
          height="480"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            objectFit: 'cover',
            width: '100%',
            height: '100%',
          }}
        />
        <canvas
          ref={canvasRef}
          width="640"
          height="480"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
          }}
        />
      </div>

      {/* 버튼 영역 (영상 아래 분리) */}
      <div style={{ marginTop: '20px' }}>
        {!recording ? (
          <button
            onClick={startRecording}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: '#f28b82',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            🎥 녹화 시작
          </button>
        ) : (
          <button
            onClick={stopRecording}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: '#ff5252',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            🛑 녹화 중지
          </button>
        )}
      </div>
    </div>
  );
}

export default CameraRecorder;
