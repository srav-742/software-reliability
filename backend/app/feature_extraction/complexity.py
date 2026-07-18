import os
from typing import List
from difflib import SequenceMatcher


def calculate_duplicate_code_score(file_contents: List[str]) -> float:
    """
    Computes a duplication similarity score (0.0 to 1.0) across a collection of source code files.
    """
    if len(file_contents) < 2:
        return 0.0

    total_comparisons = 0
    total_similarity = 0.0

    # Clean and normalize lines
    cleaned_contents = []
    for content in file_contents[:20]:  # Limit comparison to top 20 files for performance
        lines = [l.strip() for l in content.splitlines() if len(l.strip()) > 5]
        if lines:
            cleaned_contents.append("\n".join(lines))

    n = len(cleaned_contents)
    for i in range(n):
        for j in range(i + 1, n):
            matcher = SequenceMatcher(None, cleaned_contents[i], cleaned_contents[j])
            ratio = matcher.quick_ratio()
            if ratio > 0.3:  # Only account for significant overlap
                total_similarity += ratio
            total_comparisons += 1

    if total_comparisons == 0:
        return 0.0

    score = total_similarity / total_comparisons
    return round(float(score), 4)
