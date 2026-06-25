// Must be set before video.js / YouTube tech load (ds-frontend media logic)
window.VIDEOJS_NO_AUTOMATIC_YOUTUBE_INIT = true;
window.VIDEOJS_NO_DYNAMIC_STYLE = true;

import {
  Cookies,
  initAll,
} from "@nationalarchives/frontend/nationalarchives/all.mjs";

import "../styles/main.scss";

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
  // Cookie domain setup (required for tna-cookie-banner and YouTube usage gating)
  const cookiesDomain = document.documentElement.getAttribute(
    "data-tna-cookies-domain",
  );
  new Cookies({ defaultDomain: cookiesDomain });

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
