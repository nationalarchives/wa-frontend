/**
 * Keyword Detector component
 * Enhances search inputs to split keywords by comma/space and display them as tokens
 *
 * This replicates the keyword tokenization functionality from:
 * https://webarchive.nationalarchives.gov.uk/search/
 *
 * Ideally, once this functionality has been removed from the legacy search page,
 * we can ditch this component. For now, this is just to ensure consistency
 * between services.
 */

class KeywordDetector {
  static selector() {
    return "input[data-search-keywords]";
  }

  constructor(input) {
    // Validate input element
    if (!input || !(input instanceof HTMLInputElement)) {
      console.error("KeywordDetector: Invalid input element provided");
      return;
    }

    /* ===== BEM CLASS NAMES ===== */
    this.CLASS_BLOCK = "keyword-detector";
    this.CLASS_LIST = `${this.CLASS_BLOCK}__list`;
    this.CLASS_TOKEN = `${this.CLASS_BLOCK}__token`;
    this.CLASS_REMOVE = `${this.CLASS_BLOCK}__remove`;
    this.CLASS_ENTRY = `${this.CLASS_BLOCK}__entry`;
    this.CLASS_FIELD = `${this.CLASS_BLOCK}__field`;
    this.CLASS_SUGGEST = `${this.CLASS_BLOCK}__suggest`;
    this.CLASS_HIDDEN_SOURCE = "tna-visually-hidden";
    this.CLASS_STATUS = `${this.CLASS_BLOCK}__status`;

    this.input = input;
    this.tokens = [];
    this.announceTimeout = null;
    this.MAX_TOKENS = 50; // Reasonable limit to prevent abuse
    this.originalInputId = this.input.id || "";

    this.buildUI();
    this.seedTokens();
    this.bindEvents();
  }

  /* ===== UTILS ===== */
  normalise(s) {
    return s.trim().replace(/\s+/g, " ");
  }

  parseTerms(s) {
    const terms = [];
    let current = "";
    let inQuotes = false;

    for (const char of s.trim()) {
      if (char === '"') {
        inQuotes = !inQuotes;
        continue;
      }

      if (!inQuotes && /[,\s]/.test(char)) {
        const term = this.normalise(current);
        if (term) {
          terms.push(term);
        }
        current = "";
        continue;
      }

      current += char;
    }

    const trailingTerm = this.normalise(current);
    if (trailingTerm) {
      terms.push(trailingTerm);
    }

    return { terms, inQuotes };
  }

  splitTerms(s) {
    return this.parseTerms(s).terms;
  }

  tokenKey(t) {
    return t.toLowerCase();
  }

  tokenNeedsQuotes(token) {
    return /[\s,]/.test(token);
  }

