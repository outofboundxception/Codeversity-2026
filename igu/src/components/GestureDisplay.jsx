const GestureDisplay = ({ gesture, confidence }) => {
  if (!gesture) return <p>Detecting gesture...</p>;

  return (
    <div style={{ marginTop: "20px" }}>
      <h2>Gesture: {gesture}</h2>
      <p>Confidence: {(confidence * 100).toFixed(2)}%</p>
    </div>
  );
};

export default GestureDisplay;
