"""
file_reader.py
--------------
Unified document reader.

Supported formats
    .pdf   via PyPDF2
    .txt   plain UTF-8 text
    .docx  via python-docx

All readers return a plain Python string with excess whitespace normalised.
"""

from __future__ import annotations

import re
from pathlib import Path


def read_file(path: str | Path) -> str:
    """
    Read a document and return its text content.

    Parameters
    ----------
    path : str or Path
        Path to the file. Extension determines the reader used.

    Returns
    -------
    str
        Extracted text, with redundant whitespace collapsed.

    Raises
    ------
    ValueError
        If the file extension is not supported.
    FileNotFoundError
        If the file does not exist.
    RuntimeError
        If extraction fails (e.g. encrypted PDF).
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _read_pdf(path)
    elif suffix == ".txt":
        return _read_txt(path)
    elif suffix == ".docx":
        return _read_docx(path)
    else:
        raise ValueError(
            f"Unsupported file format '{suffix}'. "
            "Accepted formats: .pdf, .txt, .docx"
        )


def _read_pdf(path: Path) -> str:
    try:
        import PyPDF2  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "PyPDF2 is required to read PDF files. "
            "Install it with: pip install PyPDF2"
        ) from exc

    text_parts: list[str] = []

    with path.open("rb") as fh:
        reader = PyPDF2.PdfReader(fh)

        if reader.is_encrypted:
            raise RuntimeError(
                f"'{path.name}' is encrypted and cannot be read. "
                "Decrypt the PDF first."
            )

        for page in reader.pages:
            raw = page.extract_text()
            if raw:
                text_parts.append(raw)

    if not text_parts:
        raise RuntimeError(
            f"No text could be extracted from '{path.name}'. "
            "The PDF may contain only scanned images."
        )

    return _normalise(" ".join(text_parts))


def _read_txt(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    return _normalise(text)


def _read_docx(path: Path) -> str:
    try:
        import docx  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "python-docx is required to read .docx files. "
            "Install it with: pip install python-docx"
        ) from exc

    doc = docx.Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return _normalise("\n".join(paragraphs))


def _normalise(text: str) -> str:
    """Collapse runs of whitespace while preserving sentence boundaries."""
    # Replace common ligatures
    text = text.replace("\ufb01", "fi").replace("\ufb02", "fl")
    # Collapse multiple spaces (but not newlines, which mark paragraph breaks)
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def discover_documents(folder: str | Path, recursive: bool = False) -> list[Path]:
    """
    Return all supported documents in *folder*.

    Parameters
    ----------
    folder : str or Path
    recursive : bool
        If True, search sub-directories as well.

    Returns
    -------
    list[Path]
        Sorted list of matching file paths.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder}")

    suffixes = {".pdf", ".txt", ".docx"}
    glob = "**/*" if recursive else "*"

    found = [p for p in folder.glob(glob) if p.suffix.lower() in suffixes]
    return sorted(found)