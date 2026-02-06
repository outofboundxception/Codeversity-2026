import axios from "axios";

const API_URL = "http://localhost:8000/api/predict";

let frameIdCounter = 0;

export const predictGesture = async (image) => {
  try {
    const response = await axios.post(API_URL, {
      frame: image,
      frame_id: frameIdCounter++,
      timestamp: Date.now() / 1000
    });

    // Map backend response to frontend format
    if (response.data.success && response.data.prediction && response.data.prediction.text) {
      return {
        gesture: response.data.prediction.text,
        confidence: response.data.prediction.confidence
      };
    }

    // No hand detected or low confidence
    return null;

  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};