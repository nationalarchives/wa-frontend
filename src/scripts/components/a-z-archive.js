import ArchiveApiClient from "./a-z-archive/api-client.js";
import {
  addPrefixToLastTerm,
  debounce,
  normalise,
} from "./a-z-archive/helpers.js";
import {
  createAccordion,
  renderError,
  renderLoading,
  renderRecords,
  resetPanelToBrowseFallback,
  updateLiveRegion,
} from "./a-z-archive/render.js";

const MIN_LIVE_SEARCH_LENGTH = 2;
const MIN_LOADER_MS = 250;
const LOADER_FADEOUT_MS = 200;

export default class AtoZArchive {
  static selector() {
    return "[data-az-enhanced-content]";
  }

  constructor(node) {
    this.enhancedContent = node;
    this.root = node.parentElement;
    this.form = this.root
      ? this.root.querySelector("[data-az-search-form]")
      : null;
    this.staticContent = this.root
      ? this.root.querySelector("[data-az-static-content]")
      : null;
    this.accordionList = node.querySelector("[data-az-accordion-list]");
    this.liveRegion = this.root
      ? this.root.querySelector("[data-az-live-region]")
      : null;
    this.clearControl = this.root
      ? this.root.querySelector("[data-az-clear]")
      : null;
    this.noResultsEl = node.querySelector("[data-az-no-results]") || null;

    this.letters = [];
    this.activeQuery = "";
    /** Run ID for async search; incremented to invalidate in-flight runs. Not a security token. */
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
      node.dataset.azRecordsApi,
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
    const nodes = this.staticContent.querySelectorAll(
      "[data-az-static-record]",
    );

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

  abortInFlightSearch() {
    if (this.searchAbortController) {
      this.searchAbortController.abort();
      this.searchAbortController = null;
    }
  }

  async fetchSearchResultsFromServer(query, runId) {
    // Always cancel older live-search requests so only the latest query remains active.
    this.abortInFlightSearch();
    this.searchAbortController = new AbortController();

    // Send last term as prefix (e.g. sear -> sear*) so FTS5 returns partial-word matches.
    const serverQuery = addPrefixToLastTerm(query);
    const searchUrl = new URL(
      `${this.baseUrl}?q=${encodeURIComponent(serverQuery)}`,
      window.location.origin
    );
    if (searchUrl.origin !== window.location.origin) {
      throw new Error("Search URL must be same-origin");
    }

    const response = await fetch(searchUrl.toString(), {
      headers: {
        Accept: "text/html",
      },
      signal: this.searchAbortController.signal,
    });

    if (!response.ok) {
      throw new Error(`Search failed (${response.status})`);
    }

    if (this.currentToken !== runId) {
      return null;
    }

    const html = await response.text();
    if (this.currentToken !== runId) {
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

  async loadLetterIntoPanel(details) {
    const letter = details.dataset.letter;
    const panel = details.querySelector("[data-panel-letter]");

    if (!panel || !letter) {
      return [];
    }

    const loadStarted = Date.now();
    renderLoading(panel);

    try {
      const records = await this.api.getRecordsForLetter(letter);
      const elapsed = Date.now() - loadStarted;
      if (elapsed < MIN_LOADER_MS) {
        await new Promise((r) => setTimeout(r, MIN_LOADER_MS - elapsed));
      }
      const loader = panel.querySelector(".accordion__loading");
      if (loader) {
        loader.classList.add("accordion__loading--out");
        await new Promise((r) => setTimeout(r, LOADER_FADEOUT_MS));
      }
      renderRecords(panel, records);
      return records;
    } catch (_error) {
      const elapsed = Date.now() - loadStarted;
      if (elapsed < MIN_LOADER_MS) {
        await new Promise((r) => setTimeout(r, MIN_LOADER_MS - elapsed));
      }
      const loader = panel.querySelector(".accordion__loading");
      if (loader) {
        loader.classList.add("accordion__loading--out");
        await new Promise((r) => setTimeout(r, LOADER_FADEOUT_MS));
      }
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
    if (this.clearControl) {
      this.clearControl.hidden = true;
    }
    if (this.noResultsEl) {
      this.noResultsEl.hidden = true;
    }
    if (this.accordionList) {
      this.accordionList.hidden = false;
    }
  }

  async applySearch(
    query,
    detailsElements,
    urlQuery = query,
    fallbackToPageOnError = false,
  ) {
    // Run ID guards ensure only the newest async search can mutate UI state (not a security token).
    const runId = this.currentToken + 1;
    this.currentToken = runId;
    this.activeQuery = query;
    const cacheKey = normalise(query);
    let matchedByLetter = this.searchResultsCache.get(cacheKey);

    if (!matchedByLetter) {
      try {
        // Live search uses one server-rendered search response, parsed client-side,
        // instead of crawling per-letter API endpoints.
        matchedByLetter = await this.fetchSearchResultsFromServer(query, runId);
      } catch (error) {
        if (error && error.name === "AbortError") {
          return;
        }
        this.liveRegion.textContent = "Live search is temporarily unavailable.";
        // On form submit, redirect to full page so user still gets server-rendered results.
        if (fallbackToPageOnError) {
          window.location.assign(
            `${this.baseUrl}?q=${encodeURIComponent(urlQuery)}`,
          );
        }
        return;
      } finally {
        this.searchAbortController = null;
      }

      if (this.currentToken !== runId || !matchedByLetter) {
        return;
      }

      this.searchResultsCache.set(cacheKey, matchedByLetter);
    } else {
      this.abortInFlightSearch();
    }

    if (this.currentToken !== runId) {
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

    if (this.noResultsEl) {
      if (resultCount === 0) {
        this.noResultsEl.textContent = `No records found for "${urlQuery}".`;
        this.noResultsEl.hidden = false;
        this.accordionList.hidden = true;
      } else {
        this.noResultsEl.hidden = true;
        this.accordionList.hidden = false;
      }
    }

    updateLiveRegion(this.liveRegion, resultCount, letterCount);
    history.replaceState(
      {},
      "",
      `${this.baseUrl}?q=${encodeURIComponent(urlQuery)}`,
    );
    if (this.clearControl) {
      this.clearControl.hidden = false;
    }
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

    searchInput.addEventListener("input", debounce(runSearch, 300));

    this.form.addEventListener("submit", async (event) => {
      event.preventDefault();
      runSearch(true);
    });

    if (this.clearControl) {
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
        staticGrouped.get(this.selectedCharacter),
      );
    }
    if (this.initialSearchQuery) {
      this.searchResultsCache.set(this.initialSearchQuery, staticGrouped);
    }

    try {
      const letters = await this.api.fetchCharacters();
      // Place 0-9 after Z in the accordion list.
      this.letters =
        letters.indexOf("0-9") === -1
          ? letters
          : [...letters.filter((l) => l !== "0-9"), "0-9"];
    } catch (_error) {
      return;
    }

    const detailsElements = this.letters.map((letter) =>
      createAccordion(letter, this.baseUrl),
    );
    detailsElements.forEach((details) =>
      this.accordionList.appendChild(details),
    );

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
        this.enhancedContent.dataset.searchQuery || initialQuery,
      );
      return;
    }

    if (selectedCharacter) {
      const selectedDetails = detailsElements.find(
        (details) => details.dataset.letter === selectedCharacter,
      );
      if (selectedDetails) {
        selectedDetails.open = true;
      }
    }
  }
}
