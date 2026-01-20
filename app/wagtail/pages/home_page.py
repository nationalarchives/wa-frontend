from flask import render_template


def render_home_page(page_data):
    return render_template(
        "main/home_page.html",
        page_data=page_data,
    )
