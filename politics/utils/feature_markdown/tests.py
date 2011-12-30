#!/usr/bin/env python
# coding=utf-8
from feature_markdown import Markdown
from markdown import Markdown as BaseMarkdown
import unittest


class TestFeatureMarkdown(unittest.TestCase):
    """Unit tests for the feature_markdown module."""

    def test_normal(self):
        """With all features enabled, conversion work normally."""
        markdown = Markdown()

        # Test some basic syntax.
        source = ("This is a *list*:\n\n* Item 1.\n* Item 2.\n\n" +
                  "This is an *image*: ![Alt text](image.png)\n\n" +
                  "This is some *code*:\n\n    Line 1.\n    Line 2.")

        expected = BaseMarkdown(safe="escape").convert(source)
        self.assertEqual(expected, markdown.convert(source))

    def test_disable_images(self):
        """If images are disabled, they should be ignored during conversion."""
        markdown = Markdown(disable=["images"])

        source = "![Image](image.png)"
        expected = "<p>![Image](image.png)</p>"
        self.assertEqual(expected, markdown.convert(source))

        # Check the reference syntax too.
        source = "![Image][reference]\n[reference]: image.png"
        expected = "<p>![Image][reference]</p>"
        self.assertEqual(expected, markdown.convert(source))

    def test_disable_newlines_code(self):
        """Disabling newlines should also disable code blocks."""
        markdown = Markdown(disable=["newlines"])

        source = "This is a code block:\n\n    Line 1.\n    Line 2."
        expected = "<p>This is a code block: Line 1. Line 2.</p>"
        self.assertEqual(expected, markdown.convert(source))

        # Code blocks at the start should be ignored too.
        source = "    Line 1.\n    Line 2."
        expected = "<p>Line 1. Line 2.</p>"
        self.assertEqual(expected, markdown.convert(source))

    def test_disable_newlines_headers(self):
        """Disabling newlines should also disable headers."""
        markdown = Markdown(disable=["newlines"])

        source = "This is a header:\n\n# Header"
        expected = "<p>This is a header: # Header</p>"
        self.assertEqual(expected, markdown.convert(source))

        # Headers at the start should be ignored too.
        source = "# Header"
        expected = "<p># Header</p>"
        self.assertEqual(expected, markdown.convert(source))

    def test_disable_newlines_horizontal_rules(self):
        """Disabling newlines should also disable horizontal rules."""
        markdown = Markdown(disable=["newlines"])

        source = "This is a horizontal rule:\n\n***"
        expected = "<p>This is a horizontal rule: ***</p>"
        self.assertEqual(expected, markdown.convert(source))

        # Horizontal rules at the start should be ignored too.
        source = "***"
        expected = "<p>***</p>"
        self.assertEqual(expected, markdown.convert(source))

    def test_disable_newlines_lists(self):
        """Disabling newlines should also disable lists."""
        markdown = Markdown(disable=["newlines"])

        source = "This is a list:\n\n* Item 1.\n* Item 2."
        expected = "<p>This is a list: * Item 1. * Item 2.</p>"
        self.assertEqual(expected, markdown.convert(source))

        # Lists at the start should be ignored too.
        source = "* Item 1.\n* Item 2."
        expected = "<p>* Item 1. * Item 2.</p>"
        self.assertEqual(expected, markdown.convert(source))

    def test_disable_newlines_quotes(self):
        """Disabling newlines should also disable quotes."""
        markdown = Markdown(disable=["newlines"])

        source = "This is a quote:\n\n> Line 1.\n> Line 2."
        expected = "<p>This is a quote: &gt; Line 1. &gt; Line 2.</p>"
        self.assertEqual(expected, markdown.convert(source))

        # Quotes at the start should be ignored too.
        source = "> Line 1.\n> Line 2."
        expected = "<p>&gt; Line 1. &gt; Line 2.</p>"
        self.assertEqual(expected, markdown.convert(source))

    def test_disable_newlines_setext_header(self):
        """Disabling newlines should also disable setext-style headers."""
        markdown = Markdown(disable=["newlines"])

        source = "This is a header:\n\nHeader\n======"
        expected = "<p>This is a header: Header ======</p>"
        self.assertEqual(expected, markdown.convert(source))

        # Headers at the start should be ignored too.
        source = "Header\n======"
        expected = "<p>Header ======</p>"
        self.assertEqual(expected, markdown.convert(source))


if __name__ == "__main__":
    unittest.main()
