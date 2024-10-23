import os
import yaml
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain_community.agent_toolkits.openapi import planner
from langchain_community.utilities import TextRequestsWrapper
from langchain.tools import Tool
import requests

# Load environment variables
load_dotenv()

# Helper function to add color to text output
def add_color(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
    }
    end_color = "\033[0m"
    return f"{colors.get(color, '')}{text}{end_color}"

# Adjusted list of essential endpoints and methods    
essential_endpoints = {
    '/content-pages': ['get', 'post'],
    '/site-config': ['get', 'put'],
    '/designs': ['get', 'post'],
    '/navigation-menus': ['get', 'post'],
    '/footer': ['get', 'put'],
}

# Load OpenAPI Definition from Strapi's schema (optimized to load only needed endpoints)
def load_openapi_definition(file_path: str) -> dict:
    with open(file_path) as f:
        raw_openapi_spec = yaml.safe_load(f)

    # Filter only essential endpoints from the full specification
    filtered_paths = {
        path: {
            method: spec
            for method, spec in methods.items() if method in essential_endpoints.get(path, [])
        }
        for path, methods in raw_openapi_spec.get("paths", {}).items() if path in essential_endpoints
    }
    raw_openapi_spec["paths"] = filtered_paths
    
    openapi_spec = reduce_openapi_spec(raw_openapi_spec)
    return raw_openapi_spec, openapi_spec

# Build request wrapper with authorization for Strapi
def build_request_wrapper():
    strapi_api_key = os.getenv("STRAPI_API_KEY")
    headers = {
        "Authorization": f"Bearer {strapi_api_key}",
        "Content-Type": "application/json",
    }
    return TextRequestsWrapper(headers=headers)

# Initialize OpenAI API
llm = ChatOpenAI(temperature=0.7)  # Increased temperature for more creative responses

# Load the OpenAPI spec
openapi_file_path = "./middleware/specific.yaml"
raw_openapi_spec, openapi_spec = load_openapi_definition(openapi_file_path)

# Create the middleware agent for OpenAPI
requests_wrapper = build_request_wrapper()
middleware_agent = planner.create_openapi_agent(
    openapi_spec, 
    requests_wrapper, 
    llm, 
    verbose=True,
    allow_dangerous_requests=True
)

# Create a proper tool using the middleware_agent
middleware_tool = Tool(
    name="Middleware",
    func=middleware_agent.run,
    description="Use this tool to interact with the middleware."
)

# Define your tools
tools = [middleware_tool]

# Create the prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant that generates website content."),
    ("human", "Generate a website design and content based on the following business description:"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent
agent = create_openai_functions_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Function to generate content using AI
def generate_content(business_description):
    # Generate content based on the business description
    generated_content = agent_executor.invoke(business_description)

    # Validate generated content against the schema
    if validate_generated_content(generated_content):
        # Create content pages using the generated content
        for page in generated_content.get('pages', []):
            create_content_page(page)
        print(f"\n{add_color('All content has been created successfully!', 'green')}")
    else:
        print(f"{add_color('Generated content is invalid.', 'red')}\n")

# Validation function
def validate_generated_content(content):
    # Implement validation logic based on your schema
    required_fields = ['title', 'route', 'content']
    return all(field in content for field in required_fields)

# Function to create a design
def create_design(design_data):
    url = f"{os.getenv('STRAPI_BASE_URL')}/designs"
    response = requests.post(url, json={"data": design_data})
    if response.status_code == 201:
        print(f"{add_color('Design created successfully.', 'green')}")
    else:
        print(f"{add_color('Failed to create design.', 'red')}\n")

# Function to create site configuration
def create_site_config(site_config_data):
    url = f"{os.getenv('STRAPI_BASE_URL')}/site-config"
    response = requests.post(url, json=site_config_data)
    if response.status_code == 201:
        print(f"{add_color('Site configuration created successfully.', 'green')}")
    else:
        print(f"{add_color('Failed to create site configuration.', 'red')}\n")

# Function to create a content page
def create_content_page(page_data):
    url = f"{os.getenv('STRAPI_BASE_URL')}/content-pages"
    response = requests.post(url, json={"data": page_data})
    if response.status_code == 201:
        print(f"{add_color(f'{page_data["title"]} page created successfully.', 'green')}")
    else:
        print(f"{add_color(f'Failed to create {page_data["title"]} page.', 'red')}\n")

# Main execution
def main():
    print("Welcome! Please provide a brief description of your business to generate your website.")
    business_description = input("Business Description: ")
    generate_content(business_description)

if __name__ == "__main__":
    main()