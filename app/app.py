"""
ASTRA: GECOM VISUALIZATION

Author: João L. Neto
Contact: https://github.com/jlnetosci
Version: 0.1.1b
Last Updated: October 11, 2023

Description:
Accepts the upload of a GEDCOM file, parses it, and displays a "star map" like network visualization of the individuals. 
"""

import streamlit as st
import os
import re
import gedcom
from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement
from gedcom.element.family import FamilyElement
from itertools import combinations, product
from pyvis.network import Network

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

    # Initialize parser
    gedcom_parser = Parser()
    gedcom_parser.parse_file(temp_file_path, False)  # Use the default encoding

    # Remove the temporary GEDCOM file
    os.remove(temp_file_path)
    
    return gedcom_parser
    
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
    
    for element in root_child_elements: #elements that are individual of family
        if isinstance(element, IndividualElement): #in elements that are individuals
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

# Sidebar to upload GEDCOM file and select colors
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'logo.png')

st.sidebar.image(IMAGE_PATH, use_column_width=True)

uploaded_file = st.sidebar.file_uploader("Upload a GEDCOM file", type=["ged", "gedcom"])

# Color pickers for customization
selected_bg_color = st.sidebar.color_picker("Select Background Color", "#222222")
selected_base_node_color = st.sidebar.color_picker("Select general node color", "#FFFFFF")
selected_ancestor_color = st.sidebar.color_picker("Select ancestor node color", "#ffa500")
selected_root_color = st.sidebar.color_picker("Select root node color", "#FF0051")

button_generate_network = None  # Initialize the button variable

# Dropdown menu for selecting an individual
if uploaded_file is not None:
    parser = parse_gedcom(uploaded_file)

    translator, nodes, labels, edges = process_gedcom(parser)

    #st.sidebar.header("Select an Individual")
    nodes_sorted = sorted(nodes)  # Sort nodes alphabetically
    selected_individual = st.sidebar.selectbox(
        "Select an Individual as root", nodes_sorted, index=next((i for i, node in enumerate(nodes_sorted) if "(I1)" in node), 0)
    )

    ancestors = get_ancestors(parser, translator, selected_individual)    

    if selected_individual:
        button_generate_network = st.sidebar.button("Generate Network", key="generate_network_button")

# Handle button click to generate network
if button_generate_network and selected_individual:
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

st.sidebar.markdown(""" **Instructions:** <div style="text-align: justify;"> \n 
1. Upload a GEDCOM file (example [here](https://github.com/jlnetosci/astra/blob/main/gedcom_files/genealogyoflife_tng/RomanGods.ged)).  
2. Select your root individual.  
3. Choose the colors of your preference.  
4. Click 'Generate Network'. \n 
Please be patient while the network loads – time increases with the number of individuals and connections.  
After generation the network goes through a physics simulation to better distribute nodes.  
Nodes can also be moved to wield better separations. </div> \n 
**Author:** [João L. Neto](https://github.com/jlnetosci)""", unsafe_allow_html=True)

st.sidebar.markdown(""" <div style="text-align: right;"><b>v0.1.1b</b></div>""", unsafe_allow_html=True)
