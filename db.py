import mysql.connector
from mysql.connector import Error

def get_connection():
    """Connect to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",          # your MySQL host
            user="your_username",      # your MySQL username
            password="your_password",  # your MySQL password
            database="recipe_db"       # your MySQL database
        )
        return conn
    except Error as e:
        print("Error connecting to MySQL:", e)
        return None

# --- User Functions ---
def create_user(username, email, password):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print("Error creating user:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# --- Recipe Functions ---
def save_recipe(user_id, ingredients, suggestion):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO recipes (user_id, ingredients, suggestion) VALUES (%s, %s, %s)",
            (user_id, ingredients, suggestion)
        )
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print("Error saving recipe:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_recipes(user_id):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recipes WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    recipes = cursor.fetchall()
    cursor.close()
    conn.close()
    return recipes
