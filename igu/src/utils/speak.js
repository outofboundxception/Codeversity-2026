const speak = (text) => {
  if (!text) return;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-IN";
  window.speechSynthesis.cancel(); // stop previous
  window.speechSynthesis.speak(utterance);
};

export default speak;
