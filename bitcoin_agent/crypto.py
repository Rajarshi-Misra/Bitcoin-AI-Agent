import requests
import os
from dotenv import load_dotenv

def get_crypto_price():
    print("Fetching...")
    load_dotenv()
    api_key = os.getenv("COIN_API")
    headers = {
    "X-Api-Key": api_key
    }
    url = f"https://api.api-ninjas.com/v1/bitcoin"
    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()
        return response.json()["price"]
    except requests.RequestException as e:
        return f"Error fetching cryptocurrency price: {e}"