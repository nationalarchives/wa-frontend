def build_navigation_items(nav_data):
    """
    Build navigation items list from Wagtail API response data.

    Transforms API link structure into TNA Design System format.

    Input format (wrapped in type/value):
    [{'type': 'link', 'value': {'text': '...', 'url': '...', 'is_page': bool}}]

    Output format:
    [
        {'text': 'Link Title', 'href': '/url/'},
        {'text': 'External Link', 'href': 'https://...', 'external': True}
    ]

    Note: External links (is_page=False) include 'external': True flag, which triggers
    rel="noreferrer nofollow noopener" in templates.

    Some components don't support this attribute.

    Args:
        nav_data (list): List of navigation items from Wagtail API

    Returns:
        list: List of navigation items in TNA format, or empty list if invalid
    """
    if not nav_data:
        return []

    items = []
    for nav_item in nav_data:
        if nav_item.get("type") == "link" and nav_item.get("value"):
            link_value = nav_item["value"]
            link_dict = {
                "text": link_value.get("text", ""),
                "href": link_value.get("url", "#"),
            }
            # Add external flag for external links (TNA macro renders rel attribute)
            if not link_value.get("is_page"):
                link_dict["external"] = True
            items.append(link_dict)

    return items


def build_footer_columns(footer_nav_data):
    """
    Build footer navigation columns from Wagtail API response data.

    Transforms API column structure into TNA Design System format.

    Input format (columns wrapped in type/value, links are flat objects):
    [{'type': 'column', 'value': {'heading': '...', 'links': [{'url': '...', 'text': '...', 'is_page': bool}]}}]

    Output format:
    [
        {
            'title': 'Column Title',
            'items': [
                {'text': 'Link', 'href': '/url/'},
                {'text': 'External', 'href': 'https://...', 'external': True}
            ]
        }
    ]

    Note: External links (is_page=False) include 'external': True flag,
    which triggers rel="noreferrer nofollow noopener" in TNA footer template.

    Args:
        footer_nav_data (list): List of footer navigation columns from Wagtail API

    Returns:
        list: List of footer columns in TNA format, or empty list if invalid
    """
    if not footer_nav_data:
        return []

    columns = []
    for column in footer_nav_data:
        if column.get("type") == "column" and column.get("value"):
            column_value = column["value"]
            column_items = []
            # Build items for this column
            for link in column_value.get("links", []):
                link_dict = {
                    "text": link.get("text", ""),
                    "href": link.get("url", "#"),
                }
                # Add external flag for external links (TNA macro renders rel attribute)
                if not link.get("is_page"):
                    link_dict["external"] = True
                column_items.append(link_dict)

            columns.append(
                {"title": column_value.get("heading", ""), "items": column_items}
            )
    return columns


def build_header_navigation(navigation_settings):
    """
    Build complete header navigation structure from navigation settings.

    Args:
        navigation_settings (dict): Navigation settings from API

    Returns:
        dict: Header navigation with 'primary' and 'secondary' keys
    """
    return {
        "primary": build_navigation_items(
            navigation_settings.get("primary_navigation", [])
        ),
        "secondary": build_navigation_items(
            navigation_settings.get("secondary_navigation", [])
        ),
    }


def build_footer_navigation(navigation_settings):
    """
    Build complete footer navigation structure from navigation settings.

    Args:
        navigation_settings (dict): Navigation settings from API

    Returns:
        dict: Footer navigation with 'columns' and 'legal' keys
    """
    return {
        "columns": build_footer_columns(
            navigation_settings.get("footer_navigation", [])
        ),
        "legal": build_navigation_items(navigation_settings.get("footer_links", [])),
    }
