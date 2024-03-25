"""
ASTRA: GEDCOM VISUALIZATION

Author: João L. Neto
Contact: https://github.com/jlnetosci
Version: 0.2.0dev
Last Updated: March 15, 2024

Description:
Accepts the upload of a GEDCOM file, parses it, and displays a "star map" like network visualization of the individuals. 
"""

import streamlit as st
import os
import re
import base64
import requests
import threading
import numpy as np
import plotly.graph_objects as go
import networkx as nx
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

    # Additional check for GEDCOM file integrity.
    #with open("temp_gedcom_file.ged") as temp_file:
    #    first_line = temp_file.readline()
    #    if not first_line.startswith("0 HEAD"):
    #        raise ValueError("The uploaded file does not appear to be a valid GEDCOM file.")

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

def color_nodes(nodes, node_color, ancestors=None, ancestors_color=None, individual=None, individual_color=None, highlight_individual=None, highlight_individual_color=None):
    """
    Defines colors for general nodes, ancestor nodes, and the selected individual node.

    input:
    :node: list of long IDs of all individuals
    :node_color: color for general nodes.
    :ancestors: list of long IDs of ancestors (optional)
    :ancestors_color: color for ancestor nodes (optional).
    :individual: list of long IDs of the selected individual (optional)
    :individual_color: color for the selected individual nodes (optional).

    return:
    :node_color: dictionary of all individuals and their respective color.
    """
    node_color = dict.fromkeys(nodes, node_color)

    if ancestors and ancestors_color:
        node_color.update({ancestor: ancestors_color for ancestor in ancestors if ancestor in node_color})
    
    if individual and individual_color:
        node_color[individual] = individual_color

    if highlight_individual and highlight_individual_color:
        node_color[highlight_individual] = highlight_individual_color
    
    return node_color

def create_network(nodes, labels, base_node_color, edges, bg_color, center_node):
    """
    Creates network visualization.

    input:
    :nodes: list of long IDs of all individuals
    :labels: dictionary, with :nodes: as keys, and values as strings with name, place of birth and date of birth of the individuals.
    :base_node_color: color for nodes.
    :edges: list of connections (pairs and parent-child).
    :bg_color: color for the background.
    :center_node: node from which the concentric circles start.

    return:
    :network: network with the data of interest
    """

    #### This function is somehow working even when the center_node is None. 
    #### which is weird but it keeps giving consistent results with and without selecting a root (which should be the selected_individual).
    #### attempts to change the behaviour have broken it, therefore it stays as is, until a new review.

    net = Network(
        notebook=True, height="800px", width="100%", bgcolor=bg_color, cdn_resources="in_line"
    )

    net.set_options('{"physics": {"solver": "force_atlas_2based"}}')

    net.options['nodes'] = {
        'font': {
            'face': 'sans-serif'  # Set font family to sans-serif
        }
    }

    # Create a dictionary for the positions
    pos = {}

    # Set the position for the center node
    pos[center_node] = (0, 0)

    # Set the positions for the other nodes
    for i, node in enumerate(nodes):
        if node == center_node:
            continue
        angle = 2 * np.pi * i / len(nodes)
        pos[node] = (np.cos(angle), np.sin(angle))

    # Add nodes with color, labels, and positions
    for node in nodes:
        net.add_node(node, label=labels[node], color=base_node_color[node], font={"color": base_node_color[node]}, x=pos[node][0]*1000, y=pos[node][1]*1000)

    net.add_edges(edges)
    #net.show_buttons()
    network = net.show("gedcom.html")
    return network

def plot_3d_network(nodes, edges, labels):
    adjusted_labels = {node: labels[node] for node in nodes if node in labels}

    # Create a networkx graph
    G = nx.Graph()
    G.add_edges_from(edges)

    # Compute Kamada-Kawai layout for 3D graphs
    pos = nx.fruchterman_reingold_layout(G, dim=3)

    # Extract node positions
    node_x = [pos[node][0] for node in nodes]
    node_y = [pos[node][1] for node in nodes]
    node_z = [pos[node][2] for node in nodes]

    # Create edges trace
    edge_x = []
    edge_y = []
    edge_z = []

    for edge in edges:
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]

    # Create figure
    fig = go.Figure()

    # Add edges trace
    fig.add_trace(go.Scatter3d(
        x=edge_x,
        y=edge_y,
        z=edge_z,
        mode='lines',
        line=dict(width=2, color='blue'),
        hoverinfo='none'
    ))

    # Add nodes trace
    fig.add_trace(go.Scatter3d(
        x=node_x,
        y=node_y,
        z=node_z,
        mode='markers',
        marker=dict(symbol='circle',
                    size=5,
                    color='red',
                    line=dict(color='black', width=0.5)),
        hovertext=list(adjusted_labels.values()),
        hoverinfo='text'
    ))

    # Update layout
    fig.update_layout(
        #title='3D Network Plot',
        #titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        scene=dict(
            xaxis_visible=False,  # Hide x-axis
            yaxis_visible=False,  # Hide y-axis
            zaxis_visible=False,  # Hide z-axis
            bgcolor='rgba(0,0,0,0)'  # Setting background color to transparent
        ),
        height=800,  # Customize height
    )

    return fig

