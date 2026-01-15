import { initAll, Cookies } from "@nationalarchives/frontend/nationalarchives/all.mjs";

import Header from "./components/header.js";
import SkipLink from "./components/skip-link.js";
import YouTubeConsentManager from "./components/youtube-consent-manager.js";
import TableHint from "./components/table-hint.js";

function initComponent(ComponentClass) {
  const items = document.querySelectorAll(ComponentClass.selector());
  items.forEach((item) => new ComponentClass(item));
}

document.addEventListener("DOMContentLoaded", () => {
  // Cookie domain setup
  const cookiesDomain = document.documentElement.getAttribute("data-cookiesdomain");
  if (cookiesDomain) {
    new Cookies({ domain: cookiesDomain });
  }

  // Init custom components
  initComponent(SkipLink);
  initComponent(YouTubeConsentManager);
  initComponent(TableHint);

  // Initialise custom header with extended mobile breakpoint
  // Must be initialised before initAll() to prevent TNA's default header from taking over
  initComponent(Header);

  // Initialise TNA Frontend components
  initAll();
});
