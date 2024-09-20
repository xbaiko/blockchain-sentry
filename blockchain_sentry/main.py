import tkinter as tk
from tkinter import ttk
import requests
import yaml
from datetime import datetime

# CoinGecko API URL for checking cryptocurrency prices
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"


def load_config(config_file="config.yaml"):
    """Load configuration from the given YAML file."""
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


def get_crypto_prices(selected_coins, update_callback, update_time_callback):
    """Fetch cryptocurrency prices from CoinGecko API and update the display."""
    if not selected_coins:
        return

    coin_ids = ",".join(selected_coins)
    params = {"ids": coin_ids, "vs_currencies": "usd"}

    try:
        response = requests.get(COINGECKO_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        result_text = ""
        for coin in selected_coins:
            coin_data = data.get(coin)
            if coin_data:
                price = coin_data.get('usd')
                result_text += f"Current {coin.capitalize()} price: ${price}\n"
            else:
                result_text += f"Price data not available for {coin}\n"

        update_callback(result_text)
        last_refreshed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_time_callback(f"Last refreshed: {last_refreshed_time}")

    except requests.exceptions.RequestException as e:
        update_callback(f"Error fetching prices: {e}")


def on_submit():
    """Handles the 'Get Prices' button click event and switches to the price display."""
    selected_indices = listbox.curselection()
    selected_coins = [cryptocurrencies[i] for i in selected_indices]

    if not selected_coins:
        result_label.config(text="No cryptocurrencies selected.")
        return

    listbox.pack_forget()
    submit_button.pack_forget()
    result_label.pack_forget()
    instruction_label.pack_forget()

    open_price_view(selected_coins)


def open_price_view(selected_coins):
    """Updates the window to display cryptocurrency prices and sets up the refresh logic."""
    root.title("BlockchainSentry - Price Monitor")

    price_label = tk.Label(root, text="", justify="left", font=("Courier", 12), bg="black", fg="#00ff00")
    price_label.pack(pady=10, padx=10)

    last_refreshed_label = tk.Label(root, text="Last refreshed: N/A", font=("Courier", 10), bg="black", fg="#00ff00")
    last_refreshed_label.pack(pady=5)

    next_refresh_label = tk.Label(root, text="Next refresh in: 3:00", font=("Courier", 10), bg="black", fg="#00ff00")
    next_refresh_label.pack(pady=5)

    countdown_id = None

    def update_price_display(text):
        """Updates the price display with the latest data."""
        price_label.config(text=text)

    def update_last_refreshed_time(text):
        """Updates the last refreshed time label."""
        last_refreshed_label.config(text=text)

    def refresh_prices():
        """Fetches new prices and resets the countdown for the next refresh."""
        nonlocal countdown_id
        if countdown_id is not None:
            root.after_cancel(countdown_id)
        get_crypto_prices(selected_coins, update_price_display, update_last_refreshed_time)
        set_refresh_countdown(refresh_interval)

    refresh_button = tk.Button(root, text="Manual Refresh", font=("Courier", 10, "bold"), bg="#00ff00", fg="black",
                               relief="flat", command=refresh_prices)
    refresh_button.pack(pady=10)

    def set_refresh_countdown(seconds_left):
        """Starts or updates the countdown to the next automatic refresh."""
        nonlocal countdown_id
        minutes, seconds = divmod(seconds_left, 60)
        next_refresh_label.config(text=f"Next refresh in: {minutes}:{seconds:02d}")
        if seconds_left > 0:
            countdown_id = root.after(1000, set_refresh_countdown, seconds_left - 1)
        else:
            refresh_prices()

    refresh_interval = config.get('refresh_interval', 180)
    refresh_prices()


# Load the config file
config = load_config()
cryptocurrencies = config.get('cryptocurrencies', [])

if not cryptocurrencies:
    raise ValueError("No cryptocurrencies found in config.yaml")

# Main application window with Punk mode styling
root = tk.Tk()
root.title("Cryptocurrency Price Checker")
root.configure(bg="black")  # Background color is black

# Centering the window on the screen
root.geometry("600x400+300+200")

instruction_label = tk.Label(root, text="Select the cryptocurrencies you want to monitor:",
                             font=("Courier", 12, "bold"), bg="black", fg="#00ff00")
instruction_label.pack(pady=10)

listbox = tk.Listbox(root, selectmode="multiple", height=15, exportselection=0, bg="black", fg="#00ff00",
                     font=("Courier", 12), selectbackground="#00ff00", selectforeground="black")
for crypto in cryptocurrencies:
    listbox.insert(tk.END, crypto)
listbox.pack(padx=10, pady=10)

submit_button = tk.Button(root, text="Get Prices", font=("Courier", 12, "bold"), bg="#00ff00", fg="black",
                          relief="flat", command=on_submit)
submit_button.pack(pady=10)

result_label = tk.Label(root, text="", justify="left", font=("Courier", 12), bg="black", fg="#00ff00")
result_label.pack(pady=10)

root.mainloop()
