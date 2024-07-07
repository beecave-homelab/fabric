import jwt
import json
import openai
from flask import Flask, request, jsonify
from functools import wraps
import re
import requests
import os
from dotenv import load_dotenv
from importlib import resources

# Load environment variables from .env file
load_dotenv()

# Set up the JWT secret
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET is not set in the environment variables")

app = Flask(__name__)

def load_api_keys():
    with resources.path("installer.server.api", "fabric_api_keys.json") as api_keys_path:
        with open(api_keys_path, 'r') as f:
            return json.load(f)

def load_users():
    with resources.path("installer.server.api", "users.json") as users_path:
        with open(users_path, 'r') as f:
            return json.load(f)

def save_api_keys(api_keys):
    with resources.path("installer.server.api", "fabric_api_keys.json") as api_keys_path:
        with open(api_keys_path, 'w') as f:
            json.dump(api_keys, f, indent=2)

def save_users(users):
    with resources.path("installer.server.api", "users.json") as users_path:
        with open(users_path, 'w') as f:
            json.dump(users, f, indent=2)

# Initialize valid_tokens and users
valid_tokens = load_api_keys()
users = load_users()

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "The requested resource was not found."}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "An internal server error occurred."}), 500

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get("Authorization", "")
        if auth_token.lower().startswith("bearer "):
            auth_token = auth_token[7:]
        endpoint = request.path
        user = check_auth_token(auth_token, endpoint)
        if user == "Unauthorized: You are not authorized for this API":
            return jsonify({"error": user}), 401
        return f(*args, **kwargs)
    return decorated_function

def check_auth_token(token, route):
    global valid_tokens, users
    valid_tokens = load_api_keys()  # Reload API keys
    users = load_users()  # Reload users
    if route in valid_tokens and token in valid_tokens[route]:
        return users[valid_tokens[route][token]]
    else:
        return "Unauthorized: You are not authorized for this API"

ALLOWLIST_PATTERN = re.compile(r"^[a-zA-Z0-9\s.,;:!?\-]+$")

def sanitize_content(content):
    return "".join(char for char in content if ALLOWLIST_PATTERN.match(char))

def fetch_content_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        sanitized_content = sanitize_content(response.text)
        return sanitized_content
    except requests.RequestException as e:
        return str(e)

pattern_path_mappings = {
    "extwis": {
        "system_url": "https://raw.githubusercontent.com/danielmiessler/fabric/main/patterns/extract_wisdom/system.md",
        "user_url": "https://raw.githubusercontent.com/danielmiessler/fabric/main/patterns/extract_wisdom/user.md"
    },
    "summarize": {
        "system_url": "https://raw.githubusercontent.com/danielmiessler/fabric/main/patterns/summarize/system.md",
        "user_url": "https://raw.githubusercontent.com/danielmiessler/fabric/main/patterns/summarize/user.md"
    }
}

@app.route("/<pattern>", methods=["POST"])
@auth_required
def milling(pattern):
    data = request.get_json()
    if "input" not in data:
        return jsonify({"error": "Missing input parameter"}), 400
    input_data = data["input"]
    urls = pattern_path_mappings[pattern]
    system_content = fetch_content_from_url(urls["system_url"])
    user_file_content = fetch_content_from_url(urls["user_url"])
    system_message = {"role": "system", "content": system_content}
    user_message = {"role": "user", "content": user_file_content + "\n" + input_data}
    messages = [system_message, user_message]
    try:
        response = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            temperature=0.0,
            top_p=1,
            frequency_penalty=0.1,
            presence_penalty=0.1,
        )
        assistant_message = response.choices[0].message.content
        return jsonify({"response": assistant_message})
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request."}), 500

@app.route("/register", methods=["POST"])
def register():
    global users, valid_tokens
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    users = load_users()  # Reload users before checking
    if username in users:
        return jsonify({"error": "Username already exists"}), 400
    new_user = {
        "username": username,
        "password": password
    }
    users[username] = new_user
    save_users(users)
    
    token = jwt.encode({"username": username}, JWT_SECRET, algorithm="HS256")
    
    # Add token to valid_tokens for all routes
    for route in pattern_path_mappings.keys():
        if route not in valid_tokens:
            valid_tokens[route] = {}
        valid_tokens[route][token] = username
    save_api_keys(valid_tokens)
    
    return jsonify({"token": token})

@app.route("/login", methods=["POST"])
def login():
    global users
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    users = load_users()  # Reload users before checking
    if username in users and users[username]["password"] == password:
        token = jwt.encode({"username": username}, JWT_SECRET, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"error": "Invalid username or password"}), 401

def main():
    """Runs the main fabric API backend server"""
    app.run(host="0.0.0.0", port=13337, debug=True)

if __name__ == "__main__":
    main()