"""Generatori dei dati di test per gli esperimenti di string matching."""

import random
import string
from typing import Tuple


def random_case(n: int, m: int, alphabet_size: int, seed: int) -> Tuple[str, str]:
    """Genera testo e pattern casuali sullo stesso alfabeto."""
    rng = random.Random(seed)
    alphabet = string.ascii_lowercase[:alphabet_size]
    text = "".join(rng.choice(alphabet) for _ in range(n))
    pattern = "".join(rng.choice(alphabet) for _ in range(m))
    return text, pattern


def naive_worst_case(n: int, m: int) -> Tuple[str, str]:
    """Caso sfavorevole per l'algoritmo ingenuo.

    Il pattern condivide molti caratteri iniziali con ogni finestra del testo,
    ma fallisce sull'ultimo confronto.
    """
    if m < 2:
        raise ValueError("m deve essere almeno 2")
    return "a" * n, "a" * (m - 1) + "b"


def many_matches_case(n: int, m: int) -> Tuple[str, str]:
    """Caso con molte occorrenze sovrapposte."""
    return "a" * n, "a" * m


def periodic_case(n: int, m: int) -> Tuple[str, str]:
    """Caso periodico, utile per osservare il riuso dell'informazione in KMP."""
    base = "ababababac"
    text = (base * ((n // len(base)) + 1))[:n]
    pattern = ("abababac" * ((m // 8) + 1))[:m]
    return text, pattern
