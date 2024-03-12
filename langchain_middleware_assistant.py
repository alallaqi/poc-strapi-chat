import os
from flask import request
import yaml
import tiktoken
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain_community.agent_toolkits.openapi import planner
from langchain_openai import ChatOpenAI
from langchain.requests import RequestsWrapper

def load_openapi_definition(file_path: str) -> dict:
    with open(file_path) as f:
        raw_openai_api_spec = yaml.load(f, Loader=yaml.Loader)
    openai_api_spec = reduce_openapi_spec(raw_openai_api_spec)

    return raw_openai_api_spec, openai_api_spec


def count_endpoints(raw_openai_api_spec):
    endpoints = [
        (route, operation)
        for route, operations in raw_openai_api_spec["paths"].items()
        for operation in operations
        if operation in ["get", "post"]
    ]
    return len(endpoints)

def add_color(text, color):
        colors = {
            "green": "\033[92m",
            "red": "\033[91m",
            "yellow": "\033[93m",
            "blue": "\033[94m"
        }
        end_color = "\033[0m"
        
        if color in colors:
            return f"{colors[color]}{text}{end_color}"
        else:
            return text

def build_request_wrapper():

    # TODO - Add auth headers here

    return RequestsWrapper()

def count_tokens(enc, s):
    return len(enc.encode(s))


def main():
    # Load OpenAPI definition
    openapi_file_path = "middleware/airline_api.openapi.yaml"
    raw_openai_api_spec, openapi_definition = load_openapi_definition(openapi_file_path)
    endpoints_count = count_endpoints(raw_openai_api_spec)
    print(add_color(f"{endpoints_count} endpoints found", "blue"))

    # Count tokens
    enc = tiktoken.encoding_for_model("gpt-4")
    tokens_count = count_tokens(enc, yaml.dump(raw_openai_api_spec))
    print(add_color(f"{tokens_count} tokens", "blue"))

    # Create middleware agent
    requests_wrapper = build_request_wrapper()
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.0)
    middleware_agent = planner.create_openapi_agent(openapi_definition, requests_wrapper, llm)
    while True:
        input_message = input(add_color("\n[Middlware Assistant] Please enter your message (Ctrl+C to quit):\n","yellow"))
        user_query = (input_message)
        middleware_agent.invoke(user_query)

if __name__ == "__main__":
    main()