#### Streamlit app ####
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# Show logo above navigation bar
add_logo()

# Customize navigation bar
show_pages([Page("app.py", "ASTRA", "🌌"), Page("pages/faq.py", "Frequently asked questions", "❓"), Page("pages/instructions.py", "Instructions", "📋"), Page("pages/contact-form.py", "Contact me", "✉️")])

# Sidebar top
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'logo.png')
#st.sidebar.image(IMAGE_PATH, use_column_width=True)

# Pre-process file github raw url for direct download
gedcom_file_url = "https://raw.githubusercontent.com/jlnetosci/astra/main/gedcom_files/genealogyoflife_tng/TolkienFamily.ged"
gedcom_file_content = requests.get(gedcom_file_url).content
gedcom_file_base64 = base64.b64encode(gedcom_file_content).decode("utf-8")

#download_link = f'<a href="data:text/plain;base64,{gedcom_file_base64}" download="TolkienFamily.ged">here</a>'

#instructions = st.sidebar.expander(label=r"$\textbf{\textsf{\normalsize Instructions}}$")

upload_gedcom = st.sidebar.expander(label=r"$\textbf{\textsf{\normalsize Add GEDCOM}}$")

uploaded_file = upload_gedcom.file_uploader("Upload a GEDCOM file", type=["ged"])

upload_gedcom.markdown(f'<a href="data:text/plain;base64,{gedcom_file_base64}" download="TolkienFamily.ged">Download example</a>', unsafe_allow_html=True)

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
        views_sb = views.selectbox(label="Select a view", options=["Classic (2D)", 
            "3D", 
            #"Map"
            ], index=0)

        #st.sidebar.header("Select an Individual")
        nodes_sorted = sorted(nodes)  # Sort nodes alphabetically
        
        if views_sb == "Classic (2D)":
            formating = st.sidebar.expander(label=r"$\textbf{\textsf{\normalsize Colors and highlight}}$", expanded=True)

            formating.markdown("**Color palette**")

            palettes = {
                "Classic": {
                    "default_background_color": "#222222",
                    "default_individual_color": "#FFFFFF",
                    "default_root_color": "#FF0051",
                    "default_ancestor_color": "#ffa500",
                    "default_hightlight_color": "#A679FF"
                },
                "Pastel": {
                    "default_background_color": "#fff0db",
                    "default_individual_color": "#eed9c4",
                    "default_root_color": "#f6a192",
                    "default_ancestor_color": "#C2DCF7",
                    "default_hightlight_color": "#B19CD8"
                },
                "Grayscale": {
                    "default_background_color": "#ffffff",
                    "default_individual_color": "#eeeeee",
                    "default_root_color": "#a3a3a3",
                    "default_ancestor_color": "#cccccc",
                    "default_hightlight_color": "#bbbbbb"
                },
                "Colorblind-friendly (Tol light)": {
                    "default_background_color": "#DDDDDD",
                    "default_individual_color": "#EEDD88",
                    "default_root_color": "#EE8866",
                    "default_ancestor_color": "#99DDFF",
                    "default_hightlight_color": "#FFAABB"
                }
            }

            palette = formating.selectbox(label="Select a color palette", options=list(palettes.keys()), index=0, key="palette")

            selected_palette = palettes.get(palette)
            if selected_palette:
                default_background_color = selected_palette["default_background_color"]
                default_individual_color = selected_palette["default_individual_color"]
                default_root_color = selected_palette["default_root_color"]
                default_ancestor_color = selected_palette["default_ancestor_color"]
                default_highlight_color = selected_palette["default_hightlight_color"]

            formating.markdown("""<hr style='margin-top:0em; margin-bottom:1em; border-width: 3px' /> """, unsafe_allow_html=True)

            formating.markdown("**Background**")

            selected_bg_color = formating.color_picker("Select color", default_background_color)

            formating.markdown("""<hr style='margin-top:0em; margin-bottom:1em; border-width: 3px' /> """, unsafe_allow_html=True)

            formating.markdown("**Individuals**")

            selected_base_node_color = formating.color_picker("Select color", default_individual_color)
            
            formating.markdown("""<hr style='margin-top:0em; margin-bottom:1em; border-width: 3px' /> """, unsafe_allow_html=True)

            formating.markdown("**Highlight individual**")
            
            root_sel = formating.checkbox(label="I want to select a root", value=True)
            if root_sel:
                default_index = next((i for i, node in enumerate(nodes_sorted) if re.search(r"\(I0*1\)", node)), 0)

                selected_individual = formating.selectbox(
                "Select an Individual as root",
                nodes_sorted,
                index=default_index
                )

                selected_root_color = formating.color_picker("Select color", default_root_color, key="selected_root_color")
                
                highlight_another_individual = formating.checkbox("Highlight another individual")

                if highlight_another_individual:
                    highlight_individual = formating.selectbox(
                        "Highlight individual",
                        [node for node in nodes_sorted if node != selected_individual],
                        index = next((i for i, node in enumerate([node for node in nodes_sorted if node != selected_individual]) if re.search(r"\(I0*2\)", node)), 0) if selected_individual == nodes_sorted[default_index] else default_index-1
                        )
                    selected_highlight_color = formating.color_picker("Select color", default_highlight_color, key="selected_highlight_color")
                
                else:
                    highlight_individual = None

                formating.markdown("""<hr style='margin-top:0em; margin-bottom:1em; border-width: 3px' /> """, unsafe_allow_html=True)

                formating.markdown("**Ancestors**")

                ancestors_sel = formating.checkbox(label="I want to highlight the root's direct ancestors", value=True)
                if ancestors_sel:
                    ancestors = get_ancestors(parser, translator, selected_individual)    
                    selected_ancestor_color = formating.color_picker("Select color", default_ancestor_color)
                else:
                    st.empty()
                    ancestors = None
           
            else:
                st.empty()
                selected_individual = None

            button_generate_network = st.sidebar.button("Generate Network", use_container_width=True, key="generate_network_button")

        if views_sb == "3D":
            # Plot the 3D network
            fig = plot_3d_network(nodes, edges, labels)
            st.plotly_chart(fig, use_container_width=True, height=800)

    #except ValueError as e:
    #    st.error(f'**Error:** {str(e)}')
    #    st.stop()

    except GedcomFormatViolationError:
        st.error("**Error:** The parser cannot process the GEDCOM file, possibly because of custom or unrecognized tags. This can probably be solved by using [Gramps](https://gramps-project.org/blog/download/) and re-exporting the file." )
        st.stop()

