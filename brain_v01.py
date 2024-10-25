# -*- coding: utf-8 -*-
"""brAIn_v01.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19oTiEgdsZFeK80lxUiFP2Gspp2HZDqOX
"""

import requests
import pandas as pd
from transformers import pipeline
import gc  # For garbage collection
import torch
from datetime import datetime

# Your existing pipelines
finbert_pipe = pipeline("text-classification", model="yiyanghkust/finbert-tone")
text_gen_pipe = pipeline("text-generation", model="microsoft/phi-2")
news_sentiment_pipe = pipeline("text-classification", model="mrm8488/deberta-v3-ft-financial-news-sentiment-analysis")

# Alpha Vantage API setup
API_KEY = '40HYVDQDMF3PJD01'  # Get free key from: https://www.alphavantage.co/support/#api-key

def get_stock_data(symbol):
    """
    Get real-time stock data including high and low
    """
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': '40HYVDQDMF3PJD01'
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if 'Global Quote' in data:
            quote = data['Global Quote']
            return {
                'symbol': quote.get('01. symbol', ''),
                'price': float(quote.get('05. price', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'change_percent': quote.get('10. change percent', ''),
                'volume': int(quote.get('06. volume', 0))
            }
        return None
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

def get_intraday_data(symbol):
    """
    Get intraday price data for technical analysis
    """
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '5min',
        'apikey': API_KEY
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if 'Time Series (5min)' in data:
            time_series = data['Time Series (5min)']
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.astype(float)
            return df
        return None
    except Exception as e:
        print(f"Error fetching intraday data: {e}")
        return None

def analyze_stock(symbol):
    """
    Comprehensive stock analysis combining real-time data and ML predictions
    """
    # Get real-time stock data
    stock_data = get_stock_data(symbol)
    if not stock_data:
        return "Error fetching stock data"

    # Get intraday data for technical analysis
    intraday_data = get_intraday_data(symbol)

    # Generate market context for sentiment analysis
    market_context = f"Stock {symbol} is trading at ${stock_data['price']}, " \
                    f"with today's high of ${stock_data['high']} and low of ${stock_data['low']}. " \
                    f"Volume is {stock_data['volume']} with {stock_data['change_percent']} change."

    # Analyze sentiment
    sentiment = finbert_pipe(market_context)

    # Generate prediction text
    prediction_prompt = f"Based on {symbol}'s current price of ${stock_data['price']}, " \
                       f"trading between ${stock_data['low']} and ${stock_data['high']}, predict the trend:"
    prediction = text_gen_pipe(prediction_prompt, max_length=100, num_return_sequences=1)

    return {
        'real_time_data': stock_data,
        'technical_data': intraday_data.tail(1).to_dict('records')[0] if intraday_data is not None else None,
        'sentiment': sentiment[0],
        'prediction': prediction[0]['generated_text']
    }

# Example usage
if __name__ == "__main__":
    symbol = 'AAPL'  # Example with Apple stock
    analysis = analyze_stock(symbol)
    print(f"\nAnalysis for {symbol}:")
    print(f"Current Price: ${analysis['real_time_data']['price']}")
    print(f"Today's High: ${analysis['real_time_data']['high']}")
    print(f"Today's Low: ${analysis['real_time_data']['low']}")
    print(f"Sentiment: {analysis['sentiment']}")
    print(f"AI Prediction: {analysis['prediction']}")

