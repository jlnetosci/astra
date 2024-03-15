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

# Streamlit configuration
st.set_page_config(layout="centered")

# Show logo above navigation bar
add_logo()

# Instructions
st.title("Instructions")

#tmp
st.markdown(f""" **Instructions:** <div style="text-align: justify;"> \n """
#1. Upload a GEDCOM file (example <a href="data:text/plain;base64,{gedcom_file_base64}" download="TolkienFamily.ged">here</a>).
#"""2. Select your root individual.  
#3. Choose the colors of your preference.  
#4. Click 'Generate Network'. \n 
#Please be patient while the network loads – time increases with the number of individuals and connections.  
#After generation the network goes through a physics simulation to better distribute nodes.  
#Nodes can also be moved to wield better separations. </div> """, unsafe_allow_html=True
)
