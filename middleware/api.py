from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Dummy data for demonstration purposes
content_pages = [
    {
        "id": 1,
        "title": "Home",
        "route": "/",
        "locale": "en",
        "content": [],
        "seoDescription": "Welcome to our homepage",
        "isFooterDisabled": False,
        "seoTitle": "Home Page",
        "tags": [],
        "navigationFontColor": "#000000",
        "navigationFontColorOnHover": "#FFFFFF",
        "urlAlias": [],
        "eventDates": [],
        "teaserImage": None,
        "teaserImageFocus": "center"
    },
    {
        "id": 2,
        "title": "About Us",
        "route": "/about",
        "locale": "en",
        "content": [],
        "seoDescription": "Learn more about us",
        "isFooterDisabled": False,
        "seoTitle": "About Us",
        "tags": [],
        "navigationFontColor": "#000000",
        "navigationFontColorOnHover": "#FFFFFF",
        "urlAlias": [],
        "eventDates": [],
        "teaserImage": None,
        "teaserImageFocus": "center"
    }
]

designs = [
    {
        "id": 1,
        "designName": "Modern Layout",
        "description": "A modern design layout for our website.",
        "colors": {
            "primary": "#3498db",
            "secondary": "#2ecc71"
        }
    },
    {
        "id": 2,
        "designName": "Classic Layout",
        "description": "A classic design layout for our website.",
        "colors": {
            "primary": "#e74c3c",
            "secondary": "#8e44ad"
        }
    }
]

# Dummy data for Site Config
site_config = {
    "id": 1,
    "logo": {
        "data": {
            "id": 1,
            "attributes": {
                "name": "Logo",
                "alternativeText": "Company Logo",
                "url": "http://example.com/logo.png"
            }
        }
    },
    "titleAppendix": "Your Company",
    "pageLocale": "en",
    "navigationFontColor": "#000000",
    "navigationFontColorOnHover": "#FFFFFF",
    "favicon": "http://example.com/favicon.ico",
    "design": "default",
    "locale": "en"
}

# Dummy data for Footer
footer = {
    "id": 1,
    "items": [
        {
            "id": 1,
            "attributes": {
                "text": "Contact Us",
                "link": "http://example.com/contact"
            }
        }
    ],
    "copyright": "© 2024 Your Company",
    "socialLinks": {
        "facebook": "http://facebook.com/yourcompany",
        "twitter": "http://twitter.com/yourcompany"
    }
}

# Define routes for Content Pages
@app.route('/content-pages', methods=['GET'])
def get_content_pages():
    return jsonify(content_pages), 200

@app.route('/content-pages', methods=['POST'])
def create_content_page():
    content_page = request.json
    if not validate_content_page(content_page):
        return jsonify({"error": "Invalid content page data"}), 400
    content_page['id'] = len(content_pages) + 1  # Assign a new ID
    content_pages.append(content_page)
    return jsonify(content_page), 201

@app.route('/content-pages/<int:id>', methods=['GET'])
def get_content_page(id):
    content_page = next((page for page in content_pages if page.get('id') == id), None)
    if content_page:
        return jsonify(content_page), 200
    return jsonify({"error": "Content page not found"}), 404

@app.route('/content-pages/<int:id>', methods=['PUT'])
def update_content_page(id):
    content_page = next((page for page in content_pages if page.get('id') == id), None)
    if content_page:
        updated_data = request.json
        content_page.update(updated_data)
        return jsonify(content_page), 200
    return jsonify({"error": "Content page not found"}), 404

@app.route('/content-pages/<int:id>', methods=['DELETE'])
def delete_content_page(id):
    global content_pages
    content_pages = [page for page in content_pages if page.get('id') != id]
    return jsonify({"message": "Content page deleted"}), 204

# Define routes for Designs
@app.route('/designs', methods=['GET'])
def get_designs():
    return jsonify(designs), 200

@app.route('/designs', methods=['POST'])
def create_design():
    design = request.json
    if not validate_design(design):
        return jsonify({"error": "Invalid design data"}), 400
    design['id'] = len(designs) + 1  # Assign a new ID
    designs.append(design)
    return jsonify(design), 201

@app.route('/designs/<int:id>', methods=['GET'])
def get_design(id):
    design = next((d for d in designs if d.get('id') == id), None)
    if design:
        return jsonify(design), 200
    return jsonify({"error": "Design not found"}), 404

@app.route('/designs/<int:id>', methods=['PUT'])
def update_design(id):
    design = next((d for d in designs if d.get('id') == id), None)
    if design:
        updated_data = request.json
        design.update(updated_data)
        return jsonify(design), 200
    return jsonify({"error": "Design not found"}), 404

@app.route('/designs/<int:id>', methods=['DELETE'])
def delete_design(id):
    global designs
    designs = [d for d in designs if d.get('id') != id]
    return jsonify({"message": "Design deleted"}), 204

# Define routes for Site Config
@app.route('/site-config', methods=['GET'])
def get_site_config():
    return jsonify(site_config), 200

@app.route('/site-config', methods=['PUT'])
def update_site_config():
    global site_config
    updated_data = request.json
    site_config.update(updated_data)
    return jsonify(site_config), 200

# Define routes for Footer
@app.route('/footer', methods=['GET'])
def get_footer():
    return jsonify(footer), 200

@app.route('/footer', methods=['PUT'])
def update_footer():
    global footer
    updated_data = request.json
    footer.update(updated_data)
    return jsonify(footer), 200

# Validation functions
def validate_content_page(content_page):
    required_fields = ['title', 'route', 'locale']  # Adjust based on your schema
    return all(field in content_page for field in required_fields)

def validate_design(design):
    required_fields = ['designName', 'description']  # Adjust based on your schema
    return all(field in design for field in required_fields)

def create_content(user_inputs):
    # Generate content based on the schema
    generated_content = generate_content(content_schema)

    # Print the generated content for debugging
    print("Generated Content:", json.dumps(generated_content, indent=2))

    # Validate generated content against the schema
    if validate_generated_content(generated_content):
        # Create content pages using the generated content
        for page in generated_content['pages']:
            create_content_page(page)
        print(f"\n{add_color('All content has been created successfully!', 'green')}")
    else:
        print(f"{add_color('Generated content is invalid.', 'red')}")

if __name__ == '__main__':
    app.run(debug=True)
