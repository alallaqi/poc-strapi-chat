from langchain_core.messages import  HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import tools_condition
from langgraph.errors import NodeInterrupt
from langchain import hub
from strapi_tools import *
from langgraph.prebuilt import create_react_agent
import json
from prompts import preprocessing_prompts, content_prompts
from console_utils import *
from strapi_api.strapi_api_utils import *
from sample_companies import *
from IPython.display import display, Markdown
import operator
from typing import Annotated, List, Tuple, Union
from typing_extensions import TypedDict
from pydantic import BaseModel,Field
from agents_deconstructed.format_tools import format_tools_args

from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file


# To rewrite based on this:
# https://medium.com/@Shrishml/a-primer-on-ai-agents-with-langgraph-understand-all-about-it-0534345190dc


class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str


class MessagesState(MessagesState):
    strapi_url: str
    headers: object
    company_profile: str
    website_data: object
    pass

class Response(BaseModel):
    """Response to user."""

    response: str


class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )   


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )



class StrapiAgent:
    def __init__(self, strapi_url: str, headers: object, llm: ChatOpenAI):

        # not yet passed to the tools
        self.strapi_url = strapi_url
        self.headers = headers
        self.llm = llm

        self.tools = [
            create_page,
            add_component_stage,
            add_component_text,
            add_component_image,
            get_pages,
            get_images]

     
        self.agent_executor = create_react_agent(self.llm, self.tools,  messages_modifier=self.messages_modifier)

        planner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """For the given objective, come up with a simple step by step plan, using ONLY the following tools: \
                    
        ```
        {tools}
        ```

        This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
        The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.""",
                ),
                ("placeholder", "{messages}"),
            ]
        )

        planner_prompt = planner_prompt.partial(
            tools = format_tools_args(self.tools),
        )
        self.planner = planner_prompt | ChatOpenAI(temperature=0).with_structured_output(Plan)
        

        replanner_prompt = ChatPromptTemplate.from_template(
            """For the given objective, come up with a simple step by step plan, using ONLY the following tools: \
                    
        ```
        {tools}
        ```

        This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
        The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

        Your objective was this:
        {input}

        Your original plan was this:
        {plan}

        You have currently done the follow steps:
        {past_steps}

        Update your plan accordingly. If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done.""",
        )
        replanner_prompt = replanner_prompt.partial(
            tools = format_tools_args(self.tools),
        )
        self.replanner = replanner_prompt | ChatOpenAI(temperature=0).with_structured_output(Act)
        
        self.app = self.build_graph()


    def messages_modifier(self, messages: list):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("placeholder", "{messages}"),
        ])
        return prompt.invoke({"messages": messages})


    async def execute_step(self, state: PlanExecute):
        plan = state["plan"]
        plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
        task = plan[0]
        task_formatted = f"""For the following plan:
    {plan_str}\n\nYou are tasked with executing step {1}, {task}."""
        agent_response = await self.agent_executor.ainvoke(
            {"messages": [("user", task_formatted)]}
        )
        return {
            "past_steps": [(task, agent_response["messages"][-1].content)],
        }
    

    async def plan_step(self, state: PlanExecute):
        plan = await self.planner.ainvoke({"messages": [("user", state["input"])]})
        return {"plan": plan.steps}


    async def replan_step(self, state: PlanExecute):
        output = await self.replanner.ainvoke(state)
        if isinstance(output.action, Response):
            return {"response": output.action.response}
        else:
            return {"plan": output.action.steps}


    def should_end(self, state: PlanExecute):
        if "response" in state and state["response"]:
            return END
        else:
            return "agent"


    def build_graph(self):

        workflow = StateGraph(PlanExecute)

        # Add the plan node
        workflow.add_node("planner", self.plan_step)

        # Add the execution step
        workflow.add_node("agent", self.execute_step)

        # Add a replan node
        workflow.add_node("replan", self.replan_step)

        workflow.add_edge(START, "planner")

        # From plan we go to agent
        workflow.add_edge("planner", "agent")

        # From agent, we replan
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
        app = workflow.compile()

        return app


    async def invoke(self, user_input):

        config = {"recursion_limit": 20}
        inputs = {"input": user_input}
        async for event in self.app.astream(inputs, config=config):
            for k, v in event.items():
                if k != "__end__":
                    print(v)
                    




        # plan = self.planner.invoke(
        #     {
        #         "messages": [("user", "Create a new page with title: 'Home' and route: '/', and add a stage component.")],
        #     }
        # )

        # print(plan)

        # config = {"configurable": {"thread_id": "2"}}
        # input_message = HumanMessage(
        #     content="Ask the user for a compny profile text, create a summary, and then call the tool to add the summary as text component in the home page.'"
        # )
        # for event in self.app.stream({"messages": [input_message]}, config, stream_mode="values"):
        #     event["messages"][-1].pretty_print()


        # tool_call_id = self.app.get_state(config).values["messages"][-1].tool_calls[0]["id"]

        # # We now create the tool call with the id and the response we want
        # company_profile = sample_companies["valid"]["wellness"]
        # tool_message = [
        #     {"tool_call_id": tool_call_id, "type": "tool", "content": company_profile}
        # ]
        # self.app.update_state(config, {"messages": tool_message}, as_node="ask_human")
        # self.app.get_state(config).next

        # for event in self.app.stream(None, config, stream_mode="values"):
        #     event["messages"][-1].pretty_print()

        # return

