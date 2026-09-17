"""Validate quoted source anchors without accepting invented wording."""
import re

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _words(value):
    return [match.group(0).casefold() for match in _WORD_RE.finditer(value or '')]


def matches(body, quote):
    """Accept formatting-only differences when the same 5-20 word sequence exists in source text."""
    if not isinstance(body, str) or not isinstance(quote, str):
        return False
    quote_words = _words(quote)
    if not 5 <= len(quote_words) <= 20:
        return False
    if quote in body:
        return True
    body_words = _words(body)
    size = len(quote_words)
    return any(body_words[index:index + size] == quote_words for index in range(len(body_words) - size + 1))
