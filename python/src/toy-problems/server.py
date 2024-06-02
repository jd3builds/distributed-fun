import os
import socket
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import threading
from protos.generated import workload_pb2



class SchedulingServer:
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
            data = client_sock.recv(4096)
            request = workload_pb2.WorkloadRequest()
            request.ParseFromString(data)

            result = self.execute_workload(request)

            response = workload_pb2.WorkloadResponse(result=result)
            serialized_response = response.SerializeToString()

            client_sock.sendall(serialized_response)

    def execute_workload(self, request):
        with self.lock:
            worker = self.get_available_worker()
            if worker:
                return worker.execute_task(request)
            else:
                return "No available workers"

    def get_available_worker(self):
        for worker in self.workers:
            if worker.is_available():
                return worker
        return None

    def register_worker(self, worker):
        with self.lock:
            self.workers.append(worker)

class SchedulableWorker:
    def __init__(self, address, server):
        self.address = address
        self.server = server
        self.server.register_worker(self)
        self.available = True

    def execute_task(self, request):
        self.available = False
        result = self.perform_task(request)
        self.available = True
        return result

    def perform_task(self, request):
        # Perform the actual task and return the result
        return f"Task '{request.task}' completed with data '{request.data}'"

    def is_available(self):
        return self.available

# Example usage
if __name__ == "__main__":
    server = SchedulingServer(('localhost', 8000))
    threading.Thread(target=server.start).start()

    worker = SchedulableWorker(('localhost', 8001), server)
