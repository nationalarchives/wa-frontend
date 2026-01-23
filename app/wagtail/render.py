from flask import current_app, render_template
from pydash import objects

from .pages import (
    home_page,
    information_page,
    listing_page,
    section_index_page,
)

page_type_templates = {
    "ukgwa.UKGWAHomePage": home_page.render_home_page,
    "ukgwa.SectionIndexPage": section_index_page.render_section_index_page,
    "ukgwa.InformationPage": information_page.render_information_page,
    "ukgwa.ListingPage": listing_page.render_listing_page,
}


def render_content_page(page_data):
    page_type = objects.get(page_data, "meta.type")
    if page_type:
        if page_type in page_type_templates:
            return page_type_templates[page_type](page_data)
        current_app.logger.error(f"Template for {page_type} not handled")
        return render_template("errors/page_not_found.html"), 404
    current_app.logger.error("Page meta information not included")
    return render_template("errors/api.html"), 502
