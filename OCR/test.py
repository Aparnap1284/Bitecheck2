import os
import json
import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, initialize_app, db
import base64

app = Flask(__name__)
CORS(app)

# 🔐 Firebase config from environment
firebase_config_base64 = os.getenv('FIREBASE_CONFIG')
firebase_json_str = base64.b64decode(firebase_config_base64).decode('utf-8')
firebase_credentials = json.loads(firebase_json_str)

cred = credentials.Certificate(firebase_credentials)
initialize_app(cred, {
    'databaseURL': 'https://ai-food-filter-aka-bitecheck-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# 🧠 Mock Nutritional Database (per ingredient)
MOCK_NUTRITION_DB = {
    "sugar": {"calories": 400, "proteins": 0, "fats": 0, "carbs": 100},
    "salt": {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0},
    "refined wheat flour": {"calories": 364, "proteins": 10, "fats": 1, "carbs": 76},
    "palm oil": {"calories": 884, "proteins": 0, "fats": 100, "carbs": 0},
    "almonds": {"calories": 579, "proteins": 21, "fats": 50, "carbs": 22},
    "oats": {"calories": 389, "proteins": 17, "fats": 7, "carbs": 66},
    "honey": {"calories": 304, "proteins": 0.3, "fats": 0, "carbs": 82},
    "olive oil": {"calories": 884, "proteins": 0, "fats": 100, "carbs": 0}
}

# 🧠 Suggestions based on excess nutrients
def suggest_alternatives(nutrition_totals):
    suggestions = []

    if nutrition_totals["carbs"] > 100:
        suggestions.append("Try low-carb snacks like roasted chickpeas or protein bars.")

    if nutrition_totals["fats"] > 70:
        suggestions.append("Consider snacks with healthy fats like nuts or avocado crisps.")

    if nutrition_totals["calories"] > 800:
        suggestions.append("Switch to lower-calorie alternatives like rice cakes or fruits.")

    if nutrition_totals["proteins"] < 5:
        suggestions.append("Consider protein-rich snacks like boiled eggs or Greek yogurt.")

    return suggestions

# 📸 OCR Function (file-based)
def extract_text_from_image(image_file):
    ocr_space_api_key = os.getenv("OCR_SPACE_API_KEY")
    url = "https://api.ocr.space/parse/image"

    files = {'file': (image_file.filename, image_file.read())}
    payload = {
        'isOverlayRequired': False,
        'apikey': ocr_space_api_key,
        'language': 'eng'
    }

    response = requests.post(url, files=files, data=payload)
    print("OCR API Status Code:", response.status_code)

    try:
        result = response.json()
        print("OCR API Raw Response:\n", json.dumps(result, indent=2))

        if result.get("IsErroredOnProcessing") or not result.get("ParsedResults"):
            return ""

        parsed_results = result["ParsedResults"]
        if len(parsed_results) == 0 or "ParsedText" not in parsed_results[0]:
            return ""

        return parsed_results[0]["ParsedText"]

    except Exception as e:
        print("OCR failed:", e)
        return ""

# 🧪 Ingredient Extraction
def extract_ingredients_from_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z,\s]', '', text)
    candidates = re.split(r',|\n', text)

    ingredients = []
    for item in candidates:
        ing = item.strip()
        if ing:
            ingredients.append(ing)

    print("Extracted Ingredients:", ingredients)
    return ingredients

# 🔍 Ingredient Analysis & Nutrition Totals
def analyze_ingredients(ingredients):
    analyzed = []
    total_nutrition = {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0}

    for ing in ingredients:
        nutrition = MOCK_NUTRITION_DB.get(ing, {"calories": 50, "proteins": 1, "fats": 1, "carbs": 5})
        total_nutrition["calories"] += nutrition["calories"]
        total_nutrition["proteins"] += nutrition["proteins"]
        total_nutrition["fats"] += nutrition["fats"]
        total_nutrition["carbs"] += nutrition["carbs"]

        analyzed.append({
            "ingredient_name": ing,
            "calories": nutrition["calories"],
            "proteins": nutrition["proteins"],
            "fats": nutrition["fats"],
            "carbs": nutrition["carbs"]
        })

    print("Total Nutrition:", total_nutrition)
    return analyzed, total_nutrition

# Home Route
@app.route('/')
def home():
    return jsonify({"message": "BiteCheck backend live for nutrient analysis!"})

# 📦 Analyze Route
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "Image file not found in request"}), 400

        image_file = request.files['image']
        extracted_text = extract_text_from_image(image_file)

        if not extracted_text.strip():
            return jsonify({
                "error": "OCR failed to extract text from image.",
                "extracted_text": "",
                "ingredients": [],
                "product_name": "Generic Item",
                "nutrition_totals": {},
                "suggested_alternatives": []
            }), 200

        ingredients = extract_ingredients_from_text(extracted_text)
        analyzed_ingredients, nutrition_totals = analyze_ingredients(ingredients)
        suggestions = suggest_alternatives(nutrition_totals)

        # Save to Firebase
        db.reference('/ocr_results').push({
            'extracted_text': extracted_text,
            'analyzed': analyzed_ingredients,
            'totals': nutrition_totals,
            'suggestions': suggestions
        })

        return jsonify({
            "product_name": "Generic Item",
            "ingredients": analyzed_ingredients,
            "nutrition_totals": nutrition_totals,
            "suggested_alternatives": suggestions,
            "extracted_text": extracted_text
        })

    except Exception as e:
        print("Error in /analyze:", e)
        return jsonify({"error": str(e)}), 500

# Run Server
from waitress import serve
if __name__ == '__main__':
    print("🚀 Waitress server starting on http://0.0.0.0:8080 ...")
    serve(app, host="0.0.0.0", port=8080)
