import os
from flask import Flask, jsonify, request
import sys

from langchain_openai import ChatOpenAI
from strapi_agent import StrapiAgent


from strapi_api.strapi_api_utils import get_heareders  # Assuming you've implemented LangGraphAgent

app = Flask(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file

STRAPI_API_URL = os.getenv("STRAPI_API_URL") # "http://localhost:1337/api"
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")

llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
strapi_headers = get_heareders(STRAPI_API_KEY)
agent = StrapiAgent(STRAPI_API_URL, strapi_headers, llm)

thread_id = 1 #uuid.uuid4()
thread_config = {"recursion_limit": 50, "configurable": {"thread_id": thread_id}}
initial_user_message = "Create a home page with a stage component, one image, one text of 100 words"
agent.invoke(initial_user_message, thread_config)

@app.route("/")
def index():
    # Serve the HTML page when accessing the root URL
    return app.send_static_file('index.html')

@app.route("/interact", methods=["POST"])
def interact_with_agent():
    user_input = request.json.get("input")
    # TODO set up and handle the return of the agent

    interrupt = agent.get_interrupt(thread_config)
    if interrupt:
        agent.resume_interrupt(user_input, thread_config)

    agent.invoke(user_input, thread_config)

    # Assuming 'respond' is how the agent processes input
    # return jsonify({"response": response})
    return jsonify({"response": "-- not implemented yet --"})

if __name__ == "__main__":
    app.run(debug=True)
