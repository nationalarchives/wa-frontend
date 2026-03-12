export function normalise(value) {
  return (value || "").trim().toLowerCase();
}

export function getDisplayLetter(letter) {
  return letter === "0-9" ? letter : letter.toUpperCase();
}

/**
 * Append FTS5-style prefix (*) to the last term so partial words match
 * (e.g. "sear" -> "sear*" so server returns "search"). Skips when query contains
 * a double-quote (phrase search).
 */
export function addPrefixToLastTerm(query) {
  if (!query || query.includes('"')) {
    return query;
  }
  const parts = query.split(/\s+/).filter(Boolean);
  if (!parts.length) {
    return query;
  }
  const last = parts[parts.length - 1];
  if (last.endsWith("*")) {
    return query;
  }
  parts[parts.length - 1] = last + "*";
  return parts.join(" ");
}

export function debounce(fn, ms) {
  let timeoutId = null;
  function debounced(...args) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    // Preserve calling context and args so this helper is safe for method callbacks.
    const context = this;
    timeoutId = setTimeout(() => {
      timeoutId = null;
      fn.apply(context, args);
    }, ms);
  }

  debounced.cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
  };

  return debounced;
}
