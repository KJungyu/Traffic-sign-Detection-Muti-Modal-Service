import React, { useState, useRef, useEffect } from 'react';
import './ChatBot.css';
import TTSButton from './TTSButton';

function ChatBot({ externalMessages, videoRef }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const currentSessionIdRef = useRef(null); 

  
  useEffect(() => {
    currentSessionIdRef.current = currentSessionId;
  }, [currentSessionId]);


  useEffect(() => {
    setMessages([
      { type: 'ai', text: '안녕하세요 AI 챗봇입니다' },
      { type: 'ai', text: '자주 묻는 질문을 선택해보세요' },
      ...(externalMessages && externalMessages.length ? externalMessages : []),
    ]);
  }, [externalMessages]);

  useEffect(() => {
    if (messages.length === 0) return;
    const lastMsg = messages[messages.length - 1];
    if (lastMsg.type === 'ai') {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new window.SpeechSynthesisUtterance(lastMsg.text);
        utter.lang = /[ㄱ-ㅎㅏ-ㅣ가-힣]/.test(lastMsg.text) ? "ko-KR" : "en-US";
        window.speechSynthesis.speak(utter);
      }
    }
  }, [messages]);


  const getVideoCurrentTime = () => {
    if (videoRef && videoRef.current) {
      console.log('getVideoCurrentTime:', videoRef.current.currentTime); 
      return videoRef.current.currentTime || 0;
    }
    return 0;
  };
  

  
  const sendMessage = (text, sttFromMic = false) => {
    if (!text.trim()) return;
    const userMessage = { type: 'user', text };

    let aiText = 'AI: 답변 준비 중입니다.';
    if (sttFromMic) {
      aiText = 'The Sign in the image is a stop sign, indicating that vehicles shoul come to a complete stop before proceeding. To act accoringly, when you see a stop sign, it is essential to come to a complete stop and obey the traffic regulations';
    } else {
      if (text.includes('표지판')) {
        aiText = 'This is a stop sign. It indicates that vehicles must stop completely before proceeding.';
      } else if (text.includes('챗봇 기능')) {
        aiText = '이 챗봇은 음성 입력을 텍스트로 변환하고, GPT 기반 응답을 생성하여 상호작용할 수 있도록 설계되었습니다.';
      }
    }
    const aiMessage = { type: 'ai', text: aiText };
    setMessages((prev) => [...prev, userMessage, aiMessage]);
    setInput('');
  };

 
  const startRecordingSession = async () => {
    try {
      const video_start_time = getVideoCurrentTime();
      const response = await fetch('http://localhost:5000/start_recording', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_current_time: video_start_time })
      });
      const data = await response.json();
      if (data.session_id) {
        setCurrentSessionId(data.session_id);
        return data.session_id;
      }
    } catch (error) {
      console.error('녹음 세션 시작 실패:', error);
      return null;
    }
  };

  
  const stopRecordingSession = async (sessionId) => {
    try {
      const video_end_time = getVideoCurrentTime();
      const response = await fetch('http://localhost:5000/stop_recording', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, video_current_time: video_end_time })
      });
      const data = await response.json();
      if (data.saved_frames > 0) {
        //setMessages((prev) => [...prev, {
          //type: 'ai',
          //text: `${data.saved_frames}개의 프레임이 STT 트리거 데이터셋에 저장되었습니다.`,
        //}]); 
      }
    } catch (error) {
      console.error('녹음 세션 종료 실패:', error);
    }
  };

  // 녹음 토글
  const toggleRecording = async () => {
    if (!isRecording) {
      const sessionId = await startRecordingSession();
      if (!sessionId) {
        alert('녹음 세션 시작에 실패했습니다.');
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        chunksRef.current = [];
        mediaRecorder.ondataavailable = (e) => chunksRef.current.push(e.data);
        mediaRecorder.onstop = async () => {
         
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('file', blob, 'recording.webm');
          try {
            const res = await fetch('http://localhost:5000/stt', {
              method: 'POST',
              body: formData,
            });
            sendMessage('What does it mean?', true);
          } catch (err) {
            console.error('STT 요청 실패:', err);
          }
          
          const sessionIdToStop = currentSessionIdRef.current;
          if (sessionIdToStop) {
            await stopRecordingSession(sessionIdToStop);
            setCurrentSessionId(null);
          }
        };
        mediaRecorder.start();
        setIsRecording(true);
        alert('녹음 시작되었습니다. 다시 누르면 중지됩니다.');
      } catch (err) {
        console.error('마이크 오류:', err);
        alert('마이크 접근에 실패했습니다.');
      }
    } else {
      if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
      if (streamRef.current) streamRef.current.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
      alert('🛑 녹음이 중지되었습니다.');
    }
  };

  // 단일 스냅샷 트리거
  const triggerSnapshot = async () => {
    try {
      const response = await fetch('http://localhost:5000/trigger_snapshot', { method: 'POST' });
      const data = await response.json();
      if (response.ok) {
        setMessages((prev) => [...prev, {
          type: 'ai',
          text: `${data.message} (프레임 번호: ${data.frame_number})`
        }]);
      } else {
        setMessages((prev) => [...prev, {
          type: 'ai',
          text: `스냅샷 저장 실패: ${data.error}`
        }]);
      }
    } catch (error) {
      console.error('스냅샷 트리거 실패:', error);
      setMessages((prev) => [...prev, {
        type: 'ai',
        text: '스냅샷 트리거 요청 실패'
      }]);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.type}`}>
            <strong>{msg.type === 'user' ? 'User' : 'AI'}:</strong> {msg.text}
            {msg.type === 'ai' && <TTSButton text={msg.text} />}
          </div>
        ))}
      </div>
      <div className="faq-buttons">
        <p><strong>자주 묻는 질문</strong></p>
        <button onClick={() => sendMessage('이 표지판에 대해 설명해줘')}>이 표지판에 대해 설명해줘</button>
        <button onClick={() => sendMessage('챗봇 기능에 대해 설명해줘')}>챗봇 기능에 대해 설명해줘</button>
        <button
          onClick={triggerSnapshot}
          style={{
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            margin: '5px'
          }}
        >
          단일 스냅샷 저장
        </button>
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          placeholder="메시지 입력..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage(input)}
        />
        <button
          onClick={toggleRecording}
          style={{
            backgroundColor: isRecording ? '#dc3545' : '#007bff',
            color: 'white',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {isRecording ? '🛑 중지' : '🎙️ 녹음'}
        </button>
        <button onClick={() => sendMessage(input)}>Send</button>
      </div>
      {isRecording && currentSessionId && (
        <div style={{
          position: 'fixed', top: '10px', right: '10px', backgroundColor: '#dc3545', color: 'white',
          padding: '10px', borderRadius: '8px', fontSize: '14px', boxShadow: '0 2px 8px rgba(0,0,0,0.3)'
        }}>
          🔴 녹음 중... (세션: {currentSessionId.substring(0, 8)})
        </div>
      )}
    </div>
  );
}

export default ChatBot;