  serialiseToken(token) {
    const normalisedToken = this.normalise(token).replace(/"/g, "");

    if (!normalisedToken) {
      return "";
    }

    return this.tokenNeedsQuotes(normalisedToken)
      ? `"${normalisedToken}"`
      : normalisedToken;
  }

  hasUnclosedQuote(s) {
    return this.parseTerms(s).inQuotes;
  }

  /* ===== UI BUILDING ===== */
  buildUI() {
    /* Hide original input */
    this.input.classList.add(this.CLASS_HIDDEN_SOURCE);
    this.input.setAttribute("aria-hidden", "true");
    this.input.tabIndex = -1;

    /* Build UI */
    this.root = document.createElement("div");
    this.root.className = this.CLASS_BLOCK;

    this.list = document.createElement("ul");
    this.list.className = this.CLASS_LIST;
    this.list.setAttribute("aria-label", "Selected search terms");

    const entry = document.createElement("div");
    entry.className = this.CLASS_ENTRY;

    this.visible = document.createElement("input");
    this.visible.type = "text";
    this.visible.className = this.CLASS_FIELD;
    this.visible.autocomplete = "off";
    this.visible.spellcheck = this.input.spellcheck;
    this.visible.placeholder = this.input.placeholder || "";
    this.copyAccessibilityAttributes();

    this.suggest = document.createElement("button");
    this.suggest.type = "button";
    this.suggest.className = this.CLASS_SUGGEST;
    this.suggest.hidden = true;

    // Add ARIA live region for screen reader announcements
    this.status = document.createElement("div");
    this.status.className = this.CLASS_STATUS;
    this.status.setAttribute("role", "status");
    this.status.setAttribute("aria-live", "polite");
    this.status.setAttribute("aria-atomic", "true");

    entry.appendChild(this.visible);
    this.root.append(this.list, entry, this.suggest, this.status);
    this.input.insertAdjacentElement("afterend", this.root);
  }

  copyAccessibilityAttributes() {
    if (this.originalInputId) {
      this.visible.id = this.originalInputId;
      this.input.removeAttribute("id");
    }

    ["aria-describedby", "aria-labelledby", "aria-label"].forEach((attr) => {
      const value = this.input.getAttribute(attr);
      if (value) {
        this.visible.setAttribute(attr, value);
      }
    });

    if (
      !this.visible.hasAttribute("aria-label") &&
      !this.visible.hasAttribute("aria-labelledby")
    ) {
      this.visible.setAttribute(
        "aria-label",
        this.input.name || "Search keywords",
      );
    }
  }

  /* ===== STATE MANAGEMENT ===== */
  syncToOriginal({ notify = true } = {}) {
    const nextValue = this.tokens
      .map((token) => this.serialiseToken(token))
      .filter(Boolean)
      .join(" ");

    if (this.input.value === nextValue) {
      return;
    }

    this.input.value = nextValue;

    if (notify) {
      this.input.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }

  render({ notify = true } = {}) {
    // Create document fragment for better performance
    const fragment = document.createDocumentFragment();

    this.tokens.forEach((t, index) => {
      const li = document.createElement("li");
      li.className = this.CLASS_TOKEN;

      const text = document.createElement("span");
      text.textContent = t;

      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = this.CLASS_REMOVE;
      remove.setAttribute("aria-label", `Remove ${t}`);
      remove.textContent = "×";
      // Store index to avoid closure over variable 't'
      remove.dataset.tokenIndex = index;

      li.append(text, remove);
      fragment.appendChild(li);
    });

    // Clear and update list in one operation
    this.list.innerHTML = "";
    this.list.appendChild(fragment);

    this.syncToOriginal({ notify });
  }

  removeToken(index) {
    const token = this.tokens[index];
    if (typeof token !== "string") {
      return;
    }

    this.tokens.splice(index, 1);
    this.render();
    // Return focus to the input field for better UX
    requestAnimationFrame(() => {
      this.visible.focus();
    });
    this.announceToScreenReader(
      `Removed ${token}. ${this.tokens.length} keyword${this.tokens.length !== 1 ? "s" : ""} remaining.`,
    );
  }

  updateSuggest() {
    const v = this.normalise(this.visible.value);
    if (!v || this.tokens.length >= this.MAX_TOKENS) {
      this.suggest.hidden = true;
      return;
    }
    this.suggest.hidden = false;
    // Truncate very long text to prevent performance issues
    const displayText = v.length > 50 ? `${v.substring(0, 50)}...` : v;
    this.suggest.textContent = `Add ${displayText}…`;
  }

  commitFromVisible() {
    const raw = this.normalise(this.visible.value);
    if (!raw) return;

    const newTerms = [];
    const existingTokens = new Set(
      this.tokens.map((token) => this.tokenKey(token)),
    );
    this.splitTerms(raw).forEach((term) => {
      // Enforce max tokens limit
      if (this.tokens.length >= this.MAX_TOKENS) {
        return;
      }
      const key = this.tokenKey(term);
      if (!existingTokens.has(key)) {
        this.tokens.push(term);
        existingTokens.add(key);
        newTerms.push(term);
      }
    });

    this.visible.value = "";
    this.suggest.hidden = true;
    this.render();

    if (newTerms.length > 0) {
      const message =
        newTerms.length === 1
          ? `Added ${newTerms[0]}`
          : `Added ${newTerms.length} keywords`;
      this.announceToScreenReader(message);
    } else if (this.tokens.length >= this.MAX_TOKENS) {
      this.announceToScreenReader("Maximum number of keywords reached");
    }
  }

  seedTokens() {
    /* Seed from prefilled value */
    if (this.input.value) {
      const seen = new Set();
      this.tokens = this.splitTerms(this.input.value).filter((term) => {
        const key = this.tokenKey(term);
        if (seen.has(key)) {
          return false;
        }
        seen.add(key);
        return true;
      });
      this.render({ notify: false });
    }
  }

  /* ===== EVENT BINDING ===== */
  bindEvents() {
    /* Key handling */
    this.visible.addEventListener("keydown", (e) => this.handleKeydown(e));
    this.visible.addEventListener("input", () => this.updateSuggest());
    this.visible.addEventListener("paste", (e) => this.handlePaste(e));

    this.suggest.addEventListener("click", () => {
      this.commitFromVisible();
      this.visible.focus();
    });

    this.input.addEventListener("focus", () => this.visible.focus());

    // Event delegation for remove buttons (prevents memory leaks)
    this.list.addEventListener("click", (e) => {
      const button = e.target.closest(`.${this.CLASS_REMOVE}`);
      if (button && button.dataset.tokenIndex !== undefined) {
        const index = parseInt(button.dataset.tokenIndex, 10);
        if (!Number.isNaN(index)) {
          this.removeToken(index);
        }
      }
    });
  }

  handleKeydown(e) {
    const hasUnclosedQuote = this.hasUnclosedQuote(this.visible.value);

    // Space, Enter, or comma triggers commit
    if ([" ", "Enter", ","].includes(e.key)) {
      if (hasUnclosedQuote && [" ", ","].includes(e.key)) {
        return;
      }
      e.preventDefault();
      this.commitFromVisible();
      return;
    }

    // Tab commits but allows default tab behavior
    if (e.key === "Tab") {
      this.commitFromVisible();
      // Don't prevent default - allow tab to move focus naturally
      return;
    }

    // Backspace on empty field removes last token
    if (e.key === "Backspace" && !this.visible.value) {
      const removedToken = this.tokens.pop();
      this.render();
      if (removedToken) {
        this.announceToScreenReader(
          `Removed ${removedToken}. ${this.tokens.length} keyword${this.tokens.length !== 1 ? "s" : ""} remaining.`,
        );
      }
    }
  }

  handlePaste(e) {
    e.preventDefault();
    const text = (e.clipboardData || window.clipboardData).getData("text");
    this.visible.value = this.normalise(text);
    this.commitFromVisible();
  }

  announceToScreenReader(message) {
    if (!this.status) return;

    // Clear any existing timeout to prevent memory leaks
    if (this.announceTimeout) {
      clearTimeout(this.announceTimeout);
    }

    this.status.textContent = message;
    // Clear after announcement to allow repeated announcements of the same message
    this.announceTimeout = setTimeout(() => {
      this.status.textContent = "";
      this.announceTimeout = null;
    }, 1000);
  }

  // Cleanup method for when component is destroyed
  destroy() {
    if (this.announceTimeout) {
      clearTimeout(this.announceTimeout);
    }
  }
}

export default KeywordDetector;
