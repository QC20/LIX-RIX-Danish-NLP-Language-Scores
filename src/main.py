"""
main.py
-------
Command-line interface for the Lix and Rix readability calculator.

Quick start
~~~~~~~~~~~
    # Analyse all documents in a folder (Danish, default)
    python main.py --input ./my_reports

    # Analyse a single PDF in Swedish, output Excel only
    python main.py --input report.pdf --language sv --format excel

    # Analyse a folder of Norwegian texts and get both outputs
    python main.py --input ./docs --language nb --format both

    # Recurse into sub-folders, show the 10 hardest sentences per doc
    python main.py --input ./archive --recursive --top-sentences 10

Run ``python main.py --help`` for the full option reference.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="readability",
        description=(
            "Calculate LIX and RIX readability scores for PDF, TXT, and DOCX files.\n\n"
            "Supported languages: da (Danish), sv (Swedish), nb (Norwegian Bokmål), nl (Dutch).\n\n"
            "LIX interpretation:\n"
            "  <20  Very easy   (children's books)\n"
            "  <30  Easy        (popular fiction)\n"
            "  <40  Moderate    (newspapers)\n"
            "  <50  Difficult   (academic texts)\n"
            "  <60  Very hard   (scientific literature)\n"
            "  60+  Extreme     (specialist research)\n\n"
            "RIX maps to school grade levels (1-12, College+).\n"
            "Target for public-facing writing: LIX <= 40, RIX grade <= 8."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        metavar="PATH",
        help=(
            "Path to a single file (.pdf, .txt, .docx) or a folder "
            "containing such files."
        ),
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        metavar="PATH",
        help=(
            "Output directory or base file name for the reports. "
            "Defaults to the same directory as --input. "
            "Extensions (.xlsx / .html) are added automatically."
        ),
    )
    parser.add_argument(
        "--language", "-l",
        default="da",
        metavar="LANG",
        help=(
            "Language of the input documents. Accepted values: "
            "da (Danish, default), sv (Swedish), nb (Norwegian Bokmål), nl (Dutch). "
            "Full names are also accepted (e.g. 'danish')."
        ),
    )
    parser.add_argument(
        "--format", "-f",
        default="both",
        choices=["excel", "html", "both"],
        help="Output format. 'both' produces Excel and HTML. (default: both)",
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="When --input is a folder, also search sub-directories.",
    )
    parser.add_argument(
        "--top-sentences",
        type=int,
        default=5,
        metavar="N",
        help=(
            "Number of hardest sentences to surface per document. "
            "(default: 5)"
        ),
    )
    parser.add_argument(
        "--top-words",
        type=int,
        default=20,
        metavar="N",
        help=(
            "Number of most frequent long words to surface per document. "
            "(default: 20)"
        ),
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress messages.",
    )

    return parser


def resolve_output_stem(input_path: Path, output_arg: str | None) -> Path:
    """Return a base path (without extension) for report files."""
    if output_arg is not None:
        out = Path(output_arg)
        # If the user passed a directory, write into it
        if out.is_dir() or not out.suffix:
            out.mkdir(parents=True, exist_ok=True)
            return out / "readability_report"
        # Strip any extension they may have added
        return out.with_suffix("")

    # Default: same directory as input
    if input_path.is_file():
        return input_path.parent / f"{input_path.stem}_readability"
    else:
        return input_path / "readability_report"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Lazy import so --help is always fast
    from batch_processor import BatchProcessor  # noqa: PLC0415

    input_path = Path(args.input)
    output_stem = resolve_output_stem(input_path, args.output)

    processor = BatchProcessor(
        language=args.language,
        top_sentences=args.top_sentences,
        top_words=args.top_words,
        recursive=args.recursive,
        verbose=not args.quiet,
    )

    results = processor.process(input_path)

    if not results:
        print("No documents were successfully analysed. Exiting.")
        return 1

    if not args.quiet:
        print(f"\nProcessed {len(results)} document(s).")

    if args.format in ("excel", "both"):
        processor.save_excel(results, output_stem.with_suffix(".xlsx"))

    if args.format in ("html", "both"):
        processor.save_html(results, output_stem.with_suffix(".html"))

    return 0


if __name__ == "__main__":
    sys.exit(main())