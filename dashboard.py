import streamlit as st
import pandas as pd
import sqlite3
import pickle
import time
import os

st.set_page_config(page_title="Real-Time Fraud Monitoring", layout="wide")
st.title("🚨 Real-Time Financial Fraud Detection Dashboard")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'fraud_model.pkl')
features_path = os.path.join(BASE_DIR, 'model_features.pkl')
db_path = os.path.join(BASE_DIR, 'bank.db')

with open(model_path, 'rb') as f:
    model = pickle.load(f)
with open(features_path, 'rb') as f:
    model_features = pickle.load(f)

metric_box = st.empty()
alert_box = st.empty()
table_box = st.empty()

def process_and_predict():
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM Transactions ORDER BY timestamp DESC LIMIT 15", conn)
    
    if not df.empty:
        processed_df = pd.get_dummies(df, columns=['merchant_category'])
        for col in model_features:
            if col not in processed_df.columns:
                processed_df[col] = 0
                
        X_live = processed_df[model_features]
        df['Predicted_Fraud'] = model.predict(X_live)
        
        cursor = conn.cursor()
        for idx, row in df.iterrows():
            if row['Predicted_Fraud'] == 1 and row['is_fraud'] == 0:
                cursor.execute("UPDATE Transactions SET is_fraud = 1 WHERE transaction_id = ?", (row['transaction_id'],))
        conn.commit()
        
        total_processed = pd.read_sql_query("SELECT COUNT(*) as count FROM Transactions", conn).iloc[0]['count']
        total_frauds = pd.read_sql_query("SELECT COUNT(*) as count FROM Transactions WHERE is_fraud = 1", conn).iloc[0]['count']
        
        with metric_box.container():
            col1, col2 = st.columns(2)
            col1.metric("Total Ingested Transactions", total_processed)
            col2.metric("Flagged Fraud Attacks", total_frauds, delta=int(total_frauds), delta_color="inverse")
            
        latest_tx = df.iloc[0]
        if latest_tx['Predicted_Fraud'] == 1:
            with alert_box.container():
                st.error(f"⚠️ HIGH RISK FRAUD ALERT: Transaction {latest_tx['transaction_id'][:8]}... "
                         f"spending ${latest_tx['amount']} at a distance of {latest_tx['distance_from_home']}km "
                         f"was blocked by the ML pipeline!")
        else:
            alert_box.empty()
            
        with table_box.container():
            st.subheader("Live Transaction Streaming Ledger Logs")
            styled_df = df[['transaction_id', 'amount', 'timestamp', 'distance_from_home', 'Predicted_Fraud']].style.apply(
                lambda x: ['background-color: #ffcccc' if v == 1 else '' for v in x], subset=['Predicted_Fraud']
            )
            st.dataframe(styled_df, use_container_width=True)
    conn.close()

while True:
    process_and_predict()
    time.sleep(2)