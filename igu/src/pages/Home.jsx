import { useState } from "react";
import FrameCapture from "../components/FrameCapture";
import GestureDisplay from "../components/GestureDisplay";
import Camera from "../components/camera";


const Home = () => {
  const [gesture, setGesture] = useState("");
  const [confidence, setConfidence] = useState(0);

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <h1>IGU – ISL Gesture Recognition</h1>

      <Camera />

      <FrameCapture
        onPrediction={(data) => {
          setGesture(data.gesture);
          setConfidence(data.confidence);
        }}
      />

      <GestureDisplay gesture={gesture} confidence={confidence} />
    </div>
  );
};

export default Home;
