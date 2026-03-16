import re
from datetime import datetime

from .content_parser import (
    add_rel_to_external_links,
    b_to_strong,
    lists_to_tna_lists,
    replace_line_breaks,
    strip_wagtail_attributes,
)


def tna_html(s):
    if not s:
        return s
    s = lists_to_tna_lists(s)
    s = b_to_strong(s)
    s = strip_wagtail_attributes(s)
    s = replace_line_breaks(s)
    s = add_rel_to_external_links(s)
    return s


def humanise_date(value: str | datetime) -> str:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if isinstance(value, datetime):
        return value.strftime("%-d %B '%y")
    return ""


def slugify(s):
    if not s:
        return s
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s
