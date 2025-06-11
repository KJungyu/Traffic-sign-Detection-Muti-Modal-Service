import React from "react";

function TTSButton({ text }) {
  const speak = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utter = new window.SpeechSynthesisUtterance(text);
      // 한글이면 ko-KR, 아니면 en-US
      utter.lang = /[ㄱ-ㅎㅏ-ㅣ가-힣]/.test(text) ? "ko-KR" : "en-US";
      window.speechSynthesis.speak(utter);
    } else {
      alert("이 브라우저는 음성 합성을 지원하지 않습니다.");
    }
  };

  return (
    <button
      onClick={speak}
      style={{
        marginLeft: "10px",
        background: "#fd7b8c",
        border: "none",
        color: "white",
        padding: "7px 15px",
        fontSize: "15px",
        borderRadius: "10px",
        cursor: "pointer",
      }}
    >
      <span role="img" aria-label="listen">🔊</span> Listen
    </button>
  );
}

export default TTSButton;
