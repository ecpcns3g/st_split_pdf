import os
import re
import fitz  # PyMuPDF
import streamlit as st
from pathlib import Path
import zipfile
import tempfile
import shutil

# Set page config
st.set_page_config(
    page_title="PDF Dela & Döp om",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create directories
input_dir = Path('input')
output_dir = Path('output')

input_dir.mkdir(exist_ok=True)
output_dir.mkdir(exist_ok=True)

# Define the function to process PDF
def bearbeta_pdf(input_pdf, output_dir, id_pattern):
    """Bearbetar en PDF-fil: delar upp den och döper om sidorna baserat på innehåll.

    Args:
        input_pdf (str or Path): Sökväg till indata-PDF-filen
        output_dir (str or Path): Mapp för att spara utdata-PDF-filer
        id_pattern (str): Reguljärt uttryck för att hitta unik identifierare

    Returns:
        list: Lista med dictionaries som innehåller sidinfo och utdatafilnamn
    """
    resultat = []

    # Open the PDF file
    doc = fitz.open(input_pdf)
    total_sidor = len(doc)


    # Create zip file
    zip_filnamn = output_dir / f"{Path(input_pdf).stem}.zip"  # Name zip file based on input file
    with zipfile.ZipFile(zip_filnamn, 'w') as zip_fil:

        # Process each page, save as separate pdf files and add to zip file:
        for i in range(total_sidor):
            print(f"Bearbetar sida {i+1} av {total_sidor}")
            sida_nummer = i + 1

            # Extract text from the page
            text = doc[i].get_text()

            # Extract identifier from text
            match = re.search(id_pattern, text)
            identifierare = match.group(1) if match else f"page_{sida_nummer}"

            # Create a new PDF with just this page
            ny_doc = fitz.open()
            ny_doc.insert_pdf(doc, from_page=i, to_page=i)

            # Save the page as a new PDF with optimization
            output_filnamn = f"{identifierare}.pdf"
            output_sokvag = output_dir / output_filnamn

            # Optimize PDF before saving
            ny_doc.save(
                output_sokvag,
                garbage=4,  # Maximum garbage collection
                deflate=True,  # Compress streams
                clean=True,  # Clean redundant elements
                pretty=False,  # Don't pretty-print
                linear=True,  # Optimize for web viewing
                ascii=False  # Use binary format
            )
            ny_doc.close()

            # Add file to zip archive
            zip_fil.write(output_sokvag, arcname=output_filnamn)

            resultat.append({
                'sida': sida_nummer,
                'identifierare': identifierare,
                'output_fil': output_filnamn
            })

    # Close original document
    doc.close()
    st.success(f"Alla filer har sparats till {zip_filnamn}")

    return resultat

# Main app
st.title("PDF Dela & Döp om")
st.markdown("""
Denna app delar upp en flersidig PDF-fil i en fil per sida och byter namn på sidorna baserat på ID-värden (t.ex. LITTERA-nummer).
""")

# Sidebar for settings
st.sidebar.header("Inställningar")

# Pattern selection
pattern_options = {
    "NUMMER": r'(?<![A-Za-z])EJ SKALA\s+([A-Z0-9-]+)',
    "LITTERA": r'LITTERA\s+([A-Z0-9]+)',
    "ID": r'ID\s*([A-Z0-9]+)',
    "REFERENS": r'REFERENS\s*(\d+)',
    "Egen Regex": None
}

selected_pattern = st.sidebar.selectbox(
    "Välj Identifierare",
    list(pattern_options.keys())
)

# Custom pattern input
if selected_pattern == "Egen Regex":
    custom_pattern = st.sidebar.text_input(
        "Ange Egen Regex",
        r'LITTERA\s+([A-Z0-9]+)',
        help="Ange ett regex-mönster med en grupp. Exempel: r'LITTERA\s+([A-Z0-9]+)'"
    )
    id_pattern = custom_pattern
else:
    id_pattern = pattern_options[selected_pattern]

# File upload
uploaded_file = st.file_uploader("Ladda upp en PDF-fil", type=["pdf"])

if uploaded_file is not None:
    # Save uploaded file to input directory
    input_path = input_dir / uploaded_file.name
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"Fil inladdad: {uploaded_file.name}")
    
    # Process button
    if st.button("Dela upp PDF"):
        with st.spinner("Bearbetar PDF..."):
            # Process the PDF
            resultat = bearbeta_pdf(input_path, output_dir, id_pattern)
            
            # Display results in a table
            st.subheader("Resultat")
            
            # Create a DataFrame for better display
            import pandas as pd
            df = pd.DataFrame(resultat)
            st.dataframe(df)
            
            # Provide download link for the zip file
            zip_path = output_dir / f"{Path(uploaded_file.name).stem}.zip"
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="Ladda ner ZIP-fil",
                    data=f,
                    file_name=zip_path.name,
                    mime="application/zip"
                )
            
            # Clean up
            os.remove(input_path)
            for file in output_dir.glob("*.pdf"):
                os.remove(file) 
