import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

export const getDetectionResult = async (imageData: File) => {
  const formData = new FormData();
  formData.append("image", imageData);

  const response = await axios.post(`${BASE_URL}/api/detect`, formData);
  return response.data;
};
