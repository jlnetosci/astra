"""
ASTRA: GEDCOM VISUALIZATION

Author: João L. Neto
Contact: https://github.com/jlnetosci
Version: 0.2.0dev
Last Updated: March 8, 2024

Description:
Accepts the upload of a GEDCOM file, parses it, and displays a "star map" like network visualization of the individuals. 
"""

import streamlit as st
import os
import re
import base64
import requests
import threading
from gedcom.parser import Parser
from gedcom.parser import GedcomFormatViolationError
from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement
from iteration_utilities import duplicates, unique_everseen
from itertools import combinations, product
from pyvis.network import Network
from st_pages import Page, show_pages, add_page_title
from streamlit_js_eval import streamlit_js_eval
from time import sleep

## Functions as a "hacky" way get logo above the multipage navigation bar. 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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

def parse_gedcom(uploaded_file):
    """
    Creates a temporary file and parses it. 

    input:
    :uploaded_file: GEDCOM file to be parsed.

    return: 
    :gedcom_parser: Parsed file.
    """

    # Save the uploaded file temporarily with UTF-8 encoding
    temp_file_path = "temp_gedcom_file.ged"
    with open(temp_file_path, "w", encoding='utf-8') as temp_file:
        temp_file.write(uploaded_file.read().decode('utf-8', 'ignore'))

    # Check if the file path does not end with a newline and add one
    if not temp_file_path.endswith('\n'):
        with open(temp_file_path, "a", encoding='utf-8') as temp_file:
            temp_file.write('\n')

    # Initialize parser
    gedcom_parser = Parser()
    gedcom_parser.parse_file(temp_file_path, False)  # Use the default encoding

    # Remove the temporary GEDCOM file
    os.remove(temp_file_path)
    
    return gedcom_parser

def check_duplicates(lst):
    dups = list(unique_everseen(duplicates(lst)))
    if dups == []:
        pass
    else:
        raise ValueError(" ".join(dups) + " duplicated. GEDCOM files should not have duplicate IDs. Please check your file.")
    
def process_gedcom(gedcom_parser):
    """
    Creates a ID to name translator (dictionary). Processes the parsed GEDCOM into nodes their label and edges.

    input:
    :gedcom_parser: Parsed GEDCOM file.

    return:
    :translator: dictionary of short ID to long ID.
    :nodes: list of long IDs of any individual with connections.
    :labels: dictionary, with :nodes: as keys, and values as strings with name, place of birth and date of birth of the individuals.
    :edges: list of connections (pairs and parent-child)
    """

    root_child_elements = gedcom_parser.get_root_child_elements()
    
    # Process data
    translator = {} #from pointer to node name
    labels = {} #collect for node labels
    
    fams = {} #collect spouses per family for pair edges
    famc = {} #collect per family for children edges

    elements = []
    
    for element in root_child_elements: #elements that are individuals or family
        if isinstance(element, IndividualElement): #in elements that are individuals
            elements.append(element.get_pointer())
            name = " ".join(element.get_name())
            id = str(element.get_pointer()).replace("@", "")
            bp = element.get_birth_data()[1] #birth place
            bd = element.get_birth_data()[0] #birth date
    
            #collect node info into translator
            translator[element.get_pointer()] = str(name + " (" + id + ")")
            labels[translator[element.get_pointer()]] = str(name + " \n " + bp + " \n " + bd)
    
            for family in gedcom_parser.get_families(element, family_type='FAMS'):
                key = str(family.get_pointer())
                value = str(translator[element.get_pointer()])
                fams.setdefault(key, []).append(value)
            
            for family in gedcom_parser.get_families(element, family_type='FAMC'):
                key = str(family.get_pointer())
                value = str(translator[element.get_pointer()])
                famc.setdefault(key, []).append(value)

    try:
        check_duplicates(elements)

    except ValueError as e:
        st.error(f'**Error:** {str(e)}')
        st.stop()

    # Create edges
    pairs = [] #edges for couples
    pairs.extend(tuple(val) for val in fams.values() if len(val) > 1)
    pairs = [tuple(val) for val in fams.values() if len(val) > 1]
    
    children = [] #edges for parent-child
    children.extend(list(product(fams[key], famc[key])) for key in fams.keys() if key in famc)
    children = sum(children, [])
    
    edges = pairs + children #merge lists
    
    # Create and filter nodes
    nodes = list(translator.values())
    nodes = [node for node in nodes if any(node in pair for sublist in [pairs, children] for pair in sublist)] #delete nodes with no edges

    # Filter label dictionary for nodes with edges
    keys_to_delete = [key for key in labels if key not in nodes]
    for key in keys_to_delete:
        del labels[key]

    # Clean up labels
    for key, value in labels.items():
        while ", , " in value:
            value = re.sub(r',\s*,', ',', value)
        labels[key] = value

    return translator, nodes, labels, edges

