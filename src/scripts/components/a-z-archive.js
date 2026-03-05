import ArchiveApiClient from "./a-z-archive/api-client.js";
import { debounce, normalise } from "./a-z-archive/helpers.js";
import {
  createAccordion,
  renderError,
  renderLoading,
  renderRecords,
  resetPanelToBrowseFallback,
  updateLiveRegion,
} from "./a-z-archive/render.js";

const MIN_LIVE_SEARCH_LENGTH = 2;

export default class AtoZArchive {
  static selector() {
    return "[data-az-enhanced-content]";
  }

  constructor(node) {
    this.enhancedContent = node;
    this.root = node.parentElement;
    this.form = this.root ? this.root.querySelector("[data-az-search-form]") : null;
    this.staticContent = this.root
      ? this.root.querySelector("[data-az-static-content]")
      : null;
    this.accordionList = node.querySelector("[data-az-accordion-list]");
    this.liveRegion = this.root
      ? this.root.querySelector("[data-az-live-region]")
      : null;
    this.clearControl = this.root ? this.root.querySelector("[data-az-clear]") : null;

    this.letters = [];
    this.activeQuery = "";
    this.currentToken = 0;
    this.searchResultsCache = new Map();
    this.activeSearchResultsByLetter = new Map();
    this.searchAbortController = null;
    this.initialSearchQuery = normalise(node.dataset.searchQuery);
    this.selectedCharacter = normalise(node.dataset.selectedCharacter);

    if (
      !this.form ||
      !this.staticContent ||
      !this.accordionList ||
      !this.liveRegion
    ) {
      return;
    }

    this.baseUrl =
      this.form.dataset.azBaseUrl ||
      this.form.getAttribute("action") ||
      window.location.pathname;

    this.api = new ArchiveApiClient(
      node.dataset.azCharactersApi,
      node.dataset.azRecordsApi
    );

    if (!this.api.charactersUrl || !this.api.recordsApiUrl) {
      return;
    }

    this.init();
  }

  parseStaticRecords() {
    // Parse server-rendered records from the page so initial enhancement can reuse them
    // without refetching immediately.
    const grouped = new Map();
    const nodes = this.staticContent.querySelectorAll("[data-az-static-record]");

    nodes.forEach((node) => {
      const letter = normalise(node.dataset.firstCharacter);
      if (!letter) {
        return;
      }

      const existing = grouped.get(letter) || [];
      existing.push({
        profile_name: node.dataset.profileName || "",
        sort_name: node.dataset.sortName || "",
        description: node.dataset.description || "",
        record_url: node.dataset.recordUrl || "",
        archive_link: node.dataset.archiveLink || "",
        domain_type: node.dataset.domainType || "",
        first_capture_display: node.dataset.firstCapture || "",
        latest_capture_display: node.dataset.latestCapture || "",
        ongoing: node.dataset.ongoing === "true",
        first_character: letter,
      });

      grouped.set(letter, existing);
    });

    return grouped;
  }

  abortInFlightSearch() {
    if (this.searchAbortController) {
      this.searchAbortController.abort();
      this.searchAbortController = null;
    }
  }

  async fetchSearchResultsFromServer(query, token) {
    // Always cancel older live-search requests so only the latest query remains active.
    this.abortInFlightSearch();
    this.searchAbortController = new AbortController();

    const response = await fetch(
      `${this.baseUrl}?q=${encodeURIComponent(query)}`,
      {
        headers: {
          Accept: "text/html",
        },
        signal: this.searchAbortController.signal,
      }
    );

    if (!response.ok) {
      throw new Error(`Search failed (${response.status})`);
    }

    if (this.currentToken !== token) {
      return null;
    }

    const html = await response.text();
    if (this.currentToken !== token) {
      return null;
    }

    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const grouped = new Map();
    const nodes = doc.querySelectorAll("[data-az-static-record]");

    nodes.forEach((node) => {
      const letter = normalise(node.dataset.firstCharacter);
      if (!letter) {
        return;
      }

      const existing = grouped.get(letter) || [];
      existing.push({
        profile_name: node.dataset.profileName || "",
        sort_name: node.dataset.sortName || "",
        description: node.dataset.description || "",
        record_url: node.dataset.recordUrl || "",
        archive_link: node.dataset.archiveLink || "",
        domain_type: node.dataset.domainType || "",
        first_capture_display: node.dataset.firstCapture || "",
        latest_capture_display: node.dataset.latestCapture || "",
        ongoing: node.dataset.ongoing === "true",
        first_character: letter,
      });
      grouped.set(letter, existing);
    });

    return grouped;
  }

  async loadLetterIntoPanel(details) {
    const letter = details.dataset.letter;
    const panel = details.querySelector("[data-panel-letter]");

    if (!panel || !letter) {
      return [];
    }

    renderLoading(panel);

    try {
      const records = await this.api.getRecordsForLetter(letter);
      renderRecords(panel, records);
      return records;
    } catch (_error) {
      renderError(panel, letter, this.baseUrl);
      return [];
    }
  }

  resetBrowseMode(detailsElements) {
    this.abortInFlightSearch();
    // Invalidate any in-flight search pipeline to prevent stale UI updates.
    this.currentToken += 1;
    this.activeQuery = "";
    this.activeSearchResultsByLetter = new Map();

    detailsElements.forEach((details) => {
      details.hidden = false;
      details.open = false;

      const panel = details.querySelector("[data-panel-letter]");
      if (!panel) {
        return;
      }

      resetPanelToBrowseFallback(panel, details.dataset.letter, this.baseUrl);
    });

    updateLiveRegion(this.liveRegion, 0, 0);
    history.replaceState({}, "", this.baseUrl);
  }

