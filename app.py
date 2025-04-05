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

# Fetch the Firebase configuration from the environment variable
raw_config_base64 = os.environ.get("FIREBASE_CONFIG")

if raw_config_base64 is None:
    raise ValueError("FIREBASE_CONFIG environment variable not set")

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

    # 1. OCR: Extract text from image
    extracted_text = extract_text_from_image(image_bytes)
    if not extracted_text:
        return jsonify({"error": "No text extracted from the image"}), 400

    # 2. Gemini AI: Extract Ingredients
    ingredients = extract_ingredients_with_gemini(extracted_text)
    if not ingredients:
        return jsonify({"error": "No ingredients found from the extracted text"}), 400
    
    # 3. Nutrition info for each ingredient
    nutrition_info = {}
    for ing in ingredients:
        nutrition_info = fetch_nutrition_data(ing)
        if nutrition_info:
            break  # Only process the first ingredient for simplicity

    # 4. Suggest product alternatives using Open Food Facts API
    alternatives = suggest_product_alternatives(ingredients)

    # 5. Prepare response with product name, ingredients, nutrition info, and alternatives
    response = {
        "product_name": "Scanned Food Product",
        "ingredients": [{"ingredient_name": i} for i in ingredients],
        "nutrition_info": [
            {
                "ingredient_name": ing,
                "calories": nutrition_info.get("calories", "N/A"),
                "fat": nutrition_info.get("fat", "N/A"),
                "protein": nutrition_info.get("protein", "N/A"),
                "carbohydrates": nutrition_info.get("carbs", "N/A")
            } for ing in ingredients
        ],
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

    # Check for errors in the response
    if response.error.message:
        raise Exception(f"Error with OCR API: {response.error.message}")
    
    texts = response.text_annotations
    if texts:
        return texts[0].description
    else:
        return ""  # Return empty string if no text found

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

    # Debug log the response
    print("Gemini AI Response: ", result)

    if 'candidates' in result and result['candidates']:
        raw_ingredients = result['candidates'][0]['content']['parts'][0]['text']
        return [i.strip() for i in raw_ingredients.replace("\n", ",").split(",") if i.strip()]
    
    return []  # Return empty list if no candidates found

def fetch_nutrition_data(ingredient):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={FOOD_API_KEY}&query={ingredient}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        if data.get("foods"):
            food = data["foods"][0]
            nutrients = food.get("foodNutrients", [])
            return {
                "calories": nutrients[0].get("value", "N/A") if len(nutrients) > 0 else "N/A",
                "fat": nutrients[1].get("value", "N/A") if len(nutrients) > 1 else "N/A",
                "protein": nutrients[2].get("value", "N/A") if len(nutrients) > 2 else "N/A",
                "carbs": nutrients[3].get("value", "N/A") if len(nutrients) > 3 else "N/A"
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
