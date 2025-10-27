"""
NIFTY 50 Stock Scraper
Fetches the list of NIFTY 50 stocks with their ISINs from NSE India website
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Nifty50Scraper:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.nifty50_url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market'
        }
        self.session = requests.Session()
        
    def _init_session(self):
        """Initialize session by visiting NSE homepage to get cookies"""
        try:
            logger.info("Initializing session with NSE...")
            self.session.get(self.base_url, headers=self.headers, timeout=10)
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            return False
    
    def fetch_nifty50_stocks(self) -> List[Dict]:
        """
        Fetch NIFTY 50 stocks from NSE API
        Returns list of dictionaries with stock details
        """
        try:
            if not self._init_session():
                raise Exception("Failed to initialize session")
            
            logger.info("Fetching NIFTY 50 stocks...")
            response = self.session.get(self.nifty50_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data. Status code: {response.status_code}")
            
            data = response.json()
            stocks = []
            
            if 'data' in data:
                for stock in data['data']:
                    if stock.get('symbol') and stock['symbol'] != 'NIFTY 50':
                        stock_info = {
                            'symbol': stock.get('symbol', ''),
                            'isin': stock.get('meta', {}).get('isin', 'NA'),
                            'company_name': stock.get('meta', {}).get('companyName', stock.get('symbol', '')),
                            'last_price': stock.get('lastPrice', 0),
                            'change': stock.get('change', 0),
                            'pChange': stock.get('pChange', 0)
                        }
                        stocks.append(stock_info)
            
            logger.info(f"Successfully fetched {len(stocks)} NIFTY 50 stocks")
            return stocks
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching NIFTY 50 stocks: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching NIFTY 50 stocks: {e}")
            return []
    
    def save_to_json(self, stocks: List[Dict], filename: str = 'nifty50_stocks.json'):
        """Save stocks data to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(stocks, f, indent=2)
            logger.info(f"Saved {len(stocks)} stocks to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def save_to_csv(self, stocks: List[Dict], filename: str = 'nifty50_stocks.csv'):
        """Save stocks data to CSV file"""
        try:
            df = pd.DataFrame(stocks)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(stocks)} stocks to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")


def main():
    scraper = Nifty50Scraper()
    stocks = scraper.fetch_nifty50_stocks()
    
    if stocks:
        scraper.save_to_json(stocks)
        scraper.save_to_csv(stocks)
        
        print("\n" + "="*80)
        print("NIFTY 50 STOCKS FETCHED SUCCESSFULLY")
        print("="*80)
        print(f"\nTotal stocks: {len(stocks)}\n")
        
        df = pd.DataFrame(stocks)
        print(df[['symbol', 'isin', 'company_name']].to_string(index=False))
        print("\n" + "="*80)
    else:
        print("Failed to fetch NIFTY 50 stocks. Please check logs.")


if __name__ == "__main__":
    main()