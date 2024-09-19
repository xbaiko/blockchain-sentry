import requests
import yaml

# CoinGecko API URL for checking cryptocurrency prices
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"


def load_config(config_file="config.yaml"):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


def get_crypto_prices(config):
    coin_ids = ",".join(config['cryptocurrencies'])

    params = {
        "ids": coin_ids,
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(COINGECKO_API_URL, params=params)
        response.raise_for_status()

        data = response.json()

        for coin, info in data.items():
            print(f"Current {coin.capitalize()} price: ${info['usd']}")

        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching cryptocurrency prices: {e}")
        return None


if __name__ == "__main__":
    config = load_config()
    get_crypto_prices(config)
