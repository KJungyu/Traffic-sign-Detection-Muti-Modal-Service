import React, { useState } from 'react';
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
  const [isAnalyzing, setIsAnalyzing] = useState(false); // 로딩 상태 추가

  const handleSaveVideo = async (blob) => {
    setVideoBlob(blob);
    setVideoList((prev) => [...prev, blob]);

    // ✅ YOLO 추론 자동 전송
  const formData = new FormData();
  formData.append('file', new File([blob], 'recorded_video.mp4', { type: 'video/mp4' }));

  setIsAnalyzing(true); // 분석 중 UI 반영

  try {
    const res = await fetch('http://localhost:5000/detect_video', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();

    if (res.ok && data.result_video_url) {
      setYoloVideoUrl(data.result_video_url);
      alert('✅ 실시간 녹화 영상 분석 완료');
    } else {
      console.error('YOLO 응답 오류:', data);
      alert('❌ YOLO 분석 실패: ' + (data.error || '알 수 없는 오류'));
    }
  } catch (err) {
    console.error('YOLO 분석 요청 실패:', err);
    alert('❌ YOLO 서버 요청 실패');
  } finally {
    setIsAnalyzing(false);
  }
};

  // ✅ YOLO 이미지 분석 요청
  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch("http://localhost:5000/detect", {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (data.result_image_url) {
        alert("✅ YOLO 이미지 분석 성공");
        window.open(data.result_image_url, "_blank");
      } else {
        alert("❌ 이미지 분석 실패");
      }
    } catch (err) {
      console.error("Fetch 실패:", err);
      alert("❌ 서버 연결 실패 또는 오류 발생");
    }
  };

  // ✅ YOLO 영상 분석 요청 (수정된 버전)
  const handleYoloVideoAnalyze = async () => {
    if (!yoloVideoFile) return alert('🎥 영상 파일을 먼저 선택해주세요');

    setIsAnalyzing(true); // 로딩 시작
    setYoloVideoUrl(''); // 이전 결과 초기화

    console.log('📹 선택된 파일:', yoloVideoFile);
    
    const formData = new FormData();
    formData.append('file', yoloVideoFile);

    try {
      console.log('🔄 서버로 요청 전송 중...');
      const res = await fetch('http://localhost:5000/detect_video', {
        method: 'POST',
        body: formData,
      });

      console.log('📡 응답 상태:', res.status);
      const data = await res.json();
      console.log('📋 응답 데이터:', data);

      if (res.ok && data.result_video_url) {
        setYoloVideoUrl(data.result_video_url);
        alert("✅ YOLO 영상 분석 완료");
        console.log('📹 설정된 비디오 URL:', data.result_video_url);
      } else {
        console.error('❌ 응답에 result_video_url이 없음:', data);
        alert(`❌ 분석 실패: ${data.error || '알 수 없는 오류'}`);
      }
    } catch (err) {
      console.error('❌ 영상 YOLO 분석 오류:', err);
      alert('❌ 서버 연결 오류');
    } finally {
      setIsAnalyzing(false); // 로딩 종료
    }
  };

  // 🎤 Whisper STT
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
        { type: 'user', text: '🎥 STT 요청' },
        { type: 'ai', text: data.text || '(응답 없음)' },
      ]);
    } catch (err) {
      console.error('STT 실패:', err);
    }
  };

  return (
    <div className="app">
      <div className="card">
        <h1>🎬 L-Lava 학습용 영상 플랫폼</h1>

        <div className="section">
          <CameraRecorder onVideoSave={handleSaveVideo} />
          <button className="gallery-button" onClick={() => setIsGalleryOpen(true)}>
            📁 녹화된 영상 갤러리
          </button>
        </div>

        <div className="section">
          <h3>📂 Whisper 영상 파일 업로드 (STT)</h3>
          <input type="file" accept="video/*" onChange={handleSttUpload} />
        </div>

        <div className="section">
          <h3>🖼 YOLO 이미지 업로드</h3>
          <YoloUpload onUpload={handleUpload} />
        </div>

        <div className="section">
          <h3>✏️ YOLO 영상 업로드</h3>
          <input 
            type="file" 
            accept="video/*" 
            onChange={(e) => setYoloVideoFile(e.target.files[0])} 
          />
          <button 
            onClick={handleYoloVideoAnalyze}
            disabled={isAnalyzing}
            style={{
              backgroundColor: isAnalyzing ? '#ccc' : '#007bff',
              cursor: isAnalyzing ? 'not-allowed' : 'pointer'
            }}
          >
            {isAnalyzing ? '🔄 분석 중...' : '업로드 및 분석'}
          </button>
          
          {/* 로딩 상태 표시 */}
          {isAnalyzing && (
            <div style={{ marginTop: 10, color: '#666' }}>
              <p>⏳ YOLO 영상 분석 중입니다. 잠시만 기다려주세요...</p>
            </div>
          )}
          
          {/* 결과 영상 표시 */}
          {yoloVideoUrl && !isAnalyzing && (
            <div style={{ marginTop: 20 }}>
              <h4>📽 분석된 YOLO 영상</h4>
              <video 
                src={yoloVideoUrl} 
                controls 
                width="100%" 
                style={{ maxHeight: '400px' }}
                onError={(e) => {
                  console.error('비디오 로드 오류:', e);
                  alert('비디오를 불러올 수 없습니다. 파일 형식을 확인해주세요.');
                }}
                onLoadStart={() => console.log('비디오 로드 시작')}
                onCanPlay={() => console.log('비디오 재생 가능')}
              >
                <p>브라우저가 이 비디오 형식을 지원하지 않습니다.</p>
              </video>
              <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                URL: {yoloVideoUrl}
              </p>
            </div>
          )}
        </div>

        <div className="section">
          <VideoDisplay videoBlob={videoBlob} />
        </div>

        <div className="section">
          <h3>💬 AI 채팅</h3>
          <ChatBot externalMessages={messages} />
        </div>
      </div>

      {isGalleryOpen && (
        <div className="gallery-modal">
          <div className="gallery-content">
            <button className="close-button" onClick={() => setIsGalleryOpen(false)}>❌</button>
            <h2>🎞 녹화 영상 갤러리</h2>
            <div className="video-gallery-list">
              {videoList.map((blob, idx) => (
                <video
                  key={idx}
                  src={URL.createObjectURL(blob)}
                  controls
                  className="gallery-video"
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
