import { useState } from "react";
import FrameCapture from "../components/FrameCapture";
import GestureDisplay from "../components/GestureDisplay";
import Camera from "../components/camera";
import SpeechInput from "../components/SpeechInput";
import { tti } from "../utils/tti";
import { predictISL } from "../services/api";
import SignAnimation from "../components/SignAnimation";

const Home = () => {
  const [mode, setMode] = useState("gesture-to-speech");

  // Gesture → Speech
  const [isRecording, setIsRecording] = useState(false);
  const [gesture, setGesture] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [recordedWords, setRecordedWords] = useState([]);

  // Speech → Text
  const [isListening, setIsListening] = useState(false);
  const [speechText, setSpeechText] = useState("");
  const [islImages, setIslImages] = useState([]);


  const handlePrediction = (data) => {
    setGesture(data.gesture);
    setConfidence(data.confidence);

    setRecordedWords((prev) => {
      if (prev[prev.length - 1] === data.gesture) return prev;
      return [...prev, data.gesture];
    });
  };


  const handleSpeechInput = async (text) => {
    const islText = tti(text);
    setSpeechText(islText);
    setIsListening(false);

    try {
      const res = await predictISL(islText);
      setIslImages(res.images || []);
    } catch (err) {
      console.error("ISL prediction failed", err);
    }
  };


  return (
    <div className="cv-root">
      {/* ===== MODE BAR ===== */}
      <div className="top-bar">
        <button
          className={mode === "gesture-to-speech" ? "active" : ""}
          onClick={() => setMode("gesture-to-speech")}
        >
          Gesture → Speech
        </button>

        <button
          className={mode === "speech-to-text" ? "active" : ""}
          onClick={() => setMode("speech-to-text")}
        >
          Speech → Text
        </button>
      </div>

      {/* ===== CAMERA VIEW ===== */}
      {mode === "gesture-to-speech" && (
        <div className="camera-stage">
          <Camera />

          {/* Overlay like OpenCV */}
          <div className="overlay">
  <div className="overlay-bar">
  <span className="overlay-text">
    {gesture
      ? `${gesture} (${confidence.toFixed(2)})`
      : "—"}
  </span>
</div>
</div>
          {isRecording && (
            <FrameCapture onPrediction={handlePrediction} />
          )}
        </div>
      )}

      {/* ===== CONTROLS ===== */}
      <div className="controls">
        {mode === "gesture-to-speech" && (
          <>
            {!isRecording ? (
              <button
                className="control-btn start"
                onClick={() => {
                  setGesture("");
                  setConfidence(0);
                  setRecordedWords([]);
                  setIsRecording(true);
                }}
              >
                ▶ Start
              </button>
            ) : (
              <button
                className="control-btn stop"
                onClick={() => setIsRecording(false)}
              >
                ⏹ Stop
              </button>
            )}
          </>
        )}

        {mode === "speech-to-text" && (
          <>
            <SpeechInput
              isListening={isListening}
              onText={handleSpeechInput}
            />

            {!isListening ? (
              <button
                className="control-btn start"
                onClick={() => {
                  setSpeechText("");
                  setIsListening(true);
                }}
              >
                🎤 Start
              </button>
            ) : (
              <button
                className="control-btn stop"
                onClick={() => setIsListening(false)}
              >
                ⏹ Stop
              </button>
            )}
          </>
        )}
      </div>

      {/* ===== TEXT OUTPUT ===== */}
      {mode === "speech-to-text" && (
        <>
          <div className="text-output">
            {speechText || "Waiting for speech input..."}
          </div>

          <SignAnimation images={islImages} speed={600} />
        </>
      )}
    </div>
  );
};

export default Home;
