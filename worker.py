import socket
import threading
import time
import sys
from utils import *

HOST = '127.0.0.1'
PORT = 5000

worker_id = sys.argv[1]

if worker_id == "1":
    algorithm = "FCFS"
elif worker_id == "2":
    algorithm = "SJF"
elif worker_id == "3":
    algorithm = "RR"
else:
    algorithm = "FCFS"

task_queue = []
lock = threading.Lock()


def schedule_task():
    global task_queue

    while True:
        time.sleep(1)

        with lock:
            if not task_queue:
                continue

            # 🔥 SJF SORTING HAPPENS HERE
            if algorithm == "SJF":
                task_queue.sort()

            task = task_queue.pop(0)

        if algorithm == "RR":
            execution_time = min(task, 2)
            print(f"[⚙] Worker {worker_id} executing {execution_time}s of task {task}s")
            
            steps = execution_time * 10
            for i in range(1, steps + 1):
                time.sleep(0.1)
                percent = int((i / steps) * 100)
                client.send(f"{PROGRESS} {percent}\n".encode())

            remaining_task = task - execution_time
            
            with lock:
                if remaining_task > 0:
                    task_queue.append(remaining_task)
                    queue_str = ",".join(map(str, task_queue))
                    client.send(f"{UPDATE_QUEUE} {queue_str}\n".encode())
                else:
                    queue_str = ",".join(map(str, task_queue))
                    client.send(f"{DONE} {queue_str}\n".encode())
        else:
            print(f"[⚙] Worker {worker_id} executing {task}s")
            
            steps = task * 10
            for i in range(1, steps + 1):
                time.sleep(0.1)
                percent = int((i / steps) * 100)
                client.send(f"{PROGRESS} {percent}\n".encode())

            # 🔥 SEND DONE + CURRENT QUEUE STATE
            with lock:
                queue_str = ",".join(map(str, task_queue))

            client.send(f"{DONE} {queue_str}\n".encode())


def receive_tasks():
    buffer = ""
    while True:
        try:
            msg = client.recv(1024).decode()
            if not msg:
                break
            
            buffer += msg
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                parts = line.split()
                if not parts:
                    continue

                if parts[0] == TASK:
                    task_time = int(parts[1])

                    with lock:
                        task_queue.append(task_time)

                    print(f"[+] Worker {worker_id} received {task_time}s")
        except:
            break

def send_heartbeat():
    while True:
        time.sleep(2)
        try:
            client.send(f"{HEARTBEAT}\n".encode())
        except:
            break


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

client.send(f"{REGISTER} {worker_id} {algorithm}\n".encode())

threading.Thread(target=receive_tasks, daemon=True).start()
threading.Thread(target=schedule_task, daemon=True).start()
threading.Thread(target=send_heartbeat, daemon=True).start()

while True:
    time.sleep(1)