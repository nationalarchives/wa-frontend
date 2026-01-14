from bs4 import BeautifulSoup


def b_to_strong(html):
    """Convert all <b> tags to <strong> tags."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("b"):
        tag.name = "strong"
    return str(soup)


def lists_to_tna_lists(html):
    """Add TNA CSS classes to <ul> and <ol> tags."""
    soup = BeautifulSoup(html, "html.parser")

    for ul in soup.find_all("ul"):
        if "class" in ul.attrs:
            ul["class"].append("tna-ul")
        else:
            ul["class"] = ["tna-ul"]

    for ol in soup.find_all("ol"):
        if "class" in ol.attrs:
            ol["class"].append("tna-ol")
        else:
            ol["class"] = ["tna-ol"]

    return str(soup)


def strip_wagtail_attributes(html):
    """Remove Wagtail-specific data attributes."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove data-block-key attribute from all tags
    for tag in soup.find_all(attrs={"data-block-key": True}):
        del tag["data-block-key"]

    return str(soup)


def replace_line_breaks(html):
    html = html.replace("\r\n", "<br>")
    html = html.replace("<br/>", "<br>")
    html = html.replace("<br />", "<br>")
    return html


def add_rel_to_external_links(html):
    """Add rel attributes to external links (not nationalarchives.gov.uk domains)."""
    soup = BeautifulSoup(html, "html.parser")

    internal_domains = [
        "www.nationalarchives.gov.uk",
        "discovery.nationalarchives.gov.uk",
        "webarchive.nationalarchives.gov.uk",
    ]

    for link in soup.find_all("a", href=True):
        href = link["href"]

        # Check if it's an external link
        is_external = href.startswith("http") and not any(
            domain in href for domain in internal_domains
        )

        if is_external:
            link["rel"] = "noreferrer nofollow noopener"

    return str(soup)
