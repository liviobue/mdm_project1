import argparse
import json
from pymongo import MongoClient
from pathlib import Path

class JsonLinesImporter:
    def __init__(self, input_file, collection, mongo_uri):
        self.input_file = input_file
        self.collection_name = collection
        self.mongo_uri = mongo_uri
    
    def to_document(self, item):
        # Convert each item in the JSON file to a MongoDB document
        document = {
            "stock_name": item.get("stock_name", []),
            "intraday_price": item.get("intraday_price", []),
            "price_change": item.get("price_change", [])
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
                document = self.to_document(item)
                collection.insert_one(document)
        print("Data imported successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uri', required=True, help="MongoDB URI with username/password")
    parser.add_argument('-i', '--input', default='stock.json', help="Input file in JSON format")
    parser.add_argument('-c', '--collection', required=True, help="Name of the MongoDB collection where the stock should be stored")
    args = parser.parse_args()
    
    importer = JsonLinesImporter(args.input, collection=args.collection, mongo_uri=args.uri)
    importer.save_to_mongodb()
