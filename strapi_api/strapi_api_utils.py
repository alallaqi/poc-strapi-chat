import os
import requests
from console_utils import *
import json
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from loguru import logger

# Strapi APIs utils functions
# 
# Note: 
# Prefer passing all the dependencies as input arguments, e.g. strapi_url.
# This will make i easy to move the functions if needed.


# Get the headers for the Strapi API
def get_heareders(strapi_api_key):
    return {
        "Authorization": f"Bearer {strapi_api_key}",
        "Content-Type": "application/json",
    }


# Load OpenAPI Definition from Strapi's schema
def load_openapi_definition(file_path: str, essential_endpoints) -> dict:
    with open(file_path) as f:
        raw_openapi_spec = json.load(f)

    filtered_paths = {}
    for path, methods in raw_openapi_spec["paths"].items():
        if path in essential_endpoints:
            filtered_methods = {
                method: spec
                for method, spec in methods.items()
                if method in essential_endpoints[path]
            }
            if filtered_methods:
                filtered_paths[path] = filtered_methods
    raw_openapi_spec["paths"] = filtered_paths
    
    openapi_spec = reduce_openapi_spec(raw_openapi_spec, dereference=False)
    return raw_openapi_spec, openapi_spec


# Count endpoints in the OpenAPI spec
def count_endpoints(raw_openapi_spec):
    endpoints = [
        (route, operation)
        for route, operations in raw_openapi_spec["paths"].items()
        for operation in operations
        if operation in ["get", "post"]
    ]
    return len(endpoints)


# Function to list all endpoints and their HTTP methods
def list_endpoints(raw_openapi_spec):
    endpoints = [
        (route, operation)
        for route, operations in raw_openapi_spec["paths"].items()
        for operation in operations
    ]
    
    for endpoint, method in endpoints:
        logger.info(f"Endpoint: {endpoint}, Method: {method.upper()}")

    return endpoints

# Create design in Strapi
def create_design(design_params, strapi_url, heareders):
    payload = {
        "data": {
            "designName": design_params['designName'],
            "primaryColor": design_params['primaryColor'],
            "secondaryColor": design_params['secondaryColor'],
        }
    }
    response = requests.post(f"{strapi_url}/designs", json=payload, headers=heareders)
    # Check the response status and print the result
    if response.status_code != 200:
        logger.error(f"Failed to create design: {response.status_code}")
        logger.error(response.text)
        return None
    
    logger("Design created successfully!")
    return response.json()["data"]

# Link a design to SiteConfig in Strapi
def link_design_to_config(design, strapi_url, headers):
    payload = {
        "data": {
            "design": design['id'],
        }
    }
    response = requests.put(f"{strapi_url}/site-config", json=payload, headers=headers)
    # Check the response status and print the result
    if response.status_code != 200:
        logger.error(f"Failed to link design: {response.status_code}")
        logger.error(response.text)
        return None
    
    logger.info("Design linked successfully!")
    return json.loads(response.text)


def upload_image_to_strapi(image_url, strapi_url, headers, tmp_images_folder="tmp_images"):
    """
    Downloads an image from the given URL and uploads it to the Strapi media library.

    :param image_url: URL of the image to download
    :param strapi_url: Base URL of the Strapi instance
    :param access_token: Optional access token for authentication
    :return: Response from the Strapi upload API
    """
    # Step 1: Download the Image
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download image from {image_url}")

    # Create the temporary images folder if it doesn't exist
    if not os.path.exists(tmp_images_folder):
        os.makedirs(tmp_images_folder)
        
    # Save the image to a temporary file
    temp_image_path = f"{tmp_images_folder}/temp_image.jpg"
    with open(temp_image_path, "wb") as file:
        file.write(response.content)

    # Step 2: Upload the Image to Strapi
    upload_endpoint = f"{strapi_url}/upload"

    # Open the image file in binary mode
    with open(temp_image_path, "rb") as file:
        files = {
            "files": file
        }

        # Remove 'Content-Type' header if it exists
        headers.pop("Content-Type", None)

        response = requests.post(upload_endpoint, files=files, headers=headers)

    # Check the response
    if response.status_code == 200:
        logger.info("Image uploaded successfully!")
        return response.json()
    else:
        raise Exception(f"Failed to upload image: {response.status_code} - {response.text}")