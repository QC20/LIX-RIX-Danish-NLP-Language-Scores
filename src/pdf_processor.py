import os
import re
import PyPDF2
import pandas as pd
from tqdm import tqdm
from text_analyzer import TextAnalyzer

class PDFProcessor:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def extract_text_from_pdf(self, pdf_file):
        text = ""
        with open(pdf_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def count_paragraph_and_section(self, text):
        # Count occurrences of "paragraf" and "§"
        paragraph_count = text.lower().count("paragraf")
        section_count = text.count("§")
        return paragraph_count, section_count

    def process_pdfs_in_folder(self):
        data = {
            "PDF Name": [],
            "LIX Score": [],
            "RIX Score": [],
            "Unique Words (no stopwords)": [],
            "Nouns": [],
            "Verbs": [],
            "Adjectives": [],
            "Paragraph Count": [],
            "Section Count": []
        }   
        
        pdf_files = [file for file in os.listdir(self.folder_path) if file.lower().endswith('.pdf')]
        
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            pdf_path = os.path.join(self.folder_path, pdf_file)
            extracted_text = self.extract_text_from_pdf(pdf_path)
            pdf_name = os.path.splitext(pdf_file)[0]

            text_analyzer = TextAnalyzer(extracted_text)
            lix_score = text_analyzer.calculate_lix()
            rix_score = text_analyzer.calculate_rix()
            unique_word_count = text_analyzer.count_unique_words()
            nouns, verbs, adjectives = text_analyzer.analyze_pos()
            paragraph_count, section_count = self.count_paragraph_and_section(extracted_text)

            data["PDF Name"].append(pdf_name)
            data["LIX Score"].append(f"{lix_score:.2f}")
            data["RIX Score"].append(f"{rix_score:.2f}")
            data["Unique Words (no stopwords)"].append(unique_word_count)
            data["Nouns"].append(nouns)
            data["Verbs"].append(verbs)
            data["Adjectives"].append(adjectives)
            data["Paragraph Count"].append(paragraph_count)
            data["Section Count"].append(section_count)

        df = pd.DataFrame(data)
        excel_file = "pdf_lix_rix_wordcount_pos_paragraph_section_scores.xlsx"
        df.to_excel(excel_file, index=False)
