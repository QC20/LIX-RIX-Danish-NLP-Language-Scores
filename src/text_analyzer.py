import re
import spacy

class TextAnalyzer:
    def __init__(self, text):
        self.text = text
        self.nlp = spacy.load("da_core_news_sm")
        self.danish_stop_words = ["og", "i", "jeg", "det", "at", "en", "den", "til", "er", "som", "på", "de", "med", "han", "af",
                     "for", "ikke", "der", "var", "mig", "sig", "men", "et", "har", "om", "vi", "min", "havde", "ham",
                     "hun", "nu", "over", "da", "fra", "du", "ud", "sin", "dem", "os", "op", "man", "hans", "hvor",
                     "eller", "hvad", "skal", "selv", "her", "alle", "vil", "blev", "kunne", "ind", "når", "være",
                     "dog", "noget", "ville", "jo", "deres", "efter", "ned", "skulle", "denne", "end", "dette", "mit",
                     "også", "under", "have", "dig", "anden", "hende", "mine", "alt", "meget", "sit", "sine", "vor",
                     "mod", "disse", "hvis", "din", "nogle", "hos", "blive", "mange", "ad", "bliver", "hendes", "været"]

    def calculate_lix(self):
        words = self.text.split()
        sentence_count = self.text.count('.') + self.text.count('!') + self.text.count('?')

        if sentence_count == 0:
            sentence_count = 1  # No division by zero

        long_words = sum(1 for word in words if len(word) > 6) # LIX threshold is 6 characters for scandinavian languages
        lix = (len(words) / sentence_count) + (long_words * 100) / len(words)
        return lix

    def calculate_rix(self):
        words = self.text.split()
        sentence_count = self.text.count('.') + self.text.count('!') + self.text.count('?')

        if sentence_count == 0:
            sentence_count = 1  # No division by zero

        long_words = sum(1 for word in words if len(word) > 7)  # RIX threshold is 7 characters
        rix = (len(words) / sentence_count) + (long_words * 100) / len(words)
        return rix

    def count_unique_words(self):
        words = re.findall(r'\b\w+\b', self.text.lower())
        words = [word for word in words if word not in self.danish_stop_words]
        unique_word_count = len(set(words))
        return unique_word_count

    def analyze_pos(self):
        doc = self.nlp(" ".join(self.text.split()))
        nouns = sum(1 for token in doc if token.pos_ == "NOUN")
        verbs = sum(1 for token in doc if token.pos_ == "VERB")
        adjectives = sum(1 for token in doc if token.pos_ == "ADJ")
        return nouns, verbs, adjectives
