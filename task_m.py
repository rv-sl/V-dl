# task_manager.py
import time, asyncio
import threading
from st import s
from autotask import runner
# Global task queue (FIFO)
task_run={
    "called":0,
    "started":0,
    "try":0
}
tasks = []

# Lock for thread-safe operations
task_lock = threading.Lock()
def task_st():
    return task_run

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

async def run_task(client, task: dict):
    """Placeholder for actual task processing logic."""
    print(f"Running task: {task}")
    # Simulate processing
    await runner(client, task)
    
    await asyncio.sleep(2)
    print(f"Task completed: {task}")

async def task_listener(client):
    """Main loop to listen and process tasks."""
    task_run["started"]=1
    print("Task listener started. Waiting for tasks...")
    while True:
        task_run["try"]+=1
        task = get_oldest_task()
        if task:
            s["run"] = 1
            await run_task(client, task)
            s["run"] = 0
            await asyncio.sleep(5)  # Sleep between tasks
        else:
            await asyncio.sleep(1)  # Idle wait

# Background listener (start this from start.py)
def start_listener(client):
    #listener_thread = threading.Thread(target=task_listener, daemon=True)
    #listener_thread.start()
    task_run["called"]=1
    def run_asyncio():
        task_run["called"]=2
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(task_listener(client))

    thread = threading.Thread(target=run_asyncio)
    thread.daemon = True  # Set the thread as a daemon thread
    thread.start()
    
