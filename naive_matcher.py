from dataclasses import dataclass
from typing import List


@dataclass
class MatchResult:
    matches: List[int]
    comparisons: int
    alignments: int
    preprocessing_cost: int = 0



def naive_search(text: str, pattern: str) -> MatchResult:
    """Return all occurrences of pattern in text using the naive algorithm.

    The function counts character comparisons performed during the search and
    the number of tested alignments.
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return MatchResult(matches=list(range(n + 1)), comparisons=0, alignments=n + 1)
    if m > n:
        return MatchResult(matches=[], comparisons=0, alignments=0)

    matches: List[int] = []
    comparisons = 0
    alignments = 0

    for shift in range(n - m + 1):
        alignments += 1
        matched = True
        for j in range(m):
            comparisons += 1
            if text[shift + j] != pattern[j]:
                matched = False
                break
        if matched:
            matches.append(shift)

    return MatchResult(matches=matches, comparisons=comparisons, alignments=alignments)
