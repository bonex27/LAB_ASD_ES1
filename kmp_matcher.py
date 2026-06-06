"""Algoritmo KMP per lo string matching.
"""

from typing import List

from matcher_types import MatchResult, PrefixResult


def compute_prefix_function(pattern: str) -> PrefixResult:
    """Calcola la funzione prefisso pi del pattern.

    pi[q] e' la lunghezza del piu' lungo prefisso proprio di pattern[0:q+1]
    che e' anche suffisso di pattern[0:q+1].
    """
    m = len(pattern)
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

    return PrefixResult(pi, comparisons)


def kmp_string_match(text: str, pattern: str) -> MatchResult:
    """Restituisce tutte le posizioni in cui pattern compare in text usando KMP."""
    n = len(text)
    m = len(pattern)
    occurrences: List[int] = []

    if m == 0:
        return MatchResult(list(range(n + 1)), 0)

    prefix = compute_prefix_function(pattern)
    pi = prefix.pi
    q = 0
    comparisons = prefix.comparisons

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
            occurrences.append(i - m + 1)
            q = pi[q - 1]

    return MatchResult(occurrences, comparisons)


if __name__ == "__main__":
    print(kmp_string_match("abababa", "aba"))
