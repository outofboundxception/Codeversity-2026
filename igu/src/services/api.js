import axios from "axios";

const API_URL = "http://localhost:8000/predict";

export const predictGesture = async (image) => {
  const response = await axios.post(API_URL, {
    image: image,
  });

  return response.data;
};
