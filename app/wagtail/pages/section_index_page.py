from flask import render_template


def render_section_index_page(page_data):
    return render_template(
        "pages/section_index_page.html",
        page_data=page_data,
    )
