"""
Script Hỗ Trợ Cập Nhật Dữ Liệu Thuê Bao Tháng 11 (Dataset Update)
Bài 8: Quản lý mã nguồn và Dữ liệu

Tác vụ:
1. Đọc tệp dữ liệu cập nhật đợt mới từ data/raw_updates/nov_batch.csv
2. Nối thêm dữ liệu vào data/telecom_churn.csv
3. Thông báo số lượng bản ghi trước và sau khi cập nhật
"""

import os
import sys
import pandas as pd

def main():
    target_path = os.path.join('data', 'telecom_churn.csv')
    batch_path = os.path.join('data', 'raw_updates', 'nov_batch.csv')

    if not os.path.exists(target_path):
        print(f"[ERROR] Không tìm thấy tệp dữ liệu đích: {target_path}")
        sys.exit(1)

    if not os.path.exists(batch_path):
        print(f"[ERROR] Không tìm thấy tệp dữ liệu cập nhật: {batch_path}")
        sys.exit(1)

    df_current = pd.read_csv(target_path)
    old_count = len(df_current)

    # Đọc bản ghi mới (không có header)
    df_new = pd.read_csv(batch_path, header=None)
    df_new.columns = df_current.columns
    new_additions = len(df_new)

    df_updated = pd.concat([df_current, df_new], ignore_index=True)
    df_updated.to_csv(target_path, index=False)

    print(f"[*] Cập nhật thành công tập dữ liệu: {target_path}")
    print(f"    - Số bản ghi ban đầu (Tháng 10): {old_count:,} bản ghi")
    print(f"    - Số bản ghi bổ sung (Tháng 11): {new_additions:,} bản ghi")
    print(f"    - Tổng số bản ghi mới (v2.0)   : {len(df_updated):,} bản ghi")
    print("\n[!] BƯỚC TIẾP THEO:")
    print("    Chạy lệnh DVC để theo dõi phiên bản mới:")
    print("    $ dvc add data/telecom_churn.csv")
    print("    $ dvc push")

if __name__ == '__main__':
    main()
