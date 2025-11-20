#!/usr/bin/env python3
"""
Test script for S&P 500 Index retrieval across different APIs and symbols.
Tests: Alpha Vantage, Finnhub, Marketstack
Symbols: SPX, ^SPX, ^GSPC
"""

import os
import requests
from datetime import datetime
import json

# Load API keys from environment
ALPHAVANTAGE_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
FINNHUB_KEY = os.getenv('FINNHUB_API_KEY')
MARKETSTACK_KEY = os.getenv('MARKETSTACK_API_KEY')

def test_alphavantage(symbol):
    """Test Alpha Vantage API for S&P 500 retrieval."""
    if not ALPHAVANTAGE_KEY:
        return {"error": "ALPHAVANTAGE_API_KEY not set"}
    
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': ALPHAVANTAGE_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'Global Quote' in data and data['Global Quote']:
            quote = data['Global Quote']
            return {
                "success": True,
                "price": float(quote.get('05. price', 0)),
                "symbol": quote.get('01. symbol'),
                "latest_day": quote.get('07. latest trading day'),
                "raw_response": quote
            }
        else:
            return {
                "success": False,
                "error": "No Global Quote in response",
                "raw_response": data
            }
    except Exception as e:
        return {"error": str(e)}

def test_finnhub(symbol):
    """Test Finnhub API for S&P 500 retrieval."""
    if not FINNHUB_KEY:
        return {"error": "FINNHUB_API_KEY not set"}
    
    url = "https://finnhub.io/api/v1/quote"
    params = {
        'symbol': symbol,
        'token': FINNHUB_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'c' in data and data['c'] > 0:
            return {
                "success": True,
                "price": data['c'],
                "timestamp": datetime.fromtimestamp(data.get('t', 0)).strftime('%Y-%m-%d'),
                "raw_response": data
            }
        else:
            return {
                "success": False,
                "error": "No valid price in response",
                "raw_response": data
            }
    except Exception as e:
        return {"error": str(e)}

def test_marketstack(symbol):
    """Test Marketstack API for S&P 500 retrieval."""
    if not MARKETSTACK_KEY:
        return {"error": "MARKETSTACK_API_KEY not set"}
    
    url = "http://api.marketstack.com/v1/eod/latest"
    params = {
        'access_key': MARKETSTACK_KEY,
        'symbols': symbol
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            quote = data['data'][0]
            return {
                "success": True,
                "price": quote.get('close'),
                "symbol": quote.get('symbol'),
                "date": quote.get('date'),
                "raw_response": quote
            }
        else:
            return {
                "success": False,
                "error": "No data in response",
                "raw_response": data
            }
    except Exception as e:
        return {"error": str(e)}

def print_result(api_name, symbol, result):
    """Pretty print test result."""
    print(f"\n{'='*60}")
    print(f"API: {api_name} | Symbol: {symbol}")
    print(f"{'='*60}")
    
    if "error" in result and not result.get("success"):
        print(f"❌ ERROR: {result['error']}")
    elif result.get("success"):
        print(f"✅ SUCCESS")
        print(f"   Price: {result.get('price', 'N/A')}")
        if 'symbol' in result:
            print(f"   Symbol: {result['symbol']}")
        if 'latest_day' in result:
            print(f"   Date: {result['latest_day']}")
        elif 'date' in result:
            print(f"   Date: {result['date']}")
        elif 'timestamp' in result:
            print(f"   Date: {result['timestamp']}")
    else:
        print(f"❌ FAILED")
    
    if result.get('raw_response'):
        print(f"\nRaw Response (first 500 chars):")
        print(f"{str(result['raw_response'])[:500]}")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("S&P 500 INDEX RETRIEVAL TEST")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Test symbols
    symbols = ['SPX', '^SPX', '^GSPC']
    
    print("\n" + "🔍 TESTING ALPHA VANTAGE".center(60, "="))
    for symbol in symbols:
        result = test_alphavantage(symbol)
        print_result("Alpha Vantage", symbol, result)
    
    print("\n\n" + "🔍 TESTING FINNHUB".center(60, "="))
    for symbol in symbols:
        result = test_finnhub(symbol)
        print_result("Finnhub", symbol, result)
    
    print("\n\n" + "🔍 TESTING MARKETSTACK".center(60, "="))
    for symbol in symbols:
        result = test_marketstack(symbol)
        print_result("Marketstack", symbol, result)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    # Summary
    print("\n📊 SUMMARY:")
    print("Test all three symbols (SPX, ^SPX, ^GSPC) with each API.")
    print("Expected S&P 500 range: ~6,000 - 7,000")
    print("\nRecommendation:")
    print("- Use the symbol that returns valid prices (~6,700 range)")
    print("- Verify the symbol works consistently across APIs")
    print("- Update portfolio_automation.py to use the working symbol")

if __name__ == "__main__":
    main()
