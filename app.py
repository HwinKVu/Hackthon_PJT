import streamlit as st
from pages import client, doctor # Replace with your actual module names

import logging
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='streamlit.log',
    filemode='a'
)

# Define a shared variable to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = "" 

# Sidebar navigation
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", ['Patient', 'Doctor'])

# Display the selected page
if selection == 'Patient':
    st.session_state.chat_history = client.show()
elif selection == 'Doctor':
    st.session_state.chat_history = doctor.show(st.session_state.chat_history)

