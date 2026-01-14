import re

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


def slugify(s):
    if not s:
        return s
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s
