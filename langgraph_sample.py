from langchain_core.messages import  HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph import MessagesState
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.errors import NodeInterrupt
from tools import *
import json
from prompts import preprocessing_prompts, content_prompts
from console_utils import *
from strapi_api.strapi_api_utils import *

STRAPI_API_URL = os.getenv("STRAPI_API_URL") # "http://localhost:1337/api"
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")

strapi_headers = get_heareders(STRAPI_API_KEY)


class MessagesState(MessagesState):
    strapi_url: str
    headers: object
    company_profile: str
    website_data: object
    # Add any keys needed beyond messages, which is pre-built 
    pass


class StrapiGraphAgent:
    def __init__(self):
        from dotenv import load_dotenv  # Import load_dotenv
        load_dotenv()  # Load the .env file

        self.tools = [create_page, add_component_stage, add_component_text, get_pages, get_images]
        self.sys_msg = SystemMessage(content="You are a helpful assistant tasked with creating websites in Strapi.")
        self.llm = ChatOpenAI(model="gpt-4o")
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.react_graph = self.build_graph()

    def build_graph(self):
        builder = StateGraph(MessagesState)
        builder.add_node("assistant", self.assistant)
        builder.add_node("tools", ToolNode(self.tools))
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
        return builder.compile()


    # def design_setup(self, state: MessagesState):
    #     # node
    #     # Preprocess the company profile and get design parameters and site structure
    #     latest_message = state["messages"][-1]
    #     state["company_profile"] = latest_message

    #     response_design = self.llm.invoke(preprocessing_prompts.generate_site_data(latest_message.content))
    #     site_data = json.loads(response_design.content)
    #     if("error" in site_data):
    #         print_color(f"Error: {site_data["error"]}", "red")
    #         return
    #     print_color(json.dumps(site_data, indent=4), "green")
    #     print_color(F"Creating the design..", "blue") 
        
    #     design = create_design(site_data,STRAPI_API_URL,strapi_headers)
    #     link_design_to_config(design,STRAPI_API_URL,strapi_headers)
    #     state["company_profile"] = design
    #     state["website_data"] = site_data
    #     return state

    
    def assistant(self, state: MessagesState): 
        #  # Let's optionally raise a NodeInterrupt if the length of the input is longer than 5 characters
        # if not state['company_profile']:
        #     raise NodeInterrupt("Company profile should be defined first")

        #node
        return {
            "messages": [self.llm_with_tools.invoke([self.sys_msg] + state["messages"])],
            }

    def invoke(self, messages):
        return self.react_graph.invoke({"messages": messages})


# # Example usage
# if __name__ == "__main__":
#     agent = StrapiGraphAgent()
#     messages = [HumanMessage(content="Create a Home page, and add a stage component to it with the text 'Welcome to our website!'")]
#     response = agent.invoke(messages)
#     for m in response['messages']:
#         m.pretty_print()