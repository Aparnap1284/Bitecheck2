import cv2
import pytesseract
import re
import requests
from spellchecker import SpellChecker
import google.generativeai as genai
from firebase_db import db  # Import Firebase database

# 🔹 Change this to your Gemini AI API Key
GEMINI_API_KEY = "AIzaSyCEiXqI6vVU9DWEoAh26x3x-It9k8fKoSs"
genai.configure(api_key=GEMINI_API_KEY)

# 🔹 Change this to your FoodData Central API Key
FOODDATA_API_KEY = "Y53tr7na8EuZPEpUMzSGEzrthSaAFt9WY2cVg6i7"

# 🔹 Update this if your Tesseract path is different
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize Spell Checker
spell = SpellChecker()


def preprocess_image(image_path):
    """Loads and preprocesses the image for better OCR accuracy."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Error: Image '{image_path}' not found or cannot be loaded.")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to improve text contrast
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh


def extract_text_from_image(image_path):
    """Extracts text from the image using Tesseract OCR and enhances it with Gemini AI."""
    try:
        preprocessed_img = preprocess_image(image_path)
        raw_text = pytesseract.image_to_string(preprocessed_img, lang='eng')

        # Use Gemini AI to enhance text extraction
        enhanced_text = enhance_text_with_gemini(raw_text)
        return enhanced_text
    except Exception as e:
        print(f"\n❌ OCR Extraction Failed: {e}")
        return None


def enhance_text_with_gemini(text):
    """Uses Gemini AI to clean and structure OCR-extracted text."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Extract ingredients from this text: {text}")
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini AI Processing Failed: {e}")
        return text  # Fallback to OCR text


def correct_spelling(text):
    """Fixes spelling errors in the extracted text."""
    words = text.split()
    corrected_words = [spell.correction(word) or word for word in words]
    return " ".join(corrected_words)


def extract_ingredients(text):
    """Uses Gemini AI to extract and refine ingredients from text."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"List only the ingredients from this text: {text}")

        # Ensure ingredients are stored as a proper list
        ingredients = response.text.strip().split("\n")
        return [ing.strip() for ing in ingredients if ing]  # Remove empty items
    except Exception as e:
        print(f"❌ Gemini AI Ingredient Extraction Failed: {e}")
        return None



def fetch_nutrition_data(ingredient):
    """Fetches nutrition data from the FoodData Central API."""
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingredient}&api_key={FOODDATA_API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if "foods" in data and len(data["foods"]) > 0:
            food = data["foods"][0]
            return {
                "name": food.get("description", "Unknown"),
                "calories": food.get("foodNutrients", [{}])[0].get("value", 0),
                "protein": food.get("foodNutrients", [{}])[1].get("value", 0),
                "carbs": food.get("foodNutrients", [{}])[2].get("value", 0),
                "fats": food.get("foodNutrients", [{}])[3].get("value", 0),
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Failed to fetch nutrition data: {e}")
        return None


def save_to_firebase(ingredients, nutrition_data):
    """Stores the extracted ingredients and their nutrition details in Firebase."""
    ref = db.reference('/bitecheck')  # Firebase Reference
    data = {
        "ingredients": ingredients,
        "nutrition": nutrition_data
    }
    ref.push(data)  # Push data to Firebase
    print("✅ Data stored in Firebase successfully!")


if __name__ == "__main__":
    image_path = "sample.jpg"  # Replace with your test image

    # Step 1: Extract Text from Image
    extracted_text = extract_text_from_image(image_path)
    print("\n📝 Extracted Text:", extracted_text)

    # Step 2: Extract Ingredients using Gemini AI
    ingredients = extract_ingredients(extracted_text)
    print("\n🛒 Extracted Ingredients:", ingredients)

    # Step 3: Fetch Nutrition Data for each ingredient
    nutrition_info = {ing: fetch_nutrition_data(ing) for ing in ingredients} if ingredients else {}

    # Step 4: Save Data to Firebase
    if ingredients and nutrition_info:
        save_to_firebase(ingredients, nutrition_info)
