"""
text_analyzer.py
----------------
Core readability analysis engine.

Key fixes and improvements over the original version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* RIX formula corrected to ``long_words / sentences`` (Anderson, 1983).
  The original code used the LIX formula for both scores.
* Sentence segmentation is performed by spaCy rather than counting
  terminal punctuation marks, which greatly improves accuracy for
  texts that contain abbreviations, decimal numbers, bullet lists, etc.
* The spaCy model is accepted as a parameter so it can be shared across
  documents instead of being reloaded for every file.
* Sentence-level diagnostics identify the hardest sentences.
* Lexical diversity (type-token ratio) is reported.
* The most frequent long/difficult words are surfaced for each document.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from language_config import (
    LIX_LONG_WORD_THRESHOLD,
    RIX_LONG_WORD_THRESHOLD,
    interpret_lix,
    interpret_rix,
)

if TYPE_CHECKING:
    import spacy


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SentenceResult:
    """Readability metrics for a single sentence."""
    text: str
    word_count: int
    long_word_count: int           # words > LIX threshold
    long_word_ratio: float         # long_word_count / word_count
    lix_contribution: float        # long_word_ratio * 100


@dataclass
class DocumentResult:
    """Full readability analysis for one document."""
    # Identification
    file_name: str
    language: str

    # Core scores
    lix: float
    rix: float

    # Human-readable interpretations
    lix_label: str
    lix_description: str
    lix_hex: str                   # colour code for the band
    rix_grade: str

    # Document-level statistics
    word_count: int
    sentence_count: int
    avg_words_per_sentence: float
    avg_word_length: float
    long_word_count: int           # words > LIX threshold
    long_word_ratio: float         # as a percentage

    # Lexical diversity
    unique_word_count: int         # after stop-word removal
    type_token_ratio: float        # unique / total content words

    # POS distribution
    noun_count: int
    verb_count: int
    adjective_count: int

    # Difficult sentences (highest LIX contribution)
    hardest_sentences: list[SentenceResult] = field(default_factory=list)

    # Most frequent long words
    top_long_words: list[tuple[str, int]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Analyser
# ---------------------------------------------------------------------------

class TextAnalyzer:
    """
    Analyse a single text document.

    Parameters
    ----------
    text : str
        The document text.
    nlp : spacy.Language
        A loaded spaCy model.  Pass this in from outside so it is shared
        across multiple documents in a batch.
    stop_words : set[str]
        Language-specific stop words used to compute lexical diversity.
    file_name : str
        Display name used in the result (typically the file stem).
    language : str
        Two-letter language code (e.g. 'da').
    """

    def __init__(
        self,
        text: str,
        nlp,
        stop_words: set[str],
        file_name: str = "",
        language: str = "da",
    ) -> None:
        self.text = text
        self.nlp = nlp
        self.stop_words = stop_words
        self.file_name = file_name
        self.language = language

        # Run spaCy once; all subsequent methods use self._doc
        self._doc = nlp(text)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def analyse(self, top_sentences: int = 5, top_words: int = 20) -> DocumentResult:
        """
        Run all analyses and return a :class:`DocumentResult`.

        Parameters
        ----------
        top_sentences : int
            Number of hardest sentences to include in the result.
        top_words : int
            Number of most-frequent long words to include.
        """
        sentences = list(self._doc.sents)
        words = [
            t.text for t in self._doc
            if not t.is_space and not t.is_punct
        ]

        sentence_count = max(len(sentences), 1)
        word_count = max(len(words), 1)

        long_words_lix = [w for w in words if len(w) > LIX_LONG_WORD_THRESHOLD]
        long_words_rix = [w for w in words if len(w) > RIX_LONG_WORD_THRESHOLD]

        lix = self._calculate_lix(word_count, sentence_count, long_words_lix)
        rix = self._calculate_rix(sentence_count, long_words_rix)

        lix_band = interpret_lix(lix)

        # Average word length (characters, excluding punctuation)
        avg_word_length = (
            sum(len(w) for w in words) / word_count
        )

        # Lexical diversity
        content_words = [
            w.lower() for w in words
            if w.lower() not in self.stop_words
        ]
        unique_word_count = len(set(content_words))
        ttr = unique_word_count / max(len(content_words), 1)

        # POS counts
        noun_count = sum(1 for t in self._doc if t.pos_ == "NOUN")
        verb_count = sum(1 for t in self._doc if t.pos_ == "VERB")
        adj_count = sum(1 for t in self._doc if t.pos_ == "ADJ")

        # Sentence-level diagnostics
        sentence_results = self._analyse_sentences(sentences)
        hardest = sorted(
            sentence_results, key=lambda s: s.lix_contribution, reverse=True
        )[:top_sentences]

        # Top long words
        from collections import Counter
        long_word_freq = Counter(w.lower() for w in long_words_lix)
        top_long_words = long_word_freq.most_common(top_words)

        return DocumentResult(
            file_name=self.file_name,
            language=self.language,
            lix=round(lix, 2),
            rix=round(rix, 2),
            lix_label=lix_band["label"],
            lix_description=lix_band["typical_text"],
            lix_hex=lix_band["hex"],
            rix_grade=interpret_rix(rix),
            word_count=word_count,
            sentence_count=sentence_count,
            avg_words_per_sentence=round(word_count / sentence_count, 1),
            avg_word_length=round(avg_word_length, 2),
            long_word_count=len(long_words_lix),
            long_word_ratio=round(len(long_words_lix) * 100 / word_count, 1),
            unique_word_count=unique_word_count,
            type_token_ratio=round(ttr, 3),
            noun_count=noun_count,
            verb_count=verb_count,
            adjective_count=adj_count,
            hardest_sentences=hardest,
            top_long_words=top_long_words,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_lix(
        word_count: int,
        sentence_count: int,
        long_words: list[str],
    ) -> float:
        """
        LIX = (words / sentences) + (long_words * 100 / words)

        Björnsson (1968) defines 'long' as > 6 characters for Scandinavian
        languages. This constant is imported from language_config.
        """
        return (word_count / sentence_count) + (len(long_words) * 100 / word_count)

    @staticmethod
    def _calculate_rix(
        sentence_count: int,
        long_words: list[str],
    ) -> float:
        """
        RIX = long_words / sentences

        Anderson (1983) defines 'long' as > 7 characters.  Note that this
        formula is fundamentally different from LIX: it produces a score
        that maps to a school grade level, not a 0-100 index.
        """
        return len(long_words) / sentence_count

    def _analyse_sentences(
        self, sentences
    ) -> list[SentenceResult]:
        results: list[SentenceResult] = []

        for sent in sentences:
            words = [
                t.text for t in sent
                if not t.is_space and not t.is_punct
            ]
            wc = len(words)
            if wc == 0:
                continue

            lw = sum(1 for w in words if len(w) > LIX_LONG_WORD_THRESHOLD)
            ratio = lw / wc
            results.append(
                SentenceResult(
                    text=sent.text.strip(),
                    word_count=wc,
                    long_word_count=lw,
                    long_word_ratio=round(ratio, 3),
                    lix_contribution=round(ratio * 100, 1),
                )
            )

        return results