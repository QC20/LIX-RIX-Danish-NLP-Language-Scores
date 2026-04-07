# Lix and Rix Readability Calculator

A Python tool for analysing the readability of texts in **Danish, Swedish, Norwegian (Bokmål), and Dutch**. It computes LIX and RIX scores, maps them to human-readable difficulty bands and school grade levels, and produces colour-coded Excel workbooks and self-contained HTML reports.

## Table of Contents

- [What are LIX and RIX?](#what-are-lix-and-rix)
- [Score Interpretation](#score-interpretation)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-line interface](#command-line-interface)
  - [Python API](#python-api)
- [Output Files](#output-files)
- [Project Structure](#project-structure)
- [Changelog (v2)](#changelog-v2)
- [Contributing](#contributing)
- [License](#license)

---

## What are LIX and RIX?

Both formulas measure text difficulty using **character counting** rather than syllable counting, making them well-suited to non-English languages.

### LIX (Björnsson, 1968)

Developed in Sweden, LIX is defined as:

```
LIX = (words / sentences) + (long_words × 100 / words)
```

where *long words* are words with **more than 6 characters** (for Scandinavian languages and Dutch).

### RIX (Anderson, 1983)

A simplification of LIX that maps directly to school grade levels:

```
RIX = long_words / sentences
```

where *long words* are words with **more than 7 characters**.

> **Note:** The original version of this project used the LIX formula for both scores. This has been corrected.

---

## Score Interpretation

### LIX bands

| LIX score | Difficulty label   | Typical text type                           |
|-----------|--------------------|---------------------------------------------|
| < 20      | Very easy          | Children's books, simple instructions       |
| 20-30     | Easy               | Fiction, popular non-fiction                |
| 30-40     | Moderate           | Newspapers, general magazines               |
| 40-50     | Difficult          | Academic papers, technical reports          |
| 50-60     | Very difficult     | Scientific literature, legal texts          |
| > 60      | Extremely difficult| Specialist research, regulatory documents   |

**Recommendation for public-facing writing:** aim for LIX 40 or below.

### RIX grade levels (Anderson, 1983)

| RIX score | Estimated grade |
|-----------|-----------------|
| 0.0-0.2   | Grade 1         |
| 0.2-0.5   | Grade 2         |
| ...       | ...             |
| 6.2-7.2   | Grade 12        |
| > 7.2     | College+        |

The full mapping is defined in `src/language_config.py`.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/readability-calc.git
cd readability-calc
```

### 2. Install Python dependencies

Python 3.9 or later is required.

```bash
pip install -r requirements.txt
```

### 3. Download the spaCy language model

Download at least one model for the language you will analyse:

```bash
# Danish (default)
python -m spacy download da_core_news_sm

# Swedish
python -m spacy download sv_core_news_sm

# Norwegian Bokmål
python -m spacy download nb_core_news_sm

# Dutch
python -m spacy download nl_core_news_sm
```

---

## Usage

### Command-line interface

All analysis is done through `src/main.py`. Run `python src/main.py --help` for the full option reference.

#### Analyse a folder of documents (Danish, default)

```bash
python src/main.py --input ./my_reports
```

#### Analyse a single file

```bash
python src/main.py --input report.pdf
```

#### Choose a language

```bash
python src/main.py --input ./docs --language sv        # Swedish
python src/main.py --input ./docs --language norwegian # full name also works
```

#### Output format

```bash
python src/main.py --input ./docs --format excel   # Excel only
python src/main.py --input ./docs --format html    # HTML only
python src/main.py --input ./docs --format both    # both (default)
```

#### Save reports to a specific location

```bash
python src/main.py --input ./docs --output ./results/my_report
# Writes:  ./results/my_report.xlsx
#          ./results/my_report.html
```

#### Search sub-directories and surface more context

```bash
python src/main.py --input ./archive --recursive --top-sentences 10 --top-words 30
```

#### Full option reference

```
--input,  -i  PATH   File or folder to analyse (required)
--output, -o  PATH   Output path stem or directory
--language,-l LANG   da | sv | nb | nl (or full name). Default: da
--format, -f         excel | html | both. Default: both
--recursive,-r       Descend into sub-folders
--top-sentences N    Hardest sentences per document (default 5)
--top-words N        Most frequent long words per document (default 20)
--quiet,  -q         Suppress progress output
```

### Python API

You can use the processor directly in your own scripts:

```python
from src.batch_processor import BatchProcessor

processor = BatchProcessor(language="da")

# Analyse a folder or a single file
results = processor.process("./my_documents")

for r in results:
    print(f"{r.file_name}: LIX={r.lix} ({r.lix_label}), RIX grade {r.rix_grade}")

# Save reports
processor.save_excel(results, "report.xlsx")
processor.save_html(results, "report.html")
```

---

## Output Files

### Excel workbook (`report.xlsx`)

| Sheet             | Contents                                                          |
|-------------------|-------------------------------------------------------------------|
| **Summary**       | One row per document. Colour-coded by LIX band. All metrics.     |
| **LIX Chart**     | Bar chart of LIX scores across all documents.                     |
| **Hard Sentences**| Top N hardest sentences per document with per-sentence statistics.|
| **Top Long Words**| Most frequent long words per document.                            |
| **Legend**        | Formula definitions, column descriptions, and recommendations.    |

### HTML report (`report.html`)

A self-contained page (no internet connection required) with:

- Colour-coded summary table.
- Interactive bar chart of LIX scores.
- Hardest sentences and most frequent long words.
- Score band reference cards.

---

## Project Structure

```
readability-calc/
├── src/
│   ├── main.py              CLI entry point
│   ├── batch_processor.py   Orchestration: file discovery, analysis, reporting
│   ├── text_analyzer.py     Core LIX/RIX calculations and sentence-level analysis
│   ├── file_reader.py       Unified reader for PDF, TXT, and DOCX files
│   ├── report_generator.py  Excel and HTML output
│   ├── language_config.py   Per-language stop words, spaCy models, score bands
│   └── pdf_processor.py     Legacy shim (backwards-compatible with v1)
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Changelog (v2)

### Corrections

- **RIX formula fixed.** The original code used the LIX formula for both scores. RIX is now correctly calculated as `long_words / sentences`, which produces a value that maps to grade levels.
- **Sentence segmentation.** Terminal punctuation counting (`.!?`) is replaced by spaCy's sentence segmenter, which handles abbreviations, decimal numbers, and bullet-point lists correctly.

### New features

- **Multi-format input.** In addition to PDF, the tool now reads `.txt` and `.docx` files.
- **Multi-language support.** The language model is configured per run via `--language`. Stop-word sets and spaCy model names for all four languages are defined in `language_config.py`.
- **Sentence-level diagnostics.** The hardest sentences in each document are identified and included in both output formats so you know exactly which passages to revise.
- **Difficult word extraction.** The most frequent long words per document are surfaced.
- **Lexical diversity (TTR).** Type-token ratio is calculated over content words (after stop-word removal).
- **Formatted Excel output.** The workbook is colour-coded by LIX band, has auto-sized columns, and includes a bar chart sheet and a legend sheet.
- **HTML report.** A self-contained, browser-ready report with an interactive chart.
- **CLI with full help text.** `python src/main.py --help` documents every option.
- **Model loading efficiency.** The spaCy model is loaded once and shared across all documents in a batch.
- **Backwards compatibility.** The original `PDFProcessor` class still works; it now emits a deprecation warning and delegates to `BatchProcessor`.

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss significant changes.

---

## License

MIT. See [LICENSE](LICENSE) for details.