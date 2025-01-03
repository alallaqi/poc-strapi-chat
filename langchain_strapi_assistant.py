import os
from flask import request
import yaml
import tiktoken
from langchain_community.agent_toolkits.openapi import planner
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain.agents import initialize_agent, load_tools
from langchain_community.utilities import RequestsWrapper
import sys
import json
from prompts import preprocessing_prompts, content_prompts
from console_utils import *
from sample_companies import *
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
    company_profile = sample_companies["valid"]["wellness"]
    # -----------
    
    print_color(F"Generating base web site data..", "blue")
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
    # Preprocess the company profile and get design parameters and site structure
    response_design = llm.invoke(preprocessing_prompts.generate_site_data(company_profile))
    site_data = json.loads(response_design.content)
    if("error" in site_data):
        print_color(f"Error: {site_data["error"]}", "red")
        return
    print_color(json.dumps(site_data, indent=4), "green")
    

    # Upload some demo images to Strapi
    img_count = 3
    print_color(F"Uploading {img_count} demo images to Strapi..", "blue")
    dalle_tool  = load_tools(["dalle-image-generator"], model_name='dall-e-3')[0]
    for _ in range(img_count):
        image_url = dalle_tool(site_data['imageGenerationPrompt'])
        # image_url = "https://picsum.photos/700"
        upload_image_to_strapi(image_url, STRAPI_API_URL, strapi_headers)
    
    # ------------------------


    # Create a design using the extracted parameters and link it to site config
    # INFO - I switched this part to direct "manual" API call as it is static, no need to use the agent here.
    print_color(F"Creating the design..", "blue") 
    design = create_design(site_data,STRAPI_API_URL,strapi_headers)
    link_design_to_config(design,STRAPI_API_URL,strapi_headers)

    # Setup the Strapi agent with the OpenAPI definition
    print_color(F"Creating content pages..", "blue") 
    strapi_agent = setup_strapi_agent(OPEN_API_FILE_PATH, llm)    
    # Invoke the strapi agent with the prompt
    response_design_creation = strapi_agent.invoke(content_prompts.create_home_page(site_data))

    # Print the response from the agent
    # print_color("Response from Strapi Agent:", "blue")
    return

if __name__ == "__main__":
    main()
