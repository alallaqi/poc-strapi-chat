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
import requests
from prompts import preprocessing_prompts, content_prompts

# sys.setrecursionlimit(999999) 
sys.stdin.reconfigure(encoding='utf-8')

# Load environment variables from .env file
from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file

STRAPI_API_URL = "http://localhost:1337/api"
OPEN_API_FILE_PATH = "./strapi_api/full_documentation.json"  # Path to your Strapi OpenAPI file

# Adjusted list of essential endpoints and methods    
essential_endpoints = {
        # '/site-config': ['get', 'put', 'delete'],
        # '/site-config/localizations': ['post'],
        # '/designs': ['get', 'post'],
        # '/designs/{id}': ['get', 'put', 'delete'],
        '/content-pages': ['get', 'post'],
        '/content-pages/{id}': ['get', 'put', 'delete'],
        '/navigation-menus': ['get', 'post'],
        '/navigation-menus/{id}': ['get', 'put', 'delete'],
        '/navigation-menus/{id}/localizations': ['post'],
        '/footer': ['get', 'put', 'delete'],
        '/footer/localizations': ['post'],
        '/upload/files': ['get'],
    }

# Load OpenAPI Definition from Strapi's schema
def load_openapi_definition(file_path: str) -> dict:
    with open(file_path) as f:
        raw_openapi_spec = json.load(f)

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

# Get the headers for the Strapi API
def get_heareders():
    STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
    return {
        "Authorization": f"Bearer {STRAPI_API_KEY}",
        "Content-Type": "application/json",
    }

# Build request wrapper with authorization for Strapi
def build_request_wrapper():
    return RequestsWrapper(headers=get_heareders())

# Count tokens using GPT encoding
def count_tokens(enc, s):
    return len(enc.encode(s))

# Create design in Strapi
def create_design(design_params):
    payload = {
        "data": {
            "designName": design_params['designName'],
            "primaryColor": design_params['primaryColor'],
            "secondaryColor": design_params['secondaryColor'],
        }
    }
    response = requests.post(f"{STRAPI_API_URL}/designs", json=payload, headers=get_heareders())
    # Check the response status and print the result
    if response.status_code != 200:
        print(add_color(f"Failed to create design: {response.status_code}", "red"))
        print(response.text)
        return None
    
    print(add_color("Design created successfully!", "green"))
    return response.json()["data"]

# Link a design to SiteConfig in Strapi
def link_design_to_config(design):
    payload = {
        "data": {
            "design": design['id'],
        }
    }
    response = requests.put(f"{STRAPI_API_URL}/site-config", json=payload, headers=get_heareders())
    # Check the response status and print the result
    if response.status_code != 200:
        print(add_color(f"Failed to link design: {response.status_code}", "red"))
        print(response.text)
        return None
    
    print(add_color("Design linked successfully!", "green"))
    return json.loads(response.text)

def setup_strapi_agent(openapi_file, llm):
    raw_openapi_spec, openapi_definition = load_openapi_definition(openapi_file)
    
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
    
    ALLOW_DANGEROUS_REQUESTS = True 
    return planner.create_openapi_agent(openapi_definition, requests_wrapper, llm, allow_dangerous_requests=ALLOW_DANGEROUS_REQUESTS)

