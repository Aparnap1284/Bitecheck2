# app.py

import os
import io
import base64
import json
import requests
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import vision
from google.oauth2 import service_account
from waitress import serve

import os, json, base64

raw_config_base64 = os.environ.get("FIREBASE_CONFIG")
if raw_config_base64 is None:
    raise ValueError("FIREBASE_CONFIG environment variable not set")

with open("firebase_config.json") as f:
    FIREBASE_CONFIG = json.load(f)

cred = credentials.Certificate(FIREBASE_CONFIG)
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DB_URL")
})


# Gemini + FoodData API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FOOD_API_KEY = os.getenv("FOOD_API_KEY")

app = Flask(__name__)
CORS(app, origins="*")
@app.route("/test-firebase")
def test_firebase():
    ref = db.reference("/")
    return {"message": "Connected!", "data": ref.get()}

@app.route("/", methods=["GET"])
def home():
    return "BiteCheck Dynamic Backend Running!"

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400
    
    image_file = request.files['image']
    image_bytes = image_file.read()

    # 1. OCR
    extracted_text = extract_text_from_image(image_bytes)

    # 2. Gemini AI: Extract Ingredients
    ingredients = extract_ingredients_with_gemini(extracted_text)
    
    # 3. Nutrition info for first ingredient
    nutrition_info = {}
    for ing in ingredients:
        nutrition_info = fetch_nutrition_data(ing)
        break

    # 4. Suggest alternatives
    alternatives = suggest_alternatives(ingredients)

    # 5. Prepare response
    response = {
        "product_name": "Scanned Food Product",
        "ingredients": [{"ingredient_name": i} for i in ingredients],
        "nutrition_info": {
            "calories": nutrition_info.get("calories", "N/A"),
            "fat": nutrition_info.get("fat", "N/A"),
            "protein": nutrition_info.get("protein", "N/A"),
            "carbohydrates": nutrition_info.get("carbs", "N/A")
        },
        "healthy_alternatives": alternatives
    }

    return jsonify(response)

# -------------------------------------
# 🔍 Supporting Functions
# -------------------------------------

def extract_text_from_image(image_bytes):
    credentials = service_account.Credentials.from_service_account_info(json.loads(os.getenv("FIREBASE_CONFIG")))
    client = vision.ImageAnnotatorClient(credentials=credentials)
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts[0].description if texts else ""

def extract_ingredients_with_gemini(text):
    prompt = f"Extract only the ingredients from this product label: {text}"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    res = requests.post(url, headers=headers, json=data)
    result = res.json()
    raw_ingredients = result['candidates'][0]['content']['parts'][0]['text']
    return [i.strip() for i in raw_ingredients.replace("\n", ",").split(",") if i.strip()]

def fetch_nutrition_data(ingredient):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={FOOD_API_KEY}&query={ingredient}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        if data.get("foods"):
            food = data["foods"][0]
            return {
                "calories": food.get("foodNutrients", [{}])[0].get("value", "N/A"),
                "fat": "N/A",
                "protein": "N/A",
                "carbs": "N/A"
            }
    return {}

def suggest_alternatives(ingredients):
    suggestions = []
    for ing in ingredients:
        ing_lower = ing.lower()
        if "sugar" in ing_lower:
            suggestions.append({"ingredient_name": "Jaggery instead of Sugar"})
        elif "salt" in ing_lower:
            suggestions.append({"ingredient_name": "Rock Salt instead of Refined Salt"})
        elif "flour" in ing_lower:
            suggestions.append({"ingredient_name": "Whole Wheat Flour instead of Refined Flour"})
    return suggestions if suggestions else [{"ingredient_name": "This product looks healthy"}]

# -------------------------------------
# 🚀 Start Server
# -------------------------------------
if __name__ == "__main__":
    print("✅ Server is starting... Available routes are:")
    for rule in app.url_map.iter_rules():
        print(f"{rule}")
    
    serve(app, host="0.0.0.0", port=8080)
