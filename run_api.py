from openai import OpenAI
import yaml
import requests
from typing import List, Tuple, Optional, Dict
import json

# Initialize the OpenAI client with your API key
client = OpenAI()

def load_openapi_definition(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        openapi_definition = yaml.safe_load(file)
    return openapi_definition

def suggest_resources(input_message: str, openapi_definition: dict) -> dict:
    resources_details = []
    for path, info in openapi_definition['paths'].items():
        for method, details in info.items():
            summary = details.get('summary', '')
            description = details.get('description', '')
            example_request = details.get('requestBody', {}).get('content', {}).get('application/json', {}).get('example', '{}')
            example_response = next(iter(details.get('responses', {}).values()), {}).get('content', {}).get('application/json', {}).get('example', '{}')
            resources_details.append(f"Path: {path}\nMethod: {method.upper()}\nSummary: {summary}\nDescription: {description}\nExample Request: {example_request}\nExample Response: {example_response}")

    resources_context = "\n\n".join(resources_details)
    prompt = f"Given the following API resources and their details:\n\n{resources_context}\n\nSuggest the most appropriate OpenAPI resource to call for the input: '{input_message}'."
    formatting = """give the result as json with the following format, replace fields between < > with the relevant data.
    {
    "suggestion": "<suggestion text>",
    "resources": [
        {
        "resource": "<resource>",
        "method": "<method>",
        "input_parameters": <parameters as object>
        }
    ]
    }
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that understands API resources."},
            {"role": "user", "content": prompt + formatting}
        ]
    )

    json_data = response.choices[0].message.content.strip()
    parsed_data = json.loads(json_data)

    return parsed_data

def execute_api_call(base_url: str, api_details: Dict) -> dict:
    resource = api_details.get('resource', '')
    method = api_details.get('method', '').lower()
    input_parameters = api_details.get('input_parameters', {})
    url = f"{base_url}{resource}"

    if method == 'get':
        response = requests.get(url, params=input_parameters)
    elif method == 'post':
        response = requests.post(url, json=input_parameters)
    else:
        return {"error": "Unsupported method or invalid API details."}

    try:
        return response.json()
    except ValueError:
        return {"error": "Failed to decode response.", "status_code": response.status_code}


def main():
    openapi_file_path = "airline_api.openapi.yaml"
    openapi_definition = load_openapi_definition(openapi_file_path)
    base_url = "http://127.0.0.1:5000"

    while True:
        input_message = input("\n[Middlware Assistant] Please enter your message (or type 'quit' to exit):\n")
        if input_message.lower() == 'quit':
            break

        suggestion_data = suggest_resources(input_message, openapi_definition)
        
        print(f"\nSuggestion:\n {suggestion_data['suggestion']}")
        
        resource = suggestion_data['resources'][0]

        if resource:
            response = execute_api_call(base_url, resource)
            print("\nAPI Response:\n", json.dumps(response, indent=2))
        else:
            print("\nCould not determine an appropriate API call based on the input.")

if __name__ == "__main__":
    main()
