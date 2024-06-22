import requests
import streamlit as st
# from streamlit_chat import message
import toml
import yaml 

def show():
    # Load secrets and config
    secrets = toml.load("secrets.toml")
    with open('./config.yml', 'r') as file:
        config = yaml.safe_load(file)

    # Generating responses from the Typhoon API
    def generate_response(prompt):
        url = 'https://api.opentyphoon.ai/v1/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {secrets["TYPHOON_API_KEY"]}'
        }
        
        full_messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. You must answer only in Thai."
            },
            {
                "role": "user",
                "content": prompt
            }
        ] + st.session_state.messages

        data = {
            "model": "typhoon-instruct",
            "messages": full_messages,
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 50,
            "repetition_penalty": 1.15,
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        message_content = result['choices'][0]['message']['content']
        return message_content

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [] 
        st.session_state.messages.append({
            "role": "assistant", 
            "content": config['streamlit']['assistant_intro_message']
            })
        
    st.title("บอต(สุขภาพ)น้อย")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Send a message"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Get bot response    
        response = generate_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        chat_history = st.session_state.messages

    return chat_history