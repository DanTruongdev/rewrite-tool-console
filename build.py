import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Kiểm tra và cài đặt requirements"""
    print("📦 Kiểm tra và cài đặt dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Đã cài đặt tất cả dependencies")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt dependencies: {e}")
        return False
    return True

def install_pyinstaller():
    """Cài đặt PyInstaller"""
    print("🔧 Cài đặt PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ Đã cài đặt PyInstaller")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt PyInstaller: {e}")
        return False
    return True

def download_model():
    """Download model nếu chưa có local"""
    print("🤖 Kiểm tra model...")
    model_dir = Path("./model")
    if not model_dir.exists():
        print("Model chưa có local, sẽ sử dụng online model trong build...")
    else:
        print("✅ Model local đã tồn tại")
    return True

def build_exe():
    """Build ứng dụng thành file .exe"""
    print("🏗️  Bắt đầu build ứng dụng...")
    
    # Tạo folder dist nếu chưa có
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Các arguments cho PyInstaller
    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Tạo 1 file exe duy nhất
        "--console",  # Hiển thị console
        "--name", "gentitle",  # Tên file exe
        "--add-data", "db_config.json;." if os.path.exists("db_config.json") else "",  # Thêm config nếu có
        "--hidden-import", "transformers",
        "--hidden-import", "torch",
        "--hidden-import", "psycopg2",
        "--hidden-import", "sentencepiece",
        "--collect-all", "transformers",
        "--collect-all", "torch",
        "--collect-all", "tokenizers",
        "--collect-all", "huggingface_hub",
        "main.py"
    ]
    
    # Loại bỏ empty strings
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    try:
        subprocess.check_call(pyinstaller_args)
        print("✅ Build thành công!")
        
        # Kiểm tra file exe
        exe_path = Path("dist/gentitle.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📁 File exe: {exe_path}")
            print(f"📏 Kích thước: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Không tìm thấy file exe sau khi build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi build: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 GENTITLE - BUILD SCRIPT")
    print("=" * 60)
    
    # Kiểm tra Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ Cần Python 3.7 trở lên")
        return
    
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Các bước build
    steps = [
        ("Cài đặt dependencies", check_requirements),
        ("Cài đặt PyInstaller", install_pyinstaller),
        ("Kiểm tra model", download_model),
        ("Build executable", build_exe)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Bước '{step_name}' thất bại!")
            return
    
    print("\n" + "=" * 60)
    print("🎉 BUILD HOÀN THÀNH!")
    print("=" * 60)
    print("📁 File exe được tạo tại: dist/gentitle.exe")
    print("💡 Lưu ý:")
    print("   - Lần chạy đầu tiên có thể chậm do download model")
    print("   - Đảm bảo máy có kết nối internet để download model")
    print("   - File exe đã bao gồm tất cả dependencies cần thiết")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Build bị hủy bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")