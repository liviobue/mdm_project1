import argparse
import yfinance as yf
from pymongo import MongoClient
from difflib import SequenceMatcher

def check_mongo_connection(mongo_uri):
    try:
        client = MongoClient(mongo_uri)
        db = client["mongodb-buergli1"]
        client.server_info()  # Check if connected
        client.close()
        print('Connected to mongo')
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def find_similar_stock(collection, stock_name):
    similar_stocks = collection.find()
    for stock in similar_stocks:
        stock_name_in_db = stock["stock_name"]
        if isinstance(stock_name_in_db, list) and stock_name_in_db:  # Check if it's a non-empty list
            stock_name_in_db = stock_name_in_db[0]  # Take the first item in the list
        stock_name_in_db = str(stock_name_in_db)
        if stock_name in stock_name_in_db:
            return stock["stock_name"]
        if similar(stock_name_in_db.lower(), stock_name.lower()) > 0.8:  # Adjust similarity threshold as needed
            return stock["stock_name"]
    return None

def import_historical_data(collection_name, stock_name, mongo_uri):
    # Check MongoDB connection
    if not check_mongo_connection(mongo_uri):
        return

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client["mongodb-buergli1"]
    collection = db[collection_name]
    symbol = stock_name
    # Check if similar stock exists
    existing_stock_name = find_similar_stock(collection, stock_name)
    if existing_stock_name:
        stock_name = existing_stock_name
        if isinstance(stock_name, list) and stock_name:  # Check if it's a non-empty list
            stock_name = stock_name[0]
        print(f"Similar stock name found in the database: {existing_stock_name}")

    # Fetch historical data from Yahoo Finance API
    stock_data = yf.download(symbol, start="2022-01-01", end="2024-01-01")

    # Extract relevant information
    intraday_price = list(stock_data['Close'])
    price_change = list(stock_data['Close'].pct_change())
    dates = list(stock_data.index.strftime('%Y-%m-%d'))
    volume = list(stock_data['Volume'])

    # Check if stock_name exists
    existing_document = collection.find_one({"stock_name": stock_name})
    if existing_document:
        # If stock_name exists, update the document
        collection.update_one({"stock_name": stock_name}, {"$set": {
            "intraday_price": intraday_price,
            "price_change": price_change,
            "volume": volume,
            "current_timestamp": dates
        }})
        print(f"Intraday price, price change, dates, and volume for {stock_name} updated successfully.")
    else:
        # If stock_name does not exist, insert a new document
        document = {
            "stock_name": stock_name,
            "intraday_price": intraday_price,
            "price_change": price_change,
            "volume": volume,
            "current_timestamp": dates
        }
        collection.insert_one(document)
        print(f"Intraday price, price change, dates, and volume for {stock_name} imported successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', required=True, help="Name of the MongoDB collection where the data should be stored")
    parser.add_argument('-s', '--stock', required=True, help="Stock name to fetch historical data for")
    parser.add_argument('-u', '--uri', required=True, help="MongoDB URI with username/password")
    args = parser.parse_args()

    import_historical_data(args.collection, args.stock, args.uri)
