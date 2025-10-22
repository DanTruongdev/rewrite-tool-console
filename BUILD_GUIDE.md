# HƯỚNG DẪN BUILD ỨNG DỤNG GENTITLE THÀNH FILE .EXE

## Mô tả

Ứng dụng này sử dụng AI model để generate movie titles và mô tả, kết nối với PostgreSQL database.

## Yêu cầu hệ thống

- Python 3.7 trở lên
- Kết nối internet (để download model lần đầu)
- Ít nhất 4GB RAM
- Khoảng 2GB dung lượng trống cho quá trình build

## Cách 1: Build tự động (Khuyến nghị)

### Bước 1: Mở PowerShell/Command Prompt tại thư mục dự án

### Bước 2: Chạy build script

```powershell
python build.py
```

Script sẽ tự động:

- Cài đặt dependencies
- Cài đặt PyInstaller
- Build ứng dụng thành file .exe
- Tạo file `dist/gentitle.exe`

## Cách 2: Build thủ công

### Bước 1: Cài đặt dependencies

```powershell
pip install -r requirements.txt
pip install pyinstaller
```

### Bước 2: Build bằng spec file (Khuyến nghị)

```powershell
pyinstaller gentitle.spec
```

### Bước 3: Hoặc build trực tiếp

```powershell
pyinstaller --onefile --console --name gentitle main.py
```

## Kết quả

- File .exe được tạo tại: `dist/gentitle.exe`
- Kích thước dự kiến: 500MB - 1GB (bao gồm AI model)
- File này có thể chạy độc lập trên máy Windows khác

## Lưu ý quan trọng

### 1. Model AI

- Ứng dụng sử dụng model `chieunq/vietnamese-sentence-paraphase` từ HuggingFace
- Lần chạy đầu tiên sẽ download model (khoảng 500MB)
- Model sẽ được cache tại: `%USERPROFILE%\.cache\huggingface`

### 2. Database

- Cần PostgreSQL server đang chạy
- Thông tin kết nối được lưu tại `db_config.json`
- Cấu trúc bảng cần có: `movie`, `movie_titles`

### 3. Phân phối

- File .exe có thể copy sang máy khác mà không cần cài Python
- Máy đích cần có:
  - Kết nối internet (lần đầu download model)
  - PostgreSQL client libraries (thường có sẵn)

## Troubleshooting

### Lỗi build

- Đảm bảo Python version >= 3.7
- Kiểm tra đủ dung lượng ổ cứng
- Chạy lại với quyền Administrator nếu cần

### Lỗi runtime

- Kiểm tra kết nối internet
- Verify PostgreSQL connection
- Kiểm tra file `db_config.json`

### File exe quá lớn

- Đã optimize loại bỏ các modules không cần thiết
- Có thể sử dụng UPX compression (đã enable)

## Cấu trúc files sau build

```
gentitle/
├── main.py                 # Source code chính
├── requirements.txt        # Dependencies
├── build.py               # Build script tự động
├── gentitle.spec          # PyInstaller config
├── db_config.json         # Database config (tạo khi chạy)
├── build/                 # Temp files (có thể xóa)
└── dist/
    └── gentitle.exe       # File exe cuối cùng
```

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:

1. Python version: `python --version`
2. Pip version: `pip --version`
3. Available disk space
4. Internet connection
