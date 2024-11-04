
def create_home_page(page_data):
      return f"""
    # Context
    You are an assistant that helps with creating website content using Strapi's APIs.

    # Objective
    Create a content-page, with the elements listed in  <page elements>, use the <actual data> for the values. A sample request is provided in the <sample request> section.
    befor you start, make sure to retrieve first the image to use then in the request.
    
    <page elements>
    - use the title and route from the <actual data> section.
    - 1x Stage component: 
        - as subtitle, put a "heading" selected from one of the content items in <page_data>.
        - as image, use a GET request to /upload/files to get a list of images url, and select a random one.
    - 1x text component: put the "text" from the same  selected in the previous point.
    - 1x text component: put the "text" from another content item, with the color inversed. 
    </page elements>

    <actual data>
    {page_data}
    </actual data>
    
    <sample request>
    {{
        "data": {{
            "title": "page name",
            "route": "page route",
            "content": [
                {{
                    "__component": "content.stage",
                    "subtitle": [
                        {{
                        "type": "paragraph",
                        "children": [
                            {{
                            "type": "text",
                            "text": "Welcome to FitWell..."
                            }}
                        ]
                        }}
                    ],
                    "invertColors": null,
                    "image": {{
                        "data": null
                    }},
                    "stageImage": {{
                        "id": 1,
                        "url": "/uploads/image.jpg",
                        "thumbnailUrl": "/uploads/thumbnail_image.jpg",
                        "smallUrl": "/uploads/small_image.jpg"
                        "alternativeText": "",
                        "width": 600,
                        "height": 400,
                    }}
                }},
                {{
                    "__component": "content.text",
                    "text": [
                        {{
                            "type": "paragraph",
                            "children": [
                                {{
                                    "type": "text",
                                    "text": "We have ..."
                                }}
                            ]
                        }}
                    ]
                }},
                {{
                    "__component": "content.image",
                    "url": "/uploads/image.jpg",
                    "alternativeText": null,
                    "width": 400,
                    "padding": true,
                    "invertColors": null
                }}
            ]
        }}
    }}
    </sample request>
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