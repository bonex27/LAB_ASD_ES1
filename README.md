# Esercizio 1 - String matching

Confronto tra algoritmo ingenuo e algoritmo KMP per il problema dello string matching.

## Struttura

```text
src/
  matcher_types.py      tipi di ritorno condivisi
  naive_matcher.py      algoritmo ingenuo
  kmp_matcher.py        funzione prefisso e algoritmo KMP
  generators.py         generatori dei casi sperimentali
  tests.py              test di correttezza
  experiments.py        esecuzione esperimenti, CSV, tabelle e grafici
report/
  relazione.tex         relazione LaTeX completa
  relazione.pdf         PDF compilato della relazione
  tables/               tabella LaTeX generata dagli esperimenti
results/
  string_matching_results.csv  tabella completa dei risultati
  summary_n16000_m32.csv       sintesi usata nella relazione
  platform_info.txt            piattaforma di esecuzione
  figures/                     grafici generati
```

## Esecuzione

Dalla cartella principale del progetto:

```bash
cd src
python tests.py
python experiments.py
```

Gli algoritmi non usano `str.find`, `str.index`, espressioni regolari o librerie esterne per cercare il pattern nel testo.

`matplotlib` è usato solo per generare i grafici. Se non è installato, gli esperimenti producono comunque i CSV.

## Compilazione relazione

```bash
cd report
pdflatex relazione.tex
pdflatex relazione.tex
```

