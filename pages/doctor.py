import streamlit as st
import requests

# Function to summarize text using pipeline
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


# Function to display page 2 content
def show(chat_history):
    st.title('Doctor dashboard - Patient record summary')

    st.subheader('ข้อมูลคนไข้:')
    #st.write(chat_history)

    # Retrieve chat_history from session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = ""

    if st.button("Generate Summary"):
        if not chat_history:
            st.warning("Please generate chat history on Page 1 first.")
        else:
            #summary = summarize_data(st.session_state.chat_history["patient_id_1"])
            summary = """Summary of follow-up data for แห้วซัง:
Date: 2024-06-23
 - ไข้: ไม่มี
 - ไอ: เล็กน้อย
 - เหนื่อยหอบ: ไม่มี
Additional Information: ไม่มี
"""
            st.subheader('Summary:')
            st.write(summary)

    return st.session_state.chat_history
