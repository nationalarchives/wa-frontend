from enum import StrEnum


class SearchType(StrEnum):
    KEYWORD = "keyword"
    URL = "url"


class ArchiveType(StrEnum):
    WEB = "web"
    SOCIAL = "social"


# Search base URLs for different search types and archive types
WEB_KEYWORD_SEARCH_BASE = "https://webarchive.nationalarchives.gov.uk/search"
WEB_SITE_SEARCH_BASE = "https://webarchive.nationalarchives.gov.uk/ukgwa/timeline1"
SOCIAL_SEARCH_BASE = "https://webarchive.nationalarchives.gov.uk/social/search"
