import socket
import threading
import time
from utils import *
from state import system_state

HOST = '127.0.0.1'
PORT = 5000

workers = {}
worker_load = {}
task_queue = [8, 3, 1, 6, 2, 9, 4, 7, 5, 2, 6, 3, 8, 1]

lock = threading.Lock()


def handle_worker(conn, addr):
    worker_id = None
    buffer = ""

    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            
            buffer += msg
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                parts = line.split()
                if not parts:
                    continue

                if parts[0] == REGISTER:
                    worker_id = parts[1]
                    algorithm = parts[2]

                    with lock:
                        workers[worker_id] = {
                            "conn": conn,
                            "algorithm": algorithm,
                            "last_seen": time.time(),
                            "status": "FREE"
                        }

                        worker_load[worker_id] = 0

                        system_state["workers"][worker_id] = {
                            "algorithm": algorithm,
                            "status": "FREE",
                            "load": 0,
                            "queue": [],
                            "logs": []
                        }

                    print(f"[+] Worker {worker_id} registered ({algorithm})")

                elif parts[0] == DONE:
                    queue_data = parts[1] if len(parts) > 1 else ""

                    with lock:
                        worker_load[worker_id] -= 1
                        workers[worker_id]["status"] = "FREE"

                        system_state["workers"][worker_id]["load"] -= 1
                        system_state["workers"][worker_id]["status"] = "FREE"
                        system_state["workers"][worker_id]["progress"] = 0

                        # 🔥 UPDATE LOCAL QUEUE FROM WORKER
                        if queue_data:
                            system_state["workers"][worker_id]["queue"] = list(map(int, queue_data.split(",")))
                        else:
                            system_state["workers"][worker_id]["queue"] = []

                    print(f"[✓] Worker {worker_id} completed task")

                elif parts[0] == UPDATE_QUEUE:
                    queue_data = parts[1] if len(parts) > 1 else ""
                    
                    with lock:
                        system_state["workers"][worker_id]["progress"] = 0
                        if queue_data:
                            system_state["workers"][worker_id]["queue"] = list(map(int, queue_data.split(",")))
                        else:
                            system_state["workers"][worker_id]["queue"] = []

                elif parts[0] == PROGRESS:
                    percent = int(parts[1])
                    with lock:
                        system_state["workers"][worker_id]["progress"] = percent

                elif parts[0] == HEARTBEAT:
                    with lock:
                        workers[worker_id]["last_seen"] = time.time()

        except:
            break

    print(f"[!] Worker {worker_id} disconnected")


def scheduler_loop():
    global task_queue

    while True:
        time.sleep(1)

        with lock:
            system_state["task_queue"] = list(task_queue)

            if not task_queue or not workers:
                continue

            alive_workers = {
                k: v for k, v in workers.items() if v["status"] != "DEAD"
            }

            if not alive_workers:
                continue

            worker_id = min(alive_workers, key=lambda w: worker_load[w])

            if worker_load[worker_id] >= 2:
                continue

            task = task_queue.pop(0)

            conn = workers[worker_id]["conn"]
            conn.send(f"{TASK} {task}\n".encode())

            worker_load[worker_id] += 1
            workers[worker_id]["status"] = "BUSY"

            system_state["workers"][worker_id]["load"] += 1
            system_state["workers"][worker_id]["status"] = "BUSY"

            # 🔥 ADD TASK TO GUI QUEUE VIEW
            system_state["workers"][worker_id]["queue"].append(task)

            print(f"[→] Assigned {task}s → Worker {worker_id}")


def heartbeat_monitor():
    while True:
        time.sleep(3)

        with lock:
            for wid, data in workers.items():
                if time.time() - data["last_seen"] > 5:
                    data["status"] = "DEAD"


def capture_logs(process, worker_id):
    for line in iter(process.stdout.readline, ''):
        if not line:
            break
        striped_line = line.strip()
        if striped_line:
            with lock:
                if worker_id in system_state["workers"]:
                    if "logs" not in system_state["workers"][worker_id]:
                        system_state["workers"][worker_id]["logs"] = []
                    system_state["workers"][worker_id]["logs"].append(striped_line)
                    if len(system_state["workers"][worker_id]["logs"]) > 50:
                        system_state["workers"][worker_id]["logs"].pop(0)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("[*] Scheduler running...")

    threading.Thread(target=scheduler_loop, daemon=True).start()
    threading.Thread(target=heartbeat_monitor, daemon=True).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_worker, args=(conn, addr)).start()


if __name__ == "__main__":
    import subprocess
    import sys
    
    # Start the scheduler server
    threading.Thread(target=start_server, daemon=True).start()

    # Give the server a moment to bind to the port
    time.sleep(1)

    # Spawn the 3 workers in the background
    p1 = subprocess.Popen([sys.executable, "-X", "utf8", "-u", "worker.py", "1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    p2 = subprocess.Popen([sys.executable, "-X", "utf8", "-u", "worker.py", "2"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    p3 = subprocess.Popen([sys.executable, "-X", "utf8", "-u", "worker.py", "3"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")

    threading.Thread(target=capture_logs, args=(p1, "1"), daemon=True).start()
    threading.Thread(target=capture_logs, args=(p2, "2"), daemon=True).start()
    threading.Thread(target=capture_logs, args=(p3, "3"), daemon=True).start()

    # Start the GUI dashboard
    import gui