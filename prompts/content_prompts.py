def create_home_page(page_data):
    return f"""
    # Context
    You are an assistant that helps with creating website content using Strapi's APIs.

    # Objective
    High level steps to create a new content page using Strapi's APIs: 
    1. **GET /upload/files** to retrieve a list of image URLs. This will provide the necessary image resources needed for creating the content page.
    
    2. **POST /content-pages** to create a new content page. Make sure to:
       - use the sample request in <<content-page request example>> for the request schema.
       - include in the content:
            - 1x content.stage component: 
                - as subtitle, put a "heading" selected from one of the content items in <<input data>>.
                - as image, use the "id" of an image from the list retrieved in step 1.
            - 1x text component: put the "text" from another content item, with the color inverted.
            - 1x text component: put the "text" from the same  selected in the previous point.
            - 1x image component: use the "id" of another image from the list retrieved in step 1.
        - use the input data defined in <<input data>>.
    3. **POST /navigation-menus** to create a navigation menu use the <<navigation menu request body>>
       - Ensure every page is configured in the navigation using the page id.
    
    
    <<input data>>
    {page_data}
    <</input data>>

    <<content-page request example>>
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
    <</content-page request example>>

    <<navigation menu request body>
    {{
        "data": {{
            "title": "Home",
            "page": "Id of the created page",
            "NavigationMenuItems": [
                {{
                    "id": "Id of the created page",
                    "title": "string",
                    "page": {{
                        "data": {{
                            "id": 0,
                            "attributes": {{}}
                        }}
                    }}
                }}
            ],
            "sortID": 1,
            "navigationTag": "string or id",
            "locale": "string"
        }}
    }}
    <</navigation menu request body>>
    """