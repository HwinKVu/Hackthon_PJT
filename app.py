import streamlit as st
from pages import client, doctor # Replace with your actual module names

# Define a shared variable to store chat history
chat_history = ""

# Sidebar navigation
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", ['Patient', 'Doctor'])

# Display the selected page
if selection == 'Patient':
    st.session_state.chat_history = client.show()
elif selection == 'Doctor':
    chat_history = doctor.show(chat_history)

st.state.sync()