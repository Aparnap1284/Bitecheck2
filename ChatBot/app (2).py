import os 
import json
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Allow frontend requests (e.g., Flutter)

# 🔹 Load Firebase Credentials from Environment Variable
firebase_credentials_path = os.getenv("FIREBASE_CONFIG")

if not firebase_credentials_path:
    print("❌ ERROR: FIREBASE_CONFIG environment variable is empty or not set.")
    exit(1)

try:
    with open(firebase_credentials_path, "r") as file:
        firebase_credentials = json.load(file)
    
    # 🔹 Initialize Firebase App
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://ai-food-filter-aka-bitecheck-default-rtdb.asia-southeast1.firebasedatabase.app/"
    })
    print("✅ Firebase Initialized Successfully!")

except FileNotFoundError:
    print(f"❌ ERROR: File '{firebase_credentials_path}' not found.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ JSON Parsing Error: {e}")
    exit(1)


# 🔹 API: Test Route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "🔥 BiteCheck Backend is Running!"})


# 🔹 API: Extract Ingredients (with Firebase store)
@app.route("/extract_ingredients", methods=["POST"])
def extract_ingredients():
    data = request.json
    image_url = data.get("image_url")
    if not image_url:
        return jsonify({"error": "Missing image URL"}), 400

    # Mock OCR (replace this with Gemini Vision API later)
    extracted_text = "Ingredients: Sugar, Palm Oil, Cocoa, Whey Powder"
    ingredients_list = extracted_text.replace("Ingredients: ", "").split(", ")

    # 🔹 Store in Firebase under /ingredients
    ref = db.reference("/ingredients")
    ref.push({
        "image_url": image_url,
        "ingredients": ingredients_list
    })

    return jsonify({
        "extracted_ingredients": ingredients_list,
        "message": "Ingredients stored in Firebase!"
    })


# 🔹 API: Get Nutrition Data (with Firebase caching)
@app.route("/get_nutrition_data", methods=["POST"])
def get_nutrition_data():
    data = request.json
    ingredient = data.get("ingredient")
    if not ingredient:
        return jsonify({"error": "Missing ingredient"}), 400

    # 🔹 Check Firebase first
    ref = db.reference(f"/nutrition/{ingredient}")
    stored_data = ref.get()

    if stored_data:
        return jsonify(stored_data)

    # 🔹 If not found, return mock data
    nutrition_info = {
        "Sugar": {"calories": 387, "fat": 0, "protein": 0},
        "Palm Oil": {"calories": 884, "fat": 100, "protein": 0},
        "Cocoa": {"calories": 228, "fat": 13.7, "protein": 19.6},
    }

    if ingredient in nutrition_info:
        # Store in Firebase for future use
        ref.set(nutrition_info[ingredient])
        return jsonify(nutrition_info[ingredient])
    else:
        return jsonify({"error": "Ingredient not found"}), 404


# 🔹 Run the Flask Server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
