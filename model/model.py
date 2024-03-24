import argparse
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import pickle
import re

def check_mongo_connection(uri):
    try:
        client = MongoClient(uri)
        client.server_info()  # Check if connection is successful
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False

parser = argparse.ArgumentParser(description='Create Model')
parser.add_argument('-u', '--uri', required=True, help="MongoDB URI with username/password")
parser.add_argument('-s', '--stock', required=True, help="Stock ticker to model")
parser.add_argument('-m', '--model_file', required=True, help="File to save the trained model")
args = parser.parse_args()

# Check MongoDB connection
if not check_mongo_connection(args.uri):
    exit(1)

# MongoDB connection
mongo_uri = args.uri
mongo_db = "mongodb-buergli1"
mongo_collection = "stock"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

pattern = re.compile(args.stock)

# Fetch data from MongoDB for the specified stock
data = list(collection.find({ "stock_name": { "$elemMatch": { "$elemMatch": { "$regex": pattern } } } }, 
                             {"_id": 0, "intraday_price": 1, "price_change": 1, "volume": 1, "current_timestamp": 1}))

# Normalize the data and create DataFrame
df = pd.json_normalize(data)

# Explode the lists to create new rows
df = df.apply(pd.Series.explode)

# Reset the index
df = df.reset_index(drop=True)

# Replace NaN values with 0
df = df.fillna(0)

# Print the DataFrame
print(df)

# If the DataFrame is empty, no data was found for the specified stock ticker
if df.empty:
    print(f"No data found for stock ticker '{args.stock}'")
    exit(1)
else:
    print("Data retrieved successfully.")

# Prepare features and target variable
X = df[['intraday_price', 'price_change', 'volume']]
y = df['intraday_price'].shift(-1)

# Remove last row as there's no target for it
X = X[:-1]
y = y[:-1]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the RandomForestRegressor
rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
rf_regressor.fit(X_train, y_train)

# Make predictions
y_pred = rf_regressor.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Save the trained model
with open(args.model_file, 'wb') as f:
    pickle.dump(rf_regressor, f)
