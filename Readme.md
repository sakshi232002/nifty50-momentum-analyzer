# Nifty50 Momentum Analyzer

## Overview
A Python-based tool for analyzing momentum indicators and price trends of Nifty50 stocks. This project helps investors and traders make data-driven decisions by analyzing technical indicators and historical price data.

## Features
- Historical price data retrieval for Nifty50 stocks
- Momentum indicator calculations (RSI, MACD, Moving Averages)
- Price trend analysis and visualization
- Performance ranking of Nifty50 stocks
- Export capabilities for analysis results

## Prerequisites
- Python 3.8 or higher
- Required Python packages:
  - pandas
  - numpy
  - yfinance
  - matplotlib
  - ta (Technical Analysis Library)

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/nifty50-momentum-analyzer.git

# Navigate to project directory
cd nifty50-momentum-analyzer

# Install required packages
pip install -r requirements.txt
```

## Usage
```python
# Example code to run the analyzer
from momentum_analyzer import MomentumAnalyzer

# Initialize analyzer
analyzer = MomentumAnalyzer()

# Get analysis for all Nifty50 stocks
results = analyzer.analyze_all_stocks()
```

## Configuration
- Customize analysis parameters in `config.py`
- Adjust technical indicator settings
- Modify time periods for analysis

## Output
- CSV reports with analysis results
- Technical charts and visualizations
- Performance rankings
- Momentum signals and alerts

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
[Your Name]

## Acknowledgments
- NSE India for stock data
- Technical analysis community
- Open source contributors