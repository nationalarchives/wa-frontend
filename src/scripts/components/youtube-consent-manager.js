import Cookies from 'js-cookie';
import 'lite-youtube-embed/src/lite-yt-embed';

/**
 * YouTubeConsentManager handles the consent for loading YouTube videos on a webpage.
 */
class YouTubeConsentManager {
    static selector() {
        return '[data-youtube-embed]';
    }

    /**
     * Create a new YouTubeConsentManager.
     */
    constructor(node) {
        this.youtubeEmbedNode = node;
        this.consentButton = this.youtubeEmbedNode.querySelector(
            '[data-youtube-consent-button]',
        );
        this.dontAskAgainCheckbox = this.youtubeEmbedNode.querySelector(
            '[data-youtube-save-prefs]',
        );
        this.placeholderContainer = this.youtubeEmbedNode.querySelector(
            '[data-youtube-placeholder-container]',
        );
        this.embedContainer = this.youtubeEmbedNode.querySelector(
            '[data-youtube-embed-container]',
        );
        this.bindEvents();
    }

    bindEvents() {
        this.consentButton.addEventListener('click', () => {
            this.handleconsentClick();
        });

        // Check if consent has been given previously
        this.checkConsent();
    }

    loadYouTubeEmbed() {
        // Hide the video placeholder and show the YouTube embed container
        this.placeholderContainer.classList.add('hidden');
        this.embedContainer.classList.remove('hidden');
    }

    handleconsentClick() {
        if (this.dontAskAgainCheckbox.checked) {
            this.handleDontAskAgainClick();
        }
        this.loadYouTubeEmbed();
        // focus on the youtube play button after accepting the terms and conditions
        const playButton =
            this.youtubeEmbedNode.querySelector('button.lty-playbtn');
        if (playButton) {
            playButton.focus();
        } else {
            // If lite-youtube hasn't rendered yet, focus on the embed container
            this.embedContainer.focus();
        }
    }

    handleDontAskAgainClick() {
        // Set a cookie to remember the user's choice not to ask again
        Cookies.set('youtube_consent', 'true', {
            expires: 365,
            sameSite: 'Strict',
        });

        this.loadYouTubeEmbed();
    }

    checkConsent() {
        // Check if the user has previously given consent
        const hasConsent = Cookies.get('youtube_consent');
        if (hasConsent) {
            this.loadYouTubeEmbed();
        }
    }
}

export default YouTubeConsentManager;
