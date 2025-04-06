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
    "olive oil": {"calories": 884, "proteins": 0, "fats": 100, "carbs": 0},
    "milk solids": {"calories": 496, "proteins": 26, "fats": 27, "carbs": 38},
    "raisins": {"calories": 299, "proteins": 3, "fats": 0.5, "carbs": 79},
    "sunflower oil": {"calories": 884, "proteins": 0, "fats": 100, "carbs": 0},
    "papaya": {"calories": 43, "proteins": 0.5, "fats": 0.3, "carbs": 11},
    "pineapple": {"calories": 50, "proteins": 0.5, "fats": 0.1, "carbs": 13},
    "orange pulp": {"calories": 47, "proteins": 0.9, "fats": 0.1, "carbs": 12},
    "invert syrup": {"calories": 310, "proteins": 0, "fats": 0, "carbs": 80},
    "maltose": {"calories": 380, "proteins": 0, "fats": 0, "carbs": 95},
    "emulsifiers": {"calories": 150, "proteins": 0, "fats": 16, "carbs": 2},
    "raising agents": {"calories": 5, "proteins": 0, "fats": 0, "carbs": 1},
    "preservatives": {"calories": 10, "proteins": 0, "fats": 0, "carbs": 2},
    "stabilizer": {"calories": 20, "proteins": 0, "fats": 0, "carbs": 5},
    "synthetic food colour": {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0},
    "flavouring substances": {"calories": 5, "proteins": 0, "fats": 0, "carbs": 1},
    "chocolate": {"calories": 546, "proteins": 4.9, "fats": 31, "carbs": 61},
    "butter": {"calories": 717, "proteins": 0.9, "fats": 81, "carbs": 0.1},
    "cashews": {"calories": 553, "proteins": 18, "fats": 44, "carbs": 30}
}

def suggest_alternatives(nutrition_totals):
    calories = nutrition_totals["calories"]
    proteins = nutrition_totals["proteins"]
    fats = nutrition_totals["fats"]
    carbs = nutrition_totals["carbs"]

    suggestions = []

    # 🍞 Carbs Suggestions
    carb_suggestions = []
    if carbs > 120:
        carb_suggestions += [
            "Too many carbs! Try 🥒 cucumber sticks or 🥚 boiled eggs.",
            "Carb overload! Try 🥜 nuts or 🧀 paneer cubes.",
            "Lighten it up with 🍿 popcorn or a 🥗 veggie bowl."
        ]
    elif carbs > 80:
        carb_suggestions += [
            "High carbs detected. Swap with 🥬 lettuce wraps or 🫛 sprouts.",
            "Lower carbs? Go for 🍄 mushrooms or 🌰 mixed seeds."
        ]
    elif carbs < 40:
        carb_suggestions += [
            "Low on carbs. Add 🍠 sweet potatoes or 🍞 whole grains."
        ]

    # 🥩 Protein Suggestions
    protein_suggestions = []
    if proteins < 5:
        protein_suggestions += [
            "Low protein. Try 🍳 eggs or 🧀 paneer.",
            "Boost protein with 🥜 peanuts or 🍗 grilled chicken.",
            "Need protein? Go for 🥚 boiled eggs or 🥛 milk."
        ]
    elif proteins > 15:
        protein_suggestions += [
            "Awesome protein pick 💪!",
            "Protein-rich snack! Keep it up 🌟."
        ]
    else:
        protein_suggestions += [
            "Add some 🫘 lentils or 🌰 nuts for protein boost."
        ]

    # 🧈 Fat Suggestions
    fat_suggestions = []
    if fats > 80:
        fat_suggestions += [
            "High in fats. Switch to 🍌 banana or 🌽 corn snacks.",
            "Too much fat. Try 🥗 leafy snacks or 🧃 smoothies.",
            "Go light with 🍎 apples or 🥝 kiwi slices."
        ]
    elif fats > 40:
        fat_suggestions += [
            "Moderate fat. Consider more 🥬 veggies or 🍓 berries.",
            "Try reducing fats with 🥣 soups or 🫐 yogurt bowls."
        ]
    elif fats < 10:
        fat_suggestions += [
            "Very low fat. Add 🥑 or 🫒 for healthy fats."
        ]

    # 🔥 Calorie Suggestions
    calorie_suggestions = []
    if calories > 1000:
        calorie_suggestions += [
            "Too many cals! Go for 🍇 fruits or 🧆 roasted snacks.",
            "Heavy snack. Choose 🥗 salads or 🍉 melon slices next time.",
            "Calories too high! Try 🌰 seeds or 🍵 green tea snacks."
        ]
    elif calories > 600:
        calorie_suggestions += [
            "Bit high on calories. Consider 🍓 smoothies or 🥒 veggies.",
            "High calorie count! Switch to 🧃 fruit juices or 🍎 apple slices."
        ]
    elif calories < 200:
        calorie_suggestions += [
            "Super light choice! Great for snacking 😌.",
            "Low-calorie and smart 💚!",
            "Guilt-free munching 👍."
        ]

    # ✅ Overall Balanced
    if calories < 500 and fats < 30 and carbs < 70 and proteins > 10:
        suggestions.append("Looks balanced! 🥗 Smart choice.")

    # 🎯 Combine all category suggestions
    all_suggestions = carb_suggestions + protein_suggestions + fat_suggestions + calorie_suggestions + suggestions

    # Shuffle for randomness and pick 4 to keep it concise
    random.shuffle(all_suggestions)
    return all_suggestions[:4]

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
import random

