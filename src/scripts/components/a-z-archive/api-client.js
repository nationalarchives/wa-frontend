export default class ArchiveApiClient {
  constructor(charactersUrl, recordsApiUrl) {
    this.charactersUrl = charactersUrl;
    this.recordsApiUrl = recordsApiUrl;
    this.recordsByLetter = new Map();
    this.loadingByLetter = new Map();
  }

  async fetchCharacters() {
    const response = await fetch(this.charactersUrl, {
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to load characters (${response.status})`);
    }

    const payload = await response.json();
    return Array.isArray(payload.characters) ? payload.characters : [];
  }

  async fetchRecords(letter) {
    const query = new URLSearchParams({ character: letter });
    const response = await fetch(`${this.recordsApiUrl}?${query.toString()}`, {
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to load records for ${letter}`);
    }

    const payload = await response.json();
    return Array.isArray(payload.items) ? payload.items : [];
  }

  seedRecords(letter, records) {
    this.recordsByLetter.set(letter, records);
  }

  hasRecords(letter) {
    return this.recordsByLetter.has(letter);
  }

  getSeededEntries() {
    return this.recordsByLetter.entries();
  }

  async getRecordsForLetter(letter) {
    // Reuse cached records when available.
    if (this.recordsByLetter.has(letter)) {
      return this.recordsByLetter.get(letter);
    }

    // Reuse a pending request so repeated opens of the same letter don't duplicate calls.
    if (this.loadingByLetter.has(letter)) {
      return this.loadingByLetter.get(letter);
    }

    const promise = this.fetchRecords(letter)
      .then((items) => {
        this.recordsByLetter.set(letter, items);
        this.loadingByLetter.delete(letter);
        return items;
      })
      .catch((error) => {
        this.loadingByLetter.delete(letter);
        throw error;
      });

    this.loadingByLetter.set(letter, promise);
    return promise;
  }
}
