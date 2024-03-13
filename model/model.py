import argparse
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

parser = argparse.ArgumentParser(description='Create Model')
parser.add_argument('-u', '--uri', required=True, help="MongoDB URI with username/password")
args = parser.parse_args()

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

# Convert lists to scalar values
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

# Evaluate model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
