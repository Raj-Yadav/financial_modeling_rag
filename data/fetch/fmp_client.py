
import requests
from utils.config import FMP_API_KEY

# The new base URL for modern FMP accounts
BASE_URL = "https://financialmodelingprep.com/stable"

def fetch_data(url):
    """Helper function to fetch data and catch HTTP errors."""
    response = requests.get(url)
    
    # Catch errors and print the actual message from FMP
    if response.status_code != 200:
        try:
            error_data = response.json()
            print(f"FMP Error ({response.status_code}): {error_data.get('Error Message', 'Access Denied')}")
        except Exception:
            print(f"HTTP Error {response.status_code}: {response.text}")
            
    response.raise_for_status() 
    return response.json()

def fetch_all(symbol):
    # Notice how the new endpoints use "?symbol=AAPL" instead of "/AAPL?"
    return {
        "profile": fetch_data(
            f"{BASE_URL}/profile?symbol={symbol}&apikey={FMP_API_KEY}"
        ),
        "metrics": fetch_data(
            f"{BASE_URL}/key-metrics?symbol={symbol}&limit=5&apikey={FMP_API_KEY}"
        ),
        "ratios": fetch_data(
            f"{BASE_URL}/ratios?symbol={symbol}&limit=5&apikey={FMP_API_KEY}"
        ),
        "price": fetch_data(
            f"{BASE_URL}/historical-price-eod/full?symbol={symbol}&apikey={FMP_API_KEY}"
        ),
    }

if __name__ == "__main__":
    import pprint
    # Using pprint just makes the large JSON output easier to read in the terminal
    pprint.pprint(fetch_all("AAPL"))
