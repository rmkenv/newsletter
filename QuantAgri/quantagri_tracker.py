import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def fetch_commodity_prices():
    """Pull live prices from Yahoo Finance"""
    symbols = {
        'Soybeans': 'ZS=F',
        'Corn': 'ZC=F',
        'Wheat': 'ZW=F',
        'Sugar': 'SB=F'
    }
    
    prices = {}
    for name, symbol in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                prices[name] = round(data['Close'].iloc[-1], 2)
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return prices

def update_portfolio_tracker():
    """Update CSV with today's prices and calculate P&L"""
    
    # Entry prices from Q1 2025 report
    entry_prices = {
        'Soybeans': 1062.00,
        'Sugar': 14.89,
        'Wheat': 512.50,
        'Corn': 444.50
    }
    
    entry_spread = entry_prices['Wheat'] - entry_prices['Corn']
    
    # Fetch live prices
    live_prices = fetch_commodity_prices()
    print(f"Fetched prices: {live_prices}")
    
    # Load existing tracker or create new
    tracker_file = 'quantagri_tracker.csv'
    today = datetime.now().strftime('%Y-%m-%d')
    
    if os.path.exists(tracker_file):
        df = pd.read_csv(tracker_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Check if today already exists
        if today in df['Date'].dt.strftime('%Y-%m-%d').values:
            print(f"Data for {today} already exists. Updating...")
            df = df[df['Date'].dt.strftime('%Y-%m-%d') != today]
    else:
        df = pd.DataFrame()
    
    # Add today's data
    new_row = {
        'Date': today,
        'Soybeans_cents_bu': live_prices.get('Soybeans', entry_prices['Soybeans']),
        'Sugar_cents_lb': live_prices.get('Sugar', entry_prices['Sugar']),
        'Wheat_cents_bu': live_prices.get('Wheat', entry_prices['Wheat']),
        'Corn_cents_bu': live_prices.get('Corn', entry_prices['Corn'])
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Calculate P&L (negative for shorts)
    df['Soybeans_PnL'] = (entry_prices['Soybeans'] - df['Soybeans_cents_bu']) * 5000
    df['Sugar_PnL'] = (entry_prices['Sugar'] - df['Sugar_cents_lb']) * 360000
    df['Spread_Value'] = df['Wheat_cents_bu'] - df['Corn_cents_bu']
    df['Spread_PnL'] = (df['Spread_Value'] - entry_spread) * 5000
    df['Total_PnL'] = df['Soybeans_PnL'] + df['Sugar_PnL'] + df['Spread_PnL']
    
    # Save
    df.to_csv(tracker_file, index=False)
    
    # Print summary
    latest = df.iloc[-1]
    print(f"\n📊 QuantAgri Tracker Updated: {today}")
    print(f"Soybeans: {latest['Soybeans_cents_bu']:.2f} ¢/bu | P&L: ${latest['Soybeans_PnL']:,.0f}")
    print(f"Sugar: {latest['Sugar_cents_lb']:.2f} ¢/lb | P&L: ${latest['Sugar_PnL']:,.0f}")
    print(f"Spread: {latest['Spread_Value']:.2f} | P&L: ${latest['Spread_PnL']:,.0f}")
    print(f"💰 Total Portfolio P&L: ${latest['Total_PnL']:,.0f}\n")
    
    return df

if __name__ == "__main__":
    update_portfolio_tracker()
