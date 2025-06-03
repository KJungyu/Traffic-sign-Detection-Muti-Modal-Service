// src/components/VideoDisplay.js
import React from 'react';

function VideoDisplay({ videoBlob }) {
  if (!videoBlob) return <p>녹화된 영상이 없습니다.</p>;

  return (
    <div>
      <video
        controls
        src={URL.createObjectURL(videoBlob)}
        style={{ width: '100%', borderRadius: '12px' }}
      />
    </div>
  );
}

export default VideoDisplay;
