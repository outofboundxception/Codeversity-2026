import { useEffect, useRef } from "react";
import { predictGesture } from "../services/api";
import speak from "../utils/speak";

const FrameCapture = ({ onPrediction }) => {
  const lastGestureRef = useRef("");

  useEffect(() => {
    const interval = setInterval(async () => {
      const video = document.getElementById("video");
      if (!video || !video.videoWidth) return;

      const canvas = document.createElement("canvas");
      canvas.width = 640;
      canvas.height = 480;

      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, 640, 480);

      const image = canvas.toDataURL("image/jpeg");

      try {
        const result = await predictGesture(image);

        if (
          result &&
          result.confidence > 0.6 &&
          result.gesture !== lastGestureRef.current
        ) {
          lastGestureRef.current = result.gesture;
          onPrediction(result);
          speak(result.gesture);
        }
      } catch (err) {
        console.error("Prediction failed:", err);
      }
    }, 500); // 2 FPS

    return () => clearInterval(interval);
  }, [onPrediction]);

  return null;
};

export default FrameCapture;
