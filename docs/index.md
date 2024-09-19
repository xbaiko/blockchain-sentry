# BlockchainSentry Documentation

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)

---

## Introduction

**BlockchainSentry** is a simple cryptocurrency price monitoring tool that allows users to select multiple cryptocurrencies and track their real-time prices. The app provides an auto-refresh feature as well as a manual refresh option, with prices displayed directly in the app window. This is the beta version of BlockchainSentry.

---

## Features

- Monitor prices for multiple cryptocurrencies using the CoinGecko API.
- Auto-refresh cryptocurrency prices at a configurable interval.
- Manual price refresh option.
- Intuitive user interface.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/blockchain-sentry.git
   cd blockchain-sentry

2. **Install dependencies: Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
   
3. **Run the application: Run the app by executing**:
    ```bash
    python main.py

## Configuration

The app uses a `config.yaml` file to configure settings such as which cryptocurrencies to monitor and how often to refresh the data.

Here is an example `config.yaml` file:

```yaml
# List of cryptocurrencies to monitor
cryptocurrencies:
  - bitcoin
  - ethereum
  - ripple

# Auto-refresh interval in seconds (default: 180 seconds)
refresh_interval: 180
```

- cryptocurrencies: A list of CoinGecko API cryptocurrency IDs that you wish to monitor.
- refresh_interval: The time (in seconds) between each automatic price refresh (default: 180 seconds).

## Usage

1. **Starting the application**:
   - When the app starts, a list of cryptocurrencies will be presented. You can select the cryptocurrencies you want to monitor.
   - Click "Get Prices" to display the selected cryptocurrency prices.

2. **Price monitoring**:
   - The app will display the current prices of the selected cryptocurrencies.
   - Prices will automatically refresh based on the interval set in `config.yaml`.
   - You can also manually refresh the prices using the "Manual Refresh" button.

3. **Example workflow**:
   - After starting the app, select cryptocurrencies like `bitcoin` and `ethereum` from the list.
   - Click **Get Prices** to view real-time prices.
   - The app will auto-refresh the prices every 3 minutes by default.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
