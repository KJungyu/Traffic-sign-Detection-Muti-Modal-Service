import React, { useState, useRef, useEffect } from 'react';
import './ChatBot.css';

function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);

  // 📌 초기 안내 문구 (최초 1회)
  useEffect(() => {
    setMessages([
      { type: 'ai', text: '안녕하세요~ AI 챗봇입니다 ❤️' },
      { type: 'ai', text: '📌 자주 묻는 질문을 선택해보세요!' },
    ]);
  }, []);

  const sendMessage = (text) => {
    const userMessage = { type: 'user', text };
    let aiText = 'AI: 답변 준비 중입니다.';

    // 사전 정의된 응답 처리
    if (text.includes('표지판')) {
      aiText = '이 표지판은 교통 안내 및 경고를 위해 사용됩니다. 종류에 따라 의미가 다르며, AI를 활용해 이미지로도 분석 가능합니다.';
    } else if (text.includes('챗봇 기능')) {
      aiText = '이 챗봇은 음성 입력을 텍스트로 변환하고, GPT 기반 응답을 생성하여 상호작용할 수 있도록 설계되었습니다.';
    }

    const aiMessage = { type: 'ai', text: aiText };
    setMessages((prev) => [...prev, userMessage, aiMessage]);
    setInput('');
  };

  const toggleRecording = async () => {
    if (!isRecording) {
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
          formData.append('audio', blob, 'recording.webm');

          try {
            const res = await fetch('http://localhost:5000/stt', {
              method: 'POST',
              body: formData,
            });
            const data = await res.json();
            if (data.text) {
              sendMessage(data.text); // 자동 전송
            } else {
              console.error('STT 오류', data);
            }
          } catch (err) {
            console.error('STT 요청 실패:', err);
          }
        };

        mediaRecorder.start();
        setIsRecording(true);
        alert('🎙️ 녹음 시작되었습니다. 다시 누르면 중지됩니다.');
      } catch (err) {
        console.error('🎙️ 마이크 오류:', err);
      }
    } else {
      mediaRecorderRef.current.stop();
      streamRef.current.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
      alert('🛑 녹음이 중지되었습니다.');
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.type}`}>
            <strong>{msg.type === 'user' ? 'User' : 'AI'}:</strong> {msg.text}
          </div>
        ))}
      </div>

      {/* 📌 FAQ 버튼들 */}
      <div className="faq-buttons">
        <p><strong>📌 자주 묻는 질문</strong></p>
        <button onClick={() => sendMessage('이 표지판에 대해 설명해줘')}>🪧 이 표지판에 대해 설명해줘</button>
        <button onClick={() => sendMessage('챗봇 기능에 대해 설명해줘')}>🤖 챗봇 기능에 대해 설명해줘</button>
      </div>

      {/* 🔽 입력창 + 마이크 */}
      <div className="chat-input-area">
        <input
          type="text"
          placeholder="메시지 입력..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage(input)}
        />
        <button onClick={toggleRecording}>{isRecording ? '🛑' : '🎙️'}</button>
        <button onClick={() => sendMessage(input)}>Send</button>
      </div>
    </div>
  );
}

export default ChatBot;
