import os
import sys
import yaml
import logging
from typing import List, Dict, Any
import copy

# Set the model name here
MODEL_NAME = 'gpt-4'  # Options: 'gpt-4', 'gpt-3.5-turbo'

# Set recursion limit and encoding
sys.setrecursionlimit(999999)
sys.stdin.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to color terminal output
def add_color(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
            "blue": "\033[94m"
        }
    end_color = "\033[0m"
    return f"{colors.get(color, '')}{text}{end_color}"

# Load and reduce OpenAPI Definition
def load_and_reduce_openapi_definition(file_path: str):
    with open(file_path, 'r') as f:
        raw_openapi_spec = yaml.safe_load(f)
    # Reduce the OpenAPI spec to minimize token usage
    from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
    reduced_spec = reduce_openapi_spec(raw_openapi_spec)
    return reduced_spec, raw_openapi_spec  # Return both reduced and raw specs

# Build request wrapper with authorization for Strapi
def build_request_wrapper():
    STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
    if not STRAPI_API_KEY:
        raise ValueError("STRAPI_API_KEY environment variable not set.")
    headers = {
        "Authorization": f"Bearer {STRAPI_API_KEY}",
        "Content-Type": "application/json",
    }
    from langchain_community.utilities import RequestsWrapper
    return RequestsWrapper(headers=headers)

def initialize_llm(model_name):
    if model_name in ['gpt-4', 'gpt-3.5-turbo']:
        # Use OpenAI's ChatOpenAI
        from langchain_openai.chat_models import ChatOpenAI
        llm = ChatOpenAI(model_name=model_name, temperature=0.0)
    else:
        raise ValueError(f"Model name {model_name} not recognized.")
    return llm

# Function to estimate token usage
def estimate_token_usage(text: str, llm) -> int:
    # OpenAI's tokenization estimation
    from tiktoken import encoding_for_model
    encoding = encoding_for_model(llm.model_name)
    tokens = encoding.encode(text)
    return len(tokens)

def split_openapi_spec(openapi_spec: dict, max_tokens: int, llm) -> List[dict]:
    # Split the OpenAPI spec into chunks that are within max_tokens
    # We'll split the 'paths' dictionary into smaller dictionaries
    base_spec = copy.deepcopy(openapi_spec)
    paths = base_spec.pop('paths', {})
    path_items = list(paths.items())

    chunks = []
    current_chunk_paths = {}
    for path, path_info in path_items:
        current_chunk_paths[path] = path_info
        temp_spec = copy.deepcopy(base_spec)
        temp_spec['paths'] = current_chunk_paths
        spec_str = yaml.dump(temp_spec)
        if estimate_token_usage(spec_str, llm) > max_tokens:
            # Remove the last added path and save the current chunk
            current_chunk_paths.pop(path)
            temp_spec['paths'] = current_chunk_paths
            chunks.append(temp_spec)
            # Start a new chunk with the current path
            current_chunk_paths = {path: path_info}
        # Continue to next path
    # Add the last chunk
    if current_chunk_paths:
        temp_spec = copy.deepcopy(base_spec)
        temp_spec['paths'] = current_chunk_paths
        chunks.append(temp_spec)
    return chunks

def main():
    # Load and reduce Strapi's OpenAPI definition
    openapi_file_path = "./middleware/1.yaml"  # Adjust the path to your OpenAPI file
    openapi_definition, raw_openapi_spec = load_and_reduce_openapi_definition(openapi_file_path)
    logger.info("Loaded and reduced OpenAPI specification.")

    # Build the request wrapper
    requests_wrapper = build_request_wrapper()

    # Initialize the language model dynamically based on MODEL_NAME
    llm = initialize_llm(MODEL_NAME)

    # Token limit settings
    MAX_INPUT_TOKENS = 2000  # Adjust based on OpenAI's token limits

    # Split the OpenAPI spec into chunks
    openapi_chunks = split_openapi_spec(openapi_definition, MAX_INPUT_TOKENS, llm)

    # Create agents for each chunk
    from langchain_community.agent_toolkits.openapi.planner import create_openapi_agent
    ALLOW_DANGEROUS_REQUESTS = True  # Be cautious with this in production

    agents = []
    for chunk in openapi_chunks:
        agent = create_openapi_agent(
            chunk,
            requests_wrapper,
            llm,
            allow_dangerous_requests=ALLOW_DANGEROUS_REQUESTS,
            verbose=True
        )
        agents.append(agent)

    print(add_color(f"Middleware Assistant is now running with {MODEL_NAME}. You can start interacting with it.", "blue"))
    while True:
        try:
            user_query = input(add_color("\n[Middleware Assistant] Enter your message:\n", "yellow"))
            if user_query.lower() in ["exit", "quit"]:
                print(add_color("Exiting Middleware Assistant. Goodbye!", "blue"))
                break

            # Process the user query with each agent until one can handle it
            response = None
            for agent in agents:
                try:
                    response = agent.invoke({"input": user_query})
                    if response:
                        break
                except Exception as e:
                    logger.info(f"Agent failed to process the query: {e}")
                    continue

            if response:
                print(add_color(f"\n[Assistant]: {response['output']}", "green"))
            else:
                print(add_color("I'm sorry, I couldn't process your request.", "red"))

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            print(add_color("An error occurred while processing your request. Please try again.", "red"))

if __name__ == "__main__":
    main()
