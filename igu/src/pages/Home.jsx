import { useState } from "react";
import FrameCapture from "../components/FrameCapture";
import GestureDisplay from "../components/GestureDisplay";
import Camera from "../components/camera";
import SpeechInput from "../components/SpeechInput";
import { tti } from "../utils/tti";

const Home = () => {
  const [mode, setMode] = useState("gesture-to-speech");

  // ---------- Gesture → Speech states ----------
  const [isRecording, setIsRecording] = useState(false);
  const [gesture, setGesture] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [recordedWords, setRecordedWords] = useState([]);

  // ---------- Speech → Text states ----------
  const [isListening, setIsListening] = useState(false);
  const [speechText, setSpeechText] = useState("");

  // ---------- Gesture → Speech logic ----------
  const handlePrediction = (data) => {
    setGesture(data.gesture);
    setConfidence(data.confidence);

    setRecordedWords((prev) => {
      if (prev[prev.length - 1] === data.gesture) return prev;
      return [...prev, data.gesture];
    });
  };

  // ---------- Speech → Text logic ----------
  const handleSpeechInput = (text) => {
    setSpeechText(tti(text)); // ISL-friendly text
    setIsListening(false);
  };

  return (
    <div className="app-container">
      <h1 className="app-title">IGU – ISL Translator</h1>

      {/* ===== MODE TOGGLE ===== */}
      <div className="mode-toggle">
        <button
          className={mode === "gesture-to-speech" ? "active" : ""}
          onClick={() => {
            setMode("gesture-to-speech");
            setIsListening(false);
          }}
        >
          ✋ Gesture → 🔊 Speech
        </button>

        <button
          className={mode === "speech-to-text" ? "active" : ""}
          onClick={() => {
            setMode("speech-to-text");
            setSpeechText("");
            setIsRecording(false);
          }}
        >
          🎤 Speech → 📝 Text
        </button>
      </div>

      {/* ===== GESTURE → SPEECH MODE ===== */}
      {mode === "gesture-to-speech" && (
        <>
          <Camera />

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

          {isRecording && (
            <FrameCapture onPrediction={handlePrediction} />
          )}

          <GestureDisplay
            gesture={gesture}
            confidence={confidence}
            recordedWords={recordedWords}
            isRecording={isRecording}
          />
        </>
      )}

      {/* ===== SPEECH → TEXT MODE ===== */}
      {mode === "speech-to-text" && (
        <>
          <SpeechInput
            isListening={isListening}
            onText={handleSpeechInput}
          />

          {!isListening ? (
            <button
              className="start-btn"
              onClick={() => {
                setSpeechText("");
                setIsListening(true);
              }}
            >
              🎤 Start Speaking
            </button>
          ) : (
            <button
              className="stop-btn"
              onClick={() => setIsListening(false)}
            >
              ⏹ Stop Speaking
            </button>
          )}

          {/* ===== OUTPUT BOX ===== */}
          <div className="gesture-box">
            <p className="gesture-text">
              {speechText || "Your ISL-formatted text will appear here..."}
            </p>
            <p className="confidence-text">
              ISL-formatted text
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default Home;
