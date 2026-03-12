export function normalise(value) {
  return (value || "").trim().toLowerCase();
}

export function getDisplayLetter(letter) {
  return letter === "0-9" ? letter : letter.toUpperCase();
}

/** Max length for search query sent to server; must match server-side limit. */
export const MAX_SEARCH_QUERY_LENGTH = 200;

/**
 * Append FTS5-style prefix (*) to the last term so partial words match
 * (e.g. "sear" -> "sear*" so server returns "search"). Skips when query contains
 * a double-quote (phrase search). Caller should pass a length-limited query;
 * server must validate/sanitize for FTS5.
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

/**
 * Parse nodes with [data-az-static-record] into a Map of letter -> records.
 * Used for both static page content and parsed search-result HTML.
 */
export function parseRecordNodes(nodes) {
  const grouped = new Map();
  nodes.forEach((node) => {
    const letter = normalise(node.dataset.firstCharacter);
    if (!letter) {
      return;
    }
    const existing = grouped.get(letter) || [];
    existing.push({
      profile_name: node.dataset.profileName || "",
      description: node.dataset.description || "",
      record_url: node.dataset.recordUrl || "",
      archive_link: node.dataset.archiveLink || "",
      first_capture_display: node.dataset.firstCapture || "",
      latest_capture_display: node.dataset.latestCapture || "",
      ongoing: node.dataset.ongoing === "true",
      first_character: letter,
    });
    grouped.set(letter, existing);
  });
  return grouped;
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
