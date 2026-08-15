import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'

class PortfolioSimulator:
    def __init__(self):
        self.symbols = self._get_sp500_symbols()
        
    def _get_sp500_symbols(self):
        """Return S&P 500 stock symbols"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK-B', 'LLY', 
            'VTI', 'UNH', 'XOM', 'JPM', 'JNJ', 'V', 'PG', 'MA', 'HD', 'CVX',
            'MRK', 'ABBV', 'PEP', 'KO', 'WMT', 'BAC', 'COST', 'MCD', 'NFLX',
            'ADBE', 'CRM', 'TM', 'TMO', 'ABT', 'NVS', 'DHR', 'PFE', 'TXN',
            'INTC', 'CMCSA', 'AMGN', 'NEE', 'HON', 'RTX', 'UNP', 'LMT', 
            'BA', 'COP', 'GS', 'VZ', 'IBM', 'UPS', 'CAT', 'GE', 'T', 'WFC',
            'QCOM', 'SPGI', 'PM', 'MDT', 'NKE', 'UPS', 'TGT', 'NOW', 'ADP'
        ]
    
    def _fetch_stock_data(self, symbol):
        """Fetch stock data from Alpha Vantage API"""
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': API_KEY,
                'outputsize': 'compact'
            }
            
            response = requests.get(BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'Time Series (Daily)' not in data:
                    return None
                
                time_series = data['Time Series (Daily)']
                dates = sorted(time_series.keys(), reverse=True)[:30]
                
                if not dates:
                    return None
                
                current_price = float(time_series[dates[0]]['4. close'])
                prices = [float(time_series[date]['4. close']) for date in dates[:20]]
                high = max(prices) if prices else current_price
                low = min(prices) if prices else current_price
                volume = float(time_series[dates[0]]['5. volume'])
                
                return {
                    'symbol': symbol,
                    'price': current_price,
                    'prices': prices,
                    'high': high,
                    'low': low,
                    'volume': volume,
                    'volatility': (high - low) / current_price * 100 if current_price > 0 else 0
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def _get_momentum_score(self, stock_data):
        """Calculate momentum score (20-day return)"""
        if not stock_data or len(stock_data['prices']) < 2:
            return 0
        prices = stock_data['prices']
        return (prices[0] - prices[-1]) / prices[-1] * 100
    
    def _get_value_score(self, stock_data):
        """Calculate value score (inverse of price)"""
        if not stock_data or stock_data['price'] <= 0:
            return 0
        return 1 / stock_data['price'] * 1000
    
    def _get_growth_score(self, stock_data):
        """Calculate growth score (price-to-high ratio)"""
        if not stock_data or stock_data['high'] <= 0:
            return 0
        return (stock_data['price'] / stock_data['high']) * 100
    
    def _get_dividend_score(self, stock_data):
        """Calculate dividend proxy score (based on volume/price ratio)"""
        if not stock_data or stock_data['price'] <= 0:
            return 0
        return (stock_data['volume'] / stock_data['price']) / 10000
    
    def _get_low_volatility_score(self, stock_data):
        """Calculate low volatility score (inverse of volatility)"""
        if not stock_data or stock_data['volatility'] <= 0:
            return 0
        return 100 / stock_data['volatility']
    
    def _get_esg_score(self, stock_data):
        """Calculate ESG proxy (based on volume stability)"""
        if not stock_data:
            return 0
        # Using volume as ESG proxy (higher volume = better liquidity/transparency)
        return min(stock_data['volume'] / 100000000, 10)
    
    def generate_portfolio(self, strategy='equal_weight', portfolio_size='standard'):
        """Generate portfolio based on strategy"""
        print(f"📊 Fetching data for {len(self.symbols)} S&P 500 stocks...")
        print("⏳ This may take 2-3 minutes...")
        
        stock_data_list = []
        total_stocks = len(self.symbols)
        
        for i, symbol in enumerate(self.symbols):
            if i % 10 == 0:
                print(f"  Progress: {i}/{total_stocks} stocks processed")
            
            stock_data = self._fetch_stock_data(symbol)
            if stock_data:
                stock_data_list.append(stock_data)
            
            if (i + 1) % 5 == 0:
                time.sleep(0.5)
        
        if not stock_data_list:
            print("❌ No data fetched. Check your API key.")
            return None
        
        df = pd.DataFrame(stock_data_list)
        
        # Map strategies to scoring functions
        strategy_map = {
            'equal_weight': self._get_value_score,  # Dummy, handled separately
            'momentum': self._get_momentum_score,
            'value': self._get_value_score,
            'growth': self._get_growth_score,
            'dividend': self._get_dividend_score,
            'low_volatility': self._get_low_volatility_score,
            'esg': self._get_esg_score
        }
        
        if strategy == 'equal_weight':
            df['allocation'] = 1.0 / len(df)
        elif strategy in strategy_map:
            df['score'] = df.apply(strategy_map[strategy], axis=1)
            total_score = df['score'].sum()
            if total_score > 0:
                df['allocation'] = df['score'] / total_score
            else:
                df['allocation'] = 1.0 / len(df)
        else:
            df['allocation'] = 1.0 / len(df)
        
        # Portfolio size variations
        if portfolio_size == 'small':
            top_n = 15
        elif portfolio_size == 'large':
            top_n = 50
        else:  # standard
            top_n = 30
        
        df = df.sort_values('allocation', ascending=False).head(top_n)
        
        # Normalize allocations for selected stocks
        df['allocation'] = df['allocation'] / df['allocation'].sum()
        df['position_value'] = df['allocation'] * 1000000
        
        df['shares'] = df['position_value'] / df['price']
        df['shares'] = df['shares'].apply(lambda x: int(x))
        df['actual_position'] = df['shares'] * df['price']
        
        return df

    def export_to_excel(self, df, strategy_name, portfolio_size):
        """Export portfolio to Excel with formatting"""
        filename = f"portfolio_{strategy_name}_{portfolio_size}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            columns_to_export = ['symbol', 'price', 'shares', 'allocation', 'position_value', 'actual_position']
            if 'volatility' in df.columns:
                columns_to_export.append('volatility')
            
            export_df = df[columns_to_export].copy()
            export_df.columns = ['Symbol', 'Price', 'Shares', 'Allocation %', 'Position Value', 'Actual Value'] + (['Volatility %'] if 'volatility' in df.columns else [])
            export_df['Allocation %'] = export_df['Allocation %'] * 100
            
            export_df.to_excel(writer, sheet_name='Portfolio', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Portfolio']
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#1e3a5f',
                'font_color': 'white',
                'border': 1
            })
            
            money_format = workbook.add_format({'num_format': '$#,##0.00'})
            percent_format = workbook.add_format({'num_format': '0.00%'})
            
            for col_num, value in enumerate(export_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 18)
            worksheet.set_column('F:F', 18)
            
            row = len(export_df) + 2
            worksheet.write(row, 0, 'Total Value:', header_format)
            total_value = export_df['Actual Value'].sum()
            worksheet.write(row, 1, f'${total_value:,.2f}', money_format)
            
            row += 1
            worksheet.write(row, 0, 'Strategy:', header_format)
            worksheet.write(row, 1, strategy_name.title())
            
            row += 1
            worksheet.write(row, 0, 'Portfolio Size:', header_format)
            worksheet.write(row, 1, portfolio_size.title())
            
            row += 1
            worksheet.write(row, 0, 'Generated:', header_format)
            worksheet.write(row, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return filename

    def run_portfolio(self, strategy='equal_weight', portfolio_size='standard'):
        """Main function to generate portfolio"""
        print(f"\n🚀 Generating {strategy.replace('_', ' ')} portfolio ({portfolio_size})...")
        
        df = self.generate_portfolio(strategy, portfolio_size)
        
        if df is None:
            return None, None
        
        total_value = df['actual_position'].sum()
        filename = self.export_to_excel(df, strategy, portfolio_size)
        
        print(f"\n✅ Portfolio generated successfully!")
        print(f"📊 Total Value: ${total_value:,.2f}")
        print(f"📁 Excel file: {filename}")
        print(f"📈 Stocks selected: {len(df)}")
        
        portfolio_data = df[['symbol', 'price', 'shares', 'allocation', 'position_value', 'actual_position']].to_dict('records')
        
        return portfolio_data, filename