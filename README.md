# ASTRA

<p align="center">
  <img src="/app/logo.png" width="300px" height="135px">
</p>

## About
<p align="justify">
[ASTRA](https://astraviz.streamlit.app/) is a web app that displays a "star map" like network visualization of the individuals in a GEDCOM file. Powered by [python-gedcom](https://github.com/nickreynke/python-gedcom), [pyvis](https://pyvis.readthedocs.io/) and [streamlit](https://streamlit.io/).

**Instructions:** \n 
1. Upload a GEDCOM file (example [here](https://github.com/jlnetosci/astra/gedcom_files/genealogyoflife_tng/RomanGods.ged)).  
2. Select your root individual.  
3. Choose the colors of your preference.  
4. Click 'Generate Network'. \n 
Please be patient while the network loads – time increases with the number of individuals and connections.  
After generation the network goes through a physics simulation.  
Nodes can also be moved to wield better separations. \n 
</p>

# Examples

<div style="display: flex; flex-wrap: wrap;">
  <div style="flex: 50%; padding: 10px;">
    <img src="img/starmap.jpg" style="width: 400px;">
  </div>
  <div style="flex: 50%; padding: 10px;">
    <img src="img/light.jpg" style="width: 400px;">
  </div>
  <div style="flex: 50%; padding: 10px;">
    <img src="img/soft.jpg" style="width: 400px;">
  </div>
  <div style="flex: 50%; padding: 10px;">
    <img src="img/zoom.jpg" style="width: 400px;">
  </div>
</div>

# 🐳 Dockerfile

A local instance of this app can be run using Docker ([download](https://docs.docker.com/get-docker/), [installation](https://docs.docker.com/engine/install/)).

Usage example:

1.  Pull the image from dockerhub, with `docker pull jlnetosci/astra:v0.1.0b`.
2.  Run `docker run -p 8501:8501 jlnetosci/astra:0.1.0b` to start the application.
3.  Open `http://localhost:8501/` in your browser.

The fully functional app should be available in your local machine.
