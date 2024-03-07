import json
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
import yaml
import pprint

GPT_MODEL = "gpt-3.5-turbo"
client = OpenAI()

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


def openapi_to_tools(yaml_definition):
    with open(yaml_definition, 'r') as file:
        openapi_data = yaml.safe_load(file)
    
    tools = []
    for path, methods in openapi_data['paths'].items():
        for http_method, details in methods.items():
            tool_function = {
                "type": "function",
                "function": {
                    "name": details.get("operationId", details['summary'].lower().replace(" ", "_")),
                    "description": details['description'],
                    "parameters": {},
                    # "returns": {}
                }
            }
            if 'requestBody' in details:
                tool_function['function']['parameters'] = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
                for content_type, content in details['requestBody']['content'].items():
                    for prop, prop_details in content['schema']['properties'].items():
                        tool_function['function']['parameters']['properties'][prop] = {
                            "type": prop_details.get('type')
                        }
                        if prop_details.get('description'):
                            tool_function['function']['parameters']['properties'][prop]['description'] = prop_details['description']
                        if 'required' in content['schema'] and prop in content['schema']['required']:
                            tool_function['function']['parameters']['required'].append(prop)

            # responses = details.get('responses', {})
            # success_response = responses.get('200', {}) or responses.get('201', {})
            # if success_response:
            #     tool_function['function']['returns'] = {
            #         "type": "object",
            #         "properties": {}
            #     }
            #     content = next(iter(success_response['content'].values()))
            #     if 'schema' in content:
            #         schema = content['schema']
            #         if 'properties' in schema:
            #             for prop, prop_details in schema['properties'].items():
            #                 tool_function['function']['returns']['properties'][prop] = {
            #                     "type": prop_details.get('type')
            #                 }
            #                 if prop_details.get('description'):
            #                     tool_function['function']['returns']['properties'][prop]['description'] = prop_details['description']

            tools.append(tool_function)
    
    return tools

def main():
    openapi_file_path = "middleware/airline_api.openapi.yaml"
    tool_object = openapi_to_tools(openapi_file_path)
    # Assuming you have an object named 'obj'
    pprint.pprint(tool_object)

    # tool_object = [{
    #         'function': {
    #             'description': 'Retrieve the upcoming flight schedule.',
    #             'name': 'flight_schedule',
    #             'parameters': {}
    #         },
    #         'type': 'function'
    #     },
    #     {
    #         'function': {
    #             'description': 'Send notifications to passengers about flight updates.',
    #             'name': 'passenger_notifications',
    #             'parameters': {
    #                 'type': 'object',
    #                 'properties': {
    #                     'passenger_email': { 'type': 'string' },
    #                     'flight_number': { 'type': 'string' },
    #                     'notification': { 'type': 'string' }
    #                 },                    
    #             },
    #             'required': ['reservation','flight_number'],
    #         },
    #         'type': 'function'
    #     },
    #     {
    #         'function': {
    #             'description': 'Book a flight for a passenger.',
    #             'name': 'book_a_flight',
    #             'parameters': {
    #                 'type': 'object',
    #                 'properties': {
    #                     'flight_number': { 'type': 'string' },
    #                     'passenger_name': { 'type': 'string' },
    #                     'seat_preference': { 'type': 'string' }
    #                 },
    #             },
    #             'required': [],
    #         },
    #         'type': 'function'
    #     }]


    messages = []
    messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
    messages.append({"role": "user", "content": "I want to notify a passenger"})
    chat_response = chat_completion_request(
        messages, tools=tool_object
    )
    assistant_message = chat_response.choices[0].message
    message = assistant_message.content or  assistant_message.tool_calls
    messages.append({"role": assistant_message.role, "content": message})
    
    pretty_print_conversation(messages)

if __name__ == "__main__":
    main()