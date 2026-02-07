// Text → ISL-friendly text
export const tti = (text) => {
  if (!text) return "";

  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, "")
    .split(/\s+/)
    .filter(word => !["is", "am", "are", "the", "a"].includes(word))
    .join(" ");
};
