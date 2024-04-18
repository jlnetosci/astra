#########################################################################
#                   STREAMLIT CONTACT FORM TEMPLATE                     #
# Version: 0.2.0                                                        #
# License: MIT License (https://opensource.org/license/mit/)            #
# Author: João L. Neto (https://github.com/jlnetosci/)                  #
# Release date: 2023-11-07                                              #
# Documentation: https://github.com/jlnetosci/streamlit-contact-form    #
# Credit is not mandatory, but it is kindly appreciated.                #
# For a subtle link to github you may just uncomment the last line.     #
#########################################################################

import streamlit as st
import smtplib
import random
import os
import time
import datetime
import base64

from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from captcha.image import ImageCaptcha
from io import BytesIO
from PIL import Image
from streamlit_js_eval import streamlit_js_eval

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

## Load secrets.toml variables
options = os.environ["OPTIONS"]
#options = "ABCDEF"
server = os.environ["SERVER"]
port = os.environ["PORT"]
u = os.environ["U"]
secret = os.environ["SECRET"]
recipient = os.environ["RECIPIENT"]

## Functions
def generate_captcha():
    captcha_text = "".join(random.choices(options, k=6)) # options is a string of characters that can be included in the CAPTCHA. It may be as simple or as complex as you wish. 
    image = ImageCaptcha(width=400, height=100).generate(captcha_text)
    return captcha_text, image

## Generate CAPTCHA
if 'captcha_text' not in st.session_state:
    st.session_state.captcha_text = generate_captcha()

captcha_text, captcha_image = st.session_state.captcha_text

## Contact Form

## Page configuration options
st.set_page_config(layout="wide", page_icon=favicon, initial_sidebar_state="expanded") # column widths set below are dependent on the layout being set to wide

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

st.header("📫 Contact Form")

col1, col2, col3, col4 =  st.columns([3, 0.25, 1, 0.25]) # column widths for a balanced distribution of elements in the page

captcha_input = None # initiate CAPTCHA

## CAPTCHA
with col3: # right side of the layout
    st.markdown('<p style="text-align: justify; font-size: 12px;">CAPTCHAs are active to prevent automated submissions. <br> Thank you for your understanding.</p>', unsafe_allow_html=True) # warning for user.
    captcha_placeholder = st.empty()
    captcha_placeholder.image(captcha_image, use_column_width=True)

    if st.button("Refresh", type="secondary", use_container_width=True): # option to refresh CAPTCHA without refreshing the page
        st.session_state.captcha_text = generate_captcha()
        captcha_text, captcha_image = st.session_state.captcha_text
        captcha_placeholder.image(captcha_image, use_column_width=True)

    captcha_input = st.text_input("Enter the CAPTCHA") # box to insert CAPTCHA

## Contact form
with col1: # left side of the layout
    email = st.text_input("**Your email***", value=st.session_state.get('email', ''), key='email') # input widget for contact email
    message = st.text_area("**Your message***", value=st.session_state.get('message', ''), key='message') # input widget for message

    st.markdown('<p style="font-size: 13px;">*Required fields</p>', unsafe_allow_html=True) # indication to user that both fields must be filled

    if st.button("Send", type="primary"):
        if not email or not message:
            st.error("Please fill out all required fields.") # error for any blank field
        else:
            try:
                # Robust email validation
                valid = validate_email(email, check_deliverability=True)

                # Check CAPTCHA
                if captcha_input.upper() == captcha_text:

                    # Email configuration - **IMPORTANT**: for security these details should be present in the "Secrets" section of Streamlit
                    #### NOTE FOR DEVELOPERS: UNCOMMENT THE LINES BELOW ####
                    
                    smtp_server = server
                    smtp_port = port
                    smtp_username = u
                    smtp_password = secret
                    recipient_email = recipient

                    ## Create an SMTP connection
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(smtp_username, smtp_password)

                    ## Compose the email message
                    subject = "ASTRAview Contact" # subject of the email you will receive upon contact.
                    body = f"Email: {email}\nMessage: {message}"
                    msg = MIMEMultipart()
                    msg['From'] = smtp_username
                    msg['To'] = recipient_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))

                    ## Send the email
                    server.sendmail(smtp_username, recipient_email, msg.as_string())

                    ## Send the confirmation email to the message sender # If you do not want to send a confirmation email leave this section commented
                    current_datetime = datetime.datetime.now()
                    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    confirmation_subject = f"Confirmation of Contact Form Submission ({formatted_datetime})"
                    confirmation_body = f"Thank you for contacting us! Your message has been received.\n\nYour message:\n {message}"
                    confirmation_msg = MIMEMultipart()
                    confirmation_msg['From'] = smtp_username
                    confirmation_msg['To'] = email  # Use the sender's email address here
                    confirmation_msg['Subject'] = confirmation_subject
                    confirmation_msg.attach(MIMEText(confirmation_body, 'plain'))
                    server.sendmail(smtp_username, email, confirmation_msg.as_string())

                    ## Close the SMTP server connection
                    server.quit()

                    st.success("Sent successfully!") # Success message to the user.
                    
                    #### NOTE FOR DEVELOPERS: UPON DEPLOYMENT DELETE THE SECTION BELOW ####
                    #st.info("""This would have been a message sent successfully!  
                    #For more information on activating the contact form, please check the [documentation](https://github.com/jlnetosci/streamlit-contact-form).""") # Please delete this info box if you have the contact form setup correctly.

                    # Generate a new captcha to prevent button spamming.
                    st.session_state.captcha_text = generate_captcha()
                    captcha_text, captcha_image = st.session_state.captcha_text
                    # Update the displayed captcha image
                    captcha_placeholder.image(captcha_image, use_column_width=True)

                    time.sleep(3)
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

                else:
                    st.error("Text does not match the CAPTCHA.") # error to the user in case CAPTCHA does not match input

            except EmailNotValidError as e:
                st.error(f"Invalid email address. {e}") # error in case any of the email validation checks have not passed

#st.markdown(f'<div style="position: fixed; bottom: 0; width: 100%; "><p style="text-align: left; color: #a3a0a3; margin-bottom: 28px; font-size: 11px;"><a href="https://github.com/jlnetosci/streamlit-contact-form" target="_blank" style="color: inherit;">Base template</a> by: <a href="https://github.com/jlnetosci" target="_blank" style="color: inherit;">João L. Neto</a></p></div>', unsafe_allow_html=True)
