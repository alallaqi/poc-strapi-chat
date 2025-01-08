import operator
from typing import Annotated, List, Tuple, Union
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class PageContent(BaseModel):
    """Content of a page"""

    heading: str = Field(description="Item heading")
    text: str = Field(description="Item text, at least 100 words")


class SiteData(BaseModel):
    """Initial data to set up web site design and structure."""
    
    company_name: str = Field(description="Company name")
    industry: str = Field(description="The industry in which the company operates")
    short_description: str = Field(description="A short description")
    image_generation_prompt: str = Field(description="Prompt for generating related images")
    primary_color: str = Field(description="A random primary background color in hex value that works for a modern minimalistic website, and may be related to the industry of the company.")
    secondary_color: str = Field(description="A secondary accent color in hex value that works well with the primary color")
    design_name: str = Field(description="The name to use for the design.")
    footer_next: str = Field(description="A short footer text")
    # Currently not used
    website_structure: str = Field(description="""The structure of the website as a list of pages, where each page can several components of the following types: text, image, stage.  
Default structure: 
- Page Home: 1 stage component, 2 images and 2 text components.
- Page Services: 2 images 2 text components.
- Page Contact: 1 text component.
                                
Add additional components and pages as needed to make the website look professional.
Do NOT provide the content of the components, only the structure.""")
    error: str = Field(description="Error message")

    
class Error(BaseModel):
    """Error response"""

    error: str = Field(description="Error message")

class ExtractedSiteData:
    """Extracted site data"""

    data: Union[SiteData, Error] = Field(
            description="Extracted site data. If there are validation errors, use Error, otherwise use SiteData"
        )

class Response(BaseModel):
    """Response to user."""

    response: str


class Plan(BaseModel):
    """A step-by-step plan to follow in future"""

    steps: List[str] = Field(
        description="List of steps to follow, should be in sorted order."
    )   


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )


class AgentState(MessagesState):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    company_profile: str
    site_data: SiteData
    response: str
    end: bool
    user_feedback: str