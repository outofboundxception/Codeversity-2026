const GestureDisplay = ({
  gesture,
  confidence,
  recordedWords = [],
  isRecording = false,
}) => {
  // While recording
  if (isRecording) {
    return (
      <div className="gesture-box">
        <div className="gesture-text">
          {gesture || "Detecting gesture…"}
        </div>

        {gesture && (
          <div className="confidence-text">
            Confidence: {(confidence * 100).toFixed(2)}%
          </div>
        )}
      </div>
    );
  }

  // After recording stopped
  if (recordedWords.length > 0) {
    return (
      <div className="gesture-box">
        <h3>Recorded Output</h3>
        <p className="recorded-text">
          {recordedWords.join(" ")}
        </p>
      </div>
    );
  }

  // Default idle state
  return (
    <p className="status-text">
      Click <strong>Start Recording</strong> to begin
    </p>
  );
};

export default GestureDisplay;
