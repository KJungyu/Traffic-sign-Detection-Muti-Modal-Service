import React, { useState } from 'react';
import './App.css';
import CameraRecorder from './components/CameraRecorder';
import VideoDisplay from './components/VideoDisplay';
import ChatBot from './components/ChatBot';

function App() {
  const [videoBlob, setVideoBlob] = useState(null);
  const [videoList, setVideoList] = useState([]);
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);

  const handleSaveVideo = (blob) => {
    setVideoBlob(blob);
    setVideoList((prev) => [...prev, blob]);
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
          <h3>💬 AI 채팅</h3>
          <ChatBot />
        </div>
      </div>

      {/* ✅ 모달 추가 위치는 카드 바깥에서 전체 앱의 마지막에 위치해야 함 */}
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
