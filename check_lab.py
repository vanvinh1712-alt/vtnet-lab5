#!/usr/bin/env python3
"""
Bộ Công Cụ Tự Động Thẩm Định & Nghiệm Thu Kỹ Thuật (Automated Lab Validator)
Bài 8: Quản lý mã nguồn và Dữ liệu

Công cụ này giúp học viên tự kiểm chứng từng điều kiện nghiệm thu kỹ thuật:
1. Trạng thái Git & Cấu trúc Phân nhánh Doanh nghiệp
2. Khởi tạo DVC & Cấu hình Kho lưu trữ Phụ trợ (Remote Storage)
3. Cơ chế Con trỏ Siêu dữ liệu (.dvc) & Tuân thủ An toàn Thông tin (ATTT)
4. Đóng băng Phiên bản Dữ liệu & Hệ thống Nhãn Release (Tags v1.0, v2.0)
5. Tính toàn vẹn Dữ liệu CAS & Khả năng Tái lập (Time-Travel)
6. Đường ống Tự động hóa Pipeline (dvc.yaml) & Chỉ số Kiểm thử (metrics.json)
"""

import os
import sys
import json
import yaml
import hashlib
import subprocess

# Mã màu ANSI
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

MD5_V1 = "d9ff2d8919ff9265e9939a885cb14650"
MD5_V2 = "c366b44c73b3338485a2cb311635175d"

