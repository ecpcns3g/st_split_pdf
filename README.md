# PDF Splitter & Renamer

A Streamlit app that allows you to split multi-page PDF files into individual pages and rename them based on content identifiers.

## Features

- Upload multi-page PDF files
- Split PDF into individual pages
- Rename pages based on content identifiers (LITTERA numbers, ID numbers, etc.)
- Custom regular expression patterns for identification
- Download results as a ZIP file

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
2. Upload a PDF file
3. Select an identifier pattern or enter a custom pattern
4. Click "Split PDF" to process the file
5. Download the resulting ZIP file

## Deployment

This app is designed to be deployed on Streamlit Community Cloud. Follow these steps:

1. Push your code to a GitHub repository
2. Connect your repository to Streamlit Community Cloud
3. Deploy the app

## License

MIT 