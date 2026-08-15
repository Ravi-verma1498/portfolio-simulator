# 📈 Portfolio Simulator Pro

> Intelligent S&P 500 portfolio generator with 7 strategies for $1M virtual capital

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🎯 **7 Investment Strategies** - Equal Weight, Momentum, Value, Growth, Dividend, Low Volatility, ESG
- 📦 **3 Portfolio Sizes** - Small (15 stocks), Standard (30 stocks), Large (50 stocks)
- 📊 **Interactive Dashboard** - Real-time portfolio generation with pie charts
- 🌓 **Dark Mode** - Toggle between light and dark themes
- 📥 **Multiple Exports** - Excel (.xlsx), JSON, and Print-ready reports
- 🚀 **Live Data** - Real-time S&P 500 data via Alpha Vantage API
- 💰 **$1M Virtual Portfolio** - Execute trading strategies with simulated capital

## 🚀 Quick Start

cd backend 
python -m venv venv

source venv/scripts/activate (in my case i was using bash)
or
venv\scripts\activate

pip install -r requirement.txt

python app.py

'''**open new terminal** '''
cd frontend

python -m http.server 3000/8000


'''**now add 3000 or 8000 at server where backend is running**'''
   
   here backend is running on "http://127.0.0.1:5000"
   replace 5000 with 3000/8000



### Prerequisites
- Python 3.8+
- Alpha Vantage API Key ([Get free key](https://www.alphavantage.co/support/#api-key))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/portfolio-simulator.git
cd portfolio-simulator


