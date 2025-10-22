# 🚀 GENTITLE - Ứng dụng Generate Movie Titles

## 📝 Mô tả

Ứng dụng sử dụng AI model để tự động generate movie titles và descriptions bằng tiếng Việt. Ứng dụng kết nối với PostgreSQL database để lưu trữ và xử lý dữ liệu phim.

## ✨ Tính năng

- 🤖 Sử dụng AI model `chieunq/vietnamese-sentence-paraphase`
- 📊 Kết nối PostgreSQL database
- 🔄 Generate titles và descriptions tự động
- 💾 Lưu cấu hình database
- 📈 **Hiển thị tiến trình load model với progress bar**
- ⚡ **Smart caching - chỉ download model lần đầu**
- 🎯 **Spinner animation trong khi xử lý**
- 🛡️ Xử lý lỗi an toàn

## 📦 Files đã tạo

### 🎯 File chính

- `gentitle.exe` - File thực thi chính (168.5MB)

### 🔧 Build files

- `build.py` - Script build tự động
- `gentitle.spec` - Cấu hình PyInstaller
- `requirements.txt` - Dependencies
- `BUILD_GUIDE.md` - Hướng dẫn build chi tiết

## 🎮 Cách sử dụng

### Bước 1: Chạy ứng dụng

```powershell
# Chạy trực tiếp file exe
.\dist\gentitle.exe
```

**🆕 Tính năng mới:** Ứng dụng sẽ hiển thị tiến trình load model:

- ✅ Nếu model đã cache: Load nhanh với spinner
- 📥 Nếu chưa có: Progress bar download (~500MB)

### Bước 2: Cấu hình Database

Khi chạy lần đầu, ứng dụng sẽ yêu cầu nhập thông tin PostgreSQL:

- Host (mặc định: localhost)
- Port (mặc định: 5432)
- Database name
- Username
- Password

Thông tin sẽ được lưu vào `db_config.json` để sử dụng lần sau.

### Bước 3: Nhập thông số

- Số lượng titles cần generate cho mỗi phim
- ID phim bắt đầu (tùy chọn)

### Bước 4: Chờ xử lý

Ứng dụng sẽ:

- Download AI model (lần đầu tiên)
- Kết nối database
- Xử lý từng phim
- Hiển thị tiến độ

## 💡 Lưu ý quan trọng

### 🌐 Kết nối Internet

- **Bắt buộc** cho lần chạy đầu tiên để download model
- Model sẽ được cache tại `%USERPROFILE%\.cache\huggingface`
- Sau đó có thể chạy offline (trừ khi cập nhật model)

### 🗄️ Database Requirements

```sql
-- Cấu trúc bảng cần có
CREATE TABLE movie (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT
);

CREATE TABLE movie_titles (
    movie_id INTEGER,
    site_id INTEGER,
    title TEXT,
    description TEXT
);
```

### ⚡ Performance

- RAM: Tối thiểu 4GB (khuyến nghị 8GB+)
- CPU: Sẽ sử dụng tối đa khả năng CPU
- Thời gian: ~2-5 giây/title tùy thuộc cấu hình máy

## 🔧 Troubleshooting

### ❌ Lỗi thường gặp

**1. "ModuleNotFoundError"**

```
Giải pháp: File exe đã bao gồm tất cả dependencies,
không cần cài thêm gì. Nếu vẫn lỗi, chạy lại build.
```

**2. "Connection refused"**

```
Giải pháp:
- Kiểm tra PostgreSQL server đang chạy
- Verify thông tin kết nối
- Xóa db_config.json để nhập lại
```

**3. "Model download failed"**

```
Giải pháp:
- Kiểm tra kết nối internet
- Thử chạy lại (model sẽ resume download)
- Xóa cache: %USERPROFILE%\.cache\huggingface
```

**4. "Out of memory"**

```
Giải pháp:
- Đóng các ứng dụng khác
- Giảm batch size trong code
- Nâng cấp RAM
```

### 🏃‍♂️ Chạy trên máy khác

File `gentitle.exe` có thể copy sang máy Windows khác:

- ✅ Không cần cài Python
- ✅ Không cần cài dependencies
- ⚠️ Cần kết nối internet lần đầu
- ⚠️ Cần PostgreSQL server

## 📊 Specs

### 📏 Kích thước

- File exe: **168.5 MB** (đã tối ưu)
- Bao gồm: Python runtime + dependencies (không bao gồm model)
- Model download: **~500MB** (cache tự động)

### 🎯 Model

- **chieunq/vietnamese-sentence-paraphase**
- Base: mT5 (multilingual T5)
- Specialized: Vietnamese paraphrasing
- Size: ~500MB khi download

### 🔄 Build lại (nếu cần)

```powershell
# Tự động
python build.py

# Thủ công
pyinstaller gentitle.spec
```

## 👥 Hỗ trợ

Khi gặp vấn đề:

1. Kiểm tra `BUILD_GUIDE.md`
2. Xem log trong console
3. Thử build lại với `python build.py`
4. Kiểm tra system requirements

---

_Được tạo bởi PyInstaller với tối ưu cho AI models_ 🤖
