import unittest

from app.lib.content_parser import (
    add_rel_to_external_links,
    b_to_strong,
    lists_to_tna_lists,
    replace_line_breaks,
    strip_wagtail_attributes,
)


class BToStrongTestCase(unittest.TestCase):
    def test_simple_b_tag_conversion(self):
        html = "<p>This is <b>bold</b> text</p>"
        result = b_to_strong(html)
        self.assertIn("<strong>bold</strong>", result)
        self.assertNotIn("<b>", result)

    def test_b_tag_with_attributes(self):
        html = '<p>This is <b class="highlight">bold</b> text</p>'
        result = b_to_strong(html)
        self.assertIn('<strong class="highlight">bold</strong>', result)
        self.assertNotIn("<b", result)

    def test_multiple_b_tags(self):
        html = "<p><b>First</b> and <b>second</b> bold</p>"
        result = b_to_strong(html)
        self.assertEqual(result.count("<strong>"), 2)
        self.assertEqual(result.count("</strong>"), 2)
        self.assertNotIn("<b>", result)

    def test_nested_b_tags(self):
        html = "<p><b>Outer <b>inner</b> text</b></p>"
        result = b_to_strong(html)
        self.assertIn("<strong>", result)
        self.assertNotIn("<b>", result)

    def test_no_b_tags(self):
        html = "<p>No bold tags here</p>"
        result = b_to_strong(html)
        self.assertIn("<p>No bold tags here</p>", result)


class ListsToTnaListsTestCase(unittest.TestCase):
    def test_simple_ul_gets_class(self):
        html = "<ul><li>Item 1</li></ul>"
        result = lists_to_tna_lists(html)
        self.assertIn('class="tna-ul"', result)

    def test_simple_ol_gets_class(self):
        html = "<ol><li>Item 1</li></ol>"
        result = lists_to_tna_lists(html)
        self.assertIn('class="tna-ol"', result)

    def test_multiple_lists(self):
        html = "<ul><li>A</li></ul><ol><li>B</li></ol>"
        result = lists_to_tna_lists(html)
        self.assertIn("tna-ul", result)
        self.assertIn("tna-ol", result)

    def test_nested_lists(self):
        html = "<ul><li>Item<ul><li>Nested</li></ul></li></ul>"
        result = lists_to_tna_lists(html)
        # Should add class to both outer and inner ul
        self.assertEqual(result.count("tna-ul"), 2)


class StripWagtailAttributesTestCase(unittest.TestCase):
    def test_removes_data_block_key(self):
        html = '<p data-block-key="abc123">Content</p>'
        result = strip_wagtail_attributes(html)
        self.assertNotIn("data-block-key", result)
        self.assertIn("Content", result)

    def test_multiple_data_block_keys(self):
        html = '<div data-block-key="xyz"><p data-block-key="abc">Text</p></div>'
        result = strip_wagtail_attributes(html)
        self.assertNotIn("data-block-key", result)

    def test_preserves_other_attributes(self):
        html = '<p data-block-key="abc" class="text" id="para">Content</p>'
        result = strip_wagtail_attributes(html)
        self.assertNotIn("data-block-key", result)
        self.assertIn('class="text"', result)
        self.assertIn('id="para"', result)

    def test_no_wagtail_attributes(self):
        html = '<p class="normal">Content</p>'
        result = strip_wagtail_attributes(html)
        self.assertIn("Content", result)
        self.assertIn('class="normal"', result)


class ReplaceLineBreaksTestCase(unittest.TestCase):
    def test_windows_line_breaks(self):
        html = "Line 1\r\nLine 2"
        result = replace_line_breaks(html)
        self.assertEqual(result, "Line 1<br>Line 2")

    def test_self_closing_br_tags(self):
        html = "Line 1<br/>Line 2"
        result = replace_line_breaks(html)
        self.assertEqual(result, "Line 1<br>Line 2")

    def test_br_with_space(self):
        html = "Line 1<br />Line 2"
        result = replace_line_breaks(html)
        self.assertEqual(result, "Line 1<br>Line 2")

    def test_mixed_line_breaks(self):
        html = "Line 1\r\nLine 2<br/>Line 3<br />Line 4"
        result = replace_line_breaks(html)
        self.assertEqual(result, "Line 1<br>Line 2<br>Line 3<br>Line 4")

    def test_already_normalized(self):
        html = "Line 1<br>Line 2"
        result = replace_line_breaks(html)
        self.assertEqual(result, "Line 1<br>Line 2")


class AddRelToExternalLinksTestCase(unittest.TestCase):
    def test_external_link_gets_rel(self):
        html = '<a href="https://example.com">External</a>'
        result = add_rel_to_external_links(html)
        self.assertIn('rel="noreferrer nofollow noopener"', result)

    def test_internal_www_link_no_rel(self):
        html = '<a href="https://www.nationalarchives.gov.uk/page">Internal</a>'
        result = add_rel_to_external_links(html)
        self.assertNotIn("rel=", result)

    def test_internal_discovery_link_no_rel(self):
        html = '<a href="https://discovery.nationalarchives.gov.uk/page">Internal</a>'
        result = add_rel_to_external_links(html)
        self.assertNotIn("rel=", result)

    def test_internal_webarchive_link_no_rel(self):
        html = '<a href="https://webarchive.nationalarchives.gov.uk/page">Internal</a>'
        result = add_rel_to_external_links(html)
        self.assertNotIn("rel=", result)

    def test_relative_link_no_rel(self):
        html = '<a href="/about">Relative</a>'
        result = add_rel_to_external_links(html)
        self.assertNotIn("rel=", result)

    def test_anchor_link_no_rel(self):
        html = '<a href="#section">Anchor</a>'
        result = add_rel_to_external_links(html)
        self.assertNotIn("rel=", result)

    def test_multiple_links_mixed(self):
        html = """
        <a href="https://example.com">External</a>
        <a href="https://www.nationalarchives.gov.uk">Internal</a>
        <a href="https://another-site.com">External 2</a>
        """
        result = add_rel_to_external_links(html)
        # Should have exactly 2 rel attributes
        self.assertEqual(result.count('rel="noreferrer nofollow noopener"'), 2)

    def test_preserves_existing_attributes(self):
        html = '<a href="https://example.com" class="link" target="_blank">External</a>'
        result = add_rel_to_external_links(html)
        self.assertIn('rel="noreferrer nofollow noopener"', result)
        self.assertIn('class="link"', result)
        self.assertIn('target="_blank"', result)
