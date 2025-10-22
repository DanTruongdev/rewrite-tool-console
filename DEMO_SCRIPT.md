# 🎬 DEMO SCRIPT - GENTITLE APP

## 📋 Kịch bản demo cho video hướng dẫn

### 🎯 Scene 1: Giới thiệu (30s)
```
🎭 Narrator: "Chào mừng đến với GenTitle - ứng dụng AI generate movie titles!"
🎯 "Chỉ với 1 click, bạn có thể tạo hàng ngàn titles chất lượng cao"
📱 "Đã được đóng gói thành file .exe, chạy ngay không cần cài đặt"
```

### 🚀 Scene 2: Khởi động ứng dụng (45s)
```
💻 Action: Double-click gentitle.exe
📟 Screen: Console mở ra
🎵 SFX: Khởi động

📺 Màn hình hiện:
CHƯƠNG TRÌNH GENERATE MOVIE TITLES
==================================================
🚀 Khởi tạo AI Model...

🤖 ĐANG TẢI AI MODEL...
==================================================
```

### 📥 Scene 3: Download Model lần đầu (60s)
```
🎭 Narrator: "Lần chạy đầu tiên, ứng dụng sẽ download AI model"

📺 Screen animation:
📥 Cần download model lần đầu (kích thước: ~500MB)
🌐 Đảm bảo kết nối internet ổn định...
⏳ Quá trình này có thể mất 5-15 phút tùy tốc độ mạng

📥 Download: |████████████░░░░░░░░░░░░░░░░░░░░| 45.2%

🎭 Narrator: "Progress bar giúp bạn theo dõi tiến trình download"
```

### ⚡ Scene 4: Load từ cache (30s)
```
🎭 Narrator: "Từ lần thứ 2, model load cực nhanh từ cache"

📺 Screen:
✅ Model đã có trong cache, đang load...
⠋ Đang load model từ cache...
✅ Model loaded thành công từ cache!

🎵 SFX: Success sound
```

### 🗄️ Scene 5: Database setup (90s)
```
🎭 Narrator: "Tiếp theo, cấu hình kết nối database"

📺 Screen:
==================================================
NHẬP THÔNG TIN KẾT NỐI DATABASE
==================================================

Host (mặc định: localhost): 
Port (mặc định: 5432): 
Database name: movie_db
Username: postgres
Password: ********

Đang kiểm tra kết nối...
✓ Kết nối database thành công!
Đã lưu cấu hình thành công!
```

### 📊 Scene 6: Xem thông tin database (30s)
```
📺 Screen:
✓ Kết nối database thành công!

Số lượng phim trong database: 15,847
Phạm vi ID: 1 → 15847
```

### ⚙️ Scene 7: Nhập cấu hình (45s)
```
🎭 Narrator: "Nhập số lượng titles muốn generate"

📺 Screen:
Nhập số lượng title cần generate cho mỗi phim: 5

Nhập ID movie bắt đầu (Enter để bắt đầu từ đầu): 1000
Tìm thấy 14,848 movies từ ID 1000

✓ Sẽ generate 5 titles cho mỗi phim
✓ Bắt đầu từ Movie ID: 1000

Bạn có muốn tiếp tục? (y/n): y
```

### 🔄 Scene 8: Xử lý real-time (120s)
```
🎭 Narrator: "Ứng dụng bắt đầu xử lý với AI model"

📺 Screen animation:
Bắt đầu xử lý movies với số lượng yêu cầu: 5
Bắt đầu từ Movie ID: 1000
==================================================
Tổng số movies cần xử lý: 14,848

[1/14848] Xử lý Movie ID: 1000
Title: Người hùng anh dũng...
Số lượng title hiện có: 2
Cần tạo thêm: 3 titles

  ✓ Tạo thành công site_id: 3
  ✓ Tạo thành công site_id: 4  
  ✓ Tạo thành công site_id: 5
    → Đã lưu batch 3 records vào DB
✓ Hoàn thành movie 1000, đã tạo: 3 titles

[2/14848] Xử lý Movie ID: 1001
...

🎭 Narrator: "Mỗi title được AI tạo ra hoàn toàn mới"
```

### 📈 Scene 9: Tiến độ và thống kê (60s)
```
📺 Screen:
--- Tiến độ: 100/14848 movies đã xử lý ---

[101/14848] Xử lý Movie ID: 1100
Title: Cuộc chiến sinh tồn đẫm máu...
✓ Đã đủ số lượng, bỏ qua

[102/14848] Xử lý Movie ID: 1101  
Title: Tình yêu vượt thời gian...
Cần tạo thêm: 2 titles
  ✓ Tạo thành công site_id: 8
  ✓ Tạo thành công site_id: 9

🎭 Narrator: "Ứng dụng tự động bỏ qua phim đã đủ titles"
```

### 🎊 Scene 10: Kết quả cuối cùng (45s)
```
📺 Screen:
==================================================
KẾT QUẢ XỬ LÝ
==================================================
Tổng số movies đã xử lý: 14,848
Số movies đã bỏ qua (đủ titles): 8,234
Tổng số titles đã generate: 33,070
Tổng số movies trong DB: 15,847
Bắt đầu từ Movie ID: 1000
✓ Hoàn thành!

✓ Đã đóng kết nối database

🎵 SFX: Completion fanfare
```

### 💡 Scene 11: Tips & Tricks (60s)
```
🎭 Narrator: "Một số mẹo sử dụng hiệu quả"

📺 Text overlay:
💡 TIPS & TRICKS

🚀 Model chỉ download 1 lần đầu
⚡ Lần sau chạy cực nhanh
🗄️ Cấu hình DB được lưu tự động  
🔄 Có thể chạy nhiều lần, không trùng lặp
📊 Batch processing an toàn
🛡️ Tự động rollback khi lỗi
📈 Real-time progress tracking
```

### 🎯 Scene 12: Call to Action (30s)
```
🎭 Narrator: "GenTitle - Giải pháp AI cho content creator"

📺 Text overlay:
🎬 GENTITLE
✨ AI-Powered Movie Title Generator
🚀 Ready to use • No setup required
📦 168MB • Includes everything
🔥 Made with love in Vietnam

GitHub: your-repo-link
Download: release-link
```

## 📝 Notes cho người quay
- Sử dụng screen recorder chất lượng cao
- Highlight cursor movements
- Zoom in vào progress bars
- Tăng tốc độ khi cần thiết
- Thêm sound effects phù hợp
- Logo animation ở đầu và cuối