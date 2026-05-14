import os
import joblib
import numpy as np
from xgboost import XGBClassifier
from sklearn.ensemble import IsolationForest

def export():
    print("Starting export...")
    os.makedirs('models', exist_ok=True)
    
    # 1. Behavior Model
    X = np.random.rand(10, 5)
    y = np.array([1,0,1,0,1,0,1,0,1,0])
    model_a = XGBClassifier()
    model_a.fit(X, y)
    model_a.save_model('models/behavior_model.json')
    print("Exported behavior_model.json")
    
    # 2. Anomaly Model
    model_b = IsolationForest(contamination=0.1)
    model_b.fit(X)
    joblib.dump(model_b, 'models/anomaly_model.joblib')
    print("Exported anomaly_model.joblib")
    
    print("DONE")

if __name__ == "__main__":
    export()
