import openai
import json
import os
import requests
from datetime import datetime
from colorama import Fore, Style

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
    print("Status Code:", response.status_code)
    # Check if the response content is not empty before parsing as JSON
    if response.text.strip():  # Check if the response body is not empty
        try:
            print("Response Body:", response.json())
        except ValueError as e:
            print("Raw Response Content:", response.text)
    else:
        print("Response Body is empty.")

def get_bullying_incidents():
    url = "http://172.232.185.245:3000/incidents"
    response = requests.get(url)
    print("Status Code:", response.status_code)
    print("Response Body:", response.json())
    return response.json()

def get_cheating_incidents():
    url = "http://172.232.185.245:3000/incidents"
    response = requests.get(url)
    print("Status Code:", response.status_code)
    print("Response Body:", response.json())
    return response.json()

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
    print("Status Code:", response.status_code)
    # Check if the response content is not empty before parsing as JSON
    if response.text.strip():  # Check if the response body is not empty
        try:
            print("Response Body:", response.json())
        except ValueError as e:
            print("Raw Response Content:", response.text)
    else:
        print("Response Body is empty.")

# Function to handle OpenAI function calls
def function_call(ai_response):
    function_call = ai_response.choices[0].message.function_call
    function_name = function_call.name
    arguments = json.loads(function_call.arguments)

    if function_name == "get_cheating_incidents":
        return get_cheating_incidents()
    elif function_name == "get_bullying_incidents":
        return get_bullying_incidents()
    elif function_name == "report_cheating_incident":
        name = arguments.get("name")
        email = arguments.get("email")
        incident_summary = arguments.get("incident_summary")
        return report_cheating_incident(name, email, incident_summary)
    elif function_name == "report_bullying_incident":
        name = arguments.get("name")
        email = arguments.get("email")
        incident_summary = arguments.get("incident_summary")
        return report_bullying_incident(name, email, incident_summary)
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

        # Format the response for better readability
        print(Fore.GREEN + f"\n=== Cheating Incidents Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===" + Style.RESET_ALL)
        print(assistant_response)
        print(Fore.GREEN + "=================================" + Style.RESET_ALL + "\n")

# Test queries

#1. Trigger get_cheating_incidents:
# This query will fetch all cheating incidents.
user_query = "Can you get me the latest cheating incidents?"

# 2. Trigger get_bullying_incidents:
# This query will fetch all bullying incidents. Note that the performanceId parameter is not used in the get_bullying_incidents function in the code, so you can omit it.
#user_query = "Can you retrieve all bullying incidents?"

# 3. Trigger report_cheating_incident:
# This query will report a cheating incident. Replace the placeholders with appropriate values.
#user_query = "Report a cheating incident for student John Doe with email 'john.doe@example.com' and incident summary 'John was caught cheating during the math exam.'"

# 4. Trigger report_bullying_incident:
# This query will report a bullying incident. Replace the placeholders with appropriate values.
#user_query = "Report a bullying incident for student Jane Smith with email 'jane.smith@example.com' and incident summary 'Jane was bullied during recess.'"

# 5. Mixed Query:
# You can also test a mixed query to see how the program handles multiple function calls or ambiguous requests.
#user_query = "Can you get me the latest cheating incidents and also report a bullying incident for student Alex Brown with email 'alex.brown@example.com' and incident summary 'Alex was bullied in the hallway.'"

ask_function_calling(user_query)
