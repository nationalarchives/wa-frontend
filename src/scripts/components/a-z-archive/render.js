import { getDisplayLetter } from "./helpers.js";

const CLASSES = {
  marginTopXs: "tna-!--margin-top-xs",
  marginBottomS: "tna-!--margin-bottom-s",
  headingM: "tna-heading-m",
  accordion: "accordion accordion--a-z",
  accordionSummary: "accordion__summary",
  accordionHeader: "accordion__header",
  accordionTitle: "accordion__title heading heading--two",
  accordionToggle: "accordion__toggle",
  accordionToggleText: "accordion__toggle-text",
  accordionIcon: "accordion__icon",
  accordionContent: "accordion__content",
  supporting: "supporting",
  visuallyHidden: "tna-visually-hidden",
  listingItem: "listing-item listing-item--a-z",
  listingItemLink: "listing-item__link",
  listingItemTitle: "listing-item__title heading heading--four",
  listingItemUrl: "listing-item__url supporting",
  listingItemDate: "listing-item__date supporting",
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
  list.className = `accordion__list`.trim();

  records.forEach((record) => {
    const item = document.createElement("li");
    item.className = CLASSES.listingItem;

    const article = document.createElement("article");

    const link = document.createElement("a");
    link.className = CLASSES.listingItemLink;
    link.href = record.archive_link || "#";

    const title = document.createElement("h2");
    title.className = CLASSES.listingItemTitle;
    title.textContent = record.profile_name || "";

    link.appendChild(title);
    article.appendChild(link);

    if (record.record_url) {
      const urlEl = document.createElement("p");
      urlEl.className = CLASSES.listingItemUrl;
      urlEl.textContent = record.record_url;
      article.appendChild(urlEl);
    }

    const capturesText = `Captures from ${record.first_capture_display || ""} to${
      record.ongoing ? " Ongoing" : ` ${record.latest_capture_display || ""}`
    }`;
    const dateEl = document.createElement("p");
    dateEl.className = CLASSES.listingItemDate;
    dateEl.textContent = capturesText;
    article.appendChild(dateEl);

    item.appendChild(article);
    list.appendChild(item);
  });

  panel.appendChild(list);
}

export function renderLoading(panel) {
  panel.innerHTML = "";

  const wrapper = document.createElement("div");
  wrapper.className = "accordion__loading";
  wrapper.setAttribute("aria-hidden", "true");

  const spinner = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  spinner.setAttribute("viewBox", "0 0 24 24");
  spinner.setAttribute("class", "accordion__spinner");
  spinner.setAttribute("aria-hidden", "true");
  const circle = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "circle",
  );
  circle.setAttribute("cx", "12");
  circle.setAttribute("cy", "12");
  circle.setAttribute("r", "10");
  circle.setAttribute("fill", "none");
  circle.setAttribute("stroke", "currentColor");
  circle.setAttribute("stroke-width", "2");
  circle.setAttribute("stroke-dasharray", "30 70");
  circle.setAttribute("stroke-linecap", "round");
  spinner.appendChild(circle);

  wrapper.appendChild(spinner);
  panel.appendChild(wrapper);

  const srText = document.createElement("p");
  srText.className = CLASSES.visuallyHidden;
  srText.textContent = "Loading...";
  panel.appendChild(srText);
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
