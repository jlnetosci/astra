import streamlit as st
import os
import base64
from PIL import Image
from st_social_media_links import SocialMediaIcons

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

# Instructions
st.title("Instructions")

st.header("Quickstart")


st.markdown("""<div style="text-align: justify;"> 

1. Click the "**Add GEDCOM**" section in the sidebar menu and **upload a GEDCOM** file (if you do not have one, you can use one of the provided examples).\n
2. Select a type of **view** (**2D** or **3D**) from the dropdown menu.\n
3. Press the "**Generate Network**" button. \n 

Upon data processing and network generation you will be able to interact with the visualization.
</div>""", unsafe_allow_html=True
)

st.divider()

st.header("In-depth Guide:")

st.markdown("""<div style="text-align: justify;"> 

1. Click the "**Add GEDCOM**" section in the sidebar menu.\n 
2. **Upload a GEDCOM** file (or one of the provided examples).\n
    - If the file was parsed correctly a success message will appear. \n
3. Select a type of **view** (the classic **2D** or the new **3D** visualization) from the drop down menu.\n
4. Customize the network at your own will:
    - **Highlights**
        - Consider if you want to **highlight a specific individual** as your **root/reference** and select them from the menu. Uncheck the box in case you do not.
        - If you want to **call attention to one additional person**, press "**Highlight another individual**" and select them from the drop down list.        
        - You can also emphasize the **ancestors** of your selected reference in a different color (this option will not be available if you do not want a reference).

    - **Colors**:
        - Choose a preset **color palette** (between **Classic, Pastel, Nightly, Grayscale, or Colorblind-friendly**), or
        - You can **pick a color** that bests suits your taste **for each of the highlighted** options mentioned previously. 

5. Press the "**Generate Network**" button. \n 

<p>With the completion of data processing and network generation, users will have the capability to engage with the visualization interface.</p> \
<p>For 2D networks a physics simulation will be performed in order to yield better separations, the user is also able to manually displace nodes.</p> \
<p>3D networks are positionally static (defined by a layout algorithm), the user is able to zoom in and out at will and rotate it in any direction.</p>
</div>""", unsafe_allow_html=True
)


st.sidebar.markdown(""" **Author:** [João L. Neto](https://github.com/jlnetosci)""", unsafe_allow_html=True)

st.sidebar.markdown(""" <div style="text-align: right;"><b>v0.2.0b</b></div>""", unsafe_allow_html=True)


social_media_links = ["https://www.youtube.com/@ASTRAviewer/", "https://x.com/ASTRAviewer", "https://www.instagram.com/ASTRAviewer/"]
link_colors = ["#ff6665", "#81c7dc", None]

social_media_icons = SocialMediaIcons(social_media_links, link_colors)
social_media_icons.render(sidebar=True, justify_content="start")