def get_ancestors(gedcom_parser, translator, individual):
    """
    Creates a name to ID translator (dictionary). Gets a list of ancestors of a specified individual.

    input:
    :gedcom_parser: Parsed GEDCOM file.
    :translator: dictionary of short ID to long ID.
    :individual: long ID of individual

    return:
    :ancestors: list of long IDs of ancestors of the selected :individual:
    """

    reverse_translator = {value: key for key, value in translator.items()}
    ancestors = gedcom_parser.get_ancestors(gedcom_parser.get_element_dictionary()[reverse_translator[individual]]) #takes long ID to short ID, calls location in memory to get ancestors.
    ancestors = [translator[ancestor.get_pointer()] for ancestor in ancestors] # gets short IDs (pointers) and turns them into long IDs
    ancestors.insert(0, individual)
    return ancestors

def color_ancestors(nodes, node_color, ancestors, ancestors_color, individual, individual_color):
    """
    Defines colors for general nodes, ancestor nodes and the selected individual node.

    input:
    :node: list of long IDs of all individuals
    :node_color: color for general nodes.
    :ancestors: list of long IDs of ancestors
    :ancestors_color: color for ancestor nodes.
    :individual: list of long IDs of all individuals
    :individual_color: color for the selected individual nodes.

    return:
    :node_color: dictionary of all individuals and their respective color.
    """
    node_color = dict.fromkeys(nodes, node_color)
    node_color.update({ancestor: ancestors_color for ancestor in ancestors if ancestor in node_color})
    node_color[individual] = individual_color
    return node_color

def create_network(nodes, labels, base_node_color, edges, bg_color):
    """
    Creates network visualization.

    input:
    :nodes: list of long IDs of all individuals
    :labels: dictionary, with :nodes: as keys, and values as strings with name, place of birth and date of birth of the individuals.
    :base_node_color: color for nodes.
    :edges: list of connections (pairs and parent-child).
    :bg_color: color for the background.

    return:
    :network: network with the data of interest
    """

    net = Network(
        notebook=True, height="800px", width="100%", bgcolor=bg_color, cdn_resources="in_line"
    )

    # Add nodes with color and labels
    for node in nodes:
        net.add_node(node, label=labels[node], color=base_node_color[node], font={"color": base_node_color[node]})

    net.add_edges(edges)
    #net.show_buttons()
    network = net.show("gedcom.html")
    return network

# Streamlit app
st.set_page_config(layout="wide")

# Show logo above navigation bar
add_logo()

# Customize navigation bar
show_pages([Page("app.py", "ASTRA", "🌌"), Page("pages/faq.py", "Frequently asked questions", "❓"), Page("pages/contact-form.py", "Contact me", "✉️")])

# Sidebar top
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'logo.png')
#st.sidebar.image(IMAGE_PATH, use_column_width=True)

# Pre-process file github raw url for direct download
gedcom_file_url = "https://raw.githubusercontent.com/jlnetosci/astra/main/gedcom_files/genealogyoflife_tng/TolkienFamily.ged"
gedcom_file_content = requests.get(gedcom_file_url).content
gedcom_file_base64 = base64.b64encode(gedcom_file_content).decode("utf-8")

#download_link = f'<a href="data:text/plain;base64,{gedcom_file_base64}" download="TolkienFamily.ged">here</a>'

instructions = st.sidebar.expander(label=r"$\textbf{\textsf{\normalsize Instructions}}$")
instructions.markdown(f""" **Instructions:** <div style="text-align: justify;"> \n 
1. Upload a GEDCOM file (example <a href="data:text/plain;base64,{gedcom_file_base64}" download="TolkienFamily.ged">here</a>).
2. Select your root individual.  
3. Choose the colors of your preference.  
4. Click 'Generate Network'. \n 
Please be patient while the network loads – time increases with the number of individuals and connections.  
After generation the network goes through a physics simulation to better distribute nodes.  
Nodes can also be moved to wield better separations. </div> """, unsafe_allow_html=True)

upload_gedcom = st.sidebar.expander(label=r"$\textbf{\textsf{\normalsize Add GEDCOM}}$")

uploaded_file = upload_gedcom.file_uploader("Upload a GEDCOM file", type=["ged"])

button_generate_network = None  # Initialize the button variable

