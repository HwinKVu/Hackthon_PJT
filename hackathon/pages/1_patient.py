import requests
import streamlit as st
import toml
import yaml 
from datetime import date, datetime, timedelta

st.set_page_config(page_title="Patient")

secrets = toml.load("./streamlit/secrets.toml")
url = 'https://api.opentyphoon.ai/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {secrets["TYPHOON_API_KEY"]}'
}

#initialize patient data
st.session_state.patient_record = {
    "patient_id_1" : {
        "id": 1,
        "name": "แห้วซัง",
        "visit_date": "2024-07-06",
        "follow_up_date": "2024-07-20",
        "symptoms": ["ไข้", "ไอ","เหนื่อยหอบ"],  # Raw user input for symptoms
        "daily_responses": []  # Initialized as an empty list for system responses
    },
}

patient = st.session_state.patient_record["patient_id_1"]
#days_post_visit = "1"
today_date = date.today()
#today_date = date.today()+timedelta(1)
visit_date = datetime.strptime(patient["visit_date"], "%Y-%m-%d").date()
days_post_visit = (today_date - visit_date).days

##greeting

def generate_dynamic_greeting(patient, days_post_visit):

    prompt = f"ผู้ป่วยมาแผนกผู้ป่วยนอกด้วยอาการ{', '.join(patient['symptoms'])} เมื่อวันที่ {patient['visit_date']} และมีนัดหมายวันที่ {patient['follow_up_date']} วันนี้เป็นวันที่{days_post_visit}หลังพบแพทย์ โปรดสร้างประโยคทักทายเพื่อส่งเสริมให้ผู้ป่วยรายนี้ให้ความร่วมมือในการติดตามผลการรักษา กรุณาระบุว่าวันนี้เป็นวันที่เท่าไหร่หลังการรักษาด้วย ไม่ต้องระบุว่ามาพบแพทย์วันไหนและนัดวันไหน คุณเป็นผู้หญิง"
        
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

##end of greeting

##symptom

def generate_dynamic_question(symptom):
    prompt = f"สร้างประโยคคำถามเพื่อถามผู้ป่วยถึงอาการ'{symptom}'ในปัจจุบัน คำถามไม่ต้องละเอียดมาก กรุณาใช้เสียงผู้หญิงในการถาม"
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

##end of symptom

##additional

def generate_additional_info_prompt():
    prompt = "สร้างประโยคคำถามเพื่อถามว่ามีสิ่งใดต้องการแจ้งแพทย์อีกหรือไม่ คุณเป็นผู้หญิง"
    data_addi = {
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
      "temperature": 0.5,
      "top_p": 1,
      "top_k": 50,
      "repetition_penalty": 1.15,
      "stream": False
      }
    response = requests.post(url, headers=headers, json=data_addi)
    result = response.json()
    content = result['choices'][0]['message']['content']
    return(content)
##end of additional

if "key" not in st.session_state:
    st.session_state.key = 0

if 'chat_ended' not in st.session_state:
    st.session_state.chat_ended = False


if "messages" not in st.session_state:
    st.session_state.messages = [] 
    st.session_state.messages.append({
       "role": "assistant", 
       "content": generate_dynamic_greeting(patient, days_post_visit)
       })
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
       st.markdown(message["content"]) 
if not st.session_state.chat_ended:
    if pt_input := st.chat_input("ここに入力してください"):
        st.session_state.messages.append({"role": "user", "content": pt_input})
        with st.chat_message('user'):
            st.markdown(pt_input)
            
        if st.session_state.key < len(patient["symptoms"]):
            response = generate_dynamic_question(patient["symptoms"][st.session_state.key])
        if st.session_state.key == len(patient["symptoms"]):
            response = generate_additional_info_prompt()
        if st.session_state.key == len(patient["symptoms"])+1:
            st.session_state.chat_ended = True


        if not st.session_state.chat_ended:
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.key += 1

if st.session_state.chat_ended:
    with st.chat_message("assistant"):
        st.markdown("Thank you for your response, See ya!")
    st.write("Chat has ended. No more input is allowed.")

st.session_state.chat_history = st.session_state.messages