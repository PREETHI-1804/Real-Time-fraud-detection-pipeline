import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# Find directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, 'historical_transactions.csv')

print("Generating 10,000 historical banking profiles...")
np.random.seed(42)
n_records = 10000

# Synthesize baseline fields
amounts = np.random.exponential(scale=45, size=n_records) + 2.50
distances = np.random.exponential(scale=12, size=n_records) + 0.5
categories = ['groceries', 'entertainment', 'gas_station', 'online_retail', 'travel']
merchant_cats = [random.choice(categories) for _ in range(n_records)]

df = pd.DataFrame({
    'transaction_id': [f"tx_{i:06d}" for i in range(n_records)],
    'amount': np.round(amounts, 2),
    'distance_from_home': np.round(distances, 2),
    'merchant_category': merchant_cats,
    'is_fraud': 0
})

# Inject 1.5% extreme anomalies (Fraud Signals)
fraud_indices = np.random.choice(n_records, size=150, replace=False)
df.loc[fraud_indices, 'amount'] = np.round(np.random.uniform(500, 2500, size=150), 2)
df.loc[fraud_indices, 'distance_from_home'] = np.round(np.random.uniform(300, 1500, size=150), 2)
df.loc[fraud_indices, 'is_fraud'] = 1

df.to_csv(csv_path, index=False)
print(f" SUCCESS: Historical file generated at: {csv_path}")