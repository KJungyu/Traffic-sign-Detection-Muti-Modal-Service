import React, { useState } from 'react';

const YoloUpload = () => {
  const [imageFile, setImageFile] = useState(null);
  const [resultUrl, setResultUrl] = useState('');

  const handleUpload = async () => {
    if (!imageFile) return alert('파일을 선택하세요');

    const formData = new FormData();
    formData.append('file', imageFile);

    const response = await fetch('http://localhost:5000/detect', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    if (data.result_image_url) {
      setResultUrl(data.result_image_url);
    } else {
      alert('분석 실패');
    }
  };

  return (
    <div className="section">
      <input type="file" accept="image/*" onChange={e => setImageFile(e.target.files[0])} />
      <button onClick={handleUpload}>업로드 및 분석</button>

      {resultUrl && (
        <div style={{ marginTop: 20 }}>
          <h4>📸 분석 결과</h4>
          <img src={resultUrl} alt="YOLO 분석 결과" width="100%" />
        </div>
      )}
    </div>
  );
};

export default YoloUpload;
