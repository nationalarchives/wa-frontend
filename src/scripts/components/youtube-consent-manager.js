import videojs from "video.js";
import "video.js/dist/video-js.css";

/**
 * YouTubeConsentManager handles the consent for loading YouTube videos on a webpage.
 * Uses TNA Frontend Cookies library and video.js player.
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
    this.videoElement = this.embedContainer.querySelector("video");
    this.player = null;
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

    // Initialize video.js player if not already initialized
    if (!this.player && this.videoElement) {
      const videoId = this.videoElement.getAttribute("data-video-id");
      
      this.player = videojs(this.videoElement, {
        controls: true,
        preload: "metadata",
        fluid: true,
        responsive: true,
        techOrder: ["html5"],
        html5: {
          vhs: {
            overrideNative: true
          }
        }
      });

      // For YouTube videos, use iframe embed with youtube-nocookie.com
      if (videoId) {
        const iframe = document.createElement("iframe");
        iframe.setAttribute("src", `https://www.youtube-nocookie.com/embed/${videoId}?rel=0`);
        iframe.setAttribute("frameborder", "0");
        iframe.setAttribute("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture");
        iframe.setAttribute("allowfullscreen", "true");
        iframe.setAttribute("title", this.videoElement.getAttribute("data-video-title") || "Video");
        iframe.style.width = "100%";
        iframe.style.height = "100%";
        iframe.style.position = "absolute";
        iframe.style.top = "0";
        iframe.style.left = "0";
        
        // Replace video element with iframe
        this.embedContainer.style.position = "relative";
        this.embedContainer.style.paddingBottom = "56.25%"; // 16:9 aspect ratio
        this.embedContainer.style.height = "0";
        this.embedContainer.innerHTML = "";
        this.embedContainer.appendChild(iframe);
      }
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
