from openai import OpenAI
import yaml
from typing import List
import os


# Initialize the OpenAI client with your API key
client = OpenAI()

def load_openapi_definition(file_path: str) -> dict:
    # Load the OpenAPI definition from the YAML file
    with open(file_path, 'r') as file:
        openapi_definition = yaml.safe_load(file)
    return openapi_definition

def suggest_resource(input_message: str, openapi_definition: dict) -> str:
    # Extract resource details from the OpenAPI definition
    resources_details = []
    for path, info in openapi_definition['paths'].items():
        for method, details in info.items():
            summary = details.get('summary', 'No summary available')
            description = details.get('description', 'No description available')
            example_request = details.get('requestBody', {}).get('content', {}).get('application/json', {}).get('example', 'No example request available')
            example_response = next(iter(details.get('responses', {}).values()), {}).get('content', {}).get('application/json', {}).get('example', 'No example response available')
            resources_details.append(f"Path: {path}\nMethod: {method.upper()}\nSummary: {summary}\nDescription: {description}\nExample Request: {example_request}\nExample Response: {example_response}")

    # Concatenate all resource details for the context
    resources_context = "\n\n".join(resources_details)

    # Prepare the prompt with detailed context
    prompt = f"Given the following API resources and their details:\n\n{resources_context}\n\nSuggest the most appropriate OpenAPI resource to call for the input: '{input_message}'."

    # Generate the completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that understands API resources."},
            {"role": "user", "content": prompt}
        ]
    )

    suggested_resource = extract_suggestion(response.choices[0].message.content.strip(), [path.strip('/') for path in openapi_definition['paths'].keys()])
    return suggested_resource

def extract_suggestion(gpt_response: str, resources: List[str]) -> str:
    # Here, you might need to improve the logic to better match the GPT response with your resources list
    # For simplicity, this function returns the response directly
    return gpt_response


def extract_suggestion(gpt_response: str, resources: List[str]) -> str:
    # Extract the suggested resource from GPT-3 response
    # Add additional logic here if necessary for matching the response to your resources
    return gpt_response

def main():
    openapi_file_path = "middleware/airline_api.openapi.yaml"
    openapi_definition = load_openapi_definition(openapi_file_path)

    while True:
        input_message = input(f"\n[Middlware Assistant] Please enter your message (or type 'quit' to exit):\n")
        if input_message.lower() == 'quit':
            break
        suggested_resource = suggest_resource(input_message, openapi_definition)
        print(f"\n\nAnswer:\n {suggested_resource}")


if __name__ == "__main__":
    main()