import json
import os
import sys
import time
import threading
import psycopg2
from psycopg2 import sql
from transformers import T5Tokenizer, MT5ForConditionalGeneration
from huggingface_hub import snapshot_download
from pathlib import Path

# --- Model paraphrase ---
# CKPT = './model'
CKPT = 'chieunq/vietnamese-sentence-paraphase'

# Global variables for model
tokenizer = None
model = None

def show_progress_spinner(message, stop_event):
    """Hiển thị spinner trong khi load model"""
    spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    i = 0
    while not stop_event.is_set():
        print(f"\r{spinner_chars[i % len(spinner_chars)]} {message}", end='', flush=True)
        i += 1
        time.sleep(0.1)

def check_model_cached():
    """Kiểm tra xem model đã được cache chưa"""
    cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
    model_dirs = list(cache_dir.glob(f"*{CKPT.replace('/', '--')}*"))
    
    if model_dirs:
        # Kiểm tra xem có đầy đủ files không
        for model_dir in model_dirs:
            refs_dir = model_dir / 'refs'
            snapshots_dir = model_dir / 'snapshots'
            if refs_dir.exists() and snapshots_dir.exists():
                snapshot_dirs = list(snapshots_dir.iterdir())
                if snapshot_dirs:
                    # Kiểm tra các file cần thiết
                    snapshot_dir = snapshot_dirs[0]
                    required_files = ['config.json', 'pytorch_model.bin', 'tokenizer.json']
                    has_all_files = all((snapshot_dir / f).exists() for f in required_files)
                    if has_all_files:
                        return True
    return False

def estimate_download_size():
    """Ước tính kích thước download"""
    return "~500MB"

def load_model_with_progress():
    """Load model với hiển thị tiến trình"""
    global tokenizer, model
    
    print("🤖 ĐANG TẢI AI MODEL...")
    print("=" * 50)
    
    is_cached = check_model_cached()
    
    if is_cached:
        print("✅ Model đã có trong cache, đang load...")
        stop_event = threading.Event()
        spinner_thread = threading.Thread(target=show_progress_spinner, 
                                         args=("Đang load model từ cache...", stop_event))
        spinner_thread.start()
        
        try:
            tokenizer = T5Tokenizer.from_pretrained(CKPT)
            model = MT5ForConditionalGeneration.from_pretrained(CKPT)
            stop_event.set()
            spinner_thread.join()
            print("\r✅ Model loaded thành công từ cache!           ")
        except Exception as e:
            stop_event.set()
            spinner_thread.join()
            print(f"\r❌ Lỗi load model từ cache: {e}           ")
            raise
    else:
        print(f"📥 Cần download model lần đầu (kích thước: {estimate_download_size()})")
        print("🌐 Đảm bảo kết nối internet ổn định...")
        print("⏳ Quá trình này có thể mất 5-15 phút tùy tốc độ mạng")
        print()
        
        # Hiển thị tiến trình download
        download_progress = {'current': 0, 'total': 100}
        stop_event = threading.Event()
        
        def download_progress_display():
            while not stop_event.is_set():
                progress = min(download_progress['current'], download_progress['total'])
                percentage = (progress / download_progress['total']) * 100
                bar_length = 30
                filled_length = int(bar_length * progress // download_progress['total'])
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                print(f"\r📥 Download: |{bar}| {percentage:.1f}% ", end='', flush=True)
                time.sleep(0.5)
                # Tăng progress giả để user thấy có tiến trình
                if download_progress['current'] < 30:
                    download_progress['current'] += 0.5
                elif download_progress['current'] < 60:
                    download_progress['current'] += 0.2
                elif download_progress['current'] < 90:
                    download_progress['current'] += 0.1
        
        progress_thread = threading.Thread(target=download_progress_display)
        progress_thread.start()
        
        try:
            # Load tokenizer trước
            tokenizer = T5Tokenizer.from_pretrained(CKPT)
            download_progress['current'] = 50
            
            # Load model
            model = MT5ForConditionalGeneration.from_pretrained(CKPT)
            download_progress['current'] = 100
            
            stop_event.set()
            progress_thread.join()
            print("\r✅ Model download và load thành công!                           ")
            print("💾 Model đã được cache cho lần sử dụng tiếp theo")
            
        except Exception as e:
            stop_event.set()
            progress_thread.join()
            print(f"\r❌ Lỗi download/load model: {e}                           ")
            print("💡 Kiểm tra kết nối internet và thử lại")
            raise
    
    print("=" * 50)
    return tokenizer, model

def paraphase(text: str, max_length: int = 64, num_return_sequences: int = 3, max_retry: int = 10) -> str:
    global tokenizer, model
    
    # Kiểm tra model đã được load chưa
    if tokenizer is None or model is None:
        raise RuntimeError("Model chưa được load! Gọi load_model_with_progress() trước.")
    
    for attempt in range(max_retry):
        inputs = tokenizer(text, padding='longest', max_length=max_length, return_tensors='pt')
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            top_k=50,
            top_p=0.9,
            temperature=0.8
        )
        candidate = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        if candidate != text.strip():
            return candidate
    return text

