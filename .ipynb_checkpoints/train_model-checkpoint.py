import pandas as pd
import pickle
import os
from xgboost import XGBClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, 'historical_transactions.csv')
model_path = os.path.join(BASE_DIR, 'fraud_model.pkl')
features_path = os.path.join(BASE_DIR, 'model_features.pkl')

# 1. Prepare Data
df = pd.read_csv(csv_path)
X = df[['amount', 'distance_from_home', 'merchant_category']]
y = df['is_fraud']
X = pd.get_dummies(X, columns=['merchant_category'])
model_features = list(X.columns)

# 2. Handle class imbalance ratio
scale_weight = (len(y) - sum(y)) / sum(y)

# 3. Train Model
print("Training the XGBoost Neural Fraud Network...")
model = XGBClassifier(scale_pos_weight=scale_weight, eval_metric='logloss', random_state=42)
model.fit(X, y)

# 4. Save models
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
with open(features_path, 'wb') as f:
    pickle.dump(model_features, f)

print(f" SUCCESS: Saved model configurations inside:\n -> {model_path}\n -> {features_path}")