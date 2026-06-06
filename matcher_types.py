"""Tipi di ritorno condivisi dagli algoritmi di string matching."""

from dataclasses import dataclass
from typing import List


@dataclass
class MatchResult:
    """Risultato di una ricerca di pattern nel testo.

    Attributes:
        occurrences: posizioni iniziali delle occorrenze trovate.
        comparisons: numero di confronti espliciti tra caratteri.
    """

    occurrences: List[int]
    comparisons: int


@dataclass
class PrefixResult:
    """Risultato del preprocessing usato da KMP."""

    pi: List[int]
    comparisons: int
