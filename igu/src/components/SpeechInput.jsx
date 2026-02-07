import { useEffect, useRef } from "react";

const SpeechInput = ({ isListening, onText }) => {
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech recognition not supported");
      return;
    }

    recognitionRef.current = new window.webkitSpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.lang = "en-IN";

    recognitionRef.current.onresult = (event) => {
      const text = event.results[0][0].transcript;
      onText(text);
    };
  }, [onText]);

  useEffect(() => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.start();
    } else {
      recognitionRef.current.stop();
    }
  }, [isListening]);

  return null; // UI handled in Home.jsx
};

export default SpeechInput;
