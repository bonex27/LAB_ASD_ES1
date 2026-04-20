from __future__ import annotations

import csv
import random
import statistics
import time
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict, List

from naive_matcher import naive_search
from kmp_matcher import kmp_search


RANDOM_SEED = 42
OUTPUT_DIR = Path(__file__).resolve().parent / "results"


Case = Dict[str, str]



def build_cases() -> List[Case]:
    rnd = random.Random(RANDOM_SEED)

    text_random = "".join(rnd.choice("abcd") for _ in range(20000))
    pattern_random = "abcdabc"

    text_worst = "a" * 20000
    pattern_worst = "a" * 99 + "b"

    text_periodic = "ababababab" * 2000
    pattern_periodic = "abababac"

    text_with_many_matches = "abc" * 7000
    pattern_many_matches = "abcabc"

    text_single_match = "x" * 15000 + "needle" + "x" * 4999
    pattern_single_match = "needle"

    return [
        {
            "name": "random_text",
            "text": text_random,
            "pattern": pattern_random,
            "description": "testo casuale su alfabeto piccolo; pattern presente sporadicamente",
        },
        {
            "name": "worst_case_naive",
            "text": text_worst,
            "pattern": pattern_worst,
            "description": "caso pessimo per ingenuo: molti prefissi uguali e mismatch finale",
        },
        {
            "name": "periodic_text",
            "text": text_periodic,
            "pattern": pattern_periodic,
            "description": "testo periodico che forza molti fallback sul prefisso",
        },
        {
            "name": "many_matches",
            "text": text_with_many_matches,
            "pattern": pattern_many_matches,
            "description": "molte occorrenze sovrapposte/non lontane",
        },
        {
            "name": "single_match_late",
            "text": text_single_match,
            "pattern": pattern_single_match,
            "description": "una sola occorrenza tardiva nel testo",
        },
    ]



def benchmark(function: Callable[[str, str], object], text: str, pattern: str, repeats: int = 7) -> float:
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        function(text, pattern)
        end = time.perf_counter()
        times.append(end - start)
    return statistics.mean(times)



def run_correctness_tests() -> List[dict]:
    tests = [
        ("abracadabra", "abra", [0, 7]),
        ("aaaaa", "aa", [0, 1, 2, 3]),
        ("abcdef", "gh", []),
        ("abc", "", [0, 1, 2, 3]),
        ("short", "longpattern", []),
        ("ababababaca", "ababaca", [4]),
    ]

    rows = []
    for text, pattern, expected in tests:
        naive = naive_search(text, pattern)
        kmp = kmp_search(text, pattern)
        rows.append(
            {
                "text": text,
                "pattern": pattern,
                "expected": str(expected),
                "naive_matches": str(naive.matches),
                "kmp_matches": str(kmp.matches),
                "ok": naive.matches == expected and kmp.matches == expected,
            }
        )
    return rows



def run_experiments() -> List[dict]:
    rows = []
    for case in build_cases():
        text = case["text"]
        pattern = case["pattern"]

        naive = naive_search(text, pattern)
        kmp = kmp_search(text, pattern)

        if naive.matches != kmp.matches:
            raise AssertionError(f"Mismatch tra algoritmi nel caso {case['name']}")

        naive_time = benchmark(naive_search, text, pattern)
        kmp_time = benchmark(kmp_search, text, pattern)

        rows.append(
            {
                "case": case["name"],
                "description": case["description"],
                "text_length": len(text),
                "pattern_length": len(pattern),
                "matches": len(naive.matches),
                "naive_comparisons": naive.comparisons,
                "naive_alignments": naive.alignments,
                "naive_time_ms": round(naive_time * 1000, 3),
                "kmp_preprocessing": kmp.preprocessing_cost,
                "kmp_comparisons": kmp.comparisons,
                "kmp_total_comparisons": kmp.preprocessing_cost + kmp.comparisons,
                "kmp_time_ms": round(kmp_time * 1000, 3),
            }
        )
    return rows



def save_csv(path: Path, rows: List[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)



def print_table(rows: List[dict], title: str) -> None:
    print(f"\n{title}")
    print("=" * len(title))
    if not rows:
        print("Nessun dato")
        return

    headers = list(rows[0].keys())
    widths = {h: len(h) for h in headers}
    for row in rows:
        for h in headers:
            widths[h] = max(widths[h], len(str(row[h])))

    def format_row(row: dict) -> str:
        return " | ".join(str(row[h]).ljust(widths[h]) for h in headers)

    print(format_row({h: h for h in headers}))
    print("-+-".join("-" * widths[h] for h in headers))
    for row in rows:
        print(format_row(row))



def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    correctness_rows = run_correctness_tests()
    experiment_rows = run_experiments()

    save_csv(OUTPUT_DIR / "correctness_tests.csv", correctness_rows)
    save_csv(OUTPUT_DIR / "experiment_results.csv", experiment_rows)

    print_table(correctness_rows, "Test di correttezza")
    print_table(experiment_rows, "Risultati sperimentali")


if __name__ == "__main__":
    main()
