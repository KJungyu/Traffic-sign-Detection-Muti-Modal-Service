import React, { useEffect, useRef, useState } from 'react';

const VideoPlayer = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const [recording, setRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState<Blob[]>([]);

  useEffect(() => {
    const getStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error('웹캠 연결 실패:', err);
      }
    };
    getStream();
  }, []);

  const handleStartRecording = () => {
    const stream = videoRef.current?.srcObject as MediaStream;
    if (!stream) return;

    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        setRecordedChunks((prev) => [...prev, event.data]);
      }
    };
    mediaRecorder.start();
    setRecording(true);
  };

  const handleStopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const handleDownload = () => {
    const blob = new Blob(recordedChunks, { type: 'video/webm' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'recorded-video.webm';
    a.click();
    URL.revokeObjectURL(url);
    setRecordedChunks([]);
  };

  return (
    <div>
      <video ref={videoRef} autoPlay muted style={{ width: '100%', border: '1px solid #ccc' }} />
      <div style={{ marginTop: '1rem' }}>
        {!recording && <button onClick={handleStartRecording}>🎥 녹화 시작</button>}
        {recording && <button onClick={handleStopRecording}>⏹ 녹화 중단</button>}
        {recordedChunks.length > 0 && <button onClick={handleDownload}>💾 저장하기</button>}
      </div>
    </div>
  );
};

export default VideoPlayer;
