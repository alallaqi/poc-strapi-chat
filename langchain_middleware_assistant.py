import os
from flask import request
import yaml
import tiktoken
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain_community.agent_toolkits.openapi import planner
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.utilities import RequestsWrapper
import sys
sys.setrecursionlimit(999999) 
sys.stdin.reconfigure(encoding='utf-8')

# Load environment variables from .env file
from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file


# Adjusted list of essential endpoints and methods    
essential_endpoints = {
        '/content-pages': ['get', 'post'],
        '/content-pages/{id}': ['get', 'put', 'delete'],
        '/site-config': ['get', 'put', 'delete'],
        '/site-config/localizations': ['post'],
        '/designs': ['get', 'post'],
        '/designs/{id}': ['get', 'put', 'delete'],
        '/navigation-menus': ['get', 'post'],
        '/navigation-menus/{id}': ['get', 'put', 'delete'],
        '/navigation-menus/{id}/localizations': ['post'],
        '/footer': ['get', 'put', 'delete'],
        '/footer/localizations': ['post'],
    }

# Load OpenAPI Definition from Strapi's schema
def load_openapi_definition(file_path: str) -> dict:
    with open(file_path) as f:
        raw_openapi_spec = yaml.load(f, Loader=yaml.Loader)

    filtered_paths = {}
    for path, methods in raw_openapi_spec["paths"].items():
        if path in essential_endpoints:
            filtered_methods = {
                method: spec
                for method, spec in methods.items()
                if method in essential_endpoints[path]
            }
            if filtered_methods:
                filtered_paths[path] = filtered_methods
    raw_openapi_spec["paths"] = filtered_paths
    
    openapi_spec = reduce_openapi_spec(raw_openapi_spec)
    return raw_openapi_spec, openapi_spec

# Count endpoints in the OpenAPI spec
def count_endpoints(raw_openapi_spec):
    endpoints = [
        (route, operation)
        for route, operations in raw_openapi_spec["paths"].items()
        for operation in operations
        if operation in ["get", "post"]
    ]
    return len(endpoints)


    # Function to list all endpoints and their HTTP methods
def list_endpoints(raw_openapi_spec):
    endpoints = [
        (route, operation)
        for route, operations in raw_openapi_spec["paths"].items()
        for operation in operations
    ]
    
    for endpoint, method in endpoints:
        print(add_color(f"Endpoint: {endpoint}, Method: {method.upper()}", "green"))

    return endpoints

# Helper function to color terminal output
def add_color(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m"
    }
    end_color = "\033[0m"
    return f"{colors.get(color, '')}{text}{end_color}"

# Build request wrapper with authorization for Strapi
def build_request_wrapper():
    STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
    headers = {
        "Authorization": f"Bearer {STRAPI_API_KEY}",
        "Content-Type": "application/json",
    }
    return RequestsWrapper(headers=headers)

# Count tokens using GPT encoding
def count_tokens(enc, s):
    return len(enc.encode(s))

def main():
    # Load Strapi's OpenAPI definition
    openapi_file_path = "./middleware/strapi_openapi.yaml"  # Path to your Strapi OpenAPI file
    raw_openapi_spec, openapi_definition = load_openapi_definition(openapi_file_path)

    # List and count the endpoints
    list_endpoints(raw_openapi_spec)
    endpoints_count = count_endpoints(raw_openapi_spec)
    print(add_color(f"{endpoints_count} endpoints found", "blue"))

    # Count tokens for the OpenAPI definition
    enc = tiktoken.encoding_for_model("gpt-4o")
    tokens_count = count_tokens(enc, yaml.dump(raw_openapi_spec))
    print(add_color(f"{tokens_count} tokens used in OpenAPI spec", "blue"))

    # Create the middleware agent for OpenAPI
    requests_wrapper = build_request_wrapper()
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.0)  # Use concrete class ChatOpenAI
    ALLOW_DANGEROUS_REQUESTS = True 
    middleware_agent = planner.create_openapi_agent(openapi_definition, requests_wrapper, llm, allow_dangerous_requests=ALLOW_DANGEROUS_REQUESTS)
    while True:
        input_message = input(add_color("\n[Middleware Assistant] Enter your message:\n", "yellow"))
        middleware_agent.invoke(input_message)


if __name__ == "__main__":
    main()
