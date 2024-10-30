import os
import yaml
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chat_models import ChatOpenAI
from langchain_community.agents.agent_toolkits.openapi import OpenAPIAgent, OpenAPIToolkit
from langchain.requests import RequestsWrapper

def load_openapi_definition(file_path: str) -> dict:
    with open(file_path) as f:
        raw_openapi_spec = yaml.load(f, Loader=yaml.Loader)
    return raw_openapi_spec

def build_request_wrapper():
    headers = {
        'Authorization': f'Bearer {os.getenv("STRAPI_API_TOKEN")}'
    }
    return RequestsWrapper(headers=headers)

def main():
    # Load OpenAPI definition
    openapi_file_path = "./middleware/specific.yaml"
    raw_openapi_spec = load_openapi_definition(openapi_file_path)

    # Build Requests Wrapper with authentication headers
    requests_wrapper = build_request_wrapper()

    # Create OpenAPI Toolkit
    toolkit = OpenAPIToolkit.from_openapi_spec(
        raw_openapi_spec,
        requests=requests_wrapper
    )

    # Create custom system prompt
    system_prompt = SystemMessagePromptTemplate.from_template("""
You are an AI assistant integrated with a Strapi content management system (CMS). Your primary role is to assist users in creating and managing website content through an interactive conversation. You leverage OpenAPI documentation to understand and interact with various endpoints available in the Strapi system.

Here are your key responsibilities:

1. Interactive Guidance: Guide users step-by-step to generate a complete website. This includes gathering necessary information about design preferences, site configuration, navigation menus, and footer content.

2. Endpoint Handling: Use the OpenAPI schema to intelligently interact with endpoints such as content pages, site configuration, designs, and navigation menus. You can create, update, or delete items using the authorized endpoints.

3. Data Inference and Recommendations: Make the process efficient by inferring information from the user's previous inputs to reduce redundant questions. Use a conversational approach to keep the user engaged and assist them in making decisions about their website's structure and content.

4. Error Handling and Guidance: Gracefully handle errors, such as missing information or unsupported actions. Always provide helpful suggestions to the user to guide them towards successfully completing their tasks.

5. Real-time Content Generation: Utilize the GPT model to generate engaging and appropriate website content. Whether it's text for a landing page, meta descriptions, or creating content sections, ensure the content aligns with the user's needs.
    """)

    human_prompt = HumanMessagePromptTemplate.from_template("{input}")

    chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

    # Initialize the LLM
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    # Create OpenAPI Agent
    agent = OpenAPIAgent(
        llm=llm,
        toolkit=toolkit,
        prompt=chat_prompt,
        verbose=True
    )

    # Start the interactive session
    while True:
        input_message = input("\n[Middleware Assistant] Please enter your message (Ctrl+C to quit):\n")
        user_query = input_message
        response = agent.run(user_query)
        print(response)

if __name__ == "__main__":
    main()
