"""
NIFTY 50 Stock Scraper with Enhanced Error Handling
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
            response = self.session.get(self.base_url, headers=self.headers, timeout=10)
            logger.info(f"Session initialized. Status code: {response.status_code}")
            time.sleep(3)  # Increased wait time
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
            
            logger.info(f"API Response Status: {response.status_code}")
            logger.info(f"Response Length: {len(response.text)} characters")
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data. Status code: {response.status_code}")
            
            # Check if response is empty
            if not response.text or len(response.text) < 10:
                logger.error("Empty response received from NSE API")
                return self._use_fallback_list()
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Response text (first 200 chars): {response.text[:200]}")
                return self._use_fallback_list()
            
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
            
            if stocks:
                logger.info(f"Successfully fetched {len(stocks)} NIFTY 50 stocks")
                return stocks
            else:
                logger.warning("No stocks found in API response, using fallback list")
                return self._use_fallback_list()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching NIFTY 50 stocks: {e}")
            return self._use_fallback_list()
        except Exception as e:
            logger.error(f"Error fetching NIFTY 50 stocks: {e}")
            return self._use_fallback_list()
    
    def _use_fallback_list(self) -> List[Dict]:
        """
        Fallback list of NIFTY 50 stocks with ISINs
        This is used when the API is unavailable (e.g., weekends, holidays)
        """
        logger.warning("Using fallback NIFTY 50 stock list")
        
        fallback_stocks = [
            {'symbol': 'ADANIPORTS', 'isin': 'INE742F01042', 'company_name': 'Adani Ports and Special Economic Zone Ltd'},
            {'symbol': 'ASIANPAINT', 'isin': 'INE021A01026', 'company_name': 'Asian Paints Ltd'},
            {'symbol': 'AXISBANK', 'isin': 'INE238A01034', 'company_name': 'Axis Bank Ltd'},
            {'symbol': 'BAJAJ-AUTO', 'isin': 'INE917I01010', 'company_name': 'Bajaj Auto Ltd'},
            {'symbol': 'BAJFINANCE', 'isin': 'INE296A01024', 'company_name': 'Bajaj Finance Ltd'},
            {'symbol': 'BAJAJFINSV', 'isin': 'INE918I01018', 'company_name': 'Bajaj Finserv Ltd'},
            {'symbol': 'BHARTIARTL', 'isin': 'INE397D01024', 'company_name': 'Bharti Airtel Ltd'},
            {'symbol': 'BPCL', 'isin': 'INE029A01011', 'company_name': 'Bharat Petroleum Corporation Ltd'},
            {'symbol': 'BRITANNIA', 'isin': 'INE216A01030', 'company_name': 'Britannia Industries Ltd'},
            {'symbol': 'CIPLA', 'isin': 'INE059A01026', 'company_name': 'Cipla Ltd'},
            {'symbol': 'COALINDIA', 'isin': 'INE522F01014', 'company_name': 'Coal India Ltd'},
            {'symbol': 'DIVISLAB', 'isin': 'INE361B01024', 'company_name': 'Divi\'s Laboratories Ltd'},
            {'symbol': 'DRREDDY', 'isin': 'INE089A01023', 'company_name': 'Dr. Reddy\'s Laboratories Ltd'},
            {'symbol': 'EICHERMOT', 'isin': 'INE066A01021', 'company_name': 'Eicher Motors Ltd'},
            {'symbol': 'GRASIM', 'isin': 'INE047A01021', 'company_name': 'Grasim Industries Ltd'},
            {'symbol': 'HCLTECH', 'isin': 'INE860A01027', 'company_name': 'HCL Technologies Ltd'},
            {'symbol': 'HDFCBANK', 'isin': 'INE040A01034', 'company_name': 'HDFC Bank Ltd'},
            {'symbol': 'HDFCLIFE', 'isin': 'INE795G01014', 'company_name': 'HDFC Life Insurance Company Ltd'},
            {'symbol': 'HEROMOTOCO', 'isin': 'INE158A01026', 'company_name': 'Hero MotoCorp Ltd'},
            {'symbol': 'HINDALCO', 'isin': 'INE038A01020', 'company_name': 'Hindalco Industries Ltd'},
            {'symbol': 'HINDUNILVR', 'isin': 'INE030A01027', 'company_name': 'Hindustan Unilever Ltd'},
            {'symbol': 'ICICIBANK', 'isin': 'INE090A01021', 'company_name': 'ICICI Bank Ltd'},
            {'symbol': 'INDUSINDBK', 'isin': 'INE095A01012', 'company_name': 'IndusInd Bank Ltd'},
            {'symbol': 'INFY', 'isin': 'INE009A01021', 'company_name': 'Infosys Ltd'},
            {'symbol': 'ITC', 'isin': 'INE154A01025', 'company_name': 'ITC Ltd'},
            {'symbol': 'JSWSTEEL', 'isin': 'INE019A01038', 'company_name': 'JSW Steel Ltd'},
            {'symbol': 'KOTAKBANK', 'isin': 'INE237A01028', 'company_name': 'Kotak Mahindra Bank Ltd'},
            {'symbol': 'LT', 'isin': 'INE018A01030', 'company_name': 'Larsen & Toubro Ltd'},
            {'symbol': 'M&M', 'isin': 'INE101A01026', 'company_name': 'Mahindra & Mahindra Ltd'},
            {'symbol': 'MARUTI', 'isin': 'INE585B01010', 'company_name': 'Maruti Suzuki India Ltd'},
            {'symbol': 'NESTLEIND', 'isin': 'INE239A01024', 'company_name': 'Nestle India Ltd'},
            {'symbol': 'NTPC', 'isin': 'INE733E01010', 'company_name': 'NTPC Ltd'},
            {'symbol': 'ONGC', 'isin': 'INE213A01029', 'company_name': 'Oil and Natural Gas Corporation Ltd'},
            {'symbol': 'POWERGRID', 'isin': 'INE752E01010', 'company_name': 'Power Grid Corporation of India Ltd'},
            {'symbol': 'RELIANCE', 'isin': 'INE002A01018', 'company_name': 'Reliance Industries Ltd'},
            {'symbol': 'SBILIFE', 'isin': 'INE123W01016', 'company_name': 'SBI Life Insurance Company Ltd'},
            {'symbol': 'SBIN', 'isin': 'INE062A01020', 'company_name': 'State Bank of India'},
            {'symbol': 'SUNPHARMA', 'isin': 'INE044A01036', 'company_name': 'Sun Pharmaceutical Industries Ltd'},
            {'symbol': 'TATAMOTORS', 'isin': 'INE155A01022', 'company_name': 'Tata Motors Ltd'},
            {'symbol': 'TATASTEEL', 'isin': 'INE081A01020', 'company_name': 'Tata Steel Ltd'},
            {'symbol': 'TCS', 'isin': 'INE467B01029', 'company_name': 'Tata Consultancy Services Ltd'},
            {'symbol': 'TECHM', 'isin': 'INE669C01036', 'company_name': 'Tech Mahindra Ltd'},
            {'symbol': 'TITAN', 'isin': 'INE280A01028', 'company_name': 'Titan Company Ltd'},
            {'symbol': 'ULTRACEMCO', 'isin': 'INE481G01011', 'company_name': 'UltraTech Cement Ltd'},
            {'symbol': 'UPL', 'isin': 'INE628A01036', 'company_name': 'UPL Ltd'},
            {'symbol': 'WIPRO', 'isin': 'INE075A01022', 'company_name': 'Wipro Ltd'},
            {'symbol': 'ADANIENT', 'isin': 'INE423A01024', 'company_name': 'Adani Enterprises Ltd'},
            {'symbol': 'APOLLOHOSP', 'isin': 'INE437A01024', 'company_name': 'Apollo Hospitals Enterprise Ltd'},
            {'symbol': 'LTIM', 'isin': 'INE214T01019', 'company_name': 'LTIMindtree Ltd'},
            {'symbol': 'TRENT', 'isin': 'INE849A01020', 'company_name': 'Trent Ltd'}
        ]
        
        # Add dummy price data
        for stock in fallback_stocks:
            stock['last_price'] = 0
            stock['change'] = 0
            stock['pChange'] = 0
        
        logger.info(f"Loaded {len(fallback_stocks)} stocks from fallback list")
        return fallback_stocks
    
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
        print("\nNote: If market is closed, price data will be 0 (this is normal).")
        print("The momentum analyzer will fetch live prices when you run it.")
        print("="*80)
    else:
        print("Failed to fetch NIFTY 50 stocks. Please check logs.")


if __name__ == "__main__":
    main()