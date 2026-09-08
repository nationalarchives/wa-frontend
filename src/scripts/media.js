/* eslint-disable */
/**
 * YouTube video.js player init – mostly from ds-frontend media.js.
 * Only inits when TNA usage cookie is accepted (works with tna-cookie-banner).
 */
import { initYoutubeEmbedApi } from "./components/videojs-youtube-modified";
import videojs from "video.js";
import Cookies from "@nationalarchives/cookies";

const videoJsInstances = {};

const cookies = new Cookies();

const getYouTubeVideoLinks = () =>
  document.querySelectorAll("a.etna-video--youtube[id]");

const updateYoutubeVideoMessages = ($youTubeVideoInstances) => {
  $youTubeVideoInstances.forEach(($video) => {
    $video.querySelector(".etna-video__label-cookies-message-js")?.remove();
  });
};

const initYouTubeVideos = ($youTubeVideoInstances) => {
  const links = Array.from($youTubeVideoInstances);
  links.forEach(($video) => {
    try {
      const id = $video.getAttribute("id");
      const href = $video.getAttribute("href");
      if (!href) {
        return;
      }
      const $newVideo = document.createElement("video");
      $newVideo.classList.add("etna-video", "etna-video--youtube", "video-js");
      $newVideo.setAttribute("controls", true);
      $newVideo.setAttribute("id", id);
      const poster =
        $video
          .querySelector("img.etna-video__preview-image[src]")
          ?.getAttribute("src") || null;
      $video.replaceWith($newVideo);
      const player = videojs(
        $newVideo,
        {
          techOrder: ["youtube"],
          sources: [
            {
              type: "video/youtube",
              src: href,
            },
          ],
          experimentalSvgIcons: true,
          disablePictureInPicture: true,
          enableDocumentPictureInPicture: false,
          controlBar: {
            pictureInPictureToggle: false,
            volumePanel: false,
          },
          poster,
          youtube: {
            ytControls: 0,
            color: "white",
            enablePrivacyEnhancedMode: true,
            iv_load_policy: 3,
            rel: 0,
          },
        },
        function onReady() {
          this.el().querySelector("iframe")?.setAttribute("tabindex", "-1");
          this.el().removeAttribute("tabindex");
        },
      );
      player.one("play", (e) => {
        e.target.querySelector("iframe")?.removeAttribute("tabindex");
      });
      videoJsInstances[id] = player;
    } catch (err) {
      console.error("[media.js] YouTube init error:", err);
    }
  });

  // Pause other players when one plays
  Object.entries(videoJsInstances).forEach(([key, instance]) => {
    instance.on("play", () => {
      Object.entries(videoJsInstances).forEach(([key2, instance2]) => {
        if (key2 !== key) {
          instance2.pause();
        }
      });
    });
  });
};

/**
 * Media component: inits YouTube video.js players for a.etna-video--youtube links
 * only when usage cookies are accepted. Listens for cookie acceptance to init without reload.
 */
class Media {
  static selector() {
    return "body";
  }

  constructor() {
    const $links = getYouTubeVideoLinks();
    if (!$links.length) {
      return;
    }

    const tryInit = () => {
      // Leave links pointing to YouTube and remove the JS-only copy from the fallback message.
      updateYoutubeVideoMessages($links);
      return;
      initYoutubeEmbedApi(() => initYouTubeVideos($links));
    };

    if (!cookies.preference("marketing")) {
      tryInit();
    }

    cookies.once("changePreference", (data) => {
      if (
        Object.prototype.hasOwnProperty.call(data, "marketing") &&
        data.marketing !== true
      ) {
        const $linksNow = getYouTubeVideoLinks();
        if ($linksNow.length) {
          initYoutubeEmbedApi(() => initYouTubeVideos($linksNow));
        }
      }
    });
  }
}

export default Media;
