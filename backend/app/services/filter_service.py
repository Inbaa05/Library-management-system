"""Content relevance and appropriateness filter service.

This service uses transparent, configurable rule-based checks.
It does NOT claim to use AI or machine learning — it is a keyword
and rule-based filter that can be extended.

Limitations:
- Keyword blocklists generate false positives (e.g., 'bad' in 'badly needed').
- Context-aware moderation would require NLP models.
- These checks are a first line of defense; human review is still needed.
"""
from typing import List, Tuple

# Library-relevance keywords — at least one must appear in a comment
# for it to be considered relevant. This can be extended via config/database.
LIBRARY_RELEVANCE_KEYWORDS: List[str] = [
    'book', 'library', 'study', 'read', 'reading', 'catalog',
    'shelf', 'shelves', 'journal', 'magazine', 'reference', 'resource',
    'staff', 'librarian', 'loan', 'return', 'checkout', 'borrow',
    'wifi', 'wi-fi', 'internet', 'computer', 'printer', 'digital',
    'seat', 'seating', 'table', 'quiet', 'noise', 'facility',
    'service', 'hour', 'opening', 'closing', 'fine', 'renewal',
    'recommendation', 'suggest', 'review', 'rating', 'author',
    'collection', 'database', 'research', 'academic', 'textbook'
]

# Minimum word count to be considered non-trivial feedback
MIN_WORD_COUNT = 3

# Inappropriate content blocklist — conservative and documented
# These are explicit terms that clearly violate a library content policy.
# The list is intentionally limited to avoid excessive false positives.
INAPPROPRIATE_TERMS: List[str] = [
    'spam', 'advertisement', 'click here', 'buy now', 'free money',
    'casino', 'gambling', 'lottery', 'prize winner',
    # Profanity subset — only strongest terms to reduce false positives
    'fuck', 'shit', 'asshole', 'bitch', 'bastard',
]


def check_relevance(text: str, title: str = '') -> Tuple[bool, str]:
    """Check whether a comment is relevant to library services.

    A comment is considered relevant if:
    - It has at least MIN_WORD_COUNT words, AND
    - It contains at least one library-relevance keyword.

    Returns (is_relevant, reason).
    """
    combined = f"{title} {text}".lower()
    word_count = len(combined.split())

    if word_count < MIN_WORD_COUNT:
        return False, f'Comment is too short ({word_count} words). Minimum is {MIN_WORD_COUNT} words.'

    if not any(kw in combined for kw in LIBRARY_RELEVANCE_KEYWORDS):
        return (
            False,
            'Comment does not appear to be related to library services. '
            'If this is incorrect, a librarian can manually approve it.'
        )

    return True, ''


def check_appropriateness(text: str) -> Tuple[bool, str]:
    """Check whether a comment contains inappropriate content.

    Uses a configurable keyword blocklist. Returns (is_appropriate, reason).
    """
    lower_text = text.lower()
    for term in INAPPROPRIATE_TERMS:
        if term in lower_text:
            return (
                False,
                f'Comment was flagged for inappropriate content. '
                f'Please revise your feedback and resubmit.'
            )
    return True, ''