# Main function to run the Strapi Assistant
def main():
    # Load Strapi's OpenAPI definition
    

    input_message = input(add_color("\n[Strapi Assistant] Enter a company profile description (press Enter to use the sample description):\n", "yellow"))
    #company_profile = input_message
    # -----------
    # I'm too lazy to copy paste the company profile description 
    # so here a couple of predefined ones
    company_profile = "My company is a software development company that specializes in creating custom software solutions for businesses. We have a team of experienced developers who can build web applications, mobile apps, and more. Our goal is to help businesses streamline their processes and improve their efficiency through technology."
    # company_profile = "My company is a fitness and wellness center that offers a variety of services including personal training, group fitness classes, and nutritional counseling. We have a team of certified trainers and nutritionists who are dedicated to helping our clients achieve their health and fitness goals. Our state-of-the-art facility is equipped with the latest fitness equipment and offers a welcoming and supportive environment for people of all fitness levels."
    # -----------
    
    # init the llm model
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)

    # Preprocess the company profile and get design parameters and site structure
    response_design = llm.invoke(preprocessing_prompts.generate_site_data(company_profile))
    site_data = json.loads(response_design.content)
    print(add_color(json.dumps(site_data, indent=4), "green"))
    
    # Create a design using the extracted parameters and link it to site config
    # INFO - I switched this part to direct "manual" API call as it is static, no need to use the agent here.  
    design = create_design(site_data)
    link_design_to_config(design)

    # Setup the Strapi agent with the OpenAPI definition
    strapi_agent = setup_strapi_agent(OPEN_API_FILE_PATH, llm)

    
    # Invoke the strapi agent with the prompt
    response_design_creation = strapi_agent.invoke(content_prompts.create_home_page(site_data))

    # Print the response from the agent
    print(add_color("Response from Strapi Agent:", "blue"))
    print(response_design_creation)

    return

    # Prepare a prompt template for the strapi_agent
    # ----------------------------------------
    # TODO - This prompt is just a quick try, it does create the nav and the page but it's still very minimal.
    # As the request is complex, we need to provide some specific examples, and eventually structure in multiple prompts 
    # ----------------------------------------
    prompt_template_content_creation = f"""
    # Context
    You are an assistant that helps with creating website content using Strapi's APIs.

    # Objective
    Given the company profile in the <company profile> section below, create:
    1. One main content page with elements listed in the <page elements> section. In the <sample request> section, an example of the request payload is provided for schema guidance; follow the instructions in <page elements> for the actual content.
    2. A contact page with dummy contact information and a professional tone.
    3. A navigation menu with links to the created pages. Make sure every page is configured in the navigation. 
    
    
    
    # Company Profile
    <company profile>
    {company_profile}
    </company profile>

    # Page Elements
    <page elements>
    For the main content page, include:
    - 1x Stage component: In this section put a subtitle derived from the <company profile>.
    - 1x text component: In this text section you need to put some text and multiple expanded bullet points derived from the <company profile>.
    - 1x text component: with the color inversed and more detailed text on <company profile>.
    - 1x image component: Include an image that represents the company. Use a placeholder image URL for now.
    - 1x CTA component: Include a call-to-action with the text "Learn More" that routes to the contact us page.
    

        
    <page elements>

    # API Calls 
    Use one POST request for each of the 3 points in the #Objective. Make sure to wrap the request in a JSON object with a 'data' key.
    
    # Sample Request    
    <sample request>
    {{
        "data": {{
            "title": "string",
            "route": "string",
            "content": [
                {{
                    "__component": "content.stage",
                    "subtitle": [
                        {{
                            "type": "paragraph",
                            "children": [
                                {{
                                    "type": "text",
                                    "text": "Subtitle derived from the company profile."
                                }}
                            ]
                        }}
                    ]
                }},
                {{
                    "__component": "content.text",
                    "text": [
                        {{
                            "type": "paragraph",
                            "children": [
                                {{
                                    "type": "text",
                                    "text": "We have state-of-the-art gym equipment."
                                }}
                            ]
                        }}
                    ],
                    "invertColors": null,
                    "noPadding": null,
                    "hideForSignedIn": false
                }},
                {{
                    "__component": "content.text",
                    "text": [
                        {{
                            "type": "paragraph",
                            "children": [
                                {{
                                    "type": "text",
                                    "text": "Join our wellness programs for a healthier lifestyle."
                                }}
                            ]
                        }}
                    ],
                    "invertColors": null,
                    "noPadding": null,
                    "hideForSignedIn": false
                }},
                {{
                    "__component": "content.image",
                    "alternativeText": null,
                    "width": null,
                    "padding": true,
                    "invertColors": null
                }}
            ]
        }}
    }}
    </sample request>

    """


# todo 
# Navigation needs to be updated we need to a more detailed prompt.
# Add a metod to add an image to the stage component and the image just a tempory way for the demo
# expand on the Prompt and add min max on the texts from the model 
# ADD config for Footer 

if __name__ == "__main__":
    main()
