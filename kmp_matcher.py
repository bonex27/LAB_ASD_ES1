from dataclasses import dataclass
from typing import List


@dataclass
class MatchResult:
    matches: List[int]
    comparisons: int
    alignments: int
    preprocessing_cost: int
    prefix_function: List[int]



def compute_prefix_function(pattern: str) -> tuple[List[int], int]:
    """Compute the prefix function used by KMP.

    Returns the prefix array and the number of character comparisons performed
    during preprocessing.
    """
    m = len(pattern)
    if m == 0:
        return [], 0

    pi = [0] * m
    k = 0
    comparisons = 0

    for q in range(1, m):
        while k > 0:
            comparisons += 1
            if pattern[k] == pattern[q]:
                break
            k = pi[k - 1]

        comparisons += 1
        if pattern[k] == pattern[q]:
            k += 1
        pi[q] = k

    return pi, comparisons



def kmp_search(text: str, pattern: str) -> MatchResult:
    """Return all occurrences of pattern in text using KMP.

    Counts comparisons both in preprocessing and searching. The alignments
    metric is included for consistency with the naive algorithm and is reported
    as the number of text positions consumed by the search loop.
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return MatchResult(
            matches=list(range(n + 1)),
            comparisons=0,
            alignments=n + 1,
            preprocessing_cost=0,
            prefix_function=[],
        )
    if m > n:
        pi, prep = compute_prefix_function(pattern)
        return MatchResult(matches=[], comparisons=0, alignments=0, preprocessing_cost=prep, prefix_function=pi)

    pi, preprocessing_cost = compute_prefix_function(pattern)
    matches: List[int] = []
    comparisons = 0
    q = 0

    for i in range(n):
        while q > 0:
            comparisons += 1
            if pattern[q] == text[i]:
                break
            q = pi[q - 1]

        comparisons += 1
        if pattern[q] == text[i]:
            q += 1

        if q == m:
            matches.append(i - m + 1)
            q = pi[q - 1]

    return MatchResult(
        matches=matches,
        comparisons=comparisons,
        alignments=n,
        preprocessing_cost=preprocessing_cost,
        prefix_function=pi,
    )
