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

        update_callback(data)
        last_refreshed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_time_callback(f"Last refreshed: {last_refreshed_time}")

    except requests.exceptions.RequestException as e:
        update_callback(f"Error fetching prices: {e}")


# Close the application
def close_app():
    root.destroy()


# Handles the 'Get Prices' button click event and switches to the price display
def on_submit():
    selected_indices = listbox.curselection()
    selected_coins = [cryptocurrencies[i] for i in selected_indices]

    # Display a warning message if no currencies are selected
    if not selected_coins:
        result_label.config(text="Please select at least one cryptocurrency.", fg="#ff0000")  # Red warning text
        return

    # Clear the warning if selections were made
    result_label.config(text="")

    # Hide selection elements and show price view
    selection_frame.pack_forget()

    # Dynamically adjust window size based on the number of selected coins and content below
    dynamic_height = 300 + (len(selected_coins) * 40) + 100  # Extra 100 for last refreshed and buttons
    root.geometry(f"600x{dynamic_height}+300+200")

    # Adjust width based on the longest text "Last refreshed" and "Next refresh"
    longest_text_width = max(len("Last refreshed: YYYY-MM-DD HH:MM:SS"), len("Next refresh in: 00:00"))
    dynamic_width = longest_text_width * 10  # Estimate character width
    root.geometry(f"{dynamic_width + 100}x{dynamic_height}+300+200")  # Add 100 for padding

    price_frame.pack(fill="both", expand=True)

    open_price_view(selected_coins)


# Display cryptocurrency prices and set up refresh logic
def open_price_view(selected_coins):
    # Clear previous price data in case the frame was already used
    for widget in price_display_frame.winfo_children():
        widget.destroy()

    def update_price_display(data):
        """Updates the price display with the latest data."""
        for widget in price_display_frame.winfo_children():
            widget.destroy()

        longest_coin = max(len(coin) for coin in selected_coins)
        for i, coin in enumerate(selected_coins):
            coin_data = data.get(coin)
            if coin_data:
                price = f"${coin_data.get('usd'):,.2f}"
                # Create labels for coin name, symbol, and price
                coin_label = tk.Label(price_display_frame, text=coin.capitalize(), font=("Courier", 12), bg="black",
                                      fg="#00ff00")
                symbol_label = tk.Label(price_display_frame, text="⚡", font=("Courier", 12, "bold"), bg="black",
                                        fg="#00ff00")  # Cyberpunk/crypto symbol
                price_label = tk.Label(price_display_frame, text=price, font=("Courier", 12, "bold"), bg="black",
                                       fg="white")

                # Place the labels in a grid, with reduced padding for tighter layout
                coin_label.grid(row=i, column=0, padx=(40, 5), pady=5,
                                sticky="e")  # Shift coin name slightly left, reduce right padding
                symbol_label.grid(row=i, column=1, padx=5, pady=5)  # Reduce padding around the symbol
                price_label.grid(row=i, column=2, padx=5, pady=5, sticky="w")  # Reduce padding for price
            else:
                coin_label = tk.Label(price_display_frame, text=f"{coin.capitalize()} Price data not available",
                                      font=("Courier", 12), bg="black", fg="#00ff00")
                coin_label.grid(row=i, column=0, columnspan=3, pady=5)

    def update_last_refreshed_time(text):
        last_refreshed_label.config(text=text)

    def refresh_prices():
        """Fetches new prices and resets the countdown for the next refresh."""
        get_crypto_prices(selected_coins, update_price_display, update_last_refreshed_time)

    # Start the countdown for the next refresh
    def set_refresh_countdown(seconds_left):
        if seconds_left > 0:
            minutes, seconds = divmod(seconds_left, 60)
            next_refresh_label.config(text=f"Next refresh in: {minutes}:{seconds:02d}")
            root.after(1000, set_refresh_countdown, seconds_left - 1)
        else:
            refresh_prices()
            set_refresh_countdown(refresh_interval)

    # Show the refresh button after displaying the prices
    refresh_button.pack(pady=10)

    refresh_interval = config.get('refresh_interval', 180)  # Default to 3 minutes
    refresh_prices()
    set_refresh_countdown(refresh_interval)


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

# Frame for the selection page
selection_frame = tk.Frame(root, bg="black")
selection_frame.pack(fill="both", expand=True, padx=10, pady=10)

instruction_label = tk.Label(selection_frame, text="Select the cryptocurrencies you want to monitor:",
                             font=("Courier", 12, "bold"), bg="black", fg="#00ff00")
instruction_label.pack(pady=10)

# Listbox for cryptocurrency selection
listbox = tk.Listbox(selection_frame, selectmode="multiple", height=20, exportselection=0, bg="black", fg="#00ff00",
                     font=("Courier", 12), selectbackground="#00ff00", selectforeground="black")
for crypto in cryptocurrencies:
    listbox.insert(tk.END, crypto)
listbox.pack(padx=10, pady=10)

# "Get Prices" button
submit_button = tk.Button(selection_frame, text="Get Prices", font=("Courier", 12, "bold"), bg="#00ff00", fg="black",
                          relief="flat", command=on_submit)
submit_button.pack(pady=10)

# Label for displaying the warning when no currencies are selected
result_label = tk.Label(selection_frame, text="", justify="left", font=("Courier", 12), bg="black", fg="#00ff00")
result_label.pack(pady=10)

# Frame for the price display page (initially hidden)
price_frame = tk.Frame(root, bg="black")

# Frame to hold the price data, centered
price_display_frame = tk.Frame(price_frame, bg="black")
price_display_frame.grid_columnconfigure(0, weight=1)
price_display_frame.grid_columnconfigure(1, weight=1)
price_display_frame.grid_columnconfigure(2, weight=1)
price_display_frame.pack(fill="both", expand=True, pady=10, padx=10)

# Center the price display within the window
price_frame.pack_propagate(False)

# Labels for refresh information
last_refreshed_label = tk.Label(price_frame, text="Last refreshed: N/A", font=("Courier", 10), bg="black", fg="#00ff00")
last_refreshed_label.pack(pady=5)

next_refresh_label = tk.Label(price_frame, text="Next refresh in: 3:00", font=("Courier", 10), bg="black", fg="#00ff00")
next_refresh_label.pack(pady=5)

# Manual refresh button
refresh_button = tk.Button(price_frame, text="Manual Refresh", font=("Courier", 10, "bold"), bg="#00ff00", fg="black",
                           relief="flat")

# Bind the title bar for moving the window
title_bar.bind("<Button-1>", start_move)
title_bar.bind("<ButtonRelease-1>", stop_move)
title_bar.bind("<B1-Motion>", do_move)

root.mainloop()
