"""
Module Tiền Xử Lý Dữ Liệu Thuê Bao Viễn Thông (Data Preprocessing Pipeline)
Bài 8: Quản lý mã nguồn và Dữ liệu

Tác vụ:
1. Đọc dữ liệu thô telecom_churn.csv
2. Kiểm tra chất lượng dữ liệu: tính toàn vẹn 14 cột, xử lý giá trị khuyết
3. Chuẩn hóa tên đặc trưng sang dạng snake_case
4. Xuất dữ liệu đặc trưng đã làm sạch: data/churn_features.csv
"""

import os
import sys
import pandas as pd

REQUIRED_COLUMNS = [
    'Call Failure', 'Complains', 'Subscription Length', 'Charge Amount',
    'Seconds of Use', 'Frequency of use', 'Frequency of SMS',
    'Distinct Called Numbers', 'Age Group', 'Tariff Plan', 'Status',
    'Age', 'Customer Value', 'Churn'
]

COLUMN_MAPPING = {
    'Call Failure': 'call_failure',
    'Complains': 'complains',
    'Subscription Length': 'subscription_length',
    'Charge Amount': 'charge_amount',
    'Seconds of Use': 'seconds_of_use',
    'Frequency of use': 'frequency_of_use',
    'Frequency of SMS': 'frequency_of_sms',
    'Distinct Called Numbers': 'distinct_called_numbers',
    'Age Group': 'age_group',
    'Tariff Plan': 'tariff_plan',
    'Status': 'status',
    'Age': 'age',
    'Customer Value': 'customer_value',
    'Churn': 'churn'
}

def main():
    raw_path = os.path.join('data', 'telecom_churn.csv')
    out_dir = 'data'
    out_path = os.path.join(out_dir, 'churn_features.csv')

    if not os.path.exists(raw_path):
        print(f"[ERROR] Không tìm thấy tệp dữ liệu thô: {raw_path}")
        print("Vui lòng kiểm tra lại vị trí tệp hoặc chạy 'dvc checkout' để đồng bộ dữ liệu.")
        sys.exit(1)

    print(f"[*] Đang đọc dữ liệu thô từ: {raw_path}")
    df = pd.read_csv(raw_path)
    total_rows = len(df)
    print(f"[+] Tổng số bản ghi thuê bao đọc được: {total_rows:,} bản ghi")

    # Kiểm tra cột bắt buộc
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        print(f"[ERROR] Thiếu các cột bắt buộc: {missing_cols}")
        sys.exit(1)

    # Kiểm tra giá trị khuyết
    null_counts = df[REQUIRED_COLUMNS].isnull().sum().sum()
    if null_counts > 0:
        print(f"[!] Phát hiện {null_counts} giá trị khuyết, tiến hành điền trung vị...")
        df = df.fillna(df.median(numeric_only=True))

    # Chuẩn hóa tên cột
    df_clean = df[REQUIRED_COLUMNS].rename(columns=COLUMN_MAPPING)

    # Thống kê phân bố nhãn Churn
    churn_rate = (df_clean['churn'].sum() / len(df_clean)) * 100
    print(f"[+] Tỷ lệ thuê bao rời mạng (Churn Rate): {churn_rate:.2f}%")

    os.makedirs(out_dir, exist_ok=True)
    df_clean.to_csv(out_path, index=False)
    print(f"[OK] Xuất thành công tệp đặc trưng đã làm sạch: {out_path} ({len(df_clean):,} dòng)")

if __name__ == '__main__':
    main()
