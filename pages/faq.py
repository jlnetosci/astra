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

def show():
    st.title(r"\textbf{FAQ Page}")  # Use LaTeX for bold title

    # FAQ data
    faq_data = {
        "Question 1": "Answer 1",
        "Question 2": "Answer 2",
        "Question 3": "Answer 3",
        # Add more questions and answers as needed
    }

    # Display expandable boxes for each question-answer pair
    for question, answer in faq_data.items():
        with st.expander(r"\textbf{" + question + r"}"):  # Use LaTeX for bold label
            st.write(answer)

# Streamlit configuration
st.set_page_config(layout="centered")

# Show logo above navigation bar
add_logo()

# Show FAQ.
show()