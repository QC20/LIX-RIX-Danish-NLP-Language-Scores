'''
LIX
This script calculates the readability index of some text: Just paste it into the box below and remember not to include the headings. "LIX" or readability index is a measure of how hard a text is to read. It is defined as the percentage of words longer than six letters plus the average number of words per sentence. The following outline shows what the index you will get tells you about your text:

LIX < 20: it is very easy to read
LIX < 30: it is easy to read
LIX < 40: it is a little hard to read
LIX < 50: it is hard to read
LIX < 60: it is very hard to read
Note: This applies only to languages where LIX is applicable. These include Danish, Swedish, Norwegian (Bokmål and Nynorsk), as well as Dutch.

'''

import os
import re
import PyPDF2
import pandas as pd
from tqdm import tqdm
import spacy

# Load the Danish language model
nlp = spacy.load("da_core_news_sm")


# Danish stop words
danish_stop_words = ["og", "i", "jeg", "det", "at", "en", "den", "til", "er", "som", "på", "de", "med", "han", "af",
                     "for", "ikke", "der", "var", "mig", "sig", "men", "et", "har", "om", "vi", "min", "havde", "ham",
                     "hun", "nu", "over", "da", "fra", "du", "ud", "sin", "dem", "os", "op", "man", "hans", "hvor",
                     "eller", "hvad", "skal", "selv", "her", "alle", "vil", "blev", "kunne", "ind", "når", "være",
                     "dog", "noget", "ville", "jo", "deres", "efter", "ned", "skulle", "denne", "end", "dette", "mit",
                     "også", "under", "have", "dig", "anden", "hende", "mine", "alt", "meget", "sit", "sine", "vor",
                     "mod", "disse", "hvis", "din", "nogle", "hos", "blive", "mange", "ad", "bliver", "hendes", "været"]

def extract_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def calculate_lix(text):
    words = text.split()
    sentence_count = text.count('.') + text.count('!') + text.count('?')

    if sentence_count == 0:
        sentence_count = 1  # No division by zero

    long_words = sum(1 for word in words if len(word) > 6) # LIX threshold is 6 characters for scandinavian languages
    lix = (len(words) / sentence_count) + (long_words * 100) / len(words)
    return lix

def calculate_rix(text):
    words = text.split()
    sentence_count = text.count('.') + text.count('!') + text.count('?')

    if sentence_count == 0:
        sentence_count = 1  # No division by zero

    long_words = sum(1 for word in words if len(word) > 7)  # RIX threshold is 7 characters
    rix = (len(words) / sentence_count) + (long_words * 100) / len(words)
    return rix

def process_pdfs_in_folder(folder_path):
    data = {"PDF Name": [], "LIX Score": [], "RIX Score": [], "Unique Words (no stopwords)": [], "Nouns": [], "Verbs": [], "Adjectives": []}
    pdf_files = [file for file in os.listdir(folder_path) if file.lower().endswith('.pdf')]
    
    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        pdf_path = os.path.join(folder_path, pdf_file)
        extracted_text = extract_text_from_pdf(pdf_path)
        lix_score = calculate_lix(extracted_text)
        rix_score = calculate_rix(extracted_text)
        pdf_name = os.path.splitext(pdf_file)[0]

        # Remove punctuation and split text into words
        words = re.findall(r'\b\w+\b', extracted_text.lower())

        # Remove stop words
        words = [word for word in words if word not in danish_stop_words]

        # Calculate unique word count
        unique_word_count = len(set(words))

        # Analyze POS using spaCy
        doc = nlp(" ".join(words))
        
        # Count different types of words
        nouns = sum(1 for token in doc if token.pos_ == "NOUN")
        verbs = sum(1 for token in doc if token.pos_ == "VERB")
        adjectives = sum(1 for token in doc if token.pos_ == "ADJ")

        data["PDF Name"].append(pdf_name)
        data["LIX Score"].append(f"{lix_score:.2f}")
        data["RIX Score"].append(f"{rix_score:.2f}")
        data["Unique Words (no stopwords)"].append(unique_word_count)
        data["Nouns"].append(nouns)
        data["Verbs"].append(verbs)
        data["Adjectives"].append(adjectives)

    df = pd.DataFrame(data)
    excel_file = "pdf_lix_rix_wordcount_pos_scores.xlsx"
    df.to_excel(excel_file, index=False)


if __name__ == "__main__":
    folder_path = "C:/Users/w33762/Desktop/NLP/test"  # Replace with the path to your folder containing PDFs
    process_pdfs_in_folder(folder_path)
