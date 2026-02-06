import { useEffect } from "react";
import { predictGesture } from "../services/api";
import speak from "../utils/speak";

const FrameCapture = ({ onPrediction }) => {
  useEffect(() => {
    const interval = setInterval(async () => {
      const video = document.getElementById("video");
      if (!video) return;

      const canvas = document.createElement("canvas");
      canvas.width = 224;
      canvas.height = 224;

      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, 224, 224);

      const image = canvas.toDataURL("image/jpeg");

      try {
        const result = await predictGesture(image);
        if (result.confidence > 0.7) {
          onPrediction(result);
          speak(result.gesture);
        }
      } catch (err) {
        console.error("Prediction failed");
      }
    }, 500); // 2 FPS

    return () => clearInterval(interval);
  }, [onPrediction]);

  return null;
};

export default FrameCapture;
