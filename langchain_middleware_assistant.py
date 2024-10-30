import os
import sys
import yaml
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain_community.agent_toolkits.openapi.planner import OpenAPIPlanner
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.utilities import RequestsWrapper
import tiktoken

# Load environment variables
load_dotenv()

# Set up Flask app
app = Flask(__name__)

# Load OpenAPI schema
with open('./middleware/specific.yaml', 'r') as file:
    openapi_spec = yaml.safe_load(file)

# Reduce OpenAPI spec for simplified processing
reduced_spec = reduce_openapi_spec(openapi_spec)

# Set up the Chat LLM model
llm = ChatOpenAI(temperature=0.7)

# Initialize the requests wrapper with headers
headers = {
    "Authorization": f"Bearer {os.getenv('STRAPI_API_KEY')}",
    "Content-Type": "application/json"
}
requests_wrapper = RequestsWrapper(headers=headers)

# Set up OpenAPI Planner with reduced spec and LLM
planner = OpenAPIPlanner.from_llm(llm=llm, json_spec=reduced_spec, requests_wrapper=requests_wrapper)

# Define a system prompt
system_prompt = "You are tasked with creating a website page for a company. Parse the user input and structure it according to the Strapi components. Ensure relevant sections like 'About Us' are created based on the company description provided."

@app.route('/create_content', methods=['POST'])
def create_content():
    data = request.json
    user_input = data.get("company_description", "")

    # Check if user input exists
    if not user_input:
        return jsonify({"error": "No company description provided"}), 400

    # Combine the system prompt and user input
    prompt = f"{system_prompt} Company description: {user_input}"

    # Invoke the planner to process the prompt
    response = planner.plan_and_execute(prompt)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
