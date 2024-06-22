import streamlit as st
import requests

# Function to summarize text using pipeline
def summarize_chat_history(chat_history):
    url = 'https://api.opentyphoon.ai/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer YOUR_TYPHOON_API_KEY'  # Replace with your Typhoon API key
    }

    # Prepare messages in the required format for Typhoon API
    full_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. You must summarize the input only in Thai."
        },
        {
            "role": "user",
            "content": chat_history
        }
    ]

    data = {
        "model": "typhoon-instruct",
        "messages": full_messages,
        "max_tokens": 150,  # Adjust max_tokens as needed
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 50,
        "repetition_penalty": 1.15,
        "stream": False
    }

    # Send request to Typhoon LLM API
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    message_content = result['choices'][0]['message']['content']
    return message_content


# Function to display page 2 content
def show(chat_history):
    st.title('Doctor dashboard - Patient record summary')

    st.subheader('Chat History:')
    st.write(chat_history)

    # Retrieve chat_history from session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = ""

    if st.button("Generate Summary"):
        if not chat_history:
            st.warning("Please generate chat history on Page 1 first.")
        else:
            summary = summarize_chat_history(chat_history)
            st.subheader('Summary:')
            st.write(summary)
