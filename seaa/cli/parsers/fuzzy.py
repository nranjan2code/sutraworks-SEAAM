"""
SEAA CLI Fuzzy Matching

Typo-tolerant command matching using Levenshtein distance.
"""

from typing import List, Optional, Tuple


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.

    This is the minimum number of single-character edits
    (insertions, deletions, substitutions) required to
    change one string into the other.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Edit distance (0 = identical)
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row = [i + 1]

        for j, c2 in enumerate(s2):
            # Cost is 0 if characters match, 1 otherwise
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)

            current_row.append(min(insertions, deletions, substitutions))

        previous_row = current_row

    return previous_row[-1]


def normalized_distance(s1: str, s2: str) -> float:
    """
    Calculate normalized Levenshtein distance.

    Normalized to [0, 1] where 0 = identical, 1 = completely different.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Normalized distance (0.0 to 1.0)
    """
    if not s1 and not s2:
        return 0.0

    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 0.0

    return levenshtein_distance(s1, s2) / max_len


def similarity(s1: str, s2: str) -> float:
    """
    Calculate similarity between two strings.

    Returns value in [0, 1] where 1 = identical.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Similarity score (0.0 to 1.0)
    """
    return 1.0 - normalized_distance(s1, s2)


def fuzzy_match(
    input_text: str,
    candidates: List[str],
    threshold: float = 0.6,
) -> List[Tuple[str, float]]:
    """
    Find candidates that fuzzy-match the input.

    Args:
        input_text: User input to match
        candidates: List of valid candidates
        threshold: Minimum similarity score (0.0 to 1.0)

    Returns:
        List of (candidate, score) tuples, sorted by score descending
    """
    input_lower = input_text.lower().strip()

    matches = []
    for candidate in candidates:
        candidate_lower = candidate.lower()
        score = similarity(input_lower, candidate_lower)

        if score >= threshold:
            matches.append((candidate, score))

    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def get_best_match(
    input_text: str,
    candidates: List[str],
    threshold: float = 0.6,
    require_prefix: bool = False,
) -> Optional[Tuple[str, float]]:
    """
    Get the best fuzzy match for input.

    Args:
        input_text: User input to match
        candidates: List of valid candidates
        threshold: Minimum similarity score
        require_prefix: If True, also check prefix matching

    Returns:
        (best_match, score) or None if no match above threshold
    """
    input_lower = input_text.lower().strip()

    # First check exact match
    for candidate in candidates:
        if candidate.lower() == input_lower:
            return (candidate, 1.0)

    # Check prefix match if required
    if require_prefix:
        prefix_matches = [c for c in candidates if c.lower().startswith(input_lower)]
        if len(prefix_matches) == 1:
            return (prefix_matches[0], 0.95)  # High score for unique prefix

    # Fall back to fuzzy match
    matches = fuzzy_match(input_text, candidates, threshold)
    return matches[0] if matches else None


def suggest_correction(
    input_text: str,
    candidates: List[str],
    threshold: float = 0.5,
) -> Optional[str]:
    """
    Suggest a correction for a typo.

    Returns None if no good suggestion found.

    Args:
        input_text: Potentially misspelled input
        candidates: Valid options
        threshold: Minimum similarity for suggestion

    Returns:
        Suggested correction or None
    """
    result = get_best_match(input_text, candidates, threshold)
    if result and result[1] < 1.0:  # Don't suggest if already exact
        return result[0]
    return None


def is_likely_typo(
    input_text: str,
    expected: str,
    max_distance: int = 2,
) -> bool:
    """
    Check if input is likely a typo of expected text.

    Args:
        input_text: User input
        expected: Expected correct text
        max_distance: Maximum edit distance to consider a typo

    Returns:
        True if likely a typo
    """
    distance = levenshtein_distance(input_text.lower(), expected.lower())
    return 0 < distance <= max_distance
