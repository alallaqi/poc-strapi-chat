import os
from flask import request
import yaml
import tiktoken
from langchain_community.agent_toolkits.openapi import planner
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.utilities import RequestsWrapper
import sys
import json
from prompts import preprocessing_prompts, content_prompts
from console_utils import *
from strapi_api.strapi_api_utils import *

sys.stdin.reconfigure(encoding='utf-8')

# Load environment variables from .env file
from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file

STRAPI_API_URL = "http://localhost:1337/api"
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
OPEN_API_FILE_PATH = "./strapi_api/full_documentation.json"  # Path to your Strapi OpenAPI file


# Get the headers for the Strapi API
strapi_headers = get_heareders(STRAPI_API_KEY)

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


# Count tokens using GPT encoding
def count_tokens(enc, s):
    return len(enc.encode(s))


def setup_strapi_agent(openapi_file, llm):
    raw_openapi_spec, openapi_definition = load_openapi_definition(openapi_file, essential_endpoints)
    
    # List and count the endpoints
    list_endpoints(raw_openapi_spec)
    endpoints_count = count_endpoints(raw_openapi_spec)
    print_color(f"{endpoints_count} endpoints found", "blue")

    # Count tokens for the OpenAPI definition
    enc = tiktoken.encoding_for_model("gpt-4")
    tokens_count = count_tokens(enc, yaml.dump(raw_openapi_spec))
    print_color(f"{tokens_count} tokens used in OpenAPI spec", "blue")

    # Create the strapi agent for OpenAPI
    requests_wrapper = RequestsWrapper(headers=strapi_headers)
    
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
    
    # Upload some demo images to Strapi
    img_count = 3
    print_color(F"Uploading {img_count} demo images to Strapi...", "blue")
    for _ in range(img_count):
        upload_image_to_strapi("https://picsum.photos/700", STRAPI_API_URL, strapi_headers)
    
    
    # init the llm model
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)

    # Preprocess the company profile and get design parameters and site structure
    response_design = llm.invoke(preprocessing_prompts.generate_site_data(company_profile))
    site_data = json.loads(response_design.content)
    print_color(json.dumps(site_data, indent=4), "green")
    
    # Create a design using the extracted parameters and link it to site config
    # INFO - I switched this part to direct "manual" API call as it is static, no need to use the agent here.  
    design = create_design(site_data,STRAPI_API_URL,strapi_headers)
    link_design_to_config(design,STRAPI_API_URL,strapi_headers)

    # Setup the Strapi agent with the OpenAPI definition
    strapi_agent = setup_strapi_agent(OPEN_API_FILE_PATH, llm)

    
    # Invoke the strapi agent with the prompt
    response_design_creation = strapi_agent.invoke(content_prompts.create_home_page(site_data))

    # Print the response from the agent
    print_color("Response from Strapi Agent:", "blue")
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
