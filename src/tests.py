"""Test minimi di correttezza per gli algoritmi implementati."""

from naive_matcher import naive_string_match
from kmp_matcher import compute_prefix_function, kmp_string_match


def assert_same(text: str, pattern: str) -> None:
    naive = naive_string_match(text, pattern).occurrences
    kmp = kmp_string_match(text, pattern).occurrences
    assert naive == kmp, (text, pattern, naive, kmp)


def run_tests() -> None:
    cases = [
        ("", ""),
        ("abc", ""),
        ("", "a"),
        ("abc", "d"),
        ("abc", "abc"),
        ("abababa", "aba"),
        ("aaaaa", "aa"),
        ("abcxabcdabxabcdabcdabcy", "abcdabcy"),
    ]
    for text, pattern in cases:
        assert_same(text, pattern)

    assert compute_prefix_function("ababaca").pi == [0, 0, 1, 2, 3, 0, 1]
    print("Tutti i test sono stati superati.")


if __name__ == "__main__":
    run_tests()
