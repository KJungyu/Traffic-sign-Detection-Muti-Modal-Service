function VideoDisplay({ videoBlob }) {
    if (!videoBlob) return null;
    const videoURL = URL.createObjectURL(videoBlob);
  
    return (
      <div>
        <h3>녹화된 영상</h3>
        <video src={videoURL} controls style={{ width: '400px' }} />
      </div>
    );
  }
  
  export default VideoDisplay;
  
