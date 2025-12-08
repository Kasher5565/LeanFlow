# run.py - исправленная версия
import subprocess
import time
import sys
import threading
import webbrowser

def run_backend():
    """Запуск FastAPI бэкенда"""
    print("🚀 Запуск FastAPI бэкенда...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Вывод логов бэкенда в реальном времени
    def print_output(pipe, label):
        for line in iter(pipe.readline, ''):
            if line:
                print(f"[{label}] {line.strip()}")
    
    threading.Thread(target=print_output, args=(backend_process.stdout, "BACKEND"), daemon=True).start()
    threading.Thread(target=print_output, args=(backend_process.stderr, "BACKEND-ERROR"), daemon=True).start()
    
    return backend_process

def check_backend_ready():
    """Проверяем, готов ли бэкенд"""
    import requests
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=1)
            if response.status_code == 200:
                print("✅ Бэкенд готов!")
                return True
        except:
            print(f"⏳ Ожидание бэкенда... ({i+1}/{max_attempts})")
            time.sleep(1)
    return False

def run_frontend():
    """Запуск Tkinter фронтенда"""
    print("🎨 Запуск Tkinter интерфейса...")
    frontend_process = subprocess.Popen([sys.executable, "welcom_page.py"])
    return frontend_process

def main():
    print("=" * 50)
    print("🚀 LeanFlow - Запуск приложения")
    print("=" * 50)
    
    # Запускаем бэкенд
    backend = run_backend()
    
    # Ждем, пока бэкенд запустится
    print("\n⏳ Ожидание запуска бэкенда...")
    if not check_backend_ready():
        print("❌ Не удалось запустить бэкенд!")
        backend.terminate()
        return
    
    print("\n✅ Бэкенд успешно запущен на http://localhost:8000")
    print("📚 Документация API: http://localhost:8000/docs")
    
    # Открываем документацию в браузере
    try:
        webbrowser.open("http://localhost:8000/docs")
    except:
        pass
    
    # Запускаем фронтенд
    frontend = run_frontend()
    
    print("\n" + "=" * 50)
    print("✅ Приложение запущено!")
    print("   - Бэкенд: http://localhost:8000")
    print("   - Документация: http://localhost:8000/docs")
    print("   - Интерфейс: Tkinter окно")
    print("=" * 50)
    
    try:
        # Ждем завершения фронтенда
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал прерывания...")
    finally:
        print("🛑 Остановка бэкенда...")
        backend.terminate()
        backend.wait()
        print("✅ Приложение остановлено.")

if __name__ == "__main__":
    main()