def print_header(title):
    print(f"\n{BOLD}{CYAN}{'='*68}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*68}{RESET}\n")

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def compute_md5(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def check_git_setup():
    print(f"{BOLD}[Tiêu chí 1] Kiểm tra Khởi tạo Git & Cấu hình Danh tính{RESET}")
    if not os.path.exists(".git"):
        print(f"  {RED}[FAIL]{RESET} Thư mục .git chưa tồn tại! Hãy chạy: git init -b main")
        return False, "Git repository chưa được khởi tạo."

    ok, user_name, _ = run_cmd("git config user.name")
    ok2, user_email, _ = run_cmd("git config user.email")
    if not ok or not user_name:
        print(f"  {YELLOW}[WARN]{RESET} Chưa cấu hình git config user.name (Khuyến nghị: Họ tên kỹ sư)")
    else:
        print(f"  {GREEN}[PASS]{RESET} Git user.name: {user_name}")

    if not ok2 or not user_email:
        print(f"  {YELLOW}[WARN]{RESET} Chưa cấu hình git config user.email (Khuyến nghị: email cá nhân / công vụ)")
    else:
        print(f"  {GREEN}[PASS]{RESET} Git user.email: {user_email}")

    # Kiểm tra nhánh
    ok3, branch, _ = run_cmd("git branch --show-current")
    ok_branches, all_branches, _ = run_cmd("git branch")
    print(f"  {GREEN}[PASS]{RESET} Nhánh hiện tại: {BOLD}{branch or 'detached'}{RESET}")
    return True, f"Git đã sẵn sàng (Nhánh: {branch})"

def check_dvc_setup():
    print(f"\n{BOLD}[Tiêu chí 2] Kiểm tra Khởi tạo DVC & Cấu hình Remote Storage{RESET}")
    if not os.path.exists(".dvc"):
        print(f"  {RED}[FAIL]{RESET} Thư mục .dvc chưa tồn tại! Hãy chạy: dvc init")
        return False, "DVC chưa được khởi tạo."
    print(f"  {GREEN}[PASS]{RESET} Thư mục quản trị siêu dữ liệu .dvc đã được khởi tạo")

    if not os.path.exists(".dvcignore"):
        print(f"  {YELLOW}[WARN]{RESET} Không tìm thấy tệp .dvcignore")
    else:
        print(f"  {GREEN}[PASS]{RESET} Tệp cấu hình .dvcignore hợp lệ")

    # Kiểm tra remote storage
    ok, remotes, _ = run_cmd("dvc remote list")
    if not ok or not remotes.strip():
        print(f"  {RED}[FAIL]{RESET} Chưa cấu hình DVC Remote! Hãy chạy: dvc remote add -d <tên> <đường_dẫn>")
        return False, "Thiếu DVC Remote Storage."
    
    for r in remotes.strip().split("\n"):
        print(f"  {GREEN}[PASS]{RESET} DVC Remote Storage đã thiết lập: {BOLD}{r}{RESET}")
    return True, "DVC và Remote Storage đã sẵn sàng."

def check_attt_compliance():
    print(f"\n{BOLD}[Tiêu chí 3] Kiểm tra Con trỏ Siêu dữ liệu (.dvc) & An toàn Thông tin (ATTT){RESET}")
    dvc_file = os.path.join("data", "telecom_churn.csv.dvc")
    if not os.path.exists(dvc_file):
        print(f"  {RED}[FAIL]{RESET} Không tìm thấy tệp con trỏ {dvc_file}! Hãy chạy: dvc add data/telecom_churn.csv")
        return False, "Chưa theo dõi dữ liệu bằng DVC."

    print(f"  {GREEN}[PASS]{RESET} Tìm thấy tệp con trỏ siêu dữ liệu: {dvc_file}")

    # Đọc nội dung tệp .dvc
    try:
        with open(dvc_file, 'r', encoding='utf-8') as f:
            dvc_meta = yaml.safe_load(f)
        tracked_md5 = dvc_meta['outs'][0]['md5']
        tracked_size = dvc_meta['outs'][0]['size']
        print(f"  {GREEN}[PASS]{RESET} Con trỏ DVC: MD5={tracked_md5}, Size={tracked_size:,} bytes")
    except Exception as e:
        print(f"  {RED}[FAIL]{RESET} Tệp .dvc không hợp lệ: {e}")
        return False, "Tệp .dvc bị lỗi định dạng."

    # Kiểm tra quy định ATTT: Dữ liệu thô CSV không bao giờ được commit trực tiếp vào Git
    gitignore_file = os.path.join("data", ".gitignore")
    if not os.path.exists(gitignore_file):
        print(f"  {RED}[FAIL]{RESET} Thiếu tệp data/.gitignore bảo vệ kho mã nguồn!")
        return False, "Thiếu data/.gitignore."

    with open(gitignore_file, 'r', encoding='utf-8') as f:
        gi_content = f.read()
    if "telecom_churn.csv" not in gi_content:
        print(f"  {RED}[FAIL]{RESET} Tệp data/.gitignore chưa chặn tệp telecom_churn.csv!")
        return False, "Dữ liệu thô chưa được loại trừ khỏi Git."
    print(f"  {GREEN}[PASS]{RESET} data/.gitignore đã loại trừ tệp dữ liệu lớn theo chuẩn ATTT")

    # Kiểm tra Git index có vô tình theo dõi file CSV không
    ok, tracked_by_git, _ = run_cmd("git ls-files data/telecom_churn.csv")
    if tracked_by_git.strip():
        print(f"  {RED}[VIOLATION]{RESET} CẢNH BÁO ATTT: Tệp telecom_churn.csv đang bị Git theo dõi trực tiếp!")
        print("              Hãy gỡ khỏi Git index: git rm --cached data/telecom_churn.csv")
        return False, "Vi phạm ATTT: Tệp dữ liệu lớn đang nằm trong Git index."
    print(f"  {GREEN}[PASS]{RESET} Tuân thủ ATTT: Dữ liệu lớn không bị rò rỉ vào kho mã nguồn Git")

    return True, "Hệ thống con trỏ và hàng rào ATTT hoàn hảo."

def check_version_tags():
    print(f"\n{BOLD}[Tiêu chí 4] Kiểm tra Lịch sử Phiên bản & Nhãn Release (Git Tags){RESET}")
    ok, tags, _ = run_cmd("git tag -l")
    tag_list = [t.strip() for t in tags.split("\n") if t.strip()]

    has_v1 = "v1.0" in tag_list
    has_v2 = "v2.0" in tag_list

    if has_v1:
        print(f"  {GREEN}[PASS]{RESET} Tìm thấy nhãn phiên bản cơ sở: {BOLD}v1.0{RESET}")
    else:
        print(f"  {YELLOW}[WARN]{RESET} Chưa gắn nhãn Git tag v1.0 cho phiên bản tháng 10")

    if has_v2:
        print(f"  {GREEN}[PASS]{RESET} Tìm thấy nhãn phiên bản mở rộng: {BOLD}v2.0{RESET}")
    else:
        print(f"  {YELLOW}[WARN]{RESET} Chưa gắn nhãn Git tag v2.0 cho phiên bản tháng 11")

    if not has_v1 and not has_v2:
        return False, "Chưa tìm thấy nhãn Release (v1.0 hoặc v2.0)."
    return True, f"Tìm thấy các nhãn phiên bản: {', '.join(tag_list)}"

def check_time_travel():
    print(f"\n{BOLD}[Tiêu chí 5] Kiểm tra Tính Toàn Vẹn CAS & Trạng thái Dữ liệu Hiện tại{RESET}")
    csv_file = os.path.join("data", "telecom_churn.csv")
    if not os.path.exists(csv_file):
        print(f"  {RED}[FAIL]{RESET} Không tìm thấy tệp dữ liệu thật {csv_file}! Hãy chạy: dvc checkout")
        return False, "Thiếu tệp dữ liệu thật trong workspace."

    cur_md5 = compute_md5(csv_file)
    with open(csv_file, 'r', encoding='utf-8') as f:
        line_count = len(f.readlines()) - 1  # trừ header

    print(f"  {GREEN}[PASS]{RESET} Tệp dữ liệu hiện tại: {BOLD}{line_count:,} bản ghi{RESET}")
    print(f"  {GREEN}[PASS]{RESET} Mã băm MD5 hiện tại: {BOLD}{cur_md5}{RESET}")

    if cur_md5 == MD5_V1:
        print(f"  {CYAN}[INFO]{RESET} Không gian làm việc đang ở đúng trạng thái {BOLD}Phiên bản v1.0 (Tháng 10){RESET}")
        return True, "Dữ liệu khớp chuẩn phiên bản v1.0"
    elif cur_md5 == MD5_V2:
        print(f"  {CYAN}[INFO]{RESET} Không gian làm việc đang ở đúng trạng thái {BOLD}Phiên bản v2.0 (Tháng 11){RESET}")
        return True, "Dữ liệu khớp chuẩn phiên bản v2.0"
    else:
        print(f"  {YELLOW}[WARN]{RESET} Mã băm MD5 ({cur_md5}) không khớp mã băm mẫu v1.0 hoặc v2.0.")
        return True, "Dữ liệu hợp lệ (tùy biến riêng của học viên)"

def check_pipeline_and_metrics():
    print(f"\n{BOLD}[Tiêu chí 6] Kiểm tra Pipeline Tự động hóa (dvc.yaml) & Chỉ số Kiểm thử{RESET}")
    if not os.path.exists("dvc.yaml"):
        print(f"  {RED}[FAIL]{RESET} Chưa tìm thấy tệp cấu hình pipeline dvc.yaml")
        return False, "Thiếu tệp dvc.yaml."
    print(f"  {GREEN}[PASS]{RESET} Tìm thấy tệp cấu trúc pipeline: dvc.yaml")

    metrics_file = "metrics.json"
    if not os.path.exists(metrics_file):
        print(f"  {YELLOW}[WARN]{RESET} Chưa tìm thấy metrics.json. Hãy chạy: dvc repro")
        return False, "Chưa thực thi pipeline để sinh metrics.json."
    
    try:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            m = json.load(f)
        acc = m.get('accuracy', 'N/A')
        auc = m.get('roc_auc', 'N/A')
        samples = m.get('total_samples', 'N/A')
        print(f"  {GREEN}[PASS]{RESET} Đã nghiệm thu số liệu kiểm thử: Samples={samples}, Accuracy={acc}, ROC-AUC={auc}")
        return True, "Pipeline và số liệu kiểm thử đạt yêu cầu."
    except Exception as e:
        print(f"  {RED}[FAIL]{RESET} Lỗi đọc metrics.json: {e}")
        return False, "metrics.json lỗi định dạng."

def main():
    print_header("HỆ THỐNG THẨM ĐỊNH & NGHIỆM THU LAB 8: GIT & DVC VERSIONING")
    
    checks = [
        ("Git Repository & Identity", check_git_setup),
        ("DVC Setup & Remote Storage", check_dvc_setup),
        ("Metadata Pointer & ATTT Compliance", check_attt_compliance),
        ("Version Tags & Releases", check_version_tags),
        ("Data Integrity & Time-Travel", check_time_travel),
        ("Pipeline & Metrics Verification", check_pipeline_and_metrics),
    ]

    results = []
    for name, func in checks:
        try:
            status, msg = func()
            results.append((name, status, msg))
        except Exception as e:
            results.append((name, False, f"Ngoại lệ kỹ thuật: {str(e)}"))

    print_header("TỔNG HỢP KẾT QUẢ NGHIỆM THU KỸ THUẬT")
    passed_count = sum(1 for _, st, _ in results if st)
    total_count = len(results)

    for name, st, msg in results:
        badge = f"{GREEN}[ĐẠT]{RESET}" if st else f"{RED}[CHƯA ĐẠT]{RESET}"
        print(f"  {badge} {BOLD}{name:35}{RESET} : {msg}")

    print(f"\n{BOLD}Kết quả chung: {passed_count}/{total_count} tiêu chí nghiệm thu hoàn thành.{RESET}")
    if passed_count == total_count:
        print(f"\n{BOLD}{GREEN}>>> XUẤT SẮC! BẠN ĐÃ HOÀN THÀNH TOÀN DIỆN MỤC TIÊU BÀI LAB 8 <<<{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{BOLD}{YELLOW}>>> Vui lòng xem lại các tiêu chí [CHƯA ĐẠT] và thực hiện theo hướng dẫn trong README.md <<<{RESET}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
