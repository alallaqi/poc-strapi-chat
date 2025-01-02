import uuid
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

from strapi_tools import *
from agent_models import *
from langgraph.prebuilt import create_react_agent
from console_utils import *
from strapi_api.strapi_api_utils import *
from sample_companies import *
from IPython.display import display, Markdown
import operator
from typing import Annotated, List, Literal, Tuple, Union
from pydantic import BaseModel,Field
from agents_deconstructed.format_tools import format_tools_args
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import  interrupt, Command
import webbrowser
import tempfile
import os
import inspect


from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file

    
class StrapiAgent:
    def __init__(self, strapi_url: str, headers: object, llm: ChatOpenAI):

        # not yet passed to the tools
        self.strapi_url = strapi_url
        self.headers = headers
        self.llm = llm
        self.memory = MemorySaver()
        

        self.tools = [
            create_page,
            add_component_stage,
            add_component_text,
            add_component_image,
            get_pages,
            get_images]



        site_data_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Validate the given company profile text according to the validation rules listed below.
If there are validation errors, return ONLY an error message - Do not extract any other information from the company profile text. 
If there are no validation errors, extract all the output details from the company profile text.
Do NOT make up information. If the company profile text does not contain the required information, return ONLY an error message. 
        
Validation rules:
- The text must mention the company name
- It should be possible to understand from the text in which industry the company operates.
- The text should mention what kind of services or products the company offers.
""",
                ),
                ("placeholder", "{messages}"),
            ]
        )
        self.site_data_extractor = site_data_prompt | ChatOpenAI(temperature=0).with_structured_output(SiteData)
        

     
        self.agent_executor = create_react_agent(self.llm, self.tools,  messages_modifier=self.messages_modifier)
        planner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """For the given objective, come up with a simple step-by-step plan, using ONLY the following tools:
                    
```
{tools}
```

This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps (e.g. getting all pages when not needed), do not verify previous steps.
If needed the output of each step should be used for the input to the next step.
The result of the final step should be the final answer. Make sure that the step describes what tool to use and how to use it - do not skip steps.
Each step should use only one single call to a one single tool. If multiple sequential calls to the same tool are needed, then use multiple steps.
If no value for the input parameters are given and cannot be found, then try to create it values based on the Company Profile provided below. - Text component should be at least 100 words long.
If multiple values are possible, then use a random one - do not ask the user for any additional information.

The output should be a list of steps, where each step is a string describing the task to be done.
Here an example example:
Input: add a text of 100 words to the page 'Home'
1. use get_pages to do get the id of the page 'Home'
2. Generate a text o 100 words and use add_component_text to add a text to the page with the id retrieven from the step 1

Company profile:
{company_profile}
""",
                ),
                ("placeholder", "{messages}"),
            ]
        )

        planner_prompt = planner_prompt.partial(
            tools = format_tools_args(self.tools),
        )
        self.planner = planner_prompt | ChatOpenAI(temperature=0).with_structured_output(Plan)
        

        replanner_prompt = ChatPromptTemplate.from_template(
            """
Your objective was this:
{input}

Your original plan was this:
{plan}

You have currently done the follow steps:
{past_steps}

Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done.
Make sure each step uses only one singe call to a single tool.
In case of errors try to adjust the plan accordingly. E.g., if a page already exists skip the creation step.
Do not repeat a step that has failed using the same input parameters. If you need to repeat a step, adjust the input parameters accordingly.

