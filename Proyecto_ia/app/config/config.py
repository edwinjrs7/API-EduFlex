import os 
from dotenv import load_dotenv  

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

api_keys_env = os.getenv("Gemini_Api_key")

if api_keys_env:
    API_KEYS = [key.strip() for key in api_keys_env.split(",") if key.strip()]
else:
    API_KEYS = []