def rewrite_string(text: str, num: int):
    results = []
    for i in range(1, num + 1):
        try:
            rewritten = paraphase(text)
            text = rewritten
            results.append({"key": str(i), "value": rewritten})
        except Exception as e:
            results.append({"key": str(i), "value": f"[ERROR] {e}"})
    return results

CONFIG_PATH = "db_config.json"

def save_config(config):
    """Lưu cấu hình database vào file JSON"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_config():
    """Tải cấu hình database từ file JSON"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def test_connection(config):
    """Kiểm tra kết nối database"""
    try:
        conn = psycopg2.connect(**config)
        conn.close()
        return True, "Kết nối thành công!"
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}"

def get_db_config():
    """Nhập và lưu cấu hình database"""
    print("=" * 50)
    print("NHẬP THÔNG TIN KẾT NỐI DATABASE")
    print("=" * 50)
    
    # Kiểm tra xem đã có config chưa
    existing_config = load_config()
    if existing_config:
        print("Đã tìm thấy cấu hình database cũ:")
        for key, value in existing_config.items():
            if key == 'password':
                print(f"  {key}: {'*' * len(str(value))}")
            else:
                print(f"  {key}: {value}")
        
        use_existing = input("\nSử dụng cấu hình này? (y/n): ").lower().strip()
        if use_existing == 'y':
            # Test connection
            success, message = test_connection(existing_config)
            print(f"\n{message}")
            if success:
                return existing_config
            else:
                print("Cần nhập lại cấu hình mới.")
    
    # Nhập cấu hình mới
    while True:
        config = {}
        config['host'] = input("Host (mặc định: localhost): ").strip() or "localhost"
        config['port'] = input("Port (mặc định: 5432): ").strip() or "5432"
        config['database'] = input("Database name: ").strip()
        config['user'] = input("Username: ").strip()
        config['password'] = input("Password: ").strip()
        
        # Convert port to int
        try:
            config['port'] = int(config['port'])
        except ValueError:
            print("Port phải là số nguyên!")
            continue
        
        # Test connection
        print("\nĐang kiểm tra kết nối...")
        success, message = test_connection(config)
        print(f"{message}")
        
        if success:
            save_config(config)
            print("Đã lưu cấu hình thành công!")
            return config
        else:
            retry = input("\nBạn có muốn nhập lại? (y/n): ").lower().strip()
            if retry != 'y':
                exit("Thoát chương trình.")

def get_movie_count(conn):
    """Lấy số lượng phim trong database"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM movie")
            count = cur.fetchone()[0]
            return count
    except Exception as e:
        print(f"Lỗi khi đếm số lượng phim: {e}")
        return 0

def get_max_site_id(conn, movie_id):
    """Lấy max site_id của movie_id trong bảng movie_titles"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(site_id), 0) FROM movie_titles WHERE movie_id = %s", (movie_id,))
            max_site_id = cur.fetchone()[0]
            return max_site_id
    except Exception as e:
        print(f"Lỗi khi lấy max site_id cho movie_id {movie_id}: {e}")
        try:
            conn.rollback()
        except:
            pass
        return -1  # Trả về -1 để báo lỗi

