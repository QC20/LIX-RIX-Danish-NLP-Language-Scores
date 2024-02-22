from pdf_processor import PDFProcessor
from text_analyzer import TextAnalyzer

def main():
    folder_path = "C:/Users/w33762/Desktop/NLP/test"  # Replace with the path to your folder containing PDFs
    pdf_processor = PDFProcessor(folder_path)
    pdf_processor.process_pdfs_in_folder()

if __name__ == "__main__":
    main()