  async applySearch(
    query,
    detailsElements,
    urlQuery = query,
    fallbackToPageOnError = false
  ) {
    // Token guards ensure only the newest async search can mutate UI state.
    const token = this.currentToken + 1;
    this.currentToken = token;
    this.activeQuery = query;
    const cacheKey = normalise(query);
    let matchedByLetter = this.searchResultsCache.get(cacheKey);

    if (!matchedByLetter) {
      try {
        // Live search uses one server-rendered search response, parsed client-side,
        // instead of crawling per-letter API endpoints.
        matchedByLetter = await this.fetchSearchResultsFromServer(query, token);
      } catch (error) {
        if (error && error.name === "AbortError") {
          return;
        }
        this.liveRegion.textContent =
          "Live search is temporarily unavailable.";
        if (fallbackToPageOnError) {
          window.location.assign(
            `${this.baseUrl}?q=${encodeURIComponent(urlQuery)}`
          );
        }
        return;
      } finally {
        this.searchAbortController = null;
      }

      if (this.currentToken !== token || !matchedByLetter) {
        return;
      }

      this.searchResultsCache.set(cacheKey, matchedByLetter);
    } else {
      this.abortInFlightSearch();
    }

    if (this.currentToken !== token) {
      return;
    }

    this.activeSearchResultsByLetter = matchedByLetter;

    let resultCount = 0;
    let letterCount = 0;

    detailsElements.forEach((details) => {
      const letter = details.dataset.letter;
      const panel = details.querySelector("[data-panel-letter]");
      const matches = matchedByLetter.get(letter) || [];

      if (matches.length) {
        details.hidden = false;
        details.open = true;
        letterCount += 1;
        resultCount += matches.length;
        if (panel) {
          renderRecords(panel, matches);
        }
      } else {
        details.hidden = true;
        details.open = false;
      }
    });

    updateLiveRegion(this.liveRegion, resultCount, letterCount);
    history.replaceState(
      {},
      "",
      `${this.baseUrl}?q=${encodeURIComponent(urlQuery)}`
    );
  }

  bindAccordionEvents(detailsElements) {
    detailsElements.forEach((details) => {
      details.addEventListener("toggle", async () => {
        if (!details.open) {
          return;
        }

        const panel = details.querySelector("[data-panel-letter]");
        if (!panel) {
          return;
        }

        if (this.activeQuery) {
          const matches =
            this.activeSearchResultsByLetter.get(details.dataset.letter) || [];
          renderRecords(panel, matches);
          return;
        }

        await this.loadLetterIntoPanel(details);
      });
    });
  }

  bindSearchForm(detailsElements) {
    const searchInput = this.form.querySelector('input[name="q"]');
    if (!searchInput) {
      return;
    }

    const runSearch = (fromSubmit = false) => {
      const rawQuery = searchInput.value.trim();
      const query = normalise(rawQuery);
      if (!query) {
        this.resetBrowseMode(detailsElements);
        return;
      }
      if (!fromSubmit && query.length < MIN_LIVE_SEARCH_LENGTH) {
        // Keep live typing conservative at scale; users can still submit short terms.
        this.resetBrowseMode(detailsElements);
        return;
      }

      this.applySearch(query, detailsElements, rawQuery, fromSubmit);
    };

    searchInput.addEventListener(
      "input",
      debounce(runSearch, 300)
    );

    this.form.addEventListener("submit", async (event) => {
      event.preventDefault();
      runSearch(true);
    });

    if (this.clearControl) {
      this.clearControl.hidden = false;
      this.clearControl.addEventListener("click", (event) => {
        event.preventDefault();
        if (searchInput) {
          searchInput.value = "";
        }
        this.resetBrowseMode(detailsElements);
      });
    }
  }

  async init() {
    const staticGrouped = this.parseStaticRecords();

    // Only seed browse cache from a letter page, not from search result pages
    // (search pages may include partial per-letter subsets).
    if (this.selectedCharacter && staticGrouped.has(this.selectedCharacter)) {
      this.api.seedRecords(
        this.selectedCharacter,
        staticGrouped.get(this.selectedCharacter)
      );
    }
    if (this.initialSearchQuery) {
      this.searchResultsCache.set(this.initialSearchQuery, staticGrouped);
    }

    try {
      this.letters = await this.api.fetchCharacters();
    } catch (_error) {
      return;
    }

    const detailsElements = this.letters.map((letter) =>
      createAccordion(letter, this.baseUrl)
    );
    detailsElements.forEach((details) => this.accordionList.appendChild(details));

    this.bindAccordionEvents(detailsElements);
    this.bindSearchForm(detailsElements);

    const initialQuery = this.initialSearchQuery;
    const selectedCharacter = this.selectedCharacter;

    this.enhancedContent.hidden = false;
    this.staticContent.hidden = true;

    if (initialQuery) {
      const searchInput = this.form.querySelector('input[name="q"]');
      if (searchInput) {
        searchInput.value = initialQuery;
      }

      await this.applySearch(
        initialQuery,
        detailsElements,
        this.enhancedContent.dataset.searchQuery || initialQuery
      );
      return;
    }

    if (selectedCharacter) {
      const selectedDetails = detailsElements.find(
        (details) => details.dataset.letter === selectedCharacter
      );
      if (selectedDetails) {
        selectedDetails.open = true;
      }
    }
  }
}