def generate_product_name(extracted_text):
    text_lower = extracted_text.lower()

    # Map ingredient keywords to intelligent product names
    keyword_name_map = {
        # Snacks & Bakery
        "refined wheat flour": "Classic Tea-Time Biscuit",
        "maida": "Refined Flour Snack Pack",
        "sugar": "Sweet Treat Snack Pack",
        "salt": "Salted Snack Bites",
        "palm oil": "Instant Noodle Bites",
        "cocoa solids": "Choco Fudge Bar",
        "milk solids": "Creamy Milk Delight",
        "chocolate": "Choco Bliss Bar",
        "oats": "Oat Energy Bar",
        "honey": "Honey Nutri Bar",
        "raisins": "Raisin Nut Mix",
        "almond": "Nutty Almond Crunch",
        "cashew": "Creamy Cashew Chunks",
        "peanut": "Peanut Protein Pop",
        "fruit": "Fruity Chewy Cubes",
        "spices": "Masala Mix Noodles",
        "flour": "Wholegrain Flour Base",
        "ghee": "Desi Ghee Ladoo",
        "butter": "Buttery Cracker Pack",
        "juice": "Tropical Fruit Juice Box",
        "cereal": "Morning Oatmeal Crunch",
        "protein": "Protein Punch Bar",
        "vitamin": "Vitamin Boost Sachet",
        "fiber": "Fiber Fuel Cubes",
        "rice": "Ready-to-Cook Rice Mix",
        "noodles": "Spicy Instant Noodles",
        "granola": "Nutri Crunch Granola Bar"
    }

    # Track keyword matches
    matched_keywords = []
    for keyword, name in keyword_name_map.items():
        if keyword in text_lower:
            matched_keywords.append(name)

    # If multiple names match, return the one with most important ingredient
    if matched_keywords:
        # You could later prioritize this with weighted scoring
        return matched_keywords[0]

    # Friendly fallback product names
    fallback_names = [
        "Balanced Life Snack Box",
        "Smart Energy Trail Mix",
        "Veggie Boost Crackers",
        "Fiber Fuel Cookies",
        "Clean Eats Super Bar",
        "Wholesome Oats Cereal",
        "Grainy Goodness Puffs",
        "Morning Glow Cereal",
        "Power-Up Nutri Cubes",
        "Healthylicious Mini Pack"
    ]
    return random.choice(fallback_names)

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
        
         # 🧠 NEW: Generate product name
        product_name = generate_product_name(extracted_text)

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
            "product_name": product_name,
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
