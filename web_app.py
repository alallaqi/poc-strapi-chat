import os
from flask import Flask
from flask_socketio import SocketIO, emit
from langchain_openai import ChatOpenAI
from strapi_agent import StrapiAgent
from strapi_api.strapi_api_utils import get_heareders

app = Flask(__name__)
socketio = SocketIO(app)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

STRAPI_API_URL = os.getenv("STRAPI_API_URL")
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
FRONT_END_URL = os.getenv("FRONT_END_URL")

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
strapi_headers = get_heareders(STRAPI_API_KEY)
agent = StrapiAgent(STRAPI_API_URL, strapi_headers, llm)

thread_id = 1
thread_config = {"recursion_limit": 25, "configurable": {"thread_id": thread_id}}
content_creation_prompts = [
    "Create a page 'Home' with route '/home' and it to the navigation menu",
    "Add a 'Stage' component to the 'Home' page",
    "Add 1 text component and 1 image to the 'Home' page",
    "Create a 'Contacts' page with route '/contacts' and it to the navigation menu",
    "Add a text component to the contacts page with a list of dummy contacts.",
    "Create a page 'About' with route '/about' and it to the navigation menu",
    "Add a 2 text component to the 'About' page highlighing 2 main services offered by the company.",
    "Add the copyright in the footer, make sure to use the current year 2025.",
]

agent.invoke("Hi", thread_config)

@app.route("/")
def index():
    return app.send_static_file('index.html')

@socketio.on('get_ui_setup')
def handle_get_ui_setup():
    emit('loading_start')
    emit('ui_setup', {'preview_host': FRONT_END_URL})
    emit('loading_stop')

@socketio.on('send_context')
def handle_send_context(data):
    emit('loading_start')
    user_input = data.get("input")
    setup_template = data.get("setupTemplate", False)
    
    interrupt = agent.get_interrupt(thread_config)
    if interrupt:
        agent.resume_interrupt(user_input, thread_config)

    if not agent.is_company_profile_loaded(thread_config):
        emit('context_not_valid')
        emit('loading_stop')
        return
        
    emit('context_valid')
    
    
    if setup_template:
        for item in content_creation_prompts:
            events = agent.invoke(item, thread_config)
            
            for event in events:
                emit('agent_event', {'event': event})
                

    emit('loading_stop')

@socketio.on('check_context')
def handle_check_context():
    if agent.is_company_profile_loaded(thread_config):
        state = agent.get_state(thread_config)
        emit('context_valid', {'company_profile': state.values["company_profile"]})
    else:
        emit('context_not_valid')


@socketio.on('send_message')
def handle_send_message(data):
    emit('loading_start')

    if not agent.is_company_profile_loaded(thread_config):
        emit('context_not_valid')
        emit('loading_stop')
        return
        
    user_input = data.get("input")
    events = agent.invoke(user_input, thread_config)
    for event in events:
        emit('agent_event', {'event': event})
    
    
    emit('loading_stop')


@socketio.on('generate_company_profile')
def handle_generate_company_profile():
    emit('loading_start')
    description = agent.generate_company_profile_description()
    emit('company_profile', {'company_profile': description})
    emit('loading_stop')

if __name__ == "__main__":
    socketio.run(app, debug=True)
