

# The goal of this is to use client/server architecture, with the added twist that the server can in turn create its own
# workers, over TCP to send data and execute workloads on such nodes.
# The model should be Client <-> SchedulingServer <-> 1 to many SchedulableWorker for each requesting Client


import socket
import threading
import json

class Client:
    # The Client can submit workloads to a Scheduling Server to execute operations and parallelize.
    def __init__(self, server_address):
        self.server_address = server_address

    def submit_workload(self, workload):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.server_address)
            sock.sendall(json.dumps(workload).encode('utf-8'))
            response = sock.recv(4096)
            return json.loads(response.decode('utf-8'))

class SchedulingServer:
    # The SchedulingServer can receive workloads from a Client and executes operations in parallel using SchedulableWorkers.
    def __init__(self, address):
        self.address = address
        self.workers = []
        self.lock = threading.Lock()

    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(self.address)
        server_sock.listen()

        print(f"Scheduling Server started on {self.address}")

        while True:
            client_sock, client_address = server_sock.accept()
            threading.Thread(target=self.handle_client, args=(client_sock,)).start()

    def handle_client(self, client_sock):
        with client_sock:
            workload = json.loads(client_sock.recv(4096).decode('utf-8'))
            result = self.execute_workload(workload)
            client_sock.sendall(json.dumps(result).encode('utf-8'))

    def execute_workload(self, workload):
        with self.lock:
            worker = self.get_available_worker()
            if worker:
                return worker.execute_task(workload)
            else:
                return {"error": "No available workers"}

    def get_available_worker(self):
        for worker in self.workers:
            if worker.is_available():
                return worker
        return None

    def register_worker(self, worker):
        with self.lock:
            self.workers.append(worker)

class SchedulableWorker:
    # The SchedulableWorker can execute some task and return its results to the server.
    # Could be co-located on the scheduling server, or on the client, etc, for performance tradeoffs.

    def __init__(self, address, server):
        self.address = address
        self.server = server
        self.server.register_worker(self)
        self.available = True

    def execute_task(self, task):
        self.available = False
        result = self.perform_task(task)
        self.available = True
        return result

    def perform_task(self, task):
        # Perform the actual task and return the result
        return {"result": "task completed"}

    def is_available(self):
        return self.available


