import React, { useState, useRef } from 'react';
import './App.css';
import CameraRecorder from './components/CameraRecorder';
import VideoDisplay from './components/VideoDisplay';
import ChatBot from './components/ChatBot';
import YoloUpload from './components/YoloUpload';

function App() {
  const [videoBlob, setVideoBlob] = useState(null);
  const [videoList, setVideoList] = useState([]);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [yoloVideoFile, setYoloVideoFile] = useState(null);
  const [yoloVideoUrl, setYoloVideoUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const videoRef = useRef(null);  
  const [videoFilename, setVideoFilename] = useState('');

  const handleSaveVideo = async (blob) => {
    setVideoBlob(blob);
    setVideoList((prev) => [...prev, blob]);

    const formData = new FormData();
    formData.append('file', new File([blob], 'recorded_video.mp4', { type: 'video/mp4' }));
    setIsAnalyzing(true);

    try {
      const res = await fetch('http://localhost:5000/detect_video', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok && data.result_video_url) {
        setYoloVideoUrl(data.result_video_url);
        setVideoFilename(data.filename);
        alert('실시간 녹화 영상 분석 완료');
      } else {
        alert('YOLO 분석 실패: ' + (data.error || '알 수 없는 오류'));
      }
    } catch (err) {
      alert('YOLO 서버 요청 실패');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('http://localhost:5000/detect', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.result_image_url) {
        window.open(data.result_image_url, '_blank');
      } else {
        alert('이미지 분석 실패');
      }
    } catch (err) {
      alert('서버 연결 실패');
    }
  };

  const handleYoloVideoAnalyze = async () => {
    if (!yoloVideoFile) return alert('영상 파일을 먼저 선택해주세요');
    setIsAnalyzing(true);
    setYoloVideoUrl('');
    const formData = new FormData();
    formData.append('file', yoloVideoFile);
    try {
      const res = await fetch('http://localhost:5000/detect_video', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (res.ok && data.result_video_url) {
        setYoloVideoUrl(data.result_video_url);
        setVideoFilename(data.filename);
        alert('YOLO 영상 분석 완료');
      } else {
        alert(`분석 실패: ${data.error || '알 수 없는 오류'}`);
      }
    } catch (err) {
      alert('서버 연결 오류');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSttUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('http://localhost:5000/stt', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { type: 'user', text: 'STT 요청' },
        { type: 'ai', text: data.text || '(응답 없음)' },
      ]);
    } catch (err) {
      console.error('STT 실패:', err);
    }
  };

  return (
    <div className="app">
      <div className="card">
        <h1>L-Lava 학습용 영상 플랫폼</h1>

        <div className="section">
          <CameraRecorder onVideoSave={handleSaveVideo} />
          <button className="gallery-button" onClick={() => setIsGalleryOpen(true)}>녹화된 영상 갤러리</button>
        </div>

        <div className="section">
          <h3>Whisper 영상 파일 업로드 (STT)</h3>
          <input type="file" accept="video/*" onChange={handleSttUpload} />
        </div>

        <div className="section">
          <h3>YOLO 이미지 업로드</h3>
          <YoloUpload onUpload={handleUpload} />
        </div>

        <div className="section">
          <h3>YOLO 영상 업로드</h3>
          <input type="file" accept="video/*" onChange={(e) => setYoloVideoFile(e.target.files[0])} />
          <button onClick={handleYoloVideoAnalyze} disabled={isAnalyzing}> {isAnalyzing ? '분석 중...' : '업로드 및 분석'} </button>
          {yoloVideoUrl && !isAnalyzing && (
            <div style={{ marginTop: 20 }}>
              <h4>분석된 YOLO 영상</h4>
              <video
                ref={videoRef}// 
                src={yoloVideoUrl}
                controls
                width="100%"
                style={{ maxHeight: '400px' }}
              />
              <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>URL: {yoloVideoUrl}</p>
            </div>
          )}
        </div>

        <div className="section">
          <VideoDisplay videoBlob={videoBlob} />
        </div>

        <div className="section">
          <h3>AI 채팅</h3>
          {/* videoRef를 ChatBot에 props로 전달 */}
          <ChatBot externalMessages={messages} videoRef={videoRef} videoFilename={videoFilename} />
        </div>
      </div>
    </div>
  );
}

export default App;
