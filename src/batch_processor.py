"""
batch_processor.py
------------------
Orchestrates document discovery, text extraction, analysis, and reporting.

This replaces the original PDFProcessor class with a more general-purpose
pipeline that:

* Accepts a single file or an entire folder.
* Supports PDF, TXT, and DOCX input.
* Loads the spaCy model once per language and reuses it across all documents.
* Produces colour-coded Excel and/or HTML output.
* Provides a progress bar and per-document status messages.
"""

from __future__ import annotations

import sys
from pathlib import Path

from file_reader import discover_documents, read_file
from language_config import LANGUAGE_CONFIGS, resolve_language
from text_analyzer import DocumentResult, TextAnalyzer


class BatchProcessor:
    """
    Analyse one or more documents and produce readability reports.

    Parameters
    ----------
    language : str
        Language code or alias (e.g. 'da', 'danish', 'sv', 'swedish').
    top_sentences : int
        Number of hardest sentences to surface per document.
    top_words : int
        Number of most-frequent long words to surface per document.
    recursive : bool
        When processing a folder, descend into sub-directories.
    verbose : bool
        Print per-document status to stdout.
    """

    def __init__(
        self,
        language: str = "da",
        top_sentences: int = 5,
        top_words: int = 20,
        recursive: bool = False,
        verbose: bool = True,
    ) -> None:
        self.lang_key = resolve_language(language)
        self.lang_cfg = LANGUAGE_CONFIGS[self.lang_key]
        self.top_sentences = top_sentences
        self.top_words = top_words
        self.recursive = recursive
        self.verbose = verbose

        self._nlp = None  # loaded lazily

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, input_path: str | Path) -> list[DocumentResult]:
        """
        Analyse *input_path* (file or folder) and return results.

        Parameters
        ----------
        input_path : str or Path
            A single file or a directory of documents.

        Returns
        -------
        list[DocumentResult]
            One result per successfully processed document.
        """
        input_path = Path(input_path)

        if input_path.is_file():
            paths = [input_path]
        elif input_path.is_dir():
            paths = discover_documents(input_path, recursive=self.recursive)
        else:
            raise FileNotFoundError(f"Not found: {input_path}")

        if not paths:
            self._log("No supported documents found.")
            return []

        self._log(f"Found {len(paths)} document(s). Language: {self.lang_cfg['name']}.")
        self._ensure_model()

        results: list[DocumentResult] = []

        for i, path in enumerate(paths, start=1):
            self._log(f"  [{i}/{len(paths)}] {path.name} ...", end=" ")
            try:
                text = read_file(path)
                analyzer = TextAnalyzer(
                    text=text,
                    nlp=self._nlp,
                    stop_words=self.lang_cfg["stop_words"],
                    file_name=path.stem,
                    language=self.lang_key,
                )
                result = analyzer.analyse(
                    top_sentences=self.top_sentences,
                    top_words=self.top_words,
                )
                results.append(result)
                self._log(f"LIX {result.lix:.1f} ({result.lix_label})")
            except Exception as exc:  # noqa: BLE001
                self._log(f"FAILED: {exc}")

        return results

    def save_excel(
        self,
        results: list[DocumentResult],
        output_path: str | Path,
    ) -> Path:
        """Write Excel report and return the path."""
        from report_generator import generate_excel  # noqa: PLC0415
        out = generate_excel(results, output_path)
        self._log(f"Excel report saved: {out}")
        return out

    def save_html(
        self,
        results: list[DocumentResult],
        output_path: str | Path,
    ) -> Path:
        """Write HTML report and return the path."""
        from report_generator import generate_html  # noqa: PLC0415
        out = generate_html(results, output_path)
        self._log(f"HTML report saved:  {out}")
        return out

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_model(self) -> None:
        """Load the spaCy model the first time it is needed."""
        if self._nlp is not None:
            return

        model_name = self.lang_cfg["spacy_model"]
        try:
            import spacy  # noqa: PLC0415
            self._nlp = spacy.load(model_name)
        except OSError:
            self._log(
                f"\nspaCy model '{model_name}' is not installed. "
                "Run the following command and try again:\n"
                f"    python -m spacy download {model_name}\n"
            )
            sys.exit(1)
        except ImportError:
            self._log(
                "\nspaCy is not installed. "
                "Install it with:  pip install spacy"
            )
            sys.exit(1)

    def _log(self, message: str, end: str = "\n") -> None:
        if self.verbose:
            print(message, end=end, flush=True)