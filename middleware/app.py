from flask import Flask, jsonify, request

app = Flask(__name__)

# Dummy data for CMS resources
content_pages = [
    {"pageId": 1, "title": "Home", "content": "Welcome to the homepage", "seoDescription": "Homepage", "tags": ["home"], "createdAt": "2023-01-01T10:00:00Z"},
    {"pageId": 2, "title": "About Us", "content": "About our company", "seoDescription": "About us page", "tags": ["about"], "createdAt": "2023-01-02T14:00:00Z"}
]

designs = [
    {"designId": 1, "name": "Modern Layout", "colors": {"primary": "#3498db", "secondary": "#2ecc71"}, "createdAt": "2023-01-01T12:00:00Z"},
    {"designId": 2, "name": "Classic Layout", "colors": {"primary": "#e74c3c", "secondary": "#8e44ad"}, "createdAt": "2023-01-02T16:00:00Z"}
]

navigation_menus = [
    {"menuId": 1, "title": "Main Menu", "items": [{"title": "Home", "url": "/"}, {"title": "About", "url": "/about"}]},
]

site_config = {
    "configId": 1,
    "titleAppendix": "HTC CMS",
    "locale": "en",
    "navigationFontColor": "#000000",
    "navigationFontColorOnHover": "#FFFFFF"
}

footer = {
    "footerId": 1,
    "content": "© 2023 HTC CMS",
    "links": [{"title": "Privacy Policy", "url": "/privacy"}]
}

# Define content page routes
@app.route('/content-pages', methods=['GET'])
def get_content_pages():
    return jsonify(content_pages)

@app.route('/content-pages', methods=['POST'])
def create_content_page():
    content_page = request.json
    content_page["pageId"] = len(content_pages) + 1
    content_pages.append(content_page)
    return jsonify(content_page), 201

@app.route('/content-pages/<int:page_id>', methods=['GET'])
def get_content_page(page_id):
    page = next((p for p in content_pages if p["pageId"] == page_id), None)
    return jsonify(page) if page else (jsonify({"error": "Page not found"}), 404)

@app.route('/content-pages/<int:page_id>', methods=['PUT'])
def update_content_page(page_id):
    page = next((p for p in content_pages if p["pageId"] == page_id), None)
    if page:
        page.update(request.json)
        return jsonify(page)
    return jsonify({"error": "Page not found"}), 404

@app.route('/content-pages/<int:page_id>', methods=['DELETE'])
def delete_content_page(page_id):
    global content_pages
    content_pages = [p for p in content_pages if p["pageId"] != page_id]
    return jsonify({"message": "Content page deleted"}), 204

# Define design routes
@app.route('/designs', methods=['GET'])
def get_designs():
    return jsonify(designs)

@app.route('/designs', methods=['POST'])
def create_design():
    design = request.json
    design["designId"] = len(designs) + 1
    designs.append(design)
    return jsonify(design), 201

@app.route('/designs/<int:design_id>', methods=['GET'])
def get_design(design_id):
    design = next((d for d in designs if d["designId"] == design_id), None)
    return jsonify(design) if design else (jsonify({"error": "Design not found"}), 404)

@app.route('/designs/<int:design_id>', methods=['PUT'])
def update_design(design_id):
    design = next((d for d in designs if d["designId"] == design_id), None)
    if design:
        design.update(request.json)
        return jsonify(design)
    return jsonify({"error": "Design not found"}), 404

@app.route('/designs/<int:design_id>', methods=['DELETE'])
def delete_design(design_id):
    global designs
    designs = [d for d in designs if d["designId"] != design_id]
    return jsonify({"message": "Design deleted"}), 204

# Define navigation menu routes
@app.route('/navigation-menus', methods=['GET'])
def get_navigation_menus():
    return jsonify(navigation_menus)

@app.route('/navigation-menus', methods=['POST'])
def create_navigation_menu():
    menu = request.json
    menu["menuId"] = len(navigation_menus) + 1
    navigation_menus.append(menu)
    return jsonify(menu), 201

@app.route('/navigation-menus/<int:menu_id>', methods=['PUT'])
def update_navigation_menu(menu_id):
    menu = next((m for m in navigation_menus if m["menuId"] == menu_id), None)
    if menu:
        menu.update(request.json)
        return jsonify(menu)
    return jsonify({"error": "Menu not found"}), 404

@app.route('/navigation-menus/<int:menu_id>', methods=['DELETE'])
def delete_navigation_menu(menu_id):
    global navigation_menus
    navigation_menus = [m for m in navigation_menus if m["menuId"] != menu_id]
    return jsonify({"message": "Navigation menu deleted"}), 204

# Define site config routes
@app.route('/site-config', methods=['GET'])
def get_site_config():
    return jsonify(site_config)

@app.route('/site-config', methods=['PUT'])
def update_site_config():
    site_config.update(request.json)
    return jsonify(site_config)

# Define footer routes
@app.route('/footer', methods=['GET'])
def get_footer():
    return jsonify(footer)

@app.route('/footer', methods=['PUT'])
def update_footer():
    footer.update(request.json)
    return jsonify(footer)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
