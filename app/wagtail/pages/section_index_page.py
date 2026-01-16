from flask import render_template


def section_index_page(page_data):
    return render_template(
        "main/section_index_page.html",
        page_data=page_data,
    )
