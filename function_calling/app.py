import openai
import json
import os
import requests
import streamlit as st

# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function descriptions
function_descriptions = [
    {
        "name": "get_cheating_incidents",
        "description": "Get cheating reports on all occasions, e.g. tests, exams, homeworks, etc.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_bullying_incidents",
        "description": "Get bullying incidents",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "report_cheating_incident",
        "description": "Add a cheating incident to reporting database",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "name of student reporting the incident"
                },
                "email": {
                    "type": "string",
                    "description": "email of student reporting the incident"
                },
                "incident_summary": {
                    "type": "string",
                    "description": "summary of the incident"
                },
                "incident_type": {
                    "type": "string",
                    "description": "type of the incident, e.g., cheating, bullying, others",
                    "enum": ["cheating", "bullying", "others"]
                }
            },
            "required": ["name", "email", "incident_summary"]
        }
    },
    {
        "name": "report_bullying_incident",
        "description": "Add a bullying incident to reporting database",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "name of student reporting the incident"
                },
                "email": {
                    "type": "string",
                    "description": "email of student reporting the incident"
                },
                "incident_summary": {
                    "type": "string",
                    "description": "summary of the incident"
                },
                "incident_type": {
                    "type": "string",
                    "description": "type of the incident, e.g., cheating, bullying, others",
                    "enum": ["cheating", "bullying", "others"]
                }
            },
            "required": ["name", "email", "incident_summary"]
        }
    }
]

# Functions to handle incidents
def report_cheating_incident(name, email, incident_summary):
    url = "http://172.232.185.245:3000/incidents"
    payload = {
        "name": name,
        "email": email,
        "incident_summary": incident_summary,
        "incident_type": "cheating"  # Set incident_type to "cheating"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response

def get_bullying_incidents():
    url = "http://172.232.185.245:3000/incidents"
    response = requests.get(url)
    return response

def get_cheating_incidents():
    url = "http://172.232.185.245:3000/incidents"
    response = requests.get(url)
    return response

def report_bullying_incident(name, email, incident_summary):
    url = "http://172.232.185.245:3000/incidents"
    payload = {
        "name": name,
        "email": email,
        "incident_summary": incident_summary,
        "incident_type": "bullying"  # Set incident_type to "bullying"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response

# Function to handle OpenAI function calls
def function_call(ai_response):
    function_call = ai_response.choices[0].message.function_call
    function_name = function_call.name
    arguments = json.loads(function_call.arguments)

    if function_name == "get_cheating_incidents":
        response = get_cheating_incidents()
        return response.json()
    elif function_name == "get_bullying_incidents":
        response = get_bullying_incidents()
        return response.json()
    elif function_name == "report_cheating_incident":
        name = arguments.get("name")
        email = arguments.get("email")
        incident_summary = arguments.get("incident_summary")
        response = report_cheating_incident(name, email, incident_summary)
        return f"Incident reported successfully. Status Code: {response.status_code}"
    elif function_name == "report_bullying_incident":
        name = arguments.get("name")
        email = arguments.get("email")
        incident_summary = arguments.get("incident_summary")
        response = report_bullying_incident(name, email, incident_summary)
        return f"Incident reported successfully. Status Code: {response.status_code}"
    else:
        return None

# Function to handle user queries
def ask_function_calling(query):
    messages = [{"role": "user", "content": query}]

    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        functions=function_descriptions,
        function_call="auto"
    )

    # Handle the initial response
    if response.choices[0].finish_reason == "function_call":
        function_response = function_call(response)
        messages.append({
            "role": "function",
            "name": response.choices[0].message.function_call.name,
            "content": json.dumps(function_response)
        })

        # Send the updated messages back to the API
        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=messages,
            functions=function_descriptions,
            function_call="auto"
        )

    # Extract and format the assistant's response content
    if response.choices[0].finish_reason == "stop":
        assistant_response = response.choices[0].message.content
        return assistant_response

# Streamlit App
def main():
    st.title("Incident Reporting System")

    # Sidebar for options
    st.sidebar.header("Options")
    option = st.sidebar.selectbox(
        "What would you like to do?",
        ("Chatbot Mode", "Get Cheating Incidents", "Get Bullying Incidents", "Report Cheating Incident", "Report Bullying Incident")
    )

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chatbot Mode
    if option == "Chatbot Mode":
        st.write("Chatbot Mode: Type your query below.")
        user_input = st.chat_input("Type your message here...")
        if user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Get assistant response
            assistant_response = ask_function_calling(user_input)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)

    # Specific actions
    elif option == "Get Cheating Incidents":
        st.write("Fetching cheating incidents...")
        response = get_cheating_incidents()
        st.write("Status Code:", response.status_code)
        st.write("Response Body:", response.json())
    elif option == "Get Bullying Incidents":
        st.write("Fetching bullying incidents...")
        response = get_bullying_incidents()
        st.write("Status Code:", response.status_code)
        st.write("Response Body:", response.json())
    elif option == "Report Cheating Incident":
        st.write("Report a cheating incident:")
        name = st.text_input("Name")
        email = st.text_input("Email")
        incident_summary = st.text_area("Incident Summary")
        if st.button("Submit"):
            response = report_cheating_incident(name, email, incident_summary)
            st.write("Status Code:", response.status_code)
            st.write("Response Body:", response.text)
    elif option == "Report Bullying Incident":
        st.write("Report a bullying incident:")
        name = st.text_input("Name")
        email = st.text_input("Email")
        incident_summary = st.text_area("Incident Summary")
        if st.button("Submit"):
            response = report_bullying_incident(name, email, incident_summary)
            st.write("Status Code:", response.status_code)
            st.write("Response Body:", response.text)

    # Display chat history in the main area
    st.write("### Conversation History")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Run the Streamlit app
if __name__ == "__main__":
    main()
