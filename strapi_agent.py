from langchain_openai import ChatOpenAI
from IPython.display import Image, display, Markdown
from langchain.schema import SystemMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from strapi_tools import *
from agent_models import *
from langgraph.prebuilt import create_react_agent
from console_utils import *
from strapi_api.strapi_api_utils import *
from agents_deconstructed.format_tools import format_tools_args
from loguru import logger
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import  interrupt, Command
import webbrowser
import tempfile
import os
import inspect


DISPLAY_AGENT_GRAPH = False
SETUP_DESIGN = True

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
            get_images,
            add_page_to_navigation_menu,
            add_footer_link,
            update_footer_copyright]



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
        
        
        
      
        self.agent_executor = create_react_agent(self.llm, self.tools) #, state_modifier=self.executor_state_modifier)
        
        planner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """For the given objective, come up with a simple step-by-step plan, using ONLY the following tools:
         
```
{tools}
```

This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps.
If needed the output of each step can be used for the input to the next step.
The result of the final step should be the final answer. Make sure that the step describes what tool to use and how to use it - do not skip steps.
Each step should use only one single call to a one single tool. If multiple sequential calls to the same tool are needed, then use multiple steps.
If multiple values are possible, then use a random one - do not ask the user for any additional information.


Example of a plan:
The output should be a list of steps, where each step is a string describing the task to be done.
Here an example example:
Input: add a text of 100 words to the page 'Home'
1. use get_pages to do get the id of the page 'Home'
2. Generate a text o 100 words and use add_component_text to add a text to the page with the id retrieven from the step 1

""",
                ),
                ("placeholder", "{messages}"),
            ]
        )

        planner_prompt = planner_prompt.partial(
            tools = format_tools_args(self.tools),
        )
        self.planner = planner_prompt | ChatOpenAI(temperature=0).with_structured_output(Plan)
        
        replanner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
            """For the given plan, your task is to update the plan by removing the completed steps from the plan and adjust the remaining steps based on the past steps and the following istructions

Instructions:
REMOVE the first step from the plan, remove also any superfluous step, keep only the needed steps.
IMPORTANT: DO NOT return the last done step as part of the plan, and DO NOT make up steps wich are not related to the existing plan. 
If there are no more steps and you can return to the user, then respond with that. Otherwise, adjust the steps.
Make sure each step uses only one singe call to a single tool.
In case of errors try to adjust the plan accordingly. E.g., if a page already exists skip the 'create page' step dfor that page, and remove the step form the plan.
Do not repeat a step that has failed using the same input parameters. If you need to repeat a step, adjust the input parameters accordingly.
If the last 3 completed steps look like the same, make sure not to repeat again that step but removit from the plan.


Available tools:
```
{tools}
```


""" ),
                ("user", """# Your last plan was:
```
{plan}
```

# You have currently completed, all the follow steps:
```
{past_steps}
```


Update the plan accordingly and return the new plan or a response to the user if no more steps are needed.
"""),
            ]
        )

        replanner_prompt = replanner_prompt.partial(
            tools = format_tools_args(self.tools),
        )

        self.replanner = replanner_prompt | ChatOpenAI(temperature=0).with_structured_output(Act)

        self.app = self.build_graph()
    
    
    def generate_site_data_step(self,  state: AgentState):
        logger.info(f"Executing step: {inspect.currentframe().f_code.co_name}")

        site_data = self.site_data_extractor.invoke({"messages": [("user", f"Company profile: {state["company_profile"]}")]})


        # TODO this should be handled with an interrupt step
        if SETUP_DESIGN:
            setup_website_design(site_data)

        return {"site_data" : site_data}
    

    def agent_step(self, state: AgentState):
        logger.info(f"Executing step: {inspect.currentframe().f_code.co_name}")
        plan = state["plan"]
        plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
        task = plan[0]
        task_formatted = f"""For the following plan:
    {plan_str}\n\nYou are tasked with executing step {1}, {task}.
    """
        logger.info(f"Prompt: {task_formatted}")
        
        instructions = """
You are a helpful assistant that helps creating content for a company website.

Company profile description:
```
{company_profile}
```

Guidelines:
- The context of the generated website text content must always be the provided company profile description and the name of the website page (where available). For example, a text in the stage component on the home page should highlight the key aspects of the company.
- Text should ALWAYS be at least 100 words long, and elaborated on the provided company profile description.
- If a an error occurs, try to adjust the input parameters accordingly. If the same tool call fails multiple times, skip it. Do not retry the same tool call for more than 3 times. 
- Do not run the same task for more thank 3 times, if both the tool and the input parameters are not changing, skip the task and if needed return.
"""
        instructions_formatted = instructions.format(company_profile=state["company_profile"])
        # system_prompt = SystemMessage(instructions.format(company_profile=state["company_profile"]))

        agent_response = self.agent_executor.invoke({"messages":[("system", instructions_formatted),("user", task_formatted)]})
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
        
        # sitedata = state.get("site_data", {})
        
        plan = self.planner.invoke({"company_profile":  state["company_profile"],"messages": [("user", state["input"])]})

        return {"plan": plan.steps, "response": None}


    def replan_step(self, state: AgentState):
        logger.info(f"Executing step: {inspect.currentframe().f_code.co_name}")
       
        logger.debug(state)
        output = self.replanner.invoke(state)
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
            return END
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
        workflow.add_node("agent", self.agent_step)
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
            ["input_company_profile", END])


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

        if DISPLAY_AGENT_GRAPH:
            # Generate the mermaid diagram as a PNG file
            png_data = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)

            # Print the mermaid diagram in the console as mermaid syntax
            mermaid_syntax = app.get_graph().draw_mermaid()
            print(mermaid_syntax)

            # Save the PNG to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(png_data)
                tmp_file_path = tmp_file.name

            # Open the PNG file in the default web browser
            webbrowser.open(f"file://{os.path.abspath(tmp_file_path)}")

        return app


    def invoke(self, user_input, thread_config):
        inputs = {"input": user_input}
        
        for event in self.app.stream(inputs, config=thread_config):
            for k, v in event.items():
                if k != "__end__":
                    logger.debug(v)

    def invoke(self, user_input, thread_config):
        inputs = {"input": user_input}
        events = []
        
        for event in self.app.stream(inputs, config=thread_config):
            for k, v in event.items():
                if k != "__end__":
                    logger.debug(v)
                    events.append(v)
        
        return events

    
    def resume_interrupt(self, user_input, thread_config):
        self.app.invoke(Command(resume=user_input), config=thread_config)

    
    def get_interrupt(self, thread_config):
        state = self.app.get_state(thread_config)
        # logger.debug(state)
        if state.tasks and state.tasks[0].interrupts:
            return state.tasks[0].interrupts[0]
        else:
            return None
        
    def get_state(self, thread_config):
        return self.app.get_state(thread_config)
    

    def is_company_profile_loaded(self, thread_config):
        state = self.get_state(thread_config)
        return "company_profile" in state.values and state.values["company_profile"] 

    def generate_company_profile_description(self):
        llm = ChatOpenAI(temperature=0.7)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a company profile description including the company name, industry, and information about services or products offered. pick the industry randomly, e.g. fashion, tech, food, travel, wellness, etc."),
            ("user", "Please provide a company profile description.")
        ])
        response = llm.invoke(prompt.format_messages())
        return response.content