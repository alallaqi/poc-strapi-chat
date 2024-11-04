def create_home_page(page_data):
    return f"""
    # Context
    You are an assistant that helps with creating website content using Strapi's APIs.

    # Objective
    High level steps to create a new content page using Strapi's APIs: 
    1. **GET /upload/files** to retrieve a list of image URLs. This will provide the necessary image resources needed for creating the content page.
    2. **POST /content-pages** to create a new content page. 
       - The request should include all 4 components listed in the <<page components>> section.
       - The input data for the request is defined in <<input data>>.
       - Set the route to "/" to designate it as the home page.
       - Provide a meaningful title for the page.
        - Consider the sample JSON request provided in the <<sample json request>> section for schema guidance.
    3. **POST /navigation-menus** to create a navigation menu use the <<navigation menu request body>.>
       - The request should include links to the created pages.
       - Ensure every page is configured in the navigation using the page id.
    
     - Consider the sample JSON request provided in the <<sample json request>> section for schema guidance.
     
    Make sure to follow the instructions in the <<page components>> section to create the content page and replace the placeholders with the actual content.
    
    <<page components>>
    - 1x Stage component: 
        - as subtitle, put a "heading" selected from one of the content items in <<input data>>.
        - as image, use the "id" of an image from the list retrieved in step 1.
    - 1x text component: put the "text" from another content item, with the color inverted.
    - 1x text component: put the "text" from the same  selected in the previous point.
    - 1x image component: use the "id" of another image from the list retrieved in step 1.
    <</page components>>

    <<input data>>
    {page_data}
    <</input data>>

    <<sample json request>>
    {{
        "data": {{
            "title": <page name>,
            "route": <page route>,
            "content": [
                {{
                    "__component": "content.stage",
                    "invertColors": false,
                    "subtitle": [
                        {{
                        "type": "paragraph",
                        "children": [
                            {{
                            "type": "text",
                            "text": <content item heading>
                            }}
                        ]
                        }}
                    ],
                    "image": <image ID>
                }},
                {{
                    "__component": "content.text",
                    "invertColors": false,
                    "text": [
                        {{
                            "type": "paragraph",
                            "children": [
                                {{
                                    "type": "text",
                                    "text": <content item text>
                                }}
                            ]
                        }}
                    ]
                }},
                {{
                    "__component": "content.image",
                    "image": <image ID>,
                    "padding": true,
                    "invertColors": false
                }}
            ]
        }}
    }}
    <</sample json request>>

    <<navigation menu request body>>
    {{
        "data": {{
            "title": "Home",
            "page": "id of the created page",
            "NavigationMenuItems": [
                {{
                    "id": 0,
                    "title": "string",
                    "page": {{
                        "data": {{
                            "id": 0,
                            "attributes": {{}}
                        }}
                    }}
                }}
            ],
            "sortID": 0,
            "navigationTag": "string or id",
            "locale": "string"
        }}
    }}
    <</navigation menu request body>>
    """