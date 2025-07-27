# start.py
import subprocess
import threading
from task_manager import start_listener

def start_flask():
    subprocess.call(["gunicorn", "--bind", "0.0.0.0:8000", "app:app"])

def start_bot():
    subprocess.call(["python3", "bot.py"])

if __name__ == "__main__":
    # Start task listener
    start_listener()

    # Start Flask and bot in parallel threads
    t1 = threading.Thread(target=start_flask)
    t2 = threading.Thread(target=start_bot)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
