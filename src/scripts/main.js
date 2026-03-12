// Must be set before video.js / YouTube tech load (ds-frontend media logic)
window.VIDEOJS_NO_AUTOMATIC_YOUTUBE_INIT = true;
window.VIDEOJS_NO_DYNAMIC_STYLE = true;

import {
  initAll,
  Cookies,
} from "@nationalarchives/frontend/nationalarchives/all.mjs";

import "../styles/main.scss";

import Header from "./components/header.js";
import Media from "./media.js";
import SkipLink from "./components/skip-link.js";

function initComponent(ComponentClass) {
  const items = document.querySelectorAll(ComponentClass.selector());
  items.forEach((item) => new ComponentClass(item));
}

document.addEventListener("DOMContentLoaded", () => {
  // Cookie domain setup (required for tna-cookie-banner and YouTube usage gating)
  const cookiesDomain = document.documentElement.getAttribute(
    "data-tna-cookies-domain",
  );
  new Cookies({ defaultDomain: cookiesDomain || undefined });

  // Init custom components
  initComponent(SkipLink);
  initComponent(Header);
  initComponent(Media);

  // Initialise TNA Frontend components (includes tna-cookie-banner)
  initAll();
});
