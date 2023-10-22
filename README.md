# Lix and Rix Readability Calculator

Lix and Rix are two readability formulas designed to assess the readability of text based on letter counting, rather than syllable counting used in many other formulas. These formulas are particularly well-suited for non-English languages. This repository provides a Python script that calculates the Lix and Rix readability scores for text in Danish, Swedish, Norwegian (Bokmål and Nynorsk), and Dutch.

## Table of Contents

- [Lix and Rix Readability Calculator](#lix-and-rix-readability-calculator)
  - [Table of Contents](#table-of-contents)
  - [What are Lix and Rix?](#what-are-lix-and-rix)
    - [Where did the formulas come from?](#where-did-the-formulas-come-from)
    - [When are Lix and Rix most useful?](#when-are-lix-and-rix-most-useful)
  - [How to Use the Script](#how-to-use-the-script)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
  - [Lix and Rix Score Interpretation](#lix-and-rix-score-interpretation)
  - [Contributing](#contributing)
  - [License](#license)

## What are Lix and Rix?

Lix and Rix are two versions of the same readability formula, both developed to assess readability based on letter counting. Unlike many other formulas, they do not rely on syllable counting, making them more suitable for non-English languages.

### Where did the formulas come from?

- **Lix**: Developed in Sweden by Carl-Hugo Björnsson in 1968, Lix was initially obscure but later gained popularity. Björnsson established the formula's accuracy through extensive testing, using 162 texts, including textbooks, fiction, and technical literature. Lix calculates the percentage of words with seven or more letters.

- **Rix**: Created over a decade later by Jonathan Anderson, an Australian teacher, Rix is a modification of Lix. Anderson validated his formula by studying the validity of Lix and determining cut-off points to convert Lix scores to grade levels.

### When are Lix and Rix most useful?

Both Lix and Rix are valuable for determining text difficulty for education across a wide range of ages, from young children to adults. They are particularly useful for teachers and librarians when categorizing books.

Lix has also been studied for use with non-English languages, such as French, German, Greek, and English, making it a promising solution for assessing foreign language readability. It is increasingly popular worldwide.

For public writing, it's recommended to aim for a Lix score of 40 or below and a grade level of around 8 for Rix.

## How to Use the Script

The Python script provided in this repository calculates the Lix and Rix readability scores for text. It can process PDF files and assess the readability of the text within them.

### Dependencies

Before running the script, make sure you have the following dependencies installed:

- [PyPDF2](https://pythonhosted.org/PyPDF2/)
- [pandas](https://pandas.pydata.org/)
- [tqdm](https://tqdm.github.io/)
- [spaCy](https://spacy.io/)

You can install these dependencies using `pip`:

```shell
pip install PyPDF2 pandas tqdm spacy
```

## Usage
- Place your PDF files in a folder.
- Update the folder_path variable in the script to the path of your folder containing PDFs.

Run the script:
```shell
python readability_calculator.py
```

- The script will process the PDFs in the specified folder and create an Excel file with Lix and Rix scores, unique word counts, and parts of speech analysis.

## Lix and Rix Score Interpretation
The Lix score and Rix score indicate the readability of text. The thresholds for interpretation are as follows:

LIX < 20: Very easy to read.
LIX < 30: Easy to read.
LIX < 40: A little hard to read.
LIX < 50: Hard to read.
LIX < 60: Very hard to read.
Please note that these thresholds apply only to languages where Lix is applicable, including Danish, Swedish, Norwegian (Bokmål and Nynorsk), and Dutch.

## Contributing
If you have improvements or bug fixes for the script or would like to contribute to the documentation, feel free to create a pull request. We welcome contributions from the community!

## License
This project is licensed under the MIT License. See the LICENSE file for details.

Make sure to update the paths and dependencies sections to include the specific details needed to run your script. Additionally, if your script has any specific installation or usage requirements, you should provide instructions in the README.
