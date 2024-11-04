def generate_site_data(company_profile):
    return f"""
    # Context
    Designing a website for a company based on the company profile description. 
    
    # Objective
    Given the company profile in the <text> section below, generate the parameters listed in the <parameters> section.
    The output should be in json format according to the example provided in the <output format> section.
    
     <parameters>
    - A random primary background color in hex value that works for a modern minimalistic website, and may be related to the industry of the company.
    - A secondary accent color in hex value that.
    - The name to use for the design.
    - A collection of pages, each containing multiple content sections with a heading and a text of 100 words.
      Include at least the following pages: Home, Services, Contact.
    - A short footer text
    </parameters> 

   

    <output format>
    {{
        "primaryColor": "#FF5733",
        "secondaryColor": "#33FF57",
        "designName": "Company Design",
        "footerText": "© 2022 Company. All rights reserved.",
        "pages": {{[
            {{
                "name": "Home",
                "route": "/home",
                "content": [
                    {{
                        "heading": "About Us",
                        "text": "We are a company that..."
                    }},
                    {{
                        "heading": "Our Mission",
                        "text": "Our mission is..."
                    }}
                ],
            }},
            {{
                "name": "Services",
                "route": "/services",
                "content": [
                    {{
                        "heading": "Equipment",
                        "text": "We provide state-of-the-art.."
                    }},
                    {{
                        "heading": "Training",
                        "text": "Our trainers .."
                    }}
                ],
            }},
            {{
                "name": "Contact",
                "route": "/contact",
                "content": [
                    {{
                        "heading": "Contact Us",
                        "text": "For inquiries.."
                    }}
                ]
            }}
        }}

    }}
    </output format>

    <text>
    {company_profile}
    </text>
    
    # Response
    Respond with the JSON as defined in the <output format> section. Do not format the response as markdown because it should be parsed.
    """
