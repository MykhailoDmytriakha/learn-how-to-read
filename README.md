# Syllable Processor

A Python application that processes Russian text to split words into syllables and provides different levels of text analysis.

## Installation

1. Clone this repository
2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest
# OR for more detailed output
pytest -v
```

## Running the Application

To run the web interface:
```bash
streamlit run src/app.py
```

This will open a web browser with the application interface where you can:
- Select from predefined phrases
- Enter your own text
- Process the text and view results
- Copy results to clipboard

## Features

- Split Russian text into syllables
- Process text at different levels:
  1. Individual syllables
  2. Words with syllable separation
  3. Complete text analysis
- User-friendly web interface
- Sample phrases included
- Copy results functionality
