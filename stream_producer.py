import sqlite3
import random
import time
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'bank.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id TEXT PRIMARY KEY,
        amount REAL,
        distance_from_home REAL,
        merchant_category TEXT,
        timestamp TEXT,
        is_fraud INTEGER DEFAULT 0
    )
''')
conn.commit()
conn.close()

print("Streaming active live swipes into bank.db (Press Ctrl+C to stop)...")
categories = ['groceries', 'entertainment', 'gas_station', 'online_retail', 'travel']

while True:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tx_id = f"tx_live_{int(time.time())}"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cat = random.choice(categories)
    
    # 90% normal logs, 10% malicious high-risk events
    if random.random() > 0.10:
        # random.expovariate expects (1 / mean)
        amount = round(random.expovariate(1 / 40) + 5, 2)
        distance = round(random.expovariate(1 / 10) + 1, 2)
    else:
        amount = round(random.uniform(600, 2000), 2)
        distance = round(random.uniform(400, 1200), 2)
        
    cursor.execute(
        "INSERT INTO Transactions VALUES (?, ?, ?, ?, ?, 0)",
        (tx_id, amount, distance, cat, timestamp)
    )
    conn.commit()
    conn.close()
    
    print(f" -> Logged Card Swipe: {tx_id} | ${amount} | {distance}km")
    time.sleep(2)