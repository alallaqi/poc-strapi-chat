
def create_home_page(page_data):
      return f"""
    # Context
    You are an assistant that helps with creating website content using Strapi's APIs.

    # Objective
    High level steps to create a new content page using Strapi's APIs: 
    1. **GET /upload/files** to retrieve a list of image URLs. This will provide the necessary image resources needed for creating the content page.
    2. **POST /content-pages** to create a new content page. 
       - The request should include all the components listed in the <<page components>> section.
       - Use the input data defined in <<input data>> as input.
       - A sample JSON request is provided in the <<sample json request>> section for schema guidance.
    
    <<page components>>
    - 1x Stage component: 
        - as subtitle, put a "heading" selected from one of the content items in <<input data>>.
        - as image, an image from the list retrieved in step 1.
    - 1x text component: put the "text" from the same  selected in the previous point.
    - 1x text component: put the "text" from another content item, with the color inverted.
    - 1x image component: another image from the list retrieved in step 1.
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
                    "invertColors": false
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
    """


def get_content_creation_prompt(company_profile):
    return f"""
    # Context
    You are an assistant that helps with creating website content using Strapi's APIs.

    # Objective
    Given the company profile in the <company profile> section below, create:
    1. One main content page with elements listed in the <page elements> section. In the <sample request> section, an example of the request payload is provided for schema guidance; follow the instructions in <page elements> for the actual content.
    2. A contact page with dummy contact information and a professional tone.
    3. A navigation menu with links to the created pages. Make sure every page is configured in the navigation.

    <company profile>
    {company_profile}

    <page elements>
    - 1x Stage component: In this section put a subtitle derived from the <company profile>.
    - 1x text component: In this text section you need to put some text and multiple expanded bullet points derived from the <company profile>.
    - 1x text component: with the color inversed and more detailed text on <company profile>.
    - 1x image component: Include an image that represents the company. Use a placeholder image URL for now.
    - 1x CTA component: Include a call-to-action with the text "Learn More" that routes to the contact us page.

    # API Calls 
    Use one POST request for each of the 3 points in the #Objective. Make sure to wrap the request in a JSON object with a 'data' key.
    
    # Sample Request    
    <sample request>
    {{
        "data": {{
            "title": "string",
            "route": "string",
            "content": [
                {{
                    "__component": "content.stage",
                    "subtitle": [
                        {{
                            "type": "paragraph",
                            "children": [
                                {{
                                    "type": "text",
                                    "text": "Subtitle derived from the company profile."
                                }}
                            ]
                        }}
                    ]
                }},
                {{
                    "__component": "content.text",
                    "text": [
                        {{
                            "type": "paragraph",
                            "children": [
                                {{
                                    "type": "text",
                                    "text": "We have state-of-the-art gym equipment."
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
    }}
    </sample request>
    """