import argparse
import pandas as pd
import yfinance as yf
from pymongo import MongoClient

def import_historical_data(collection_name, stock_name, mongo_uri):
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client["mongodb-buergli1"]
    collection = db[collection_name]

    # Fetch historical data from Yahoo Finance API
    stock_data = yf.download(stock_name, start="2020-01-01", end="2024-01-01")

    # Convert DataFrame to list of dictionaries (documents)
    historical_data = stock_data.reset_index().to_dict(orient='records')

    # Check if stock_name exists
    existing_document = collection.find_one({"stock_name": stock_name})
    if existing_document:
        # If stock_name exists, update the document
        collection.update_one({"stock_name": stock_name}, {"$push": {
            "historical_data": {"$each": historical_data}
        }})
        print(f"Historical data for {stock_name} added to existing arrays successfully.")
    else:
        # If stock_name does not exist, insert a new document
        document = {
            "stock_name": stock_name,
            "intraday_price": [],
            "price_change": [],
            "historical_data": historical_data
        }
        collection.insert_one(document)
        print(f"Historical data for {stock_name} imported successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', required=True, help="Name of the MongoDB collection where the data should be stored")
    parser.add_argument('-s', '--stock', required=True, help="Stock name to fetch historical data for")
    parser.add_argument('-u', '--uri', required=True, help="MongoDB URI with username/password")
    args = parser.parse_args()

    import_historical_data(args.collection, args.stock, args.uri)
