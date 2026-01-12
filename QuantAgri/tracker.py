import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def fetch_commodity_prices():
    """Pull live prices from Yahoo Finance"""
    symbols = {
        'Soybeans': 'ZS=F',      # CBOT Soybeans
        'Corn': 'ZC=F',          # CBOT Corn
        'Wheat': 'ZW=F',         # CBOT Wheat
        'Sugar': 'SB=F'          # ICE Sugar #11
    }
    
    prices = {}
    for name, symbol in symbols.items():
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        if not data.empty:
            prices[name] = data['Close'].iloc[-1]
    
    return prices

def update_portfolio_tracker():
    """Update CSV with today's prices and calculate P&L"""
    
    # Entry prices from your report
    entry_prices = {
        'Soybeans': 1062.00,
        'Sugar': 14.89,
        'Wheat': 512.50,
        'Corn': 444.50
    }
    
    # Fetch live prices
    live_prices = fetch_commodity_prices()
    
    # Load existing tracker or create new
    tracker_file = 'quantagri_tracker.csv'
    today = datetime.now().strftime('%Y-%m-%d')
    
    if os.path.exists(tracker_file):
        df = pd.read_csv(tracker_file)
    else:
        # Create initial tracker
        dates = pd.date_range('2026-01-12', periods=90)
        df = pd.DataFrame({'Date': dates})
        df['Soybeans_¢bu'] = entry_prices['Soybeans']
        df['Sugar_¢lb'] = entry_prices['Sugar']
        df['Wheat_¢bu'] = entry_prices['Wheat']
        df['Corn_¢bu'] = entry_prices['Corn']
    
    # Update today's row
    today_row = df[df['Date'].dt.strftime('%Y-%m-%d') == today]
    if today_row.empty:
        # Add new row
        new_row = pd.DataFrame({
            'Date': [pd.to_datetime(today)],
            'Soybeans_¢bu': [live_prices.get('Soybeans', entry_prices['Soybeans'])],
            'Sugar_¢lb': [live_prices.get('Sugar', entry_prices['Sugar'])],
            'Wheat_¢bu': [live_prices.get('Wheat', entry_prices['Wheat'])],
            'Corn_¢bu': [live_prices.get('Corn', entry_prices['Corn'])]
        })
        df = pd.concat([df, new_row], ignore_index=True)
    
    # Calculate P&L
    df['Soybeans_PnL'] = (df['Soybeans_¢bu'] - entry_prices['Soybeans']) * 5000
    df['Sugar_PnL'] = (df['Sugar_¢lb'] - entry_prices['Sugar']) * 360000
    df['Spread_Value'] = df['Wheat_¢bu'] - df['Corn_¢bu']
    df['Spread_PnL'] = (df['Spread_Value'] - (entry_prices['Wheat'] - entry_prices['Corn'])) * 5000
    df['Total_PnL'] = df['Soybeans_PnL'] + df['Sugar_PnL'] + df['Spread_PnL']
    
    # Save updated tracker
    df.to_csv(tracker_file, index=False)
    
    # Print summary
    latest = df.iloc[-1]
    print(f"\n📊 QuantAgri Tracker Updated: {today}")
    print(f"Soybeans: {latest['Soybeans_¢bu']:.2f} | P&L: ${latest['Soybeans_PnL']:,.0f}")
    print(f"Sugar: {latest['Sugar_¢lb']:.2f} | P&L: ${latest['Sugar_PnL']:,.0f}")
    print(f"Wheat/Corn Spread: {latest['Spread_Value']:.2f} | P&L: ${latest['Spread_PnL']:,.0f}")
    print(f"💰 Total Portfolio P&L: ${latest['Total_PnL']:,.0f}")
    
    return df

if __name__ == "__main__":
    tracker = update_portfolio_tracker()