# Dropdown menu for selecting an individual
if uploaded_file is not None:
    try:
        parser = parse_gedcom(uploaded_file)

        translator, nodes, labels, edges = process_gedcom(parser)

        success = upload_gedcom.success("✅ Processing successful.")
        #sleep(1) # Wait for 1 seconds
        #success.empty() # Clear the alert

        views = st.sidebar.expander(label=r"$\textbf{\textsf{\normalsize Views}}$", expanded=True)
        views_sb = views.selectbox(label="Select a view", options=["Classic (2D)", "3D", "Map"], index=None)

        #st.sidebar.header("Select an Individual")
        nodes_sorted = sorted(nodes)  # Sort nodes alphabetically
        
        if views_sb == "Classic (2D)":
            formating = st.sidebar.expander(label=r"$\textbf{\textsf{\normalsize Colors and highlight}}$", expanded=True)
            
            formating.markdown("**Background<br>**", unsafe_allow_html=True)

            selected_bg_color = formating.color_picker("Select color", "#222222")

            formating.markdown("""<hr style='margin-top:0em; margin-bottom:0em' /> """, unsafe_allow_html=True)

            formating.markdown("**Individuals**")

            selected_base_node_color = formating.color_picker("Select color", "#FFFFFF")
            
            formating.markdown("""<hr style='margin-top:0em; margin-bottom:0em' /> """, unsafe_allow_html=True)

            formating.markdown("**Highlight individual**")
            
            neg_root = formating.checkbox("I do not want to select a root")
            if neg_root:
                st.empty()
            else:
                selected_individual = formating.selectbox(
                "Select an Individual as root",
                nodes_sorted,
                index=next(
                    (i for i, node in enumerate(nodes_sorted) if re.search(r"\(I0*1\)", node)),
                    0,
                ),
            )
                selected_root_color = formating.color_picker("Select color", "#FF0051", key="selected_root_color")
                
                highlight_another_individual = formating.checkbox("Highlight another individual")

                if highlight_another_individual:
                    highlight_individual = formating.selectbox(
                        "Highlight individual",
                        nodes_sorted,
                        index=next(
                            (i for i, node in enumerate(nodes_sorted) if re.search(r"\(I0*2\)", node)),
                            0,
                        ),
                    )

                    selected_highlight_color = formating.color_picker("Select color", "#FF0051", key="selected_highlight_color")
                
                formating.markdown("""<hr style='margin-top:0em; margin-bottom:0em' /> """, unsafe_allow_html=True)

                formating.markdown("**Ancestors**")

                neg_ancestors = formating.checkbox("I do not want to highlight the root's direct ancestors")
                if neg_ancestors:
                    st.empty()
                else:
                    ancestors = get_ancestors(parser, translator, selected_individual)    
                    selected_ancestor_color = formating.color_picker("Select color", "#ffa500")

            button_generate_network = st.sidebar.button("Generate Network", key="generate_network_button")

    except GedcomFormatViolationError:
        st.error("**Error:** The parser cannot process the GEDCOM file, possibly because of custom or unrecognized tags. This can probably be solved by using [Gramps](https://gramps-project.org/blog/download/) and re-exporting the file." )
        st.stop()

# Handle button click to generate network
if button_generate_network and selected_individual:
    #print("Button pressed to generate network!")

    with st.spinner('Processing data'):
        # Create the network visualization with selected colors
        node_color = color_ancestors(nodes, selected_base_node_color, ancestors, selected_ancestor_color, selected_individual, selected_root_color)

        adjusted_labels = {node: labels[node] for node in nodes if node in labels}

        network = create_network(
            nodes, adjusted_labels, node_color, edges, selected_bg_color,
        )

    # Display the network HTML
    with open("gedcom.html", "r") as file:
        network_html = file.read()

    st.components.v1.html(network_html, height=800)

    # Centered download button with dynamic styles
    #st.markdown(
    #    """<div style="display: flex; justify-content: center;">
    #       <button onclick="location.href='data:text/html;base64,{}'" 
    #               style="padding: 10px; background-color: {}; color: {}; border: none; border-radius: 4px; cursor: pointer;">
    #               Download HTML
    #       </button>
    #    </div>""".format(base64.b64encode(network_html.encode()).decode(), selected_bg_color, selected_base_node_color),
    #    unsafe_allow_html=True
    #)

# Define your javascript
#my_js = """
#alert("Hola mundo");
#"""

# Wrapt the javascript as html code
#my_html = f"<script>{my_js}</script>"

# Execute your app
#st.title("Javascript example")
#st.components.v1.html(my_html)

st.sidebar.markdown(""" **Author:** [João L. Neto](https://github.com/jlnetosci)""", unsafe_allow_html=True)

st.sidebar.markdown(""" <div style="text-align: right;"><b>v0.2.0dev</b></div>""", unsafe_allow_html=True)