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
import pytesseract
from PIL import Image
import pytesseract

# Define the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux path

# Or use the correct path for your system if it's different

# Fetch the Firebase configuration from the environment variable
raw_config_base64 = os.getenv("FIREBASE_CONFIG")

if not raw_config_base64:
    raise ValueError("FIREBASE_CONFIG environment variable is missing or empty.")

# Decode the base64-encoded configuration
decoded_config = base64.b64decode(raw_config_base64).decode("utf-8")

# Parse the decoded JSON string
FIREBASE_CONFIG = json.loads(decoded_config)

# Initialize Firebase
cred = credentials.Certificate(FIREBASE_CONFIG)
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv("FIREBASE_DB_URL")
})

# API Keys for Gemini and FoodData APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FOOD_API_KEY = os.getenv("FOOD_API_KEY")

app = Flask(__name__)
CORS(app, origins="*")

@app.route("/", methods=["GET"])
def home():
    return "BiteCheck Dynamic Backend Running!"

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400
    
    image_file = request.files['image']
    image_bytes = image_file.read()

    # 1. OCR: Extract text from image using Pytesseract
    extracted_text = extract_text_from_image(image_bytes)

    # 2. Gemini AI: Extract Ingredients
    ingredients = extract_ingredients_with_gemini(extracted_text)
    
    # 3. Nutrition info for the first ingredient
    nutrition_info = {}
    for ing in ingredients:
        nutrition_info = fetch_nutrition_data(ing)
        break

    # 4. Suggest product alternatives using Open Food Facts API
    alternatives = suggest_product_alternatives(ingredients)

    # 5. Prepare response with product name, ingredients, nutrition info, and alternatives
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
    # Open the image using PIL from the byte stream
    image = Image.open(io.BytesIO(image_bytes))
    
    # Use Pytesseract to extract text from the image
    extracted_text = pytesseract.image_to_string(image)
    
    # Print the extracted text (for debugging)
    print(f"Extracted Text: {extracted_text}")
    
    return extracted_text

def extract_ingredients_with_gemini(text):
    prompt = f"Extract only the ingredients from this product label: {text}"
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    res = requests.post(url, headers=headers, json=data)
    result = res.json()

    # Log the full response for debugging purposes
    print("Gemini API response:", json.dumps(result, indent=2))

    # Handle the case where 'candidates' might be missing
    if 'candidates' in result and result['candidates']:
        raw_ingredients = result['candidates'][0]['content']['parts'][0]['text']
        return [i.strip() for i in raw_ingredients.replace("\n", ",").split(",") if i.strip()]
    else:
        print("No candidates found in the response.")
        return []  # Return empty list if no ingredients found

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

def suggest_product_alternatives(ingredients):
    alternatives = []
    for ing in ingredients:
        ing_lower = ing.lower()
        # Encode the product name for a URL query
        product_name_encoded = ing.replace(" ", "+")
        # Construct the URL with the actual product name
        url = f"https://world.openfoodfacts.org/api/v0/search?search_terms={product_name_encoded}&fields=product_name,ingredients_text,nutriments"
        
        # Request to Open Food Facts API
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            
            for product in products[:3]:  # Limit to 3 alternatives
                alternatives.append({
                    "product_name": product.get("product_name", "Unknown"),
                    "ingredients": product.get("ingredients_text", "Unknown"),
                    "nutrition_info": product.get("nutriments", {})
                })
                
            if not alternatives:
                alternatives.append({"product_name": "No alternatives found"})
        else:
            alternatives.append({"product_name": "Error fetching alternatives"})
    
    return alternatives

# -------------------------------------
# 🚀 Start Server
# -------------------------------------
if __name__ == "__main__":
    print("✅ Server is starting... Available routes are:")
    for rule in app.url_map.iter_rules():
        print(f"{rule}")
    
    serve(app, host="0.0.0.0", port=8080)
