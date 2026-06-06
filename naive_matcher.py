"""Algoritmo ingenuo per lo string matching.

"""

from typing import List

from matcher_types import MatchResult


def naive_string_match(text: str, pattern: str) -> MatchResult:
    """
    Args:
        text: stringa in cui cercare.
        pattern: stringa da cercare.

    Returns:
        MatchResult con occorrenze e numero di confronti tra caratteri.
    """
    n = len(text)
    m = len(pattern)
    occurrences: List[int] = []
    comparisons = 0

    if m == 0:
        # Scelta esplicita: il pattern vuoto occorre in ogni posizione, inclusa n.
        return MatchResult(list(range(n + 1)), comparisons)

    if m > n:
        return MatchResult([], comparisons)

    for shift in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[shift + j] != pattern[j]:
                break
            j += 1
        if j == m:
            occurrences.append(shift)

    return MatchResult(occurrences, comparisons)


if __name__ == "__main__":
    print(naive_string_match("abababa", "aba"))
