def get_user_inputs():
    """
    Prompt the user for inputs needed to create the website content based on the API schema.
    Returns a dictionary containing all the user inputs.
    """
    inputs = {}
    
    # Design
    print("Let's start with the design of your website:")
    inputs['primary_color'] = input("What should be the primary color of your website? (e.g., #FF5733) ")
    inputs['secondary_color'] = input("What should be the secondary color? (e.g., #33FF57) ")
    
    # Site Config
    print("\nNow, let's configure your site:")
    inputs['site_name'] = input("What is the name of your website? ")
    inputs['site_description'] = input("Please provide a brief description of your website: ")
    
    # Content Page
    print("\nLet's create the main content page:")
    inputs['page_title'] = input("What should be the title of your main page? ")
    inputs['page_route'] = input("What should be the URL route for this page? (e.g., /home) ")
    
    # Navigation Menu
    print("\nNow, let's set up your navigation menu:")
    inputs['menu_title'] = input("What should be the title of your navigation menu? ")
    inputs['menu_items'] = []
    while True:
        item_title = input("Enter a menu item title (or press Enter to finish): ")
        if not item_title:
            break
        item_url = input(f"Enter the URL for '{item_title}': ")
        inputs['menu_items'].append({"title": item_title, "url": item_url})
    
    # Footer
    print("\nLastly, let's add some footer content:")
    inputs['footer_content'] = input("What content would you like in the footer? ")
    
    return inputs
