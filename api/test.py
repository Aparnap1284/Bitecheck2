import json
from ocr_processing import extract_text_from_image, extract_ingredients, fetch_nutrition_data, save_to_firebase

# Path to image file
image_path = "britannia.jpg"  # Update with your image file

# Step 1: Extract text from image
print("\n📌 Extracting Text...")
raw_text = extract_text_from_image(image_path)

if not raw_text:
    print("❌ No text extracted.")
    exit()

print("\n✅ FULL OCR OUTPUT:\n", raw_text)

# Step 2: Extract ingredients
ingredients = extract_ingredients(raw_text)

if not ingredients:
    print("\n❌ No ingredients found.")
    exit()

print("\n✅ Found Ingredients:", ingredients)

# Step 3: Fetch nutrition data for each ingredient
nutrition_data = {}

for ingredient in ingredients:
    nutrition = fetch_nutrition_data(ingredient)
    if nutrition:
        nutrition_data[ingredient] = nutrition

print("\n✅ Nutrition Data:", json.dumps(nutrition_data, indent=2))

# Step 4: Save to Firebase
save_to_firebase(ingredients, nutrition_data)

print("\n🎉 Process Completed Successfully!")
