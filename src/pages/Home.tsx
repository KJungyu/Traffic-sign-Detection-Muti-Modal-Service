import React, { useEffect, useState } from 'react';
import VideoPlayer from '../components/VideoPlayer';
import SignInfo from '../components/SignInfo';
import AudioPlayer from '../components/AudioPlayer';
import axios from 'axios';

const POLL_INTERVAL = 3000; // 3초마다 프레임 분석 요청

const Home = () => {
  const [sign, setSign] = useState<any | null>(null);
  const [audioUrl, setAudioUrl] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get('http://localhost:5001/api/detect-latest');
        if (response.data && response.data.label) {
          setSign(response.data);
          setAudioUrl(response.data.audioUrl);
          console.log('✅ 실시간 감지 결과:', response.data);
        }
      } catch (err) {
        console.error('❌ 실시간 감지 실패:', err);
        setError('감지 요청 실패');
      }
    }, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1>Traffic Sign Translator (실시간)</h1>
      <VideoPlayer />
      {sign && <SignInfo sign={sign} />}
      {audioUrl && <AudioPlayer url={audioUrl} />}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default Home;
