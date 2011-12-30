#!/usr/bin/env python
# coding=utf-8
from paginator import Paginator
import unittest


class PaginatorTestCase(unittest.TestCase):
    """Unit tests for our custom paginator."""

    def setUp(self):
        self.paginator = Paginator(range(10), 5)

    def test_small_page_number(self):
        """Numbers less than 1 should be rounded up to 1."""
        page = self.paginator.page(-1)
        self.assertEqual(1, page.number)

    def test_large_page_number(self):
        """Numbers greater than the maximum n should be rounded down to n."""
        page = self.paginator.page(3)
        self.assertEqual(2, page.number)

    def test_invalid_page_number(self):
        """Numbers that can't be converted to integers should default to 1."""
        page = self.paginator.page("Hello!")
        self.assertEqual(1, page.number)


if __name__ == "__main__":
    unittest.main()
