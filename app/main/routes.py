from flask import render_template

from app.lib.cache import cache, cache_key_prefix
from app.main import bp


@bp.route("/")
@cache.cached(key_prefix=cache_key_prefix)
def index():
    # Mock data for homepage until API is connected
    page = {
        "archive_highlights": [
            {
                "title": "Brexit transition period (2016–2020)",
                "listing_title": "Brexit transition period (2016–2020)",
                "url": "#",
                "category": "HISTORICAL MOMENTS",
                "listing_summary": "",
                "introduction": "",
                "source_url": "www.open.gov.uk",
            },
            {
                "title": "Archived tweets from No10 during COVID",
                "listing_title": "Archived tweets from No10 during COVID",
                "url": "#",
                "category": "SURPRISING FINDS",
                "listing_summary": "",
                "introduction": "",
                "source_url": "@10DowningStreet",
            },
            {
                "title": "Historic HMRC Self Assessment Tax Return (SA100) forms",
                "listing_title": "Historic HMRC Self Assessment Tax Return (SA100) forms",
                "url": "#",
                "category": "DOCUMENTS & FORMS",
                "listing_summary": "",
                "introduction": "",
                "source_url": "www.hmrc.gov.uk",
            },
        ],
        "recently_archived": [
            {
                "title": "Department for Children, Schools and Families (DCSF)",
                "listing_title": "Department for Children, Schools and Families (DCSF)",
                "url": "#",
                "category": "",
                "listing_summary": "",
                "introduction": "",
                "source_url": "www.open.gov.uk",
            },
            {
                "title": "Department for Children, Schools and Families (DCSF)",
                "listing_title": "Department for Children, Schools and Families (DCSF)",
                "url": "#",
                "category": "",
                "listing_summary": "",
                "introduction": "",
                "source_url": "www.open.gov.uk",
            },
            {
                "title": "Department for Children, Schools and Families (DCSF)",
                "listing_title": "Department for Children, Schools and Families (DCSF)",
                "url": "#",
                "category": "",
                "listing_summary": "",
                "introduction": "",
                "source_url": "www.open.gov.uk",
            },
        ],
        "recently_archived_intro": "The latest websites and social media channels added to the archive.",
        "call_to_action": {
            "title": "About the UK Government Web Archive",
            "summary": "<p>We capture, preserve and make accessible UK central government information published on the web. The Web Archive includes videos, tweets, images and websites dating from 1996 to the present day.</p>",
            "link_url": "/about/",
            "link_text": "Learn more about the archive",
            "image_url": "",
        },
    }

    return render_template("main/index.html", page=page)


@bp.route("/cookies/")
@cache.cached(key_prefix=cache_key_prefix)
def cookies():
    return render_template("main/cookies.html")


@bp.route("/preview/")
@cache.cached(key_prefix=cache_key_prefix)
def preview():
    return "[Headless preview]"
