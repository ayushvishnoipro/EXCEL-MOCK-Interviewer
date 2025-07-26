import os
from dotenv import load_dotenv

print("Testing .env file loading...")

# Load environment variables
load_dotenv()

# Check if the API key is loaded
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {api_key}")
print(f"API Key length: {len(api_key) if api_key else 'None'}")
print(f"API Key type: {type(api_key)}")

if api_key:
    print("✅ API key loaded successfully!")
else:
    print("❌ API key not found!")
    
# Also check current working directory
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")
