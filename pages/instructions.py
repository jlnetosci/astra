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

st.header("Quickstart")
st.write( 
"""
1. Click the "__Add GEDCOM__" section in the sidebar menu and __upload a GEDCOM__ file (if you do not have one, you can use one of the provided examples).\n
2. Select a type of __view__ (__2D__ or __3D__) from the dropdown menu.\n
3. Press the "__Generate Network__" button. \n 

Upon data processing and network generation you will be able to interact with the visualization.
"""
)

st.divider()

st.header("In-depth Guide:")

st.write( 
"""
1. Click the "__Add GEDCOM__" section in the sidebar menu.\n 
2. __Upload a GEDCOM__ file (or one of the provided examples).\n
3. If the file was parsed correctly a success message will appear. \n
4. Select a type of __view__ (the classic __2D__ or the new __3D__ visualization) from the dropdown menu.\n
5. Customize the network at your own will:
    - __Highlights__
        - Consider if you want to __highlight a specific individual__ as your __root/reference__ and select them from the menu. Deselect option in case you do not.
        - If you want to __call attention to one additional person__, press "__Highlight another individual__" and select them from the dropdown list.        
        - You can also emphasize the __acenstors__ of your selected reference in a different color (this option will not be available if you do not want a reference).

    - __Colors__:
        - Choose a preset __color palette__ (between __Classic, Pastel, Greyscale, or Colorblind-friendly__) or
        - You can __pick a color__ that bests suits your taste __for each of the highlighted__ options mentioned previously. 

6. Press the "__Generate Network__" button. \n 

With the completion of data processing and network generation, users will have the capability to engage with the visualization interface. \\
For 2D networks a physics simulation will be performed in order to yield better separations, the user is also able to manually displace nodes. \\
3D networks are positionally static (defined by a layout algorithm), the user is able to zoom in and out at will and rotate it in any direction.
"""
)