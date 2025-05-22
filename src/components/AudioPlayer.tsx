import React from 'react';

const AudioPlayer = ({ url }: { url: string }) => (
  <audio controls autoPlay style={{ marginTop: '1rem' }}>
    <source src={url} type="audio/mpeg" />
    브라우저가 오디오 태그를 지원하지 않습니다.
  </audio>
);

export default AudioPlayer;