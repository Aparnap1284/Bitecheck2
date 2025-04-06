import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, db

# Initialize Flask app
app = Flask(__name__)  # ✅ Correct Flask initialization
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ Correct CORS setup

# Load environment variables (correct way)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Set this in Render
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS")  # JSON string from Render env
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")  # Set this in Render

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
else:
    raise ValueError("GEMINI_API_KEY environment variable is missing!")

# Initialize Firebase
if FIREBASE_CREDENTIALS_JSON and FIREBASE_DATABASE_URL:
    try:
        firebase_credentials = json.loads(FIREBASE_CREDENTIALS_JSON)  # Convert JSON string to dict
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})
        chat_ref = db.reference("/chats")
    except Exception as e:
        print(f"Firebase Initialization Error: {e}")
        chat_ref = None  # Prevent crashes if Firebase is misconfigured
else:
    print("Firebase environment variables missing! Using local mode.")
    chat_ref = None  # Avoid errors if Firebase isn't set up properly

# Predefined food-related options
food_queries = {
    "1": "Nutritional value of an ingredient (e.g., apple, paneer)",
    "2": "Health benefits of a specific food (e.g., almonds, turmeric)",
    "3": "Alternatives for a specific ingredient (e.g., dairy-free milk alternatives)",
    "4": "Best diet for specific health goals (e.g., weight loss, muscle gain)",
    "5": "Food safety and storage tips",
    "6": "Quick and healthy meal ideas",
    "7": "Allergy-friendly food options",
    "8": "Alternative options for common food allergies"
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to BiteCheck Chatbot API!"})

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        user_input = request.args.get("query", "")
    else:  # POST request
        data = request.get_json()
        user_input = data.get("query", "")

    # If no user input, return the options list as the first response
    if not user_input:
        options_list = "\n".join([f"{key}. {value}" for key, value in food_queries.items()])
        return jsonify({
            "response": "Welcome! Please choose an option by entering a number:\n" + options_list
        })

    # Process user query normally
    user_query = food_queries.get(user_input, user_input)

    response = model.generate_content(
        [{"role": "user", "parts": [user_query]}], 
        generation_config={"max_output_tokens": 150}
    )
    bot_reply = response.text
    
    # Store conversation in Firebase
    if chat_ref:  # ✅ Prevents error if Firebase isn't configured
        try:
            chat_ref.push({
                "user": user_query,
                "bot": bot_reply
            })
        except Exception as e:
            print(f"Error storing chat in Firebase: {e}")

    return jsonify({"response": bot_reply})

if __name__ == "__main__":  # ✅ Correct way to start Flask app
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))  # Works on Render
