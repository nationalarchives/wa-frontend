export function normalise(value) {
  return (value || "").trim().toLowerCase();
}

export function getDisplayLetter(letter) {
  return letter === "0-9" ? letter : letter.toUpperCase();
}

export function debounce(fn, ms) {
  let timeoutId = null;
  return function (...args) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    const context = this;
    timeoutId = setTimeout(() => {
      timeoutId = null;
      fn.apply(context, args);
    }, ms);
  };
}
