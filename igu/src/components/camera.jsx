import { useEffect, useRef, useState } from "react";

const Camera = () => {
  const videoRef = useRef(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        videoRef.current.srcObject = stream;
      } catch (err) {
        setError("Camera permission denied");
      }
    }

    startCamera();
  }, []);

  return (
  <div className="camera-box">
    {error && <p className="error-text">{error}</p>}
    <video
      ref={videoRef}
      autoPlay
      playsInline
      id="video"
    />
  </div>
);

};

export default Camera;
