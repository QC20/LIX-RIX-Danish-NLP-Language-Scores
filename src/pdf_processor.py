"""
pdf_processor.py
----------------
Backwards-compatible shim.

If you have existing code that imports PDFProcessor, this module keeps it
working.  New code should use BatchProcessor from batch_processor.py instead,
which supports PDF, TXT, and DOCX files and produces richer output.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from batch_processor import BatchProcessor


class PDFProcessor:
    """
    Legacy wrapper around BatchProcessor.

    .. deprecated::
        Use :class:`batch_processor.BatchProcessor` directly.
    """

    def __init__(self, folder_path: str, language: str = "da") -> None:
        warnings.warn(
            "PDFProcessor is deprecated. Use BatchProcessor instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.folder_path = folder_path
        self._processor = BatchProcessor(language=language)

    def process_pdfs_in_folder(self, output_path: str | None = None) -> None:
        """Process PDFs in folder_path and write an Excel report."""
        results = self._processor.process(self.folder_path)

        if not results:
            print("No documents found or processed.")
            return

        out = Path(output_path or self.folder_path) / "readability_report.xlsx"
        self._processor.save_excel(results, out)
        print(f"Report written to {out}")