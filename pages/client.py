import requests
import streamlit as st
# from streamlit_chat import message
import toml
import yaml 
from datetime import date, datetime, timedelta

# Load secrets and config
secrets = toml.load("./streamlit/secrets.toml")
with open('./config.yml', 'r') as file:
    config = yaml.safe_load(file)
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
        "visit_date": "2024-06-21",
        "follow_up_date": "2024-06-28",
        "symptoms": ["ไข้", "ไอ","เหนื่อยหอบ"],  # Raw user input for symptoms
        "daily_responses": []  # Initialized as an empty list for system responses
    },
}
days_post_visit = "1"

#def submitted():
#    st.session_state.submitted = True

# Generating responses from the Typhoon API
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

def generate_dynamic_question(symptom):
    prompt = f"สร้างประโยคคำถามเพื่อถามผู้ป่วยถึงอาการ'{symptom}'ในปัจจุบัน คำถามไม่ต้องละเอียดมาก คุณเป็นผู้หญิง"
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

def daily_interaction_with_ai(patient):
    today_date = date.today()
    #today_date = date.today()+timedelta(1)
    visit_date = datetime.strptime(patient["visit_date"], "%Y-%m-%d").date()
    days_post_visit = (today_date - visit_date).days

    greeting = generate_dynamic_greeting(patient, days_post_visit)
    with st.chat_message("assistant"):
            st.markdown(greeting)
    st.session_state.messages.append({"role": "assistant", "content": greeting})

    # Initialize responses dictionary
    if "responses" not in st.session_state:
            st.session_state.responses = {}

    # Sequentially ask questions and collect responses
    responses = {}
    with st.form(key='questions_form'):
        for symptom in patient["symptoms"]:
            question = generate_dynamic_question(symptom)
            response = st.text_input(label=question, key=f"{symptom}_response")
            responses[symptom] = response
            st.session_state.messages.append({"role": "assistant", "content": question})

        additional_info_prompt = generate_additional_info_prompt()
        additional_info_response = st.text_area(label=additional_info_prompt, key="additional_info_response")
        responses["additional_info_response"] = additional_info_response
        st.session_state.messages.append({"role": "assistant", "content": additional_info_prompt})
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
             # Store daily responses in patient's record
            patient["daily_responses"].append({
                "date": today_date.isoformat(),
                "responses": responses
            })

            st.write("### Response Recorded Successfully!")
            with st.chat_message("assistant"):
                st.markdown("ขอบคุณที่ให้ข้อมูลกับพวกเรา")
            st.session_state.messages.append({"role": "assistant", "content": "ขอบคุณที่ให้ข้อมูลกับพวกเรา"})


# Summarize data for each patient
def summarize_data(patient):
    summary = f"Summary of follow-up data for {patient['name']}:\n"
    for day_response in patient["daily_responses"]:
        summary += f"\nDate: {day_response['date']}\n"
        for symptom, response in day_response["responses"].items():
            if symptom != "additional_info":
                summary += f" - {symptom.capitalize()}: {response}\n"
        summary += f"Additional Information: {day_response['responses']['additional_info']}\n"
    return summary


def show():
    # Load secrets and config
    secrets = toml.load("./streamlit/secrets.toml")
    with open('./config.yml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [] 
        st.session_state.messages.append({
            "role": "assistant", 
            "content": config['streamlit']['assistant_intro_message']
        })


    # if "record" not in st.session_state:
    #    st.session_state.record = {}
    #    st.session_state.record["id"] = 1
    #    st.session_state.record["visit_date"] = date.today().isoformat()
    #    st.session_state.record["symptoms"] = []
    #    st.session_state.record["id"] = []

    st.title("บอต(สุขภาพ)น้อย")


    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])  

    # React to user input
    if prompt := st.chat_input("Send a message"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.patient_record["patient_id_1"]["daily_responses"].append({"role": "user", "content": prompt, "date": date.today().isoformat()})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Run daily interaction for each patient
        daily_interaction_with_ai(st.session_state.patient_record["patient_id_1"])
        #with st.chat_message("assistant"):
            #st.markdown(response)
        # Add assistant response to chat history
        #st.session_state.messages.append({"role": "assistant", "content": response})
        
    # summarize history in session state before returning
    st.session_state.chat_history = st.session_state.patient_record
    return st.session_state.chat_history