import os
import sys
import yaml
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
import json  # Add this line at the top of your file with other imports

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA, ConversationChain
from langchain.callbacks import StdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

from langchain_community.utilities import RequestsWrapper
from langchain_community.tools import OpenAPISpec
from langchain_community.agent_toolkits.openapi.planner import create_openapi_agent
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.tools import APIOperation
from langchain_community.tools.requests.tool import RequestsGetTool, RequestsPostTool, RequestsPatchTool, RequestsDeleteTool
from langchain_community.agent_toolkits.openapi import planner

# Load environment variables
load_dotenv()

# Set recursion limit and encoding
sys.setrecursionlimit(1000000)
sys.stdin.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Load and reduce OpenAPI Definition
def load_and_reduce_openapi_definition(file_path: str):
    with open(file_path, 'r') as f:
        raw_openapi_spec = yaml.safe_load(f)
    reduced_spec = reduce_openapi_spec(raw_openapi_spec)
    return reduced_spec, raw_openapi_spec

# Build request wrapper with authorization for Strapi
def build_request_wrapper():
    STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
    if not STRAPI_API_KEY:
        raise ValueError("STRAPI_API_KEY environment variable not set.")
    headers = {
        "Authorization": f"Bearer {STRAPI_API_KEY}",
        "Content-Type": "application/json",
    }
    return RequestsWrapper(headers=headers)

# Set up Retrieval Augmented Generation components
def setup_retriever():
    loader = TextLoader('suggestions.txt')
    documents = loader.load()
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    return retriever

# Validate user input against OpenAPI schema
def validate_input(schema: Dict[str, Any], user_input: Any) -> bool:
    # Implement validation logic based on the OpenAPI schema
    # This is a simplified example and should be expanded based on your needs
    if 'type' in schema:
        if schema['type'] == 'string' and not isinstance(user_input, str):
            return False
        elif schema['type'] == 'integer' and not isinstance(user_input, int):
            return False
        # Add more type checks as needed
    return True

# Get user input for a specific field
def get_user_input(field_name: str, schema: Dict[str, Any]) -> Any:
    while True:
        user_input = input(add_color(f"\nPlease enter {field_name}: ", "yellow"))
        if validate_input(schema, user_input):
            return user_input
        else:
            print(add_color(f"Invalid input. Please try again.", "red"))

def load_and_process_openapi_spec(spec_path: str) -> OpenAPISpec:
    """Load and process the OpenAPI specification."""
    with open(spec_path, "r") as file:
        raw_spec = file.read()
    spec = OpenAPISpec.from_text(raw_spec)
    logger.info("Loaded and reduced OpenAPI specification.")
    return spec

def create_vector_store(docs: List[Document]) -> FAISS:
    """Create a vector store from the given documents."""
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    return FAISS.from_documents(texts, embeddings)

def setup_rag_chain(vector_store: FAISS) -> ConversationChain:
    """Set up the RAG chain."""
    llm = ChatOpenAI(temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    template = """You are an AI assistant for a headless CMS called Strapi. Use the following pieces of context to answer the human's question. If you don't know the answer, just say that you don't know, don't try to make up an answer.

    {context}

    Human: {human_input}
    AI: """
    prompt = PromptTemplate(
        input_variables=["context", "human_input"], template=template
    )
    return ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )

def create_middleware_agent(spec: OpenAPISpec) -> AgentExecutor:
    """Create the middleware agent."""
    llm = ChatOpenAI(temperature=0)
    tools = []

    for path, methods in spec.paths.items():
        for method, operation in methods.items():
            if method.lower() == 'get':
                tool_class = RequestsGetTool
            elif method.lower() == 'post':
                tool_class = RequestsPostTool
            elif method.lower() == 'patch':
                tool_class = RequestsPatchTool
            elif method.lower() == 'delete':
                tool_class = RequestsDeleteTool
            else:
                continue  # Skip unsupported methods

            tool = tool_class(
                name=operation.get('operationId', f"{method}_{path}"),
                description=operation.get('summary', ''),
                url=f"{spec.servers[0]['url']}{path}",
                method=method.upper(),
                allow_dangerous_requests=True
            )

            # Add required parameters to the tool's description
            if 'parameters' in operation:
                required_params = [p for p in operation['parameters'] if p.get('required', False)]
                if required_params:
                    tool.description += "\nRequired parameters:\n"
                    for param in required_params:
                        tool.description += f"- {param['name']} ({param['in']}): {param.get('description', '')}\n"

            # Add request body information if present
            if 'requestBody' in operation:
                content = operation['requestBody'].get('content', {})
                if 'application/json' in content:
                    schema = content['application/json'].get('schema', {})
                    if 'properties' in schema:
                        tool.description += "\nRequest body (JSON):\n"
                        for prop, details in schema['properties'].items():
                            required = prop in schema.get('required', [])
                            tool.description += f"- {prop}: {details.get('type', 'any')} {'(required)' if required else ''}\n"

            tools.append(tool)

    prompt = OpenAIFunctionsAgent.create_prompt()
    agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
    )

def main():
    # Load and reduce Strapi's OpenAPI definition
    openapi_file_path = os.getenv("OPENAPI_FILE_PATH", "./middleware/specific.yaml")
    openapi_definition, raw_openapi_spec = load_and_reduce_openapi_definition(openapi_file_path)
    logger.info("Loaded and reduced OpenAPI specification.")

    # Build the request wrapper
    requests_wrapper = build_request_wrapper()

    # Initialize the language model
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4", temperature=0.0)

    # Create the middleware agent for OpenAPI
    ALLOW_DANGEROUS_REQUESTS = True
    middleware_agent = planner.create_openapi_agent(
        openapi_definition, 
        requests_wrapper, 
        llm, 
        allow_dangerous_requests=ALLOW_DANGEROUS_REQUESTS
    )

    print(add_color("Middleware Assistant: Let's set up your site content.", "blue"))

    while True:
        input_message = input(add_color("\n[Middleware Assistant] Enter your message (or 'quit' to exit):\n", "yellow"))
        if input_message.lower() == 'quit':
            break
        response = middleware_agent.invoke(input_message)
        print(add_color(f"[Assistant]: {response}", "green"))

    print(add_color("\nSetup complete! Your site content has been configured.", "blue"))

if __name__ == "__main__":
    main()