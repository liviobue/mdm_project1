import argparse
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import pickle

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

# Fetch data from MongoDB
data = list(collection.find({}, {"_id": 0, "stock_name": 1, "intraday_price": 1, "price_change": 1}))

# Convert data to DataFrame
df = pd.DataFrame(data)

# Filter out documents with empty 'intraday_price' arrays
df = df[df['intraday_price'].apply(lambda x: bool(x))]  

# Extracting values from arrays
df['stock_name'] = df['stock_name'].apply(lambda x: x[0])
df['intraday_price'] = df['intraday_price'].apply(lambda x: float(x[0]))
df['price_change'] = df['price_change'].apply(lambda x: float(x[0].strip('()').replace('%', '')))

# Define target variable
df['price_change_label'] = pd.cut(df['price_change'], bins=[-float('inf'), 0, float('inf')], labels=['Negative', 'Positive'])

# Features and target variable
X = df[['intraday_price']]
y = df['price_change_label']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create RandomForestClassifier model
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train model
model.fit(X_train, y_train)

# Save the trained model to disk
with open(args.model_file, 'wb') as model_file:
    pickle.dump(model, model_file)

# Evaluate model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
