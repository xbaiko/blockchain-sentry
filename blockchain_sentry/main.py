import tkinter as tk
import requests
import yaml
from datetime import datetime

# CoinGecko API URL for checking cryptocurrency prices
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"


# Load configuration from config.yaml
def load_config(config_file="config.yaml"):
    """Load configuration from the given YAML file."""
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


# Fetch cryptocurrency prices from the CoinGecko API and update the display
def get_crypto_prices(selected_coins, update_callback, update_time_callback):
    if not selected_coins:
        return

    coin_ids = ",".join(selected_coins)
    params = {"ids": coin_ids, "vs_currencies": "usd"}

    try:
        response = requests.get(COINGECKO_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        result_text = ""
        longest_coin = max(len(coin) for coin in selected_coins)
        for coin in selected_coins:
            coin_data = data.get(coin)
            if coin_data:
                price = f"${coin_data.get('usd'):,.2f}"
                result_text += f"{coin.capitalize().ljust(longest_coin)} {price}\n"
            else:
                result_text += f"{coin.capitalize().ljust(longest_coin)} Price data not available\n"

        update_callback(result_text, data)
        last_refreshed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_time_callback(f"Last refreshed: {last_refreshed_time}")

    except requests.exceptions.RequestException as e:
        update_callback(f"Error fetching prices: {e}", {})


# Close the application
def close_app():
    root.destroy()


# Handles the 'Get Prices' button click event and switches to the price display
def on_submit():
    selected_indices = listbox.curselection()
    selected_coins = [cryptocurrencies[i] for i in selected_indices]

    if not selected_coins:
        result_label.config(text="No cryptocurrencies selected.")
        return

    # Hide selection elements and show price view
    listbox.pack_forget()
    submit_button.pack_forget()
    instruction_label.pack_forget()

    open_price_view(selected_coins)


# Display cryptocurrency prices and set up refresh logic
def open_price_view(selected_coins):
    price_frame.pack(pady=10, padx=10)

    countdown_id = None  # Initialize countdown_id here

    def update_price_display(text, data):
        """Updates the price display with the latest data."""
        for widget in price_frame.winfo_children():
            widget.destroy()

        longest_coin = max(len(coin) for coin in selected_coins)
        for coin in selected_coins:
            coin_data = data.get(coin)
            if coin_data:
                price = f"${coin_data.get('usd'):,.2f}"
                row_frame = tk.Frame(price_frame, bg="black")
                coin_label = tk.Label(row_frame, text=coin.capitalize().ljust(longest_coin), font=("Courier", 12),
                                      bg="black", fg="#00ff00")
                coin_label.pack(side="left")
                price_label = tk.Label(row_frame, text=price, font=("Courier", 12, "bold"), bg="black", fg="white")
                price_label.pack(side="left", padx=10)
                row_frame.pack(anchor="w")
            else:
                coin_label = tk.Label(price_frame,
                                      text=f"{coin.capitalize().ljust(longest_coin)} Price data not available",
                                      font=("Courier", 12), bg="black", fg="#00ff00")
                coin_label.pack(anchor="w")

    def update_last_refreshed_time(text):
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
        nonlocal countdown_id
        minutes, seconds = divmod(seconds_left, 60)
        next_refresh_label.config(text=f"Next refresh in: {minutes}:{seconds:02d}")
        if seconds_left > 0:
            countdown_id = root.after(1000, set_refresh_countdown, seconds_left - 1)
        else:
            refresh_prices()

    refresh_interval = config.get('refresh_interval', 180)
    refresh_prices()


# Make the window draggable by clicking and dragging the custom title bar
def start_move(event):
    root.x = event.x
    root.y = event.y


def stop_move(event):
    root.x = None
    root.y = None


def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    root.geometry(f"+{root.winfo_x() + deltax}+{root.winfo_y() + deltay}")


# Load the config file
config = load_config()
cryptocurrencies = config.get('cryptocurrencies', [])

if not cryptocurrencies:
    raise ValueError("No cryptocurrencies found in config.yaml")

# Main application window with custom title bar
root = tk.Tk()
root.overrideredirect(True)  # Remove the OS title bar

# Custom window size and background
root.geometry("800x600+300+200")
root.configure(bg="black")

# Custom title bar
title_bar = tk.Frame(root, bg="#00ff00", relief="raised", bd=2)
title_bar.pack(side="top", fill="x")

# Title in the custom title bar
title_label = tk.Label(title_bar, text="Blockchain Sentry", font=("Courier", 12, "bold"), bg="#00ff00", fg="black")
title_label.pack(side="left", padx=10)

# Close button in the custom title bar
close_button = tk.Button(title_bar, text="X", font=("Courier", 12, "bold"), bg="#ff0000", fg="white", command=close_app,
                         relief="flat")
close_button.pack(side="right", padx=10)

# Main content area
content_frame = tk.Frame(root, bg="black")
content_frame.pack(fill="both", expand=True, padx=10, pady=10)

instruction_label = tk.Label(content_frame, text="Select the cryptocurrencies you want to monitor:",
                             font=("Courier", 12, "bold"), bg="black", fg="#00ff00")
instruction_label.pack(pady=10)

# Listbox for cryptocurrency selection
listbox = tk.Listbox(content_frame, selectmode="multiple", height=20, exportselection=0, bg="black", fg="#00ff00",
                     font=("Courier", 12), selectbackground="#00ff00", selectforeground="black")
for crypto in cryptocurrencies:
    listbox.insert(tk.END, crypto)
listbox.pack(padx=10, pady=10)

# "Get Prices" button
submit_button = tk.Button(content_frame, text="Get Prices", font=("Courier", 12, "bold"), bg="#00ff00", fg="black",
                          relief="flat", command=on_submit)
submit_button.pack(pady=10)

result_label = tk.Label(content_frame, text="", justify="left", font=("Courier", 12), bg="black", fg="#00ff00")
result_label.pack(pady=10)

# Create frame for displaying prices - This frame will take the place of the selection elements
price_frame = tk.Frame(root, bg="black")

# Labels for refresh information
last_refreshed_label = tk.Label(root, text="Last refreshed: N/A", font=("Courier", 10), bg="black", fg="#00ff00")
last_refreshed_label.pack(pady=5)

next_refresh_label = tk.Label(root, text="Next refresh in: 3:00", font=("Courier", 10), bg="black", fg="#00ff00")
next_refresh_label.pack(pady=5)

countdown_id = None

# Bind the title bar for moving the window
title_bar.bind("<Button-1>", start_move)
title_bar.bind("<ButtonRelease-1>", stop_move)
title_bar.bind("<B1-Motion>", do_move)

root.mainloop()
