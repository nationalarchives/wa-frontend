/**
 * YouTubeConsentManager handles the consent for loading YouTube videos on a webpage.
 * Uses TNA Frontend Cookies library and youtube-nocookie.com for privacy compliance.
 */
class YouTubeConsentManager {
  static selector() {
    return "[data-youtube-embed]";
  }

  /**
   * Create a new YouTubeConsentManager.
   */
  constructor(node) {
    this.youtubeEmbedNode = node;
    this.consentButton = this.youtubeEmbedNode.querySelector("[data-youtube-consent-button]");
    this.dontAskAgainCheckbox = this.youtubeEmbedNode.querySelector("[data-youtube-save-prefs]");
    this.placeholderContainer = this.youtubeEmbedNode.querySelector("[data-youtube-placeholder-container]");
    this.embedContainer = this.youtubeEmbedNode.querySelector("[data-youtube-embed-container]");
    this.videoId = this.embedContainer.getAttribute("data-video-id");
    this.videoTitle = this.embedContainer.getAttribute("data-video-title") || "Video";
    this.cookies = window.TNAFrontendCookies;
    this.bindEvents();
  }

  bindEvents() {
    this.consentButton.addEventListener("click", () => {
      this.handleConsentClick();
    });

    // Check if consent has been given previously
    this.checkConsent();
  }

  loadYouTubeEmbed() {
    // Hide the video placeholder and show the YouTube embed container
    this.placeholderContainer.classList.add("hidden");
    this.embedContainer.classList.remove("hidden");

    // Create YouTube iframe embed using youtube-nocookie.com for privacy
    if (this.videoId && this.embedContainer.children.length === 0) {
      const iframe = document.createElement("iframe");
      iframe.setAttribute("src", `https://www.youtube-nocookie.com/embed/${this.videoId}?rel=0`);
      iframe.setAttribute("frameborder", "0");
      iframe.setAttribute(
        "allow",
        "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture",
      );
      iframe.setAttribute("allowfullscreen", "true");
      iframe.setAttribute("title", this.videoTitle);
      iframe.className = "video-embed__iframe";

      this.embedContainer.appendChild(iframe);
    }
  }

  handleConsentClick() {
    if (this.dontAskAgainCheckbox.checked) {
      this.handleDontAskAgainClick();
    }
    this.loadYouTubeEmbed();

    // Focus on the embed container after accepting
    setTimeout(() => {
      const iframe = this.embedContainer.querySelector("iframe");
      if (iframe) {
        iframe.focus();
      } else {
        this.embedContainer.focus();
      }
    }, 100);
  }

  handleDontAskAgainClick() {
    // Set a cookie to remember the user's choice not to ask again
    // Using TNA Frontend Cookies library
    if (this.cookies) {
      this.cookies.set("youtube_consent", "true", {
        maxAge: 31536000, // 365 days in seconds
        sameSite: "Strict",
      });
    }
  }

  checkConsent() {
    // Check if the user has previously given consent
    // Using TNA Frontend Cookies library
    if (this.cookies) {
      const hasConsent = this.cookies.get("youtube_consent");
      if (hasConsent === "true") {
        this.loadYouTubeEmbed();
      }
    }
  }
}

export default YouTubeConsentManager;
