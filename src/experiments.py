"""Esecuzione esperimenti per confrontare algoritmo ingenuo e KMP.

Output principali:
- report/resources/data/string_matching_results.csv: tabella completa dei risultati.
- report/resources/data/summary_n16000_m32.csv: sintesi leggibile per il caso n=16000, m=32.
- report/resources/data/platform_info.txt: informazioni sulla piattaforma di esecuzione.
- report/resources/figures/*.png: grafici usati nella relazione.

Per comodità viene mantenuta anche una copia degli stessi risultati nella
cartella results/. La relazione LaTeX usa però solo path relativi a report/.
"""

import csv
import os
import platform
import shutil
import statistics
import time
import argparse
from typing import Callable, Dict, Iterable, List, Tuple

from generators import many_matches_case, naive_worst_case, periodic_case, random_case
from kmp_matcher import kmp_string_match
from naive_matcher import naive_string_match

Matcher = Callable[[str, str], object]



def run_correctness_checks() -> None:
    """Esegue controlli di correttezza prima degli esperimenti.

    I controlli sono tenuti nello stesso file degli esperimenti per evitare
    un modulo separato di test nella consegna. Ogni caso confronta il risultato
    dell'algoritmo ingenuo con quello di KMP e verifica anche un esempio noto
    della funzione prefisso.
    """
    from kmp_matcher import compute_prefix_function

    cases = [
        ("", "", [0]),
        ("abc", "", [0, 1, 2, 3]),
        ("abc", "d", []),
        ("abc", "abc", [0]),
        ("abcabc", "abc", [0, 3]),
        ("aaaaa", "aa", [0, 1, 2, 3]),
        ("abc", "abcd", []),
    ]

    for text, pattern, expected in cases:
        naive_result = naive_string_match(text, pattern).occurrences
        kmp_result = kmp_string_match(text, pattern).occurrences
        if naive_result != expected:
            raise AssertionError(f"Algoritmo ingenuo non corretto per text={text!r}, pattern={pattern!r}")
        if kmp_result != expected:
            raise AssertionError(f"KMP non corretto per text={text!r}, pattern={pattern!r}")

    prefix = compute_prefix_function("ABABACA")
    if prefix.pi != [0, 0, 1, 2, 3, 0, 1]:
        raise AssertionError("Funzione prefisso KMP non corretta per il pattern ABABACA")


def measure(func: Matcher, text: str, pattern: str, repeats: int) -> Tuple[float, float, int, int]:
    """Misura tempo medio, deviazione standard, confronti e occorrenze.

    I confronti e il numero di occorrenze sono deterministici per gli stessi
    dati in input; per questo vengono letti dall'ultima esecuzione.
    """
    times: List[float] = []
    last_result = None
    for _ in range(repeats):
        start = time.perf_counter()
        last_result = func(text, pattern)
        end = time.perf_counter()
        times.append(end - start)

    assert last_result is not None
    std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
    return (
        statistics.mean(times),
        std_dev,
        getattr(last_result, "comparisons"),
        len(getattr(last_result, "occurrences")),
    )


