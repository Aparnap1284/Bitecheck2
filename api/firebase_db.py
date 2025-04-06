import os
import json

firebase_credentials = os.getenv("FIREBASE_CONFIG")

if not firebase_credentials:
    print("❌ ERROR: FIREBASE_CONFIG environment variable is empty or not set.")
    exit(1)

try:
    # Convert JSON string from env variable into a dictionary
    cred_data = json.loads(firebase_credentials)
    
    # Save credentials as a file
    credentials_path = "/tmp/serviceAccountKey.json"
    with open(credentials_path, "w") as file:
        json.dump(cred_data, file)

    print("✅ Firebase Credentials Saved Successfully!")

except json.JSONDecodeError as e:
    print(f"❌ JSON Parsing Error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    exit(1)
