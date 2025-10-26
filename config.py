"""
Configuration file for NIFTY 50 Momentum Analyzer
Modify these settings to customize the analysis
"""

# Analysis Parameters
MOVING_AVERAGE_PERIOD = 10  # Number of data points for MA calculation
ANALYSIS_DURATION_MINUTES = 60  # Total duration to run analysis
DATA_FETCH_INTERVAL_SECONDS = 60  # Interval between price fetches

# Data Sources
NSE_BASE_URL = "https://www.nseindia.com"
NSE_NIFTY50_API = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
NSE_QUOTE_API = "https://www.nseindia.com/api/quote-equity?symbol={symbol}"

# HTTP Headers
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.nseindia.com/market-data/live-equity-market'
}

# File Paths
NIFTY50_JSON_FILE = 'nifty50_stocks.json'
NIFTY50_CSV_FILE = 'nifty50_stocks.csv'
RESULTS_JSON_FILE = 'momentum_analysis_results.json'
RESULTS_CSV_FILE = 'momentum_analysis_results.csv'

# Analysis Settings
TOP_N_STOCKS = 5  # Number of top stocks to display in results
MOMENTUM_WINDOW_MINUTES = 60  # Time window to consider for momentum shifts

# Timeouts and Retries
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

# Logging
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Display Settings
DISPLAY_RECENT_SHIFTS = True
RECENT_SHIFTS_COUNT = 5

# Demo/Testing Mode
DEMO_MODE = False  # Set to True for testing without live data
DEMO_DURATION_MINUTES = 5  # Shorter duration for demo mode