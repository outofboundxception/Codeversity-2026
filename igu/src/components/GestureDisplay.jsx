const GestureDisplay = ({ gesture, confidence }) => {
  if (!gesture) {
    return (
      <p className="status-text">
        Detecting gesture…
      </p>
    );
  }

  return (
    <div className="gesture-box">
      <div className="gesture-text">
        {gesture}
      </div>
      <div className="confidence-text">
        Confidence: {(confidence * 100).toFixed(2)}%
      </div>
    </div>
  );
};

export default GestureDisplay;
