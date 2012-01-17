# coding=utf-8
from markdown import Markdown as BaseMarkdown
from markdown.inlinepatterns import Pattern
import re


class Markdown(object):
    """A markdown converter that allows selectively supporting syntax.

    In some circumstances, you may not want to allow certain syntax elements
    (e.g. no images in comments). This class lets you explicitly permit or
    forbid various constructs in markdown. To disable images, for example:

    .. code-block:: python

        >>> markdown = Markdown()
        >>> markdown.convert("![Image](http://www.example.com/image.png)")
        u'<p><img alt="Image" src="http://www.example.com/image.png" /></p>'
        >>> markdown = Markdown(ignore=["images"])
        >>> markdown.convert("![Image](http://www.example.com/image.png)")
        u'![Image](http://www.example.com/image.png)'

    Features that can be controlled: "images", "newlines".

    :param     disable: The features that should be disabled. If given,
                        ``enable`` must be ``None`` (they are incompatible).
    :type      disable: *Iterable* or ``None``
    :param      enable: The features that should be enabled. If given,
                        ``disable`` must be ``None`` (they are incompatible).
    :type       enable: *Iterable* or ``None``
    :raises  TypeError: If either argument is neither a list or ``None``.
    :raises ValueError: If both arguments are not ``None``.
    """

    class DisablePattern(Pattern):
        """A ``markdown`` pattern that simply returns the raw markdown.

        By replacing default patterns with this, we can disable syntax.
        """

        # Pass the markdown back.
        def handleMatch(self, match):
            return match.group()

    def __init__(self, disable=None, enable=None):
        if None not in (disable, enable):
            raise ValueError("Only one argument may be provided.")

        # The features that can be controlled.
        features = set(["images", "newlines"])

        # As we must explicitly disable features, we must calculate, from
        # enable and the set of features, which ones are to be disabled.
        if enable:
            enable = set(enable)
            if not enable <= features:
                raise ValueError("enable contains invalid features.")

            disable = features - enable

        # If disable is None, both arguments were None. Just enable all
        # features as that's expected behaviour.
        if disable is None:
            disable = []

        disable = set(disable)
        if not disable <= features:
            raise ValueError("disable contains invalid features.")

        self._disabled = disable
        self._markdown = BaseMarkdown(safe="escape")

        if "images" in self._disabled:
            self._disable_inline_pattern("image_link")
            self._disable_inline_pattern("image_reference")

        if "newlines" in self._disabled:
            # Disable block-level syntax (e.g. code, lists). As we remove
            # newlines in convert(), these won't match within the block, but
            # they will if they appear at the start; thus we must remove them.
            block_processors = ("code", "hashheader", "hr", "olist",
                                "setextheader", "quote", "ulist")

            for processor in block_processors:
                del self._markdown.parser.blockprocessors[processor]

            # Two spaces at the end of a line results in a line break.
            self._disable_inline_pattern("linebreak")
            self._disable_inline_pattern("linebreak2")

    def _disable_inline_pattern(self, name):
        """Disables the inline pattern described by ``name``."""
        regular_expression = self._markdown.inlinePatterns[name].pattern
        pattern = self.DisablePattern(regular_expression, self._markdown)
        self._markdown.inlinePatterns[name] = pattern

    def convert(self, source):
        # Remove newlines if they're disabled. This may result in excess
        # whitespace (e.g. if there was an indented list), so remove that too.
        # TODO: This collapses whitespace in backticks, which isn't ideal.
        if "newlines" in self._disabled:
            source = re.sub("\s+", " ", source)

        return self._markdown.convert(source)
