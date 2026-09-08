// Must be set before video.js / YouTube tech load (ds-frontend media logic)
window.VIDEOJS_NO_AUTOMATIC_YOUTUBE_INIT = true;
window.VIDEOJS_NO_DYNAMIC_STYLE = true;

import { initAll } from "@nationalarchives/frontend/nationalarchives/all.mjs";
import { GA4 } from "@nationalarchives/frontend/nationalarchives/analytics.mjs";

const ga4Id = document.documentElement.getAttribute("data-ga4id");
if (ga4Id) {
  new GA4({ id: ga4Id });
}

import AtoZArchive from "./components/a-z-archive.js";
import FeaturedSearchKeywordToggle from "./components/featured-search-keyword-toggle.js";
import Header from "./components/header.js";
import KeywordDetector from "./components/keyword-detector.js";
import SkipLink from "./components/skip-link.js";
import Media from "./media.js";

const initComponent = (ComponentClass) => {
  const items = document.querySelectorAll(ComponentClass.selector());
  items.forEach((item) => new ComponentClass(item));
};

document.addEventListener("DOMContentLoaded", () => {
  // Init custom components
  initComponent(SkipLink);
  initComponent(Header);
  initComponent(AtoZArchive);
  initComponent(KeywordDetector);
  initComponent(FeaturedSearchKeywordToggle);
  initComponent(Media);

  // Initialise TNA Frontend components (includes tna-cookie-banner)
  initAll();
});
