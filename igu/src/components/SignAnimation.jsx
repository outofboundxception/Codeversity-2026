import { useEffect, useState } from "react";

const SignAnimation = ({ images, speed = 600 }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!images || images.length === 0) return;

    setCurrentIndex(0);

    const interval = setInterval(() => {
      setCurrentIndex((prev) => {
        if (prev >= images.length - 1) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, speed);

    return () => clearInterval(interval);
  }, [images, speed]);

  if (!images || images.length === 0) return null;

  return (
    <div className="gesture-box">
      <img
        src={`http://localhost:8001${images[currentIndex]}`}
        alt="ISL sign"
        style={{
          width: "260px",
          height: "260px",
          objectFit: "contain"
        }}
      />
      <p className="confidence-text">
        Sign {currentIndex + 1} / {images.length}
      </p>
    </div>
  );
};

export default SignAnimation;
