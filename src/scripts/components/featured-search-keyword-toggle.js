import KeywordDetector from "./keyword-detector.js";

/**
 * Progressive enhancement for web featured search: keyword tokenisation only when
 * "Keyword search" is selected; plain input for "Search by website URL".
 */
export default class FeaturedSearchKeywordToggle {
  static selector() {
    return "[data-featured-search-keyword-toggle]";
  }

  /** Search query input inside the form */
  static SEARCH_INPUT_SELECTOR = 'input[name="q"]';
  static SEARCH_TYPE_INPUT_NAME = "search_type";
  static SEARCH_TYPE_KEYWORD = "keyword";
  static ATTR_SEARCH_KEYWORDS = "data-search-keywords";

  constructor(form) {
    this.form = form;
    this.input = form.querySelector(
      FeaturedSearchKeywordToggle.SEARCH_INPUT_SELECTOR,
    );
    this.detector = null;

    if (!this.input || this.input.tagName !== "INPUT") {
      return;
    }

    this._onRadioChange = () => this.applyMode();
    form
      .querySelectorAll(
        `input[name="${FeaturedSearchKeywordToggle.SEARCH_TYPE_INPUT_NAME}"]`,
      )
      .forEach((radio) => {
        radio.addEventListener("change", this._onRadioChange);
      });

    this.applyMode();
  }

  _checkedSearchType() {
    const checked = this.form.querySelector(
      `input[name="${FeaturedSearchKeywordToggle.SEARCH_TYPE_INPUT_NAME}"]:checked`,
    );
    return checked
      ? checked.value
      : FeaturedSearchKeywordToggle.SEARCH_TYPE_KEYWORD;
  }

  applyMode() {
    if (
      this._checkedSearchType() ===
      FeaturedSearchKeywordToggle.SEARCH_TYPE_KEYWORD
    ) {
      this.enableKeywordTokens();
    } else {
      this.disableKeywordTokens();
    }
  }

  enableKeywordTokens() {
    if (this.detector) {
      return;
    }
    this.input.setAttribute(
      FeaturedSearchKeywordToggle.ATTR_SEARCH_KEYWORDS,
      "",
    );
    this.detector = new KeywordDetector(this.input);
  }

  disableKeywordTokens() {
    if (this.detector) {
      this.detector.destroy();
      this.detector = null;
    }
    this.input.removeAttribute(
      FeaturedSearchKeywordToggle.ATTR_SEARCH_KEYWORDS,
    );
  }
}
