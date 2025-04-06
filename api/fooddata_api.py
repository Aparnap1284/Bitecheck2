import requests

# Replace with your actual FoodData Central API Key
API_KEY = "YOUR_FOODDATA_CENTRAL_API_KEY"
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

def get_nutrition(ingredient):
    """Fetch nutritional data for a given ingredient using FoodData API."""
    params = {
        "query": ingredient,
        "api_key": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "foods" in data and len(data["foods"]) > 0:
            food_item = data["foods"][0]  # Take the first match
            nutrition_info = {
                "name": food_item.get("description", "Unknown"),
                "calories": food_item.get("foodNutrients", [{}])[0].get("value", "N/A"),
                "protein": food_item.get("foodNutrients", [{}])[1].get("value", "N/A"),
                "fat": food_item.get("foodNutrients", [{}])[2].get("value", "N/A"),
            }
            return nutrition_info
    return {"error": "Ingredient not found"}
