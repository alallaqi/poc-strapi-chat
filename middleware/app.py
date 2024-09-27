from flask import Flask, jsonify, request

app = Flask(__name__)

# Dummy data for testing
site_configs = [
    {
        "id": 1,
        "titleAppendix": "Example Site Config",
        "pageLocale": "US"
    }
]

# Dummy route to simulate Strapi's content API
@app.route('/site-configs', methods=['GET'])
def get_site_configs():
    return jsonify(site_configs), 200

@app.route('/site-configs', methods=['POST'])
def create_site_config():
    new_config = request.json
    site_configs.append(new_config)
    return jsonify(new_config), 201

if __name__ == "__main__":
    app.run(port=5000)
