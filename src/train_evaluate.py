"""
Module Huấn Luyện & Đánh Giá Mô Hình Dự Đoán Churn Viễn Thông
Bài 8: Quản lý mã nguồn và Dữ liệu

Tác vụ:
1. Đọc dữ liệu đặc trưng data/churn_features.csv
2. Huấn luyện mô hình phân loại Gradient Boosting / Logistic Regression
3. Tính toán các chỉ số kiểm thử: Accuracy, Precision, Recall, F1-score, ROC-AUC
4. Xuất mô hình vào models/churn_model.pkl và xuất số liệu vào metrics.json
"""

import os
import sys
import json
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def main():
    features_path = os.path.join('data', 'churn_features.csv')
    models_dir = 'models'
    model_path = os.path.join(models_dir, 'churn_model.pkl')
    metrics_path = 'metrics.json'

    if not os.path.exists(features_path):
        print(f"[ERROR] Không tìm thấy tệp đặc trưng: {features_path}")
        print("Vui lòng chạy bước tiền xử lý trước: python src/prepare.py")
        sys.exit(1)

    print(f"[*] Đang nạp dữ liệu đặc trưng từ: {features_path}")
    df = pd.read_csv(features_path)
    print(f"[+] Kích thước tập dữ liệu: {df.shape[0]} mẫu, {df.shape[1]} cột")

    X = df.drop(columns=['churn'])
    y = df['churn']

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    print(f"[+] Phân chia tập huấn luyện: {len(X_train)} mẫu; tập kiểm định: {len(X_val)} mẫu")

    # Huấn luyện mô hình Random Forest cơ bản
    print("[*] Đang huấn luyện mô hình dự đoán rời mạng...")
    clf = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
    clf.fit(X_train, y_train)

    # Dự đoán và tính toán chỉ số
    y_pred = clf.predict(X_val)
    y_prob = clf.predict_proba(X_val)[:, 1]

    metrics = {
        'total_samples': int(len(df)),
        'train_samples': int(len(X_train)),
        'val_samples': int(len(X_val)),
        'accuracy': round(float(accuracy_score(y_val, y_pred)), 4),
        'precision': round(float(precision_score(y_val, y_pred, zero_division=0)), 4),
        'recall': round(float(recall_score(y_val, y_pred, zero_division=0)), 4),
        'f1_score': round(float(f1_score(y_val, y_pred, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_val, y_prob)), 4)
    }

    print("\n--- KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH CHURN ---")
    for k, v in metrics.items():
        print(f"  {k:15}: {v}")
    print("--------------------------------------\n")

    os.makedirs(models_dir, exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(clf, f)
    print(f"[OK] Đã lưu mô hình nhị phân tại: {model_path}")

    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    print(f"[OK] Đã xuất tệp chỉ số kiểm thử tại: {metrics_path}")

if __name__ == '__main__':
    main()
