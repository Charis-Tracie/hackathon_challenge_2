from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import openai
from db import create_user, get_user_by_email, save_recipe, get_user_recipes
from dotenv import load_dotenv
import bcrypt
import mysql.connector

app = Flask(__name__)
CORS(app)
load_dotenv()

# Load local recipes
with open("recipes.json") as f:
    local_recipes = json.load(f)

# API keys
SPOON_API_KEY = "eb9b0535102b42febf34e71a9e403906"
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"

# ----------------- Load local recipes -----------------
with open("recipes.json", encoding="utf-8") as f:
    local_recipes = json.load(f)

@app.route("/recommend", methods=["GET"])
def recommend():
    ingredient = request.args.get("ingredient", "").lower()
    if not ingredient:
        return jsonify({"recipes": []})

    # 1️⃣ Local JSON
    local_matches = []
    for key, recipes_list in local_recipes.items():
        if ingredient == key.lower() or ingredient in key.lower():
            local_matches.extend(recipes_list)
    if local_matches:
        return jsonify({"recipes": local_matches})

    # 2️⃣ Spoonacular API
    try:
        url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredient}&number=5&apiKey={SPOON_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            recipes = []
            for item in data:
                recipes.append({
                    "name": item.get("title", "No title"),
                    "ingredients": [ing["name"] for ing in item.get("usedIngredients", []) + item.get("missedIngredients", [])],
                    "image": item.get("image") or f"https://source.unsplash.com/400x300/?{ingredient}"
                })
            return jsonify({"recipes": recipes})
    except Exception as e:
        print("Spoonacular error:", e)

    #  OpenAI fallback
    try:
        prompt = f"Create a simple recipe using {ingredient}. Include recipe name and ingredients."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        text = response['choices'][0]['message']['content']
        import re
        name_match = re.search(r"^(.*?):", text)
        name = name_match.group(1) if name_match else f"{ingredient.title()} Recipe"
        ingredients = re.findall(r"-\s*(.+)", text)
        if not ingredients:
            ingredients = [ingredient]
        return jsonify({"recipes": [{"name": name, "ingredients": ingredients, "image": f"https://source.unsplash.com/400x300/?{ingredient}"}]})
    except Exception as e:
        print("OpenAI error:", e)

    # Fallback empty
    return jsonify({"recipes": []})


# ----------------- Database Connection -----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",          # change to your MySQL user
    password="password",  # change to your MySQL password
    database="recipes_db" # make sure this DB exists
)
cursor = db.cursor(dictionary=True)

# ----------------- Helper Functions -----------------
def get_user_by_email(email):
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    return cursor.fetchone()

def create_user(username, email, password):
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_pw.decode("utf-8"))
        )
        db.commit()
        return True
    except:
        return False

def save_recipe(user_id, ingredients, suggestion):
    try:
        cursor.execute(
            "INSERT INTO saved_recipes (user_id, ingredients, suggestion) VALUES (%s, %s, %s)",
            (user_id, ingredients, suggestion)
        )
        db.commit()
        return True
    except:
        return False

def get_user_recipes(user_id):
    cursor.execute("SELECT * FROM saved_recipes WHERE user_id=%s", (user_id,))
    return cursor.fetchall()

# ----------------- User Endpoints -----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    if get_user_by_email(email):
        return jsonify({"success": False, "message": "User already exists"}), 400

    if create_user(username, email, password):
        return jsonify({"success": True, "message": "Signup successful"})

    return jsonify({"success": False, "message": "Error creating user"}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = get_user_by_email(email)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # check password with bcrypt
    if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({
            "success": True,
            "user_id": user["id"],
            "username": user["username"]
        })
    else:
        return jsonify({"success": False, "message": "Invalid password"}), 401

# ----------------- Save & Get Recipes -----------------
@app.route("/save_recipe", methods=["POST"])
def save_user_recipe():
    data = request.json
    user_id = data.get("user_id")
    ingredients = data.get("ingredients")
    suggestion = data.get("suggestion")

    if save_recipe(user_id, ingredients, suggestion):
        return jsonify({"success": True})

    return jsonify({"success": False}), 500

@app.route("/get_recipes/<int:user_id>", methods=["GET"])
def get_user_saved(user_id):
    recipes = get_user_recipes(user_id)
    return jsonify({"recipes": recipes})

if __name__ == "__main__":
    app.run(debug=True)