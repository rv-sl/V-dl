# task_manager.py
import time
import threading
from st import s

# Global task queue (FIFO)
tasks = []

# Lock for thread-safe operations
task_lock = threading.Lock()

def all_tasks():
    return tasks
    
def add_task(task: dict):
    """Add a single task to the list."""
    with task_lock:
        tasks.append(task)
        print(f"Task added: {task}")

def add_task_list(task_list: list):
    """Add multiple tasks to the list."""
    with task_lock:
        tasks.extend(task_list)
        print(f"{len(task_list)} tasks added.")

def get_oldest_task():
    """Return and remove the oldest task (FIFO)."""
    with task_lock:
        if tasks and s.get("run") == 0:
            return tasks.pop(0)
        return None

def run_task(task: dict):
    """Placeholder for actual task processing logic."""
    print(f"Running task: {task}")
    # Simulate processing
    time.sleep(2)
    print(f"Task completed: {task}")

def task_listener():
    """Main loop to listen and process tasks."""
    print("Task listener started. Waiting for tasks...")
    while True:
        task = get_oldest_task()
        if task:
            s["run"] = 1
            run_task(task)
            s["run"] = 0
            time.sleep(5)  # Sleep between tasks
        else:
            time.sleep(1)  # Idle wait

# Background listener (start this from start.py)
def start_listener():
    listener_thread = threading.Thread(target=task_listener, daemon=True)
    listener_thread.start()
