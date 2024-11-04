def generate_site_data(company_profile):
    return f"""
    # Context
    Designing a website for a company based on the company profile description. 
    
    # Objective
    - Validation - Verify that the <company profile> text pass the  <validation rules>, do not make up information for this step.
    - Validation error - In case of validation errors return output in json as defined in <validation errors> section. 
    - JSON Data creation - Only if there are no validation errors, based on the <company profile> generate the parameters listed in the <parameters> section.
       The output should be in json format according to the example provided in the <output format> section.

    <validation rules>
    - The <company profile> must contain the company name.
    - The <company profile> must contain a brief description of the company.
    - The <company profile> must contain information about the company's mission or goals.
    - The <company profile> must contain information about the services provided by the company.
    - The <company profile> must contain information about the company's target audience.
    </validation rules>

    
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
        "companyName": <company name>,
        "industry": <the industry in which the company operates>,
        "shortDesctiption": <a shord description>,
        "imageGenerationPrompt": <prompt for generating related images>,
        "primaryColor": <primary color>,
        "secondaryColor": <secondary color>,
        "designName": <design name>,
        "footerText": <footer text>,
        "pages": [
            {{
                "name": <page name>,
                "route": <page route>,
                "content": [
                    {{
                        "heading": <item heading>,
                        "text": <item text, >100 words>
                    }},
                    {{
                        "heading": <item heading>,
                        "text": <item text, >100 words>
                    }},
                ],
            }}
            ]
    }}
    </output format>

    <validation error>
    {{ "error": <error message> }}
    </validation error>

    <company profile>
    {company_profile}
    </company profile>
    
    # Response
    Respond with the JSON as defined in the <output format> section. Do not format the response as markdown because it should be parsed.
    """
