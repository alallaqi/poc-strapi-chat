import requests
from console_utils import *
from strapi_api.strapi_api_utils import *
from langchain.agents import tool
from loguru import logger


# TODO: define handle how to handle the errors from the API calls, in a way that the model can understand

# Load environment variables from .env file
from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file

STRAPI_API_URL = os.getenv("STRAPI_API_URL") # "http://localhost:1337/api"
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
strapi_headers = get_heareders(STRAPI_API_KEY)


def send_request(method, url, **kwargs):
    """Log the request and make the HTTP request.

    Args:
        method: HTTP method (e.g., 'get', 'post', 'put', etc.)
        url: URL for the request
        **kwargs: Additional arguments passed to the request method
    """
    print_color(f"{url}\n{kwargs.get('json', '')}", "grey")
    response = requests.request(method, url, **kwargs)
    print_color(f"Response: {response.status_code}\n{response.text}", "grey")
    # if response.status_code != 200:
    #     print_color(f"Failed request: {response.status_code}", "red")
    #     print(response.text)
    # else:
    #     print_color("Request successful!", "green")
    return response


@tool
def create_page(title: str, route: str) -> str:
    """Create a new page.

    Args:
        title: title of the page
        route: route of the page
    """
    print(f"Creating a new page with title: '{title}' and route: '{route}'")
    payload = {
        "data": {
            "title": title,
            "route": route
        }
    }
    request_url = f"{STRAPI_API_URL}/content-pages"
    response = send_request('post', request_url, json=payload, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        print_color(f"Failed to create {title} page: {response.status_code}", "red")
        print(response.text)
        return response
    
    logger.info("Page created successfully!")
    return response.json()["data"]


@tool
def get_images() -> object:
    """Get all images from the Strapi API. Used to find the id of the an image."""

    print("Getting all images")
    request_url = f"{STRAPI_API_URL}/upload/files"
    response = send_request('get', request_url, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        print_color(f"Failed to get images: {response.status_code}", "red")
        print(response.text)
        return response
    
    logger.info("Images retrieved successfully!")
    return response.json()



@tool
def get_pages() -> object:
    """Get the list of all pages of the web site from the Strapi API. 
    Used to find the id of the a page."""

    logger.info("Getting all pages")
    request_url = f"{STRAPI_API_URL}/content-pages"
    response = send_request('get', request_url, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        print_color(f"Failed to get pages: {response.status_code}", "red")
        print(response.text)
        return response
    
    logger.info("Pages retrieved successfully!")
    return response.json()



def get_page(page_id: int) -> object:
    """Get the content a single pages from the Strapi API, vased on the page id.
     
    Args:
        page_id: id of the page to update
    """
    logger.info(f"Getting the page with id pages {page_id}")
    request_url = f"{STRAPI_API_URL}/content-pages/{page_id}"
    response = send_request('get', request_url, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        print_color(f"Failed to get page: {response.status_code}", "red")
        print(response.text)
        return response
    
    logger.info("Page retrieved successfully!")
    return response.json()



@tool
def add_component_stage(page_id: int, main_text: str, image_id: str) -> object:
    """Add a stage component to an existing page.

    Args:
        page_id: id of the page to update
        main_text: text of the stage component
    """
    logger.info(f"Adding a stage component to the page with id {page_id}")

    content = get_page(page_id)["content"]
    content.append({
        "__component": "content.stage",
        "invertColors": False,
        "subtitle": [
            {
                "type": "paragraph",
                "children": [
                    {
                        "type": "text",
                        "text": main_text
                    }
                ]
            }
        ],
        "image": image_id
    })

    payload = {
        "data": {
           "content": content
        }
    }
    request_url = f"{STRAPI_API_URL}/content-pages/{page_id}"
    response = send_request('put', request_url, json=payload, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        print_color(f"Failed to create component: {response.status_code}", "red")
        print(response.text)
        return response
    
    logger.info("Component successfully!")
    return response.json()["data"]


@tool
def add_component_image(page_id: int, image_id: str) -> object:
    """Add an image component to an existing page.

    Args:
        page_id: id of the page to update
        image_id: id of the image to add
    """
    logger.info(f"Adding an image component to the page with id {page_id}")

    content = get_page(page_id)["content"]
    content.append({
        "__component": "content.image",
        "image": image_id,
        "padding": True,
        "invertColors": False
    })

    payload = {
        "data": {
           "content": content
        }
    }
    request_url = f"{STRAPI_API_URL}/content-pages/{page_id}"
    response = send_request('put', request_url, json=payload, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        logger.error(f"Failed to create component: {response.status_code}")
        logger.error(response.text)
        return response
    
    logger.info("Component added successfully!")
    return response.json()["data"]


@tool
def add_component_text(page_id: int, main_text: str) -> object:
    """Add a text component to an existing page.

    Args:
        page_id: id of the page to update
        main_text: text of the text component
    """
    logger.info(f"Adding a text component to the page with id {page_id}")

    content = get_page(page_id)["content"]
    content.append({
        "__component": "content.text",
        "invertColors": False,
        "text": [
            {
                "type": "paragraph",
                "children": [
                    {
                        "type": "text",
                        "text": main_text
                    }
                ]
            }
        ]
    })

    payload = {
        "data": {
           "content": content
        }
    }
    
    logger.debug(payload)
    request_url = f"{STRAPI_API_URL}/content-pages/{page_id}"
    response = send_request('put', request_url, json=payload, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        logger.error(f"Failed to create component: {response.status_code}")
        logger.error(response.text)
        return response
    
    logger.info("Component added successfully!")
    return response.json()["data"]
