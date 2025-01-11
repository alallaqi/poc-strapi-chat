import random
from console_utils import *
from agent_models import SiteData
from strapi_api.strapi_api_utils import *
from langchain.agents import tool
from loguru import logger
from langchain_community.agent_toolkits.load_tools import load_tools


# Load environment variables from .env file
from dotenv import load_dotenv  # Import load_dotenv
load_dotenv()  # Load the .env file

STRAPI_API_URL = os.getenv("STRAPI_API_URL") # "http://localhost:1337/api"
STRAPI_API_KEY = os.getenv("STRAPI_API_KEY")
strapi_headers = get_heareders(STRAPI_API_KEY)
IMAGES_TO_GENERATE_COUNT = 2


@tool
def create_page(title: str, route: str, seoTitle: str, seoDescription: str) -> str:
    """Create a new page.

    Args:
        title: title of the page
        route: route of the page, e.g. /home
        seoTitle: Title for search engine optimization 
        seoDescription: Description for search engine optimization 
    """
    logger.info(f"Creating a new page with title: '{title}' and route: '{route}'")
    payload = {
        "data": {
            "title": title,
            "route": route,
            "seoTitle": seoTitle,
            "seoDescription": seoDescription,
        }
    }
    request_url = f"{STRAPI_API_URL}/content-pages"
    response = send_request('post', request_url, json=payload, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        logger.error(f"Failed to create {title} page: {response.status_code}")
        logger.error(response.text)
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
        logger.error(f"Failed to get images: {response.status_code}")
        logger.error(response.text)
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
        logger.error(f"Failed to get pages: {response.status_code}")
        logger.error(response.text)
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
        logger.error(f"Failed to get page: {response.status_code}")
        logger.error(response.text)
        return response
    
    logger.info("Page retrieved successfully!")
    return response.json()



@tool
def add_component_stage(page_id: int, main_text: str, image_id: str) -> object:
    """Add a stage component to an existing page.

    Args:
        page_id: id of the page to update
        main_text: text of the stage component
        image_id: id of the image
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
        logger.error(f"Failed to create component: {response.status_code}")
        logger.error(response.text)
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


# Consider to include as tools
def generate_ai_image(image_generation_prompt: str) -> object:
    """Generate an image using an AI model.

    Args:
        image_generation_prompt: prompt to generate the image
    """
    logger.info(f"Generating an image with prompt: '{image_generation_prompt}'")
    dalle_tool = load_tools(["dalle-image-generator"], model_name='dall-e-3')[0]
    image_url = dalle_tool.invoke(image_generation_prompt)
    return upload_image_to_strapi(image_url, STRAPI_API_URL, strapi_headers)


# Consider to include as tools - The input should be simplified into a list of simple types
def setup_website_design(site_data: SiteData):
    """Set up the website theme and upload a few demo images.

    Args:
        site_data: details of the web site
    """
   
    logger.info("Setting up the website theme..")
    
    img_count = IMAGES_TO_GENERATE_COUNT
    logger.info(f"Generatig and uploading {img_count} demo images..")
    
    images = []
    for _ in range(img_count):
        image = generate_ai_image(site_data.image_generation_prompt)
        images.append(image)

    
    logo_image_id = None
    if images:
        logo_image = random.choice(images)
        logo_image_id = logo_image[0]["id"]
        
    
    
    logger.info(F"Creating the design..")
    design = create_design(site_data, STRAPI_API_URL, strapi_headers)
    setup_site_config(design, logo_image_id, STRAPI_API_URL, strapi_headers)

  
@tool
def add_page_to_navigation_menu(title: str, page_id: int) -> object:
    """Add a new item in the navigation menu 

    Args:
        title: title of the item n the navigation menu
        page_id: id of the page to link in the navigation menu
    """
    logger.info(f"Adding the item with title: '{title}' to the navigation menu")

    payload = {
        "data": {
            "title": title,
            "page": page_id,
            # "NavigationMenuItems": [
            #     {
            #         "id": page_id,
            #         "title": title,
            #         "page": {
            #             "data": {
            #                 "id": page_id,
            #                 "attributes": {}
            #             }
            #         }
            #     }
            # ],
            "sortID": 1,
            # "locale": locale
        }
    }

    # Check if the navigation menu already exists
    request_url = f"{STRAPI_API_URL}/navigation-menus"
    
    # Create a new navigation menu
    response = send_request('post', request_url, json=payload, headers=strapi_headers)
    if response.status_code != 200:
        logger.error(f"Failed to create navigation menu item: {response.status_code}")
        logger.error(response.text)
        return response
    logger.info("Navigation menu item created successfully!")

    return response.json()["data"]

@tool
def update_footer_copyright(copyright: str) -> object:
    """Update the footer copiryght text

    Args:
        copyright: text of the copyright component
    """
    logger.info(f"Update the footer copytight")
    
    payload = {
        "data": {
            "copyright": {
                "text": copyright
            }
        }
    }
    
    request_url = f"{STRAPI_API_URL}/footer"
    response = send_request('put', request_url, json=payload, headers=strapi_headers)
    # Check the response status and print the result
    if response.status_code != 200:
        logger.error(f"Failed to update footer: {response.status_code}")
        logger.error(response.text)
        return response
    
    logger.info("Footer updated successfully!")
    return response.json()["data"]


@tool
def add_footer_link(text: str, url: str) -> object:
    """
    Adds a new link to the footer.
    
    Args:
        text (str): The text for the new footer link.
        url (str): The URL for the new footer link.
    """
    logger.info(f"Adding a footer link with text: '{text}' and url: '{url}'")

    # Get the current footer content
    request_url = f"{STRAPI_API_URL}/footer"
    response = send_request('get', request_url, headers=strapi_headers)
    if response.status_code != 200:
        logger.error(f"Failed to get footer: {response.status_code}")
        logger.error(response.text)
        return response

    footer_data = response.json()
    footer_links = footer_data.get("footer_links", [])

    # Remove the "id" from each footer link
    for link in footer_links:
        if "id" in link:
            del link["id"]

    # Append the new footer link
    footer_links.append({"text": text, "url": url})

    # Update the footer with the new list of footer links
    payload = {
        "data": {
            "footer_links": footer_links
        }
    }

    response = send_request('put', request_url, json=payload, headers=strapi_headers)
    if response.status_code != 200:
        logger.error(f"Failed to update footer: {response.status_code}")
        logger.error(response.text)
        return response

    logger.info("Footer link added successfully!")
    return response.json()["data"]
   