def generate_rows(sizes: Iterable[int], pattern_lengths: Iterable[int], repeats: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    algorithms: List[Tuple[str, Matcher]] = [
        ("ingenuo", naive_string_match),
        ("kmp", kmp_string_match),
    ]

    for n in sizes:
        for m in pattern_lengths:
            if m > n:
                continue

            cases = {
                "casuale_alfabeto_4": random_case(n, m, 4, seed=n * 1000 + m),
                "casuale_alfabeto_26": random_case(n, m, 26, seed=n * 2000 + m),
                "sfavorevole_ingenuo": naive_worst_case(n, m),
                "molte_occorrenze": many_matches_case(n, m),
                "periodico": periodic_case(n, m),
            }

            for case_name, (text, pattern) in cases.items():
                expected = naive_string_match(text, pattern).occurrences
                for algorithm_name, algorithm in algorithms:
                    mean_time, std_time, comparisons, occurrences_count = measure(algorithm, text, pattern, repeats)
                    actual = algorithm(text, pattern).occurrences
                    if actual != expected:
                        raise AssertionError(f"Risultati diversi: {case_name}, {algorithm_name}")

                    rows.append({
                        "caso": case_name,
                        "n": n,
                        "m": m,
                        "algoritmo": algorithm_name,
                        "tempo_medio_s": mean_time,
                        "deviazione_standard_s": std_time,
                        "confronti": comparisons,
                        "occorrenze": occurrences_count,
                        "ripetizioni": repeats,
                    })
    return rows


def write_csv(rows: List[Dict[str, object]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_platform_info(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Python: {platform.python_version()}\n")
        f.write(f"Sistema: {platform.system()} {platform.release()}\n")
        f.write(f"Macchina: {platform.machine()}\n")
        f.write(f"Processore: {platform.processor() or 'non disponibile'}\n")


def make_summary(rows: List[Dict[str, object]], n: int, m: int) -> List[Dict[str, object]]:
    summary: List[Dict[str, object]] = []
    cases = sorted({str(r["caso"]) for r in rows})
    for case in cases:
        data = [r for r in rows if r["caso"] == case and r["n"] == n and r["m"] == m]
        by_alg = {str(r["algoritmo"]): r for r in data}
        if "ingenuo" not in by_alg or "kmp" not in by_alg:
            continue
        naive = by_alg["ingenuo"]
        kmp = by_alg["kmp"]
        summary.append({
            "caso": case,
            "tempo_ingenuo_ms": float(naive["tempo_medio_s"]) * 1000,
            "tempo_kmp_ms": float(kmp["tempo_medio_s"]) * 1000,
            "rapporto_tempi": float(naive["tempo_medio_s"]) / float(kmp["tempo_medio_s"]),
            "confronti_ingenuo": int(naive["confronti"]),
            "confronti_kmp": int(kmp["confronti"]),
            "rapporto_confronti": int(naive["confronti"]) / int(kmp["confronti"]),
            "occorrenze": int(naive["occorrenze"]),
        })
    return summary


def write_latex_summary_table(summary: List[Dict[str, object]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\\begin{table}[H]\n")
        f.write("\\centering\n")
        f.write("\\small\n")
        f.write("\\begin{tabular}{lrrrrrr}\n")
        f.write("\\toprule\n")
        f.write("Caso & Ing. ms & KMP ms & Rap. t. & Conf. ing. & Conf. KMP & Rap. c.\\\\\n")
        f.write("\\midrule\n")
        for r in summary:
            case = str(r["caso"]).replace("_", "\\_")
            f.write(
                f"{case} & {r['tempo_ingenuo_ms']:.2f} & {r['tempo_kmp_ms']:.2f} & "
                f"{r['rapporto_tempi']:.2f} & {r['confronti_ingenuo']} & {r['confronti_kmp']} & "
                f"{r['rapporto_confronti']:.2f}\\\\\n"
            )
        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
        f.write("\\caption{Sintesi dei risultati per $n=16000$ e $m=32$. Il rapporto indica quante volte il valore dell'algoritmo ingenuo e' maggiore del valore di KMP.}\n")
        f.write("\\label{tab:sintesi-16000-32}\n")
        f.write("\\end{table}\n")


def try_make_plots(rows: List[Dict[str, object]], out_dir: str) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib non installato: salto la generazione dei grafici.")
        return

    os.makedirs(out_dir, exist_ok=True)
    selected_cases = [
        "casuale_alfabeto_26",
        "sfavorevole_ingenuo",
        "molte_occorrenze",
        "periodico",
    ]
    m = 32
    for case_name in selected_cases:
        for metric, ylabel, filename_prefix in [
            ("tempo_medio_s", "tempo medio (s)", "tempi"),
            ("confronti", "numero di confronti", "confronti"),
        ]:
            plt.figure()
            for algorithm in ["ingenuo", "kmp"]:
                data = [
                    r for r in rows
                    if r["caso"] == case_name and r["m"] == m and r["algoritmo"] == algorithm
                ]
                data.sort(key=lambda r: int(r["n"]))
                plt.plot([r["n"] for r in data], [r[metric] for r in data], marker="o", label=algorithm)
            plt.xlabel("lunghezza del testo n")
            plt.ylabel(ylabel)
            plt.title(f"{filename_prefix.capitalize()} - {case_name.replace('_', ' ')} - m={m}")
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(out_dir, f"{filename_prefix}_{case_name}.png"), dpi=160)
            plt.close()



def sync_report_resources(base_dir: str, results_dir: str) -> None:
    """Copia i risultati nella cartella report/resources usata dalla relazione."""
    report_resources = os.path.join(base_dir, "report", "resources")
    data_dir = os.path.join(report_resources, "data")
    figures_dir = os.path.join(report_resources, "figures")
    tables_dir = os.path.join(report_resources, "tables")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    for filename in ["string_matching_results.csv", "summary_n16000_m32.csv", "platform_info.txt"]:
        src = os.path.join(results_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(data_dir, filename))

    results_figures = os.path.join(results_dir, "figures")
    if os.path.isdir(results_figures):
        for filename in os.listdir(results_figures):
            if filename.endswith(".png"):
                shutil.copy2(os.path.join(results_figures, filename), os.path.join(figures_dir, filename))


def main() -> None:
    parser = argparse.ArgumentParser(description="Confronto tra algoritmo ingenuo e KMP per string matching.")
    parser.add_argument("--quick", action="store_true", help="esegue una versione ridotta degli esperimenti, utile su PythonAnywhere free")
    args = parser.parse_args()

    run_correctness_checks()
    if args.quick:
        sizes = [500, 1000, 2000, 4000]
        pattern_lengths = [4, 8, 16, 32]
        repeats = 3
    else:
        sizes = [500, 1000, 2000, 4000, 8000, 16000]
        pattern_lengths = [4, 8, 16, 32]
        repeats = 7
    rows = generate_rows(sizes, pattern_lengths, repeats)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    results_dir = os.path.join(base_dir, "results")
    write_csv(rows, os.path.join(results_dir, "string_matching_results.csv"))
    summary_n = 4000 if args.quick else 16000
    summary = make_summary(rows, n=summary_n, m=32)
    write_csv(summary, os.path.join(results_dir, "summary_n16000_m32.csv"))
    write_latex_summary_table(summary, os.path.join(base_dir, "report", "resources", "tables", "summary_n16000_m32.tex"))
    write_platform_info(os.path.join(results_dir, "platform_info.txt"))
    try_make_plots(rows, os.path.join(results_dir, "figures"))
    sync_report_resources(base_dir, results_dir)
    print(f"Esperimenti completati: {len(rows)} righe generate.")
    print(f"Risultati salvati in: {results_dir}")
    print("Grafici salvati in: results/figures e report/resources/figures")


if __name__ == "__main__":
    main()
