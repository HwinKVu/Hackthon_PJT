import requests
import streamlit as st
import toml
import yaml 
from datetime import date, datetime, timedelta

st.set_page_config(page_title="Doctor")


secrets = toml.load("./streamlit/secrets.toml")
url = 'https://api.opentyphoon.ai/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {secrets["TYPHOON_API_KEY"]}'
}

def summarize(conversation):
    prompt = f"{conversation} \nจากบทสนทนาดังกล่าว จงสรุปอาการปัจจุบันของผู้ป่วยดังกล่าว"
    data_symp = {
      "model": "typhoon-instruct",
      "messages": [
          {
              "role": "system",
              "content": "You are a helpful assistant. You must answer only in Thai.  You are female."
          },
          {
              "role": "user",
              "content": prompt
          }
          ],
      "max_tokens": 500,
      "temperature": 0.3,
      "top_p": 1,
      "top_k": 50,
      "repetition_penalty": 1.15,
      "stream": False
      }
    response = requests.post(url, headers=headers, json=data_symp)
    result = response.json()
    content = result['choices'][0]['message']['content']
    return(content)


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = ""

if st.button("Generate Summary"):
    if not st.session_state.chat_history :
        st.warning("Please generate chat history first.")
    else:
        st.write(st.session_state.chat_history)
        st.session_state.conversation = "\n".join(
            f"  \n{'patient' if item['role'] == 'user' else item['role']} - {item['content']}" for i, item in enumerate(st.session_state.chat_history)
            )
        st.write(st.session_state.conversation)
        summary = summarize(st.session_state.conversation)
        st.session_state.summary = summary
        
if "summary" in st.session_state:
    st.write(date.today())
    st.write(st.session_state.summary)