def get_movie_titles_count(conn, movie_id):
    """Đếm số lượng title hiện có của movie_id"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM movie_titles WHERE movie_id = %s", (movie_id,))
            count = cur.fetchone()[0]
            return count
    except Exception as e:
        print(f"Lỗi khi đếm movie_titles cho movie_id {movie_id}: {e}")
        try:
            conn.rollback()
        except:
            pass
        return -1  # Trả về -1 để báo lỗi

def create_movie_titles(conn, movie_id, site_id, title, description):
    """Tạo bản ghi mới trong bảng movie_titles"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO movie_titles (movie_id, site_id, title, description)
                VALUES (%s, %s, %s, %s)
            """, (movie_id, site_id, title, description))
        return True
    except Exception as e:
        print(f"Lỗi khi tạo movie_titles: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False

def process_movies(conn, site_ids, start_id=None, end_id=None):
    """Xử lý tất cả movies theo logic yêu cầu"""
    print(f"\nBắt đầu xử lý movies với danh sách site_ids: {site_ids}")
    print(f"Số lượng titles sẽ gen cho mỗi phim: {len(site_ids)}")
    if start_id:
        print(f"Bắt đầu từ Movie ID: {start_id}")
    if end_id:
        print(f"Kết thúc tại Movie ID: {end_id}")
    print("=" * 50)
    
    try:
        with conn.cursor() as cur:
            # Lấy movies theo range hoặc tất cả
            if start_id and end_id:
                cur.execute("SELECT id, title, description FROM movie WHERE id >= %s AND id <= %s ORDER BY id", (start_id, end_id))
            elif start_id:
                cur.execute("SELECT id, title, description FROM movie WHERE id >= %s ORDER BY id", (start_id,))
            else:
                cur.execute("SELECT id, title, description FROM movie ORDER BY id")
            movies = cur.fetchall()
            
            total_movies = len(movies)
            processed_count = 0
            skipped_count = 0
            generated_count = 0
            
            print(f"Tổng số movies cần xử lý: {total_movies}")
            
            for i, (movie_id, movie_titles, movie_description) in enumerate(movies, 1):
                print(f"\n[{i}/{total_movies}] Xử lý Movie ID: {movie_id}")
                
                # Hiển thị title an toàn
                title_display = movie_titles[:50] + "..." if movie_titles and len(movie_titles) > 50 else (movie_titles or "No title")
                print(f"Title: {title_display}")
                
                # Bắt đầu transaction mới cho mỗi movie
                try:
                    # Lấy max site_id hiện có để kiểm tra site_ids nào có thể sử dụng
                    max_site_id = get_max_site_id(conn, movie_id)
                    if max_site_id == -1:  # Lỗi khi lấy max_site_id
                        print("✗ Lỗi khi lấy max site_id, bỏ qua movie này")
                        continue
                    
                    # Lọc ra các site_ids có thể sử dụng (chưa tồn tại)
                    available_site_ids = []
                    existing_site_ids = []
                    
                    for site_id in site_ids:
                        # Kiểm tra xem site_id này đã tồn tại chưa
                        with conn.cursor() as check_cur:
                            check_cur.execute("SELECT COUNT(*) FROM movie_titles WHERE movie_id = %s AND site_id = %s", 
                                            (movie_id, site_id))
                            exists = check_cur.fetchone()[0] > 0
                            
                        if exists:
                            existing_site_ids.append(site_id)
                        else:
                            available_site_ids.append(site_id)
                    
                    if existing_site_ids:
                        print(f"Site_ids đã tồn tại: {existing_site_ids}")
                    
                    if not available_site_ids:
                        print("✓ Tất cả site_ids đã tồn tại, bỏ qua")
                        skipped_count += 1
                        continue
                    
                    print(f"Site_ids sẽ tạo mới: {available_site_ids}")
                    need_to_create = len(available_site_ids)
                
                except Exception as e:
                    print(f"✗ Lỗi khi kiểm tra dữ liệu movie {movie_id}: {e}")
                    try:
                        conn.rollback()
                    except:
                        pass
                    continue
                
                created_in_this_movie = 0
                batch_size = 5  # Commit sau mỗi 5 records
                batch_count = 0
                
                # Xử lý theo batch để giảm rủi ro
                try:                    
                    for j, target_site_id in enumerate(available_site_ids):
                        # Generate new title and description
                        if movie_titles:
                            new_title = paraphase(movie_titles)
                        else:
                            new_title = f"Generated Title {target_site_id}"
                        
                        if movie_description:
                            new_description = paraphase(movie_description)
                        else:
                            new_description = f"Generated Description {target_site_id}"
                        
                        # Tạo bản ghi mới
                        success = create_movie_titles(conn, movie_id, target_site_id, new_title, new_description)
                        if success:
                            created_in_this_movie += 1
                            generated_count += 1
                            batch_count += 1
                            print(f"  ✓ Tạo thành công site_id: {target_site_id}")
                            
                            # Commit sau mỗi batch_size records hoặc khi hoàn thành
                            if batch_count >= batch_size or j == len(available_site_ids) - 1:
                                try:
                                    conn.commit()
                                    print(f"    → Đã lưu batch {batch_count} records vào DB")
                                    batch_count = 0
                                except Exception as commit_error:
                                    print(f"    ✗ Lỗi khi commit batch: {commit_error}")
                                    conn.rollback()
                                    break
                        else:
                            print(f"  ✗ Lỗi tạo site_id: {target_site_id}")
                            # Nếu có lỗi tạo record, vẫn tiếp tục với record tiếp theo
                            continue
                    
                except Exception as e:
                    print(f"  ✗ Lỗi khi xử lý movie {movie_id}: {e}")
                    try:
                        conn.rollback()
                    except:
                        pass
                    continue
                print(f"✓ Hoàn thành movie {movie_id}, đã tạo: {created_in_this_movie} titles")
                processed_count += 1
                
                # Hiển thị tiến độ mỗi 10 movies
                if i % 10 == 0:
                    print(f"\n--- Tiến độ: {i}/{total_movies} movies đã xử lý ---")
    
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý: {e}")
        try:
            conn.rollback()
        except:
            pass
        
    return processed_count, skipped_count, generated_count

def main():
    print("CHƯƠNG TRÌNH GENERATE MOVIE TITLES")
    print("=" * 50)
    
    # Bước 1: Load AI Model
    print("🚀 Khởi tạo AI Model...")
    try:
        load_model_with_progress()
        print("✅ AI Model sẵn sàng!")
    except Exception as e:
        print(f"❌ Không thể load model: {e}")
        print("💡 Kiểm tra kết nối internet và thử lại")
        return
    
    # Bước 2: Cấu hình database
    config = get_db_config()
    
    # Bước 3: Kết nối database
    try:
        print("\nĐang kết nối database...")
        conn = psycopg2.connect(**config)
        print("✓ Kết nối database thành công!")
        
        # Bước 4: Hiển thị thông tin database
        movie_count = get_movie_count(conn)
        print(f"\nSố lượng phim trong database: {movie_count:,}")
        
        if movie_count == 0:
            print("Không có phim nào trong database!")
            return
        
        # Hiển thị phạm vi ID để tham khảo
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT MIN(id), MAX(id) FROM movie")
                min_id, max_id = cur.fetchone()
                print(f"Phạm vi ID: {min_id} → {max_id}")
        except Exception as e:
            print(f"Không thể lấy phạm vi ID: {e}")
        
        # Bước 5: Nhập danh sách site_id (bắt buộc)
        site_ids = None
        while True:
            site_ids_input = input(f"\nNhập danh sách site_id cần generate (VD: 1,2,3,4,5): ").strip()
            if not site_ids_input:
                print("Danh sách site_id là bắt buộc!")
                continue
            try:
                # Parse danh sách site_id
                site_ids = [int(x.strip()) for x in site_ids_input.split(',') if x.strip()]
                if not site_ids:
                    print("Danh sách site_id không được để trống!")
                    continue
                
                # Kiểm tra tất cả site_id > 0
                if any(sid <= 0 for sid in site_ids):
                    print("Tất cả site_id phải lớn hơn 0!")
                    continue
                
                # Kiểm tra không có site_id trùng lặp
                if len(site_ids) != len(set(site_ids)):
                    print("Danh sách site_id không được có phần tử trùng lặp!")
                    continue
                
                # Sắp xếp site_ids để xử lý theo thứ tự
                site_ids.sort()
                print(f"Sẽ generate {len(site_ids)} titles cho mỗi phim với site_ids: {site_ids}")
                break
            except ValueError:
                print("Vui lòng nhập danh sách số nguyên cách nhau bởi dấu phẩy!")
        
        # Bước 6: Nhập ID movie bắt đầu (tùy chọn)
        start_id = None
        while True:
            start_input = input(f"\nNhập ID movie bắt đầu (Enter để bắt đầu từ đầu): ").strip()
            if not start_input:
                break
            try:
                start_id = int(start_input)
                if start_id <= 0:
                    print("ID movie phải lớn hơn 0!")
                    continue
                # Kiểm tra ID có tồn tại không
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM movie WHERE id >= %s", (start_id,))
                    count = cur.fetchone()[0]
                    if count == 0:
                        print(f"Không tìm thấy movie nào có ID >= {start_id}!")
                        continue
                    else:
                        print(f"Tìm thấy {count:,} movies từ ID {start_id}")
                break
            except ValueError:
                print("Vui lòng nhập số nguyên hợp lệ!")
        
        # Bước 7: Nhập ID movie kết thúc (tùy chọn)
        end_id = None
        if start_id is not None:
            while True:
                end_input = input(f"Nhập ID movie kết thúc (Enter để xử lý đến hết): ").strip()
                if not end_input:
                    break
                try:
                    end_id = int(end_input)
                    if end_id <= 0:
                        print("ID movie phải lớn hơn 0!")
                        continue
                    if end_id < start_id:
                        print(f"ID kết thúc phải >= ID bắt đầu ({start_id})!")
                        continue
                    # Kiểm tra ID có tồn tại không
                    with conn.cursor() as cur:
                        cur.execute("SELECT COUNT(*) FROM movie WHERE id >= %s AND id <= %s", (start_id, end_id))
                        count = cur.fetchone()[0]
                        if count == 0:
                            print(f"Không tìm thấy movie nào trong khoảng {start_id} - {end_id}!")
                            continue
                        else:
                            print(f"Tìm thấy {count:,} movies trong khoảng {start_id} - {end_id}")
                    break
                except ValueError:
                    print("Vui lòng nhập số nguyên hợp lệ!")
        

        
        print(f"\n✓ Sẽ generate {len(site_ids)} titles cho mỗi phim")
        if start_id:
            print(f"✓ Bắt đầu từ Movie ID: {start_id}")
        else:
            print("✓ Bắt đầu từ movie đầu tiên")
        if end_id:
            print(f"✓ Kết thúc tại Movie ID: {end_id}")
        print(f"✓ Sử dụng site_ids: {site_ids}")
        
        # Xác nhận trước khi bắt đầu
        confirm = input("\nBạn có muốn tiếp tục? (y/n): ").lower().strip()
        if confirm != 'y':
            print("Hủy bỏ thao tác.")
            return
        
        # Bước 8: Xử lý movies
        processed, skipped, generated = process_movies(conn, site_ids, start_id, end_id)
        
        # Bước 9: Hiển thị kết quả
        print("\n" + "=" * 50)
        print("KẾT QUẢ XỬ LÝ")
        print("=" * 50)
        print(f"Tổng số movies đã xử lý: {processed:,}")
        print(f"Số movies đã bỏ qua (tất cả site_ids đã tồn tại): {skipped:,}")
        print(f"Tổng số titles đã generate: {generated:,}")
        print(f"Tổng số movies trong DB: {movie_count:,}")
        if start_id:
            print(f"Bắt đầu từ Movie ID: {start_id}")
        if end_id:
            print(f"Kết thúc tại Movie ID: {end_id}")
        print(f"Site_ids đã sử dụng: {site_ids}")
        print("✓ Hoàn thành!")
        
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print("\n✓ Đã đóng kết nối database")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nChương trình đã được dừng bởi người dùng.")
    except Exception as e:
        print(f"\nLỗi không mong muốn: {e}")
