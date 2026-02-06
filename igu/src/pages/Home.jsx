import { useState } from "react";
import FrameCapture from "../components/FrameCapture";
import GestureDisplay from "../components/GestureDisplay";
import Camera from "../components/camera";

const Home = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [gesture, setGesture] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [recordedWords, setRecordedWords] = useState([]);

  const handlePrediction = (data) => {
    setGesture(data.gesture);
    setConfidence(data.confidence);

    setRecordedWords((prev) => {
      // avoid duplicate consecutive words
      if (prev[prev.length - 1] === data.gesture) return prev;
      return [...prev, data.gesture];
    });
  };

  return (
    <div className="app-container">
      <h1 className="app-title">
        IGU – ISL Gesture Recognition
      </h1>

      <Camera />

      {/* Start / Stop Buttons */}
      {!isRecording ? (
        <button
          className="start-btn"
          onClick={() => {
            setRecordedWords([]);
            setGesture("");
            setConfidence(0);
            setIsRecording(true);
          }}
        >
          ▶ Start Recording
        </button>
      ) : (
        <button
          className="stop-btn"
          onClick={() => setIsRecording(false)}
        >
          ⏹ Stop Recording
        </button>
      )}

      {/* Only capture frames when recording */}
      {isRecording && (
        <FrameCapture onPrediction={handlePrediction} />
      )}

      <GestureDisplay
        gesture={gesture}
        confidence={confidence}
        recordedWords={recordedWords}
        isRecording={isRecording}
      />
    </div>
  );
};

export default Home;
