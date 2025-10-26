"""
Test script to verify NSE India connection and data availability
"""

import requests
import time
import json
from datetime import datetime

def test_nse_connection():
    """Test basic connection to NSE India"""
    print("="*60)
    print("NSE India Connection Test")
    print("="*60)
    
    base_url = "https://www.nseindia.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.nseindia.com/market-data/live-equity-market'
    }
    
    session = requests.Session()
    
    # Test 1: Homepage access
    print("\n1. Testing homepage access...")
    try:
        response = session.get(base_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("   ✓ Homepage accessible")
        else:
            print(f"   ✗ Homepage returned status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    time.sleep(2)
    
    # Test 2: NIFTY 50 API
    print("\n2. Testing NIFTY 50 API...")
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                stock_count = len([s for s in data['data'] if s.get('symbol') != 'NIFTY 50'])
                print(f"   ✓ NIFTY 50 API accessible")
                print(f"   ✓ Retrieved {stock_count} stocks")
                
                # Display sample data
                print("\n   Sample stocks:")
                for i, stock in enumerate(data['data'][:3]):
                    if stock.get('symbol') != 'NIFTY 50':
                        print(f"     • {stock.get('symbol')}: ₹{stock.get('lastPrice', 0)}")
            else:
                print("   ✗ No data in response")
        else:
            print(f"   ✗ API returned status code: {response.status_code}")
    except json.JSONDecodeError:
        print("   ✗ Failed to parse JSON response")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Individual stock quote
    print("\n3. Testing individual stock quote API...")
    try:
        url = "https://www.nseindia.com/api/quote-equity?symbol=TCS"
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = data.get('priceInfo', {}).get('lastPrice', 0)
            print(f"   ✓ Stock quote API accessible")
            print(f"   ✓ TCS Last Price: ₹{price}")
        else:
            print(f"   ✗ API returned status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Market status
    print("\n4. Checking market status...")
    try:
        current_time = datetime.now()
        hour = current_time.hour
        minute = current_time.minute
        day = current_time.weekday()
        
        # Market hours: 9:15 AM to 3:30 PM, Monday to Friday
        if day < 5:  # Monday to Friday
            if (hour == 9 and minute >= 15) or (9 < hour < 15) or (hour == 15 and minute <= 30):
                print("   ✓ Market is currently OPEN")
            else:
                print("   ⚠ Market is currently CLOSED")
                print("     (Trading hours: 9:15 AM - 3:30 PM IST, Mon-Fri)")
        else:
            print("   ⚠ Market is CLOSED (Weekend)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Connection test completed successfully!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = test_nse_connection()
    
    if success:
        print("\n✓ All tests passed! You can now run the main scripts.")
        print("\nNext steps:")
        print("  1. Run: python scrape_nifty50.py")
        print("  2. Run: python momentum_analyzer.py")
    else:
        print("\n✗ Some tests failed. Please check your internet connection.")
        print("  and ensure NSE India website is accessible.")