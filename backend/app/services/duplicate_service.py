"""Duplicate detection service.

Provides two levels of duplicate detection:
1. Exact duplicate: SHA-256 hash comparison (O(1) lookup via DB index).
2. Near-duplicate: Jaccard similarity on word token sets.

Jaccard similarity is chosen because it is:
- Lightweight (no ML model or external library required)
- Deterministic and easy to explain
- Adequate for short library feedback comments

Limitation: Jaccard similarity is sensitive to vocabulary but not to
synonyms. A more sophisticated approach (e.g., TF-IDF cosine similarity
or embedding similarity) would improve recall but adds dependencies.
"""
from typing import Optional, Tuple
from ..extensions import db
from ..models.comment import Comment


def check_exact_duplicate(
    content_hash: str,
    exclude_id: Optional[int] = None
) -> Optional[Comment]:
    """Check if a comment with the same normalized content hash already exists.

    Returns the first existing comment with that hash, or None.
    """
    query = Comment.query.filter(
        Comment.content_hash == content_hash,
        Comment.status != 'archived'
    )
    if exclude_id:
        query = query.filter(Comment.id != exclude_id)
    return query.first()


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """Compute Jaccard similarity between the word token sets of two texts.

    jaccard(A, B) = |A ∩ B| / |A ∪ B|
    Range: 0.0 (completely different) to 1.0 (identical tokens).
    """
    tokens_a = set(text_a.split())
    tokens_b = set(text_b.split())
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def check_near_duplicate(
    normalized_text: str,
    exclude_id: Optional[int] = None,
    threshold: float = 0.75
) -> Tuple[Optional[Comment], float]:
    """Find the most similar approved or pending comment above the threshold.

    Scans approved and pending_review comments (not duplicates, archived, etc.)
    and returns (most_similar_comment, similarity_score) or (None, 0.0).

    Note: This is a linear scan and should be replaced with an approximate
    nearest-neighbor index (e.g., faiss, annoy) for databases with >10,000
    comments.
    """
    candidates = Comment.query.filter(
        Comment.status.in_(['approved', 'pending_review']),
        Comment.content_hash.isnot(None)
    )
    if exclude_id:
        candidates = candidates.filter(Comment.id != exclude_id)

    best_match: Optional[Comment] = None
    best_score: float = 0.0

    for candidate in candidates:
        candidate_normalized = candidate.comment_text.lower()
        score = jaccard_similarity(normalized_text, candidate_normalized)
        if score >= threshold and score > best_score:
            best_score = score
            best_match = candidate

    return best_match, best_score
