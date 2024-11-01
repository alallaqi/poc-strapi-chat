import os
from flask import request
import yaml
import tiktoken
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain_community.agent_toolkits.openapi import planner
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.utilities import RequestsWrapper
import sys
import json
# sys.setrecursionlimit(999999) 
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
    
    openapi_spec = reduce_openapi_spec(raw_openapi_spec, dereference=False)
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
    enc = tiktoken.encoding_for_model("gpt-4")
    tokens_count = count_tokens(enc, yaml.dump(raw_openapi_spec))
    print(add_color(f"{tokens_count} tokens used in OpenAPI spec", "blue"))

    # Create the strapi agent for OpenAPI
    requests_wrapper = build_request_wrapper()
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.0)  # Use concrete class ChatOpenAI
    ALLOW_DANGEROUS_REQUESTS = True 
    strapi_agent = planner.create_openapi_agent(openapi_definition, requests_wrapper, llm, allow_dangerous_requests=ALLOW_DANGEROUS_REQUESTS)
    while True:
        input_message = input(add_color("\n[Strapi Assistant] Enter a company profile description:\n", "yellow"))
        #company_profile = input_message
        # -----------
        # I'm too lazy to copy paste the company profile description 
        # so here a couple of predefined ones
        company_profile_software = "My company is a software development company that specializes in creating custom software solutions for businesses. We have a team of experienced developers who can build web applications, mobile apps, and more. Our goal is to help businesses streamline their processes and improve their efficiency through technology."
        company_profile_fitness = "My company is a fitness and wellness center that offers a variety of services including personal training, group fitness classes, and nutritional counseling. We have a team of certified trainers and nutritionists who are dedicated to helping our clients achieve their health and fitness goals. Our state-of-the-art facility is equipped with the latest fitness equipment and offers a welcoming and supportive environment for people of all fitness levels."
        company_profile = company_profile_fitness
        # -----------
        prompt_template_design_params = f"""# Context
        Designing a website for a company based on the company p[rofile description. 
        
        # Objective
        Given the company profile in the <text> section below, extract the parameters listed in the <parameters> section.
        The output shoud be in json format according to the example defined in the <output format> section.
        
        <text>
        {company_profile}
        </text>

        <parameters>
        - A primary color in hex value that is common in the company sector.
        - A secondary color in hex value that complements the primary color.
        - The name to use for the design.
        <parameters> 

        
        <output format>
        {{
            "primary_color": "#FF5733",
            "secondary_color": "#33FF57",
            "design_name": "Company Design"
        }}
        </output format>


        # Response
        Respond with the JSON as defined in the <output format> section. Do not format the response as markdown because it should be parsed.
        """
        

        response_design = llm.invoke(prompt_template_design_params)
        response_json = json.loads(response_design.content)
        print(add_color(f"Primary Color: {response_json['primary_color']}", "green"))
        print(add_color(f"Secondary Color: {response_json['secondary_color']}", "green"))
        print(add_color(f"Design Name: {response_json['design_name']}", "green"))
    
        # Prepare a prompt template for the strapi_agent
        prompt_template_design_creation = f"""
        # Context
        You are an assistant that helps with creating and configuring a website design using Strapi's API.

        # Objective
        Given the design parameters in the <design_parameters> section, perform the following steps:
        1. Create a new design using the /designs endpoint.
        2. Use the designId from the created design to update the site configuration using the /site-config endpoint.

        <design_parameters>
        {response_json}
        </design_parameters>

        # Endpoints
        - POST /designs
        - PUT /site-config

        # Sequence of Calls
        1. Call POST /designs with the design parameters to create a new design.
        2. Extract the designId from the response.
        3. Call PUT /site-config with the designId to update the site configuration.
        """

        # Invoke the strapi agent with the prompt
        response_design_creation = strapi_agent.invoke(prompt_template_design_creation)

        # Print the response from the agent
        print(add_color("Response from Strapi Agent:", "blue"))
        print(response_design_creation)



if __name__ == "__main__":
    main()
