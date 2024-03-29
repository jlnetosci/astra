import streamlit as st
import os
import base64

## Functions as a "hacky" way get logo above the multipage navigation bar. 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_PATH = os.path.join(BASE_DIR, 'logo.png')

def get_base64_of_image(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode()

def add_logo():
    image_base64 = get_base64_of_image(IMAGE_PATH)
    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url('data:image/png;base64,{image_base64}');
                background-repeat: no-repeat;
                padding-top: 120px;
                background-position: 20px 20px;
                background-size:  90%;  /* Adjust this value to control the size */
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def faq():
    st.title("FAQ Page")
    #st.header(r"$\textbf{\textsf{FAQ Page}}$")  
    
    expand_all = st.toggle("Expand all", value=False)

    # FAQ data
    faq_data = {
        'What is ASTRA GEDCOM Viewer?': 'ASTRA is a web app that displays a "star map" like network visualization of a family tree organized as GEDCOM file.',

        'What is a GEDCOM?': 'GEDCOM is the shorthand for <b><u>Ge</b></u>nealogical <b><u>D</b></u>ata <b><u>Com</b></u>munication. GEDCOM files are the standard to store and share genealogical data. While the format was developed by the Church of Jesus Christ of Latter-day Saints, it is an open standard used by most genealogical software. <p> \
        More information on GEDCOM: <a href="https://en.wikipedia.org/wiki/GEDCOM" target="_blank" rel="noopener noreferrer">Wikipedia</a>; <a href="https://www.familysearch.org/en/wiki/GEDCOM" target="_blank" rel="noopener noreferrer">Familysearch</a>.',

        'How do I get a GEDCOM file?': 'The usage of this web app assumes you already have already started your genealogical research and are using a web tool or genealogical software to build your family tree. <p> \
        GEDCOM files are usually exported with a .ged extension. Depending on your prefered genealogical software there may be different steps in obtaining the file. Most tools have instructions on how to export the family tree as GEDCOM \
        (for example <a href="https://gramps-project.org/gramps-manual/2.2/en/ch03s05.html" target="_blank">Gramps</a>, <a href="https://www.myheritage.com/help-center?a=How-do-I-download-(export)-a-GEDCOM-file-of-my-family-tree-from-my-family-site---id--bPSFTnHBQNauRgs6JzqGiA" target="_blank">MyHeritage</a>, or <a href="https://en.geneanet.org/help/how-to-export-your-geneanet-family-tree" target="_blank">Geneanet</a>).',
        
        'Can I export a GEDCOM file from FamilySearch?': 'As of the date of writing this FAQ (March 2024), FamilySearch’s documentation states: “Currently, a GEDCOM file cannot be exported directly from FamilySearch Family Tree.”',

        'Will I be able to upload my family tree in other formats into ASTRA?': 'Currently, ASTRA solely parses GEDCOM files, if you have any suggestions regarding other formats please contact me with your suggestion.',

        'Does ASTRA keep my GEDCOM data?': 'Short answer: No. <p>\
        Longer answer: The GEDCOM file is read into a temporary file and deleted immediately after its parsing. Furthermore, the app is deployed on the Streamlit Cloud where data is ephemeral and files are removed upon changing the state of the app (i.e. refreshing) or closing the browser tab.',

        'What should I do if I encounter an error?': 'Please contact me.'

    }

    # Display expandable boxes for each question-answer pair
    for question, answer in faq_data.items():
        with st.expander(r"$\textbf{\textsf{" + question + r"}}$", expanded=expand_all):  # Use LaTeX for bold label
            st.markdown(f'<div style="text-align: justify;"> {answer} </div>', unsafe_allow_html=True)

# Streamlit configuration
st.set_page_config(layout="centered")

# Show logo above navigation bar
add_logo()

#Show FAQ.
faq()