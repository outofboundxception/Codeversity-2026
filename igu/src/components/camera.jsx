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
    <div>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        width="400"
        style={{ borderRadius: "10px", border: "2px solid black" }}
        id="video"
      />
    </div>
  );
};

export default Camera;