Always consider the following company profile description when generationg content:
{company_profile}
""",
        )
     
        self.replanner = replanner_prompt | ChatOpenAI(temperature=0).with_structured_output(Act)
        
        self.app = self.build_graph()
    
    
    def generate_site_data_step(self,  state: AgentState):
        logger.info(f"Executing step: {inspect.currentframe().f_code.co_name}")

        site_data = self.site_data_extractor.invoke({"messages": [("user", f"Company profile: {state["company_profile"]}")]})

        # TODO this should be handled with an interrupt step
        # setup_website_design(site_data)

        return {"site_data" : site_data}
    

    

    def messages_modifier(self, messages: list):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that helps creating websites.
             
             If no instructions related to the website to build are given, assume the following structure should be created:
             - A home page containing: 1 stage component, 1 text component of 100 words.
             - A contact pages containing: 1 image component, and 1 text component with a list of dummy contacts.

             """),
            ("placeholder", "{messages}"),
        ])
        return prompt.invoke({"messages": messages})


    def execute_step(self, state: AgentState):
        logger.info(f"Executing step: {inspect.currentframe().f_code.co_name}")
        plan = state["plan"]
        plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
        task = plan[0]
        task_formatted = f"""For the following plan:
    {plan_str}\n\nYou are tasked with executing step {1}, {task}.
    """
        agent_response = self.agent_executor.invoke(
            {"messages": [("user", task_formatted)]}
        )
        return {
            "past_steps": [(task, agent_response["messages"][-1].content)],
        }
    

    def input_company_profile_step(self, state: AgentState):
        logger.info(f"Executing step: {inspect.currentframe().f_code.co_name}")
        
        user_input = interrupt("""Please provide a company profile description to use the Strapi agent. The description should include:
- The company name.
- The industry
- Information about services or products offered""")        
        
        return {"company_profile": user_input}


    def plan_step(self, state: AgentState):
        logger.info(f"Executing step: {inspect.currentframe().f_code.co_name}")
        
        sitedata = state.get("site_data", {})
        
        plan = self.planner.invoke({"company_profile":  state["company_profile"],"messages": [("user", state["input"])]})

        return {"plan": plan.steps, "response": None}


    def replan_step(self, state: AgentState):
        logger.info(f"Executing step: {inspect.currentframe().f_code.co_name}")
       
        output = self.replanner.invoke({**state, "company_profile": state["company_profile"]})
        if isinstance(output.action, Response):
            return {"response": output.action.response}
        else:
            return {"plan": output.action.steps}


    def should_end(self, state: AgentState):
        if "response" in state and state["response"]:
            return END
        else:
            return "agent"


    def should_continue_after_site_data(self, state: AgentState):
        sitedata = state.get("site_data", {})
        if "company_profile" in state and state["company_profile"] and sitedata and not sitedata.error:
            return "planner"
        else:
            return "input_company_profile"
            
    def should_skip_company_profile(self, state: AgentState):
        sitedata = state.get("site_data", {})
        if "company_profile" in state and state["company_profile"] and sitedata and not sitedata.error:
            return "planner"
        else:
            return "input_company_profile"
    
    def build_graph(self):
       
        workflow = StateGraph(AgentState)

        workflow.add_node("generate_site_data", self.generate_site_data_step)
        workflow.add_node("input_company_profile", self.input_company_profile_step)
        workflow.add_node("planner", self.plan_step)
        workflow.add_node("agent", self.execute_step)
        workflow.add_node("replan", self.replan_step)

        
        workflow.add_conditional_edges(
            START,
            # Next, we pass in the function that will determine which node is called next.
            self.should_skip_company_profile,
            ["input_company_profile", "planner"],
        )
        workflow.add_edge("input_company_profile", "generate_site_data")
        workflow.add_conditional_edges( 
            "generate_site_data",
            self.should_continue_after_site_data,
            ["input_company_profile", "planner"])


        workflow.add_edge("planner", "agent")
        workflow.add_edge("agent", "replan")
        workflow.add_conditional_edges(
            "replan",
            # Next, we pass in the function that will determine which node is called next.
            self.should_end,
            ["agent", END],
        )

        # Finally, we compile it!
        # This compiles it into a LangChain Runnable,
        # meaning you can use it as you would any other runnable
        app = workflow.compile(checkpointer=self.memory)

        # Generate the mermaid diagram as a PNG file
        png_data = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        # Save the PNG to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(png_data)
            tmp_file_path = tmp_file.name

        # Open the PNG file in the default web browser
        webbrowser.open(f"file://{os.path.abspath(tmp_file_path)}")

        return app


    def invoke(self, user_input, thread_config):
        # thread_id = 1 #uuid.uuid4()
        # thread_config = {"recursion_limit": 50, "configurable": {"thread_id": thread_id}}
        inputs = {"input": user_input}
        
        for event in self.app.stream(inputs, config=thread_config):
            for k, v in event.items():
                if k != "__end__":
                     logger.debug(v)

    
    def resume_interrupt(self, user_input, thread_config):
        self.app.invoke(Command(resume=user_input), config=thread_config)

    
    def get_interrupt(self, thread_config):
        state = self.app.get_state(thread_config)
        # logger.debug(state)
        if state.tasks and state.tasks[0].interrupts:
            return state.tasks[0].interrupts[0]
        else:
            return None
