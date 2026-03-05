import { getDisplayLetter } from "./helpers.js";

const CLASSES = {
  marginTopXs: "tna-!--margin-top-xs",
  marginBottomS: "tna-!--margin-bottom-s",
  headingM: "tna-heading-m",
  accordion: "accordion",
  accordionSummary: "accordion__summary",
  accordionHeader: "accordion__header",
  accordionTitle: "accordion__title heading heading--four",
  accordionToggle: "accordion__toggle",
  accordionToggleText: "accordion__toggle-text",
  accordionIcon: "accordion__icon",
  accordionContent: "accordion__content",
  supporting: "supporting",
};

export function createLink(href, text, className) {
  const link = document.createElement("a");
  link.textContent = text;

  if (href) {
    link.href = href;
  }

  if (className) {
    link.className = className;
  }

  return link;
}

export function renderRecords(panel, records) {
  panel.innerHTML = "";

  if (!records.length) {
    const empty = document.createElement("p");
    empty.className = CLASSES.marginTopXs;
    empty.textContent = "No matching records.";
    panel.appendChild(empty);
    return;
  }

  const list = document.createElement("ul");
  list.className = CLASSES.marginTopXs;

  records.forEach((record) => {
    const item = document.createElement("li");
    item.className = CLASSES.marginBottomS;

    const heading = document.createElement("h3");
    heading.className = CLASSES.headingM;

    if (record.archive_link) {
      heading.appendChild(createLink(record.archive_link, record.profile_name));
    } else {
      heading.textContent = record.profile_name;
    }

    item.appendChild(heading);

    const meta = document.createElement("ul");
    meta.className = CLASSES.supporting;

    if (record.record_url) {
      const urlLine = document.createElement("li");
      urlLine.textContent = record.record_url;
      meta.appendChild(urlLine);
    }

    const capturesLine = document.createElement("li");
    capturesLine.textContent = `Captures from ${record.first_capture_display || ""} to${
      record.ongoing ? " Ongoing" : ` ${record.latest_capture_display || ""}`
    }`;
    meta.appendChild(capturesLine);

    if (meta.children.length) {
      item.appendChild(meta);
    }

    list.appendChild(item);
  });

  panel.appendChild(list);
}

export function renderLoading(panel) {
  panel.innerHTML = "";

  const loading = document.createElement("p");
  loading.className = CLASSES.marginTopXs;
  loading.textContent = "Loading...";
  panel.appendChild(loading);
}

export function renderError(panel, letter, baseUrl) {
  panel.innerHTML = "";

  const text = document.createElement("p");
  text.className = CLASSES.marginTopXs;
  text.textContent = "Sorry, records could not be loaded right now.";
  panel.appendChild(text);

  const fallback = document.createElement("p");
  fallback.className = CLASSES.marginTopXs;
  fallback.appendChild(
    createLink(
      `${baseUrl}?character=${encodeURIComponent(letter)}`,
      "Open the letter page",
    ),
  );
  panel.appendChild(fallback);
}

export function updateLiveRegion(liveRegion, resultCount, letterCount) {
  liveRegion.textContent = `${resultCount} results across ${letterCount} letters`;
}

export function createAccordion(letter, baseUrl) {
  const details = document.createElement("details");
  details.className = CLASSES.accordion;
  details.dataset.letter = letter;

  const summary = document.createElement("summary");
  summary.className = CLASSES.accordionSummary;

  const heading = document.createElement("h3");
  heading.className = CLASSES.accordionHeader;

  const title = document.createElement("span");
  title.className = CLASSES.accordionTitle;
  title.textContent = getDisplayLetter(letter);

  const toggle = document.createElement("span");
  toggle.className = CLASSES.accordionToggle;
  toggle.setAttribute("aria-hidden", "true");

  const toggleText = document.createElement("span");
  toggleText.className = CLASSES.accordionToggleText;
  toggleText.dataset.show = "Show";
  toggleText.dataset.hide = "Hide";
  toggleText.textContent = "Show";

  const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  icon.setAttribute("viewBox", "0 0 24 24");
  icon.classList.add(CLASSES.accordionIcon);

  // Reuse the sprite symbol included globally in base templates.
  const iconUse = document.createElementNS("http://www.w3.org/2000/svg", "use");
  iconUse.setAttribute("href", "#accordion-arrow");
  icon.appendChild(iconUse);

  toggle.appendChild(toggleText);
  toggle.appendChild(icon);

  heading.appendChild(title);
  heading.appendChild(toggle);
  summary.appendChild(heading);

  const panel = document.createElement("div");
  panel.className = CLASSES.accordionContent;
  panel.dataset.panelLetter = letter;

  resetPanelToBrowseFallback(panel, letter, baseUrl);

  details.appendChild(summary);
  details.appendChild(panel);

  return details;
}

export function resetPanelToBrowseFallback(panel, letter, baseUrl) {
  panel.innerHTML = "";

  // Default accordion panel state before records are loaded on demand.
  const fallback = document.createElement("p");
  fallback.className = CLASSES.marginTopXs;
  fallback.append("Select this character to load records, or ");
  fallback.appendChild(
    createLink(
      `${baseUrl}?character=${encodeURIComponent(letter)}`,
      "open the letter page",
    ),
  );
  fallback.append(".");
  panel.appendChild(fallback);
}
