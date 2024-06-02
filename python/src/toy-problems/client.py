import socket
from protos.generated import workload_pb2


class Client:
    def __init__(self, server_address):
        self.server_address = server_address

    def submit_workload(self, task, data):
        # Create a WorkloadRequest message
        request = workload_pb2.WorkloadRequest(task=task, data=data)

        # Serialize the message to a byte string
        serialized_request = request.SerializeToString()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.server_address)
            sock.sendall(serialized_request)

            # Receive the response
            response_data = sock.recv(4096)

            # Deserialize the response message
            response = workload_pb2.WorkloadResponse()
            response.ParseFromString(response_data)

            return response


# Example usage
client = Client(('localhost', 8005))
response = client.submit_workload("example task", "example data")

if response.error:
    print(f"Error: {response.error}")
else:
    print(f"Result: {response.result}")