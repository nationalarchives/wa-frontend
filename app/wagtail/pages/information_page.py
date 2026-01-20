from flask import render_template


def render_information_page(page_data):
    return render_template(
        "pages/information_page.html",
        page_data=page_data,
    )
