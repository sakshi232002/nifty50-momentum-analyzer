"""
Intraday Momentum Analyzer
Fetches live intraday price data and identifies momentum shifts for NIFTY 50 stocks
"""

import requests
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
from typing import Dict, List, Tuple
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntradayMomentumAnalyzer:
    def __init__(self, ma_period: int = 10):
        """
        Initialize momentum analyzer
        Args:
            ma_period: Number of data points for moving average calculation
        """
        self.ma_period = ma_period
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market'
        }
        self.session = requests.Session()
        
        # Store price history for each stock: {symbol: deque of (timestamp, price)}
        self.price_history = defaultdict(lambda: deque(maxlen=60))
        
        # Store momentum shifts: {symbol: list of shifts}
        self.momentum_shifts = defaultdict(list)
        
        # Store previous MA cross status
        self.prev_cross_status = {}
        
        self.stocks = []
        
    def _init_session(self):
        """Initialize session with NSE"""
        try:
            self.session.get(self.base_url, headers=self.headers, timeout=10)
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Session initialization failed: {e}")
            return False
    
    def load_nifty50_stocks(self, filename: str = 'nifty50_stocks.json') -> bool:
        """Load NIFTY 50 stocks from JSON file"""
        try:
            if not os.path.exists(filename):
                logger.error(f"File {filename} not found. Run scrape_nifty50.py first.")
                return False
            
            with open(filename, 'r') as f:
                self.stocks = json.load(f)
            
            logger.info(f"Loaded {len(self.stocks)} NIFTY 50 stocks")
            return True
        except Exception as e:
            logger.error(f"Error loading stocks: {e}")
            return False
    
    def fetch_live_price(self, symbol: str) -> Tuple[float, float, datetime]:
        """
        Fetch live price for a single stock
        Returns: (ltp, volume, timestamp)
        """
        try:
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                price_info = data.get('priceInfo', {})
                ltp = price_info.get('lastPrice', 0)
                volume = data.get('preOpenMarket', {}).get('totalTradedVolume', 0)
                
                return ltp, volume, datetime.now()
            else:
                return None, None, None
                
        except Exception as e:
            logger.debug(f"Error fetching price for {symbol}: {e}")
            return None, None, None
    
    def fetch_all_live_prices(self) -> Dict:
        """Fetch live prices for all NIFTY 50 stocks"""
        prices = {}
        
        try:
            url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
            response = self.session.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                timestamp = datetime.now()
                
                if 'data' in data:
                    for stock in data['data']:
                        symbol = stock.get('symbol')
                        if symbol and symbol != 'NIFTY 50':
                            prices[symbol] = {
                                'ltp': stock.get('lastPrice', 0),
                                'volume': stock.get('totalTradedVolume', 0),
                                'timestamp': timestamp
                            }
                
                logger.info(f"Fetched prices for {len(prices)} stocks")
            
        except Exception as e:
            logger.error(f"Error fetching live prices: {e}")
        
        return prices
    
    def calculate_moving_average(self, symbol: str) -> float:
        """Calculate moving average for a stock"""
        if len(self.price_history[symbol]) < self.ma_period:
            return None
        
        prices = [price for _, price in list(self.price_history[symbol])[-self.ma_period:]]
        return np.mean(prices)
    
    def detect_momentum_shift(self, symbol: str, current_ltp: float, timestamp: datetime):
        """
        Detect if there's a momentum shift (LTP crossing MA)
        """
        ma = self.calculate_moving_average(symbol)
        
        if ma is None:
            return
        
        # Determine current position relative to MA
        current_above_ma = current_ltp > ma
        
        # Check if we have previous status
        if symbol in self.prev_cross_status:
            prev_above_ma = self.prev_cross_status[symbol]['above_ma']
            
            # Detect cross
            if current_above_ma and not prev_above_ma:
                # Upward cross
                self.momentum_shifts[symbol].append({
                    'timestamp': timestamp,
                    'shift_type': 'Upward',
                    'price_at_cross': current_ltp,
                    'ma_at_cross': ma
                })
                logger.info(f"{symbol}: Upward momentum shift detected at {current_ltp}")
                
            elif not current_above_ma and prev_above_ma:
                # Downward cross
                self.momentum_shifts[symbol].append({
                    'timestamp': timestamp,
                    'shift_type': 'Downward',
                    'price_at_cross': current_ltp,
                    'ma_at_cross': ma
                })
                logger.info(f"{symbol}: Downward momentum shift detected at {current_ltp}")
        
        # Update previous status
        self.prev_cross_status[symbol] = {
            'above_ma': current_above_ma,
            'timestamp': timestamp
        }
    
    def calculate_percentage_change(self, symbol: str, current_ltp: float) -> List[Dict]:
        """
        Calculate percentage change from each momentum shift to current price
        """
        results = []
        
        for shift in self.momentum_shifts[symbol]:
            time_diff = (datetime.now() - shift['timestamp']).total_seconds() / 60
            
            # Only consider shifts within last 60 minutes
            if time_diff <= 60:
                pct_change = ((current_ltp - shift['price_at_cross']) / shift['price_at_cross']) * 100
                
                results.append({
                    'symbol': symbol,
                    'shift_time': shift['timestamp'],
                    'shift_type': shift['shift_type'],
                    'price_at_cross': shift['price_at_cross'],
                    'current_price': current_ltp,
                    'pct_change': pct_change,
                    'abs_pct_change': abs(pct_change),
                    'time_since_shift_mins': time_diff
                })
        
        return results
    
    def run_analysis(self, duration_minutes: int = 60, interval_seconds: int = 60):
        """
        Run continuous momentum analysis
        Args:
            duration_minutes: Total duration to run analysis
            interval_seconds: Interval between data fetches
        """
        if not self.stocks:
            logger.error("No stocks loaded. Run load_nifty50_stocks() first.")
            return
        
        if not self._init_session():
            logger.error("Failed to initialize session")
            return
        
        logger.info(f"Starting momentum analysis for {duration_minutes} minutes...")
        logger.info(f"Moving Average Period: {self.ma_period} data points")
        logger.info(f"Data fetch interval: {interval_seconds} seconds")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        iteration = 0
        
        while datetime.now() < end_time:
            iteration += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration} - {datetime.now().strftime('%H:%M:%S')}")
            logger.info(f"{'='*60}")
            
            # Fetch live prices
            prices = self.fetch_all_live_prices()
            
            # Update price history and detect momentum shifts
            for symbol, price_data in prices.items():
                ltp = price_data['ltp']
                timestamp = price_data['timestamp']
                
                # Add to price history
                self.price_history[symbol].append((timestamp, ltp))
                
                # Detect momentum shift
                self.detect_momentum_shift(symbol, ltp, timestamp)
            
            # Display current status
            self._display_current_status()
            
            # Wait for next interval
            time.sleep(interval_seconds)
        
        logger.info("\nAnalysis completed!")
        self.generate_final_report()
    
    def _display_current_status(self):
        """Display current momentum shifts"""
        total_shifts = sum(len(shifts) for shifts in self.momentum_shifts.values())
        logger.info(f"Total momentum shifts detected: {total_shifts}")
        
        if total_shifts > 0:
            recent_shifts = []
            for symbol, shifts in self.momentum_shifts.items():
                for shift in shifts[-3:]:  # Last 3 shifts per stock
                    recent_shifts.append({
                        'symbol': symbol,
                        'type': shift['shift_type'],
                        'time': shift['timestamp'].strftime('%H:%M:%S')
                    })
            
            if recent_shifts:
                logger.info("Recent momentum shifts:")
                for shift in recent_shifts[-5:]:
                    logger.info(f"  {shift['symbol']}: {shift['type']} at {shift['time']}")
    
    def generate_final_report(self):
        """Generate and display final momentum shift report"""
        all_momentum_changes = []
        
        # Calculate percentage changes for all stocks
        prices = self.fetch_all_live_prices()
        
        for symbol, price_data in prices.items():
            current_ltp = price_data['ltp']
            changes = self.calculate_percentage_change(symbol, current_ltp)
            all_momentum_changes.extend(changes)
        
        if not all_momentum_changes:
            logger.warning("No momentum shifts detected in the analysis period.")
            return
        
        # Sort by absolute percentage change
        sorted_changes = sorted(all_momentum_changes, key=lambda x: x['abs_pct_change'], reverse=True)
        
        # Separate upward and downward shifts
        upward_shifts = [s for s in sorted_changes if s['shift_type'] == 'Upward']
        downward_shifts = [s for s in sorted_changes if s['shift_type'] == 'Downward']
        
        # Display results
        print("\n" + "="*100)
        print("INTRADAY MOMENTUM ANALYSIS - TOP MOMENTUM SHIFTS (Last 1 Hour)")
        print("="*100)
        
        print("\n" + "-"*100)
        print("TOP 5 UPWARD MOMENTUM SHIFTS")
        print("-"*100)
        
        if upward_shifts:
            df_up = pd.DataFrame(upward_shifts[:5])
            df_up['shift_time'] = df_up['shift_time'].apply(lambda x: x.strftime('%H:%M:%S'))
            df_up['time_since_shift_mins'] = df_up['time_since_shift_mins'].apply(lambda x: f"{x:.1f}")
            df_up['pct_change'] = df_up['pct_change'].apply(lambda x: f"{x:.2f}%")
            df_up['price_at_cross'] = df_up['price_at_cross'].apply(lambda x: f"₹{x:.2f}")
            df_up['current_price'] = df_up['current_price'].apply(lambda x: f"₹{x:.2f}")
            
            print(df_up[['symbol', 'shift_time', 'shift_type', 'price_at_cross', 
                         'current_price', 'pct_change', 'time_since_shift_mins']].to_string(index=False))
        else:
            print("No upward momentum shifts detected.")
        
        print("\n" + "-"*100)
        print("TOP 5 DOWNWARD MOMENTUM SHIFTS")
        print("-"*100)
        
        if downward_shifts:
            df_down = pd.DataFrame(downward_shifts[:5])
            df_down['shift_time'] = df_down['shift_time'].apply(lambda x: x.strftime('%H:%M:%S'))
            df_down['time_since_shift_mins'] = df_down['time_since_shift_mins'].apply(lambda x: f"{x:.1f}")
            df_down['pct_change'] = df_down['pct_change'].apply(lambda x: f"{x:.2f}%")
            df_down['price_at_cross'] = df_down['price_at_cross'].apply(lambda x: f"₹{x:.2f}")
            df_down['current_price'] = df_down['current_price'].apply(lambda x: f"₹{x:.2f}")
            
            print(df_down[['symbol', 'shift_time', 'shift_type', 'price_at_cross',
                          'current_price', 'pct_change', 'time_since_shift_mins']].to_string(index=False))
        else:
            print("No downward momentum shifts detected.")
        
        print("\n" + "="*100)
        
        # Save to files
        self._save_results(upward_shifts[:5], downward_shifts[:5])
    
    def _save_results(self, upward: List[Dict], downward: List[Dict]):
        """Save results to JSON and CSV"""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'ma_period': self.ma_period,
                'top_upward_shifts': upward,
                'top_downward_shifts': downward
            }
            
            # Save to JSON
            with open('momentum_analysis_results.json', 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Save to CSV
            all_shifts = upward + downward
            if all_shifts:
                df = pd.DataFrame(all_shifts)
                df.to_csv('momentum_analysis_results.csv', index=False)
            
            logger.info("Results saved to momentum_analysis_results.json and .csv")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")


def main():
    # Configuration
    MA_PERIOD = 10  # Moving average period (number of data points)
    ANALYSIS_DURATION = 60  # minutes
    FETCH_INTERVAL = 60  # seconds
    
    # Initialize analyzer
    analyzer = IntradayMomentumAnalyzer(ma_period=MA_PERIOD)
    
    # Load NIFTY 50 stocks
    if not analyzer.load_nifty50_stocks():
        print("Please run scrape_nifty50.py first to fetch NIFTY 50 stocks.")
        return
    
    # Run analysis
    print("\n" + "="*80)
    print("INTRADAY MOMENTUM ANALYZER")
    print("="*80)
    print(f"Analysis Duration: {ANALYSIS_DURATION} minutes")
    print(f"Moving Average Period: {MA_PERIOD} data points")
    print(f"Data Fetch Interval: {FETCH_INTERVAL} seconds")
    print("="*80 + "\n")
    
    analyzer.run_analysis(duration_minutes=ANALYSIS_DURATION, interval_seconds=FETCH_INTERVAL)


if __name__ == "__main__":
    main()