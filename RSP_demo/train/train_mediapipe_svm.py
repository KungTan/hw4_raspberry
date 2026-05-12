import pandas as pd
import numpy as np
import joblib
import os
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def preprocess_landmarks(df):
    """將特徵轉為相對座標，以手腕 (lm_0, lm_1) 為原點"""
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    
    processed_X = []
    for row in X:
        # 手腕座標為 (row[0], row[1])
        wrist_x, wrist_y = row[0], row[1]
        relative_row = []
        for i in range(0, len(row), 2):
            relative_row.append(row[i] - wrist_x)
            relative_row.append(row[i+1] - wrist_y)
        processed_X.append(relative_row)
        
    return np.array(processed_X), y

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'train', 'landmarks.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ 錯誤：找不到 {csv_path}，請先執行 extract_landmarks.py")
        return
        
    print("⏳ 讀取資料中...")
    df = pd.read_csv(csv_path)
    X, y = preprocess_landmarks(df)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"📊 訓練樣本: {len(X_train)}, 測試樣本: {len(X_test)}")
    
    print("\n=== 開始訓練 SVM 模型 ===")
    clf = SVC(kernel='rbf', C=1.0, probability=True)
    clf.fit(X_train, y_train)
    
    print("\n=== 評估模型 ===")
    y_pred = clf.predict(X_test)
    print(f"🎯 準確率: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=['Rock', 'Paper', 'Scissors']))
    
    # 儲存模型
    model_path = os.path.join(base_dir, 'demo', 'rps_mediapipe_svm.pkl')
    joblib.dump(clf, model_path)
    print(f"✅ 模型已儲存至: {model_path}")

if __name__ == "__main__":
    main()
