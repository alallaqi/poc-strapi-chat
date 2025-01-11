import os
from langchain_openai.chat_models import ChatOpenAI
import sys
from strapi_agent import StrapiAgent
from console_utils import *
from strapi_api.strapi_api_utils import *

sys.stdin.reconfigure(encoding='utf-8')

# Load environment variables from .env file
from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file

STRAPI_API_URL = os.getenv("STRAPI_API_URL") # "http://localhost:1337/api"
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")

# Get the headers for the Strapi API
strapi_headers = get_heareders(STRAPI_API_KEY)

# Main function to run the Strapi Assistant
def main():
      
     # -----------
    # I'm too lazy to copy paste the company profile description 
    # so here a couple of predefined ones
    input_message = ""
    # -----------

    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
    agent = StrapiAgent(STRAPI_API_URL, strapi_headers, llm)

    thread_id = 1 #uuid.uuid4()
    thread_config = {"recursion_limit": 50, "configurable": {"thread_id": thread_id}}
    input_message = "Create a home page with a stage component"
    while True:
        agent.invoke(input_message, thread_config)

        # agent_state = agent.state.get_state(thread_config)
        # logger.debug(agent_state)

        interrupt = agent.get_interrupt(thread_config)
        if interrupt:
            input_message = input(add_color(f"\n{interrupt.value}\n", "yellow"))
            agent.resume_interrupt(input_message, thread_config)
         
        input_message = input(add_color("\n[Strapi Assistant] Enter an action to perform:\n", "yellow"))



if __name__ == "__main__":
    main()
