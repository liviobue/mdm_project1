import argparse
import json
from pymongo import MongoClient
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher  # Import SequenceMatcher for string similarity comparison

class JsonLinesImporter:
    def __init__(self, input_file, collection, mongo_uri):
        self.input_file = input_file
        self.collection_name = collection
        self.mongo_uri = mongo_uri
    
    def to_document(self, item):
        # Convert each item in the JSON file to a MongoDB document
        document = {
            "stock_name": item.get("stock_name", ""),
            "intraday_price": item.get("intraday_price", []),
            "price_change": item.get("price_change", []),
            "volume": item.get("volume", []),
            "current_timestamp": item.get("current_timestamp", []),
        }
        return document
    
    def save_to_mongodb(self):
        # Connect to MongoDB
        client = MongoClient(self.mongo_uri)
        db = client["mongodb-buergli1"]
        collection = db[self.collection_name]
        
        # Read JSON file and insert each item into MongoDB
        with open(self.input_file, 'r') as f:
            data = json.load(f)
            for item in data:
                stock_name = item.get("stock_name", "")
                if isinstance(stock_name, list) and stock_name:
                    stock_name = stock_name[0]
                similar_stock_name = self.find_similar_stock(collection, stock_name)
                if similar_stock_name:
                    # If a similar stock_name exists, update the document and add current timestamp
                    collection.update_one({"stock_name": similar_stock_name}, {"$push": {
                        "intraday_price": item.get("intraday_price", []),
                        "price_change": item.get("price_change", []),
                        "volume": item.get("volume", []),
                        "current_timestamp": item.get("current_timestamp", []),
                    }})
                else:
                    # If stock_name does not exist, insert a new document with current timestamp
                    document = self.to_document(item)
                    collection.insert_one(document)
        print("Data imported successfully.")
    
    def similar(self, a, b):
        # Function to calculate similarity between two strings
        return SequenceMatcher(None, a, b).ratio()
    
    def find_similar_stock(self, collection, stock_name):
        # Function to find similar stock names in the collection
        similar_stocks = collection.find({})
        for stock in similar_stocks:
            stock_name_in_db = stock["stock_name"]
            if isinstance(stock_name_in_db, list) and stock_name_in_db:  # Check if it's a non-empty list
                stock_name_in_db = stock_name_in_db[0]  # Take the first item in the list
            if self.similar(stock_name_in_db.lower(), stock_name.lower()) > 0.8:  # Adjust similarity threshold as needed
                return stock["stock_name"]
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uri', required=True, help="MongoDB URI with username/password")
    parser.add_argument('-i', '--input', default='stock.json', help="Input file in JSON format")
    parser.add_argument('-c', '--collection', required=True, help="Name of the MongoDB collection where the stock should be stored")
    args = parser.parse_args()
    
    importer = JsonLinesImporter(args.input, collection=args.collection, mongo_uri=args.uri)
    importer.save_to_mongodb()
