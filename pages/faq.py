import streamlit as st
import os
import base64
from PIL import Image

## Functions as a "hacky" way get logo above the multipage navigation bar. 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_PATH = os.path.join(BASE_DIR, 'logo.png')
favicon = os.path.join(BASE_DIR, 'favicon.png')
favicon = Image.open(favicon)

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
                padding-top: 40px;
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
        'What is ASTRAviewer?': '<p>ASTRAviewer is a web app that displays a "star map" like network visualization from family trees stored as GEDCOM files.',

        'What is a GEDCOM?': 'GEDCOM is the shorthand for <b><u>Ge</b></u>nealogical <b><u>D</b></u>ata <b><u>Com</b></u>munication. GEDCOM files are the standard to store and share genealogical data. While the format was developed by the Church of Jesus Christ of Latter-day Saints, it is an open standard used by most genealogical software. \
        <p><br>More information on GEDCOM: <a href="https://en.wikipedia.org/wiki/GEDCOM" target="_blank" rel="noopener noreferrer">Wikipedia</a>; <a href="https://www.familysearch.org/en/wiki/GEDCOM" target="_blank" rel="noopener noreferrer">Familysearch</a>.</p>',

        'How do I get a GEDCOM file?': 'GEDCOM files are usually exported with a .ged extension. Depending on your prefered genealogical software there may be different steps in obtaining the file. Most tools have instructions on how to export the family tree as GEDCOM. \
        (for example <a href="https://gramps-project.org/gramps-manual/2.2/en/ch03s05.html" target="_blank">Gramps</a>, <a href="https://www.myheritage.com/help-center?a=How-do-I-download-(export)-a-GEDCOM-file-of-my-family-tree-from-my-family-site---id--bPSFTnHBQNauRgs6JzqGiA" target="_blank">MyHeritage</a>, or <a href="https://en.geneanet.org/help/how-to-export-your-geneanet-family-tree" target="_blank">Geneanet</a>). \
        <p><br>The usage of this web app assumes you already have already started your genealogical research and are using a web tool or genealogical software to build your family tree. If you have not, there are companies that will do this research for you. Unfortunately, at this time I cannot suggest any. If you are a genealogical research company and want to discuss a partnership with us please reach out.</p>',

        'Can I export a GEDCOM file from FamilySearch?': '<p>As of the date of writing this FAQ (March 2024), FamilySearch’s documentation states: “Currently, a GEDCOM file cannot be exported directly from FamilySearch Family Tree.”</p>',

        'Will I be able to upload my family tree in other formats into ASTRAviewer?': '<p>Currently, ASTRAviewer solely parses GEDCOM files, if you have any suggestions regarding other formats please contact me with your suggestion.</p>',

        'What should I do if I encounter an error?': '<p>Please contact me.</p>'

    }

    # Display expandable boxes for each question-answer pair
    for question, answer in faq_data.items():
        with st.expander(r"$\textbf{\textsf{" + question + r"}}$", expanded=expand_all):  # Use LaTeX for bold label
            st.markdown(f'<div style="text-align: justify;"> {answer} </div>', unsafe_allow_html=True)

# Streamlit configuration
st.set_page_config(layout="centered", page_icon=favicon, initial_sidebar_state="expanded")

# Show logo above navigation bar
add_logo()

# Customize stDecoration colors
st.markdown("""
<style>
    [data-testid="stDecoration"] {
        background-image: linear-gradient(90deg, #213b52ff, #40556Bff);
    }
</style>""",
unsafe_allow_html=True)

#Show FAQ.
faq()