# Handle button click to generate network
if button_generate_network:
    #print("Button pressed to generate network!")

    info_ = st.sidebar.expander(label=r"$\textbf{\textsf{\normalsize ⓘ Info}}$", expanded=True)

    info_.markdown(""" <div style="text-align: justify;"> \n 
    <p> Please be patient while the network loads – time increases with the number of individuals and connections. </p>
    <p> After generation the network goes through a physics simulation to better distribute individuals. </p>
    <p> Individual nodes can also be moved to wield better separations. </p></div> """, unsafe_allow_html=True)

    with st.spinner('Processing data'):
        # Create the network visualization with selected colors
        if selected_individual is not None:
            args = {
                'individual': selected_individual,
                'individual_color': selected_root_color
            }
            
            if ancestors is not None:
                args['ancestors'] = ancestors
                args['ancestors_color'] = selected_ancestor_color
                
                node_color = color_nodes(nodes, selected_base_node_color, **args)

                if highlight_individual is not None:
                    args['highlight_individual'] = highlight_individual
                    args['highlight_individual_color'] = selected_highlight_color
                    node_color = color_nodes(nodes, selected_base_node_color, **args)

            if highlight_individual is not None:
                args['highlight_individual'] = highlight_individual
                args['highlight_individual_color'] = selected_highlight_color
                node_color = color_nodes(nodes, selected_base_node_color, **args)

            node_color = color_nodes(nodes, selected_base_node_color, **args)
        
        else:
            node_color = color_nodes(nodes, selected_base_node_color)

        adjusted_labels = {node: labels[node] for node in nodes if node in labels}

        network = create_network(
            nodes, adjusted_labels, node_color, edges, selected_bg_color, selected_individual
        )

    # Display the network HTML
    with open("gedcom.html", "r") as file:
        network_html = file.read()

    st.components.v1.html(network_html, height=800)

    # Centered download button with dynamic styles
    #st.markdown(
    #    """<div style="display: flex; justify-content: center;">
    #       <button onclick="location.href='data:text/html;base64,{}'" 
    #               style="padding: 10px; background-color: {}; color: {}; border: none; border-radius: 3px; cursor: pointer;">
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