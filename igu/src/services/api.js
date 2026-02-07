import axios from "axios";

const API_URL = "http://localhost:8000/api/predict";

export const predictGesture = async (image) => {
  try {
    const response = await axios.post(API_URL, {
      image: image,   // ✅ MATCH backend
    });

    // ✅ MATCH backend response
    return {
      gesture: response.data.gesture,
      confidence: response.data.confidence,
    };

  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};
