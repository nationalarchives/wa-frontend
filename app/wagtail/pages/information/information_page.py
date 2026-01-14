from flask import render_template


def information_page(page_data):
    return render_template(
        "information/information_page.html",
        page_data=page_data,
    )
