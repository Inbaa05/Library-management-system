"""Keyword-based category assignment service.

This service assigns a category to a comment based on keywords found in
the title and body. The keyword lists are intentionally transparent so
they can be extended without modifying core logic.

Limitations:
- This is a simple keyword-matching approach. It does not use ML.
- Ambiguous comments may be assigned the first matching category.
- For production, this can be replaced with a scikit-learn classifier.
"""
from typing import Dict, List, Tuple

# Ordered list of (category, keywords) — first match wins
CATEGORY_KEYWORDS: List[Tuple[str, List[str]]] = [
    ('book_suggestion', [
        'suggest', 'suggestion', 'recommend buying', 'purchase', 'acquire',
        'add book', 'new book', 'order book', 'buy book', 'request book',
        'need book', 'want book', 'book request', 'title request'
    ]),
    ('book_review', [
        'review', 'rating', 'stars', 'read', 'reading', 'enjoyed',
        'great book', 'loved the', 'excellent book', 'poor book',
        'disappointing', 'recommend', 'must read'
    ]),
    ('library_facility', [
        'facility', 'seat', 'seating', 'chair', 'table', 'room', 'space',
        'study room', 'noise', 'quiet', 'temperature', 'air conditioning',
        'lighting', 'restroom', 'bathroom', 'parking', 'building'
    ]),
    ('library_service', [
        'service', 'staff', 'librarian', 'help', 'assistance', 'opening hour',
        'closing hour', 'timing', 'hours', 'late return', 'fine', 'renewal',
        'loan', 'checkout', 'return', 'reservation', 'hold'
    ]),
    ('wifi_digital', [
        'wifi', 'wi-fi', 'internet', 'wireless', 'network', 'slow connection',
        'computer', 'printer', 'scanner', 'digital', 'online', 'device',
        'charger', 'power outlet', 'socket'
    ]),
    ('reading_recommendation', [
        'recommend reading', 'should read', 'good for', 'perfect for',
        'ideal for', 'beginner', 'advanced reader', 'reading list',
        'book club', 'classic', 'must-read'
    ]),
]


def assign_category(title: str, text: str) -> str:
    """Assign a category to a comment by matching keywords in title + text.

    Falls back to 'general_feedback' if no keywords match.
    """
    combined = f"{title} {text}".lower()

    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw in combined for kw in keywords):
            return category

    return 'general_feedback'
