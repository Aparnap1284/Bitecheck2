import requests

# Replace with your actual FoodData Central API key
API_KEY = "Y53tr7na8EuZPEpUMzSGEzrthSaAFt9WY2cVg6i7"

def get_nutrition(ingredient):
    """Fetches nutrition data for a given ingredient using FoodData Central API."""
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingredient}&api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "foods" in data and data["foods"]:
            food_item = data["foods"][0]  # Get the first match
            return {
                "name": food_item["description"],
                "calories": food_item["foodNutrients"][3]["value"],  # Energy in kcal
                "protein": food_item["foodNutrients"][0]["value"],  # Protein in g
                "carbs": food_item["foodNutrients"][1]["value"],  # Carbs in g
                "fats": food_item["foodNutrients"][2]["value"],  # Fats in g
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Nutrition API Error: {e}")
        return None

# Example Test
if __name__ == "__main__":
    ingredient = "banana"
    nutrition_info = get_nutrition(ingredient)
    print("\n✅ Nutrition Data:", nutrition_info)
