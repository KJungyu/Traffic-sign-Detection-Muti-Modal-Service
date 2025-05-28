import React, { useRef, useState } from 'react';

function CameraRecorder({ onVideoSave }) {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [stream, setStream] = useState(null);
  const [videoBlob, setVideoBlob] = useState(null);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    setStream(stream);
    videoRef.current.srcObject = stream;

    const recorder = new MediaRecorder(stream);
    let chunks = [];

    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      setVideoBlob(blob);
      onVideoSave(blob); // 부모로 전달
    };

    mediaRecorderRef.current = recorder;
    recorder.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    stream.getTracks().forEach(track => track.stop());
    setRecording(false);
  };

  return (
    <div>
      <video ref={videoRef} autoPlay muted style={{ width: '400px' }} />
      <div>
        {!recording ? (
          <button onClick={startRecording}>🎥 녹화 시작</button>
        ) : (
          <button onClick={stopRecording}>🛑 녹화 정지</button>
        )}
      </div>
    </div>
  );
}

export default CameraRecorder;
