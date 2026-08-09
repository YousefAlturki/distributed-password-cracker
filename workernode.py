import zmq
import hashlib
import socket

SERVER_IP = "192.168.1.3"
TASK_PORT = 5555
FEEDBACK_PORT = 5556
REGISTRATION_PORT = 5558

def crack_password(task):
    hash_to_crack = task['hash']
    keyspace_combinations = task['keyspace_combinations']

    for password in keyspace_combinations:
        test_hash = hashlib.md5(password.encode()).hexdigest()
        if test_hash == hash_to_crack:
            return password
    return None

def worker():
    worker_id = socket.gethostname()  # Use the hostname as the worker's ID
    context = zmq.Context()

    # Socket to receive tasks
    task_socket = context.socket(zmq.PULL)
    task_socket.connect(f"tcp://{SERVER_IP}:{TASK_PORT}")

    # Socket to send feedback
    feedback_socket = context.socket(zmq.PUSH)
    feedback_socket.connect(f"tcp://{SERVER_IP}:{FEEDBACK_PORT}")

    # Socket to notify master node of readiness
    registration_socket = context.socket(zmq.PUSH)
    registration_socket.connect(f"tcp://{SERVER_IP}:{REGISTRATION_PORT}")
    registration_socket.send_json({"status": "ready", "worker_id": worker_id})

    print(f"Worker {worker_id} connected and ready.")

    while True:
        task = task_socket.recv_json()
        if "terminate" in task:
            print(f"Worker {worker_id} received termination signal. Shutting down.")
            break

        result = crack_password(task)
        if result:
            feedback_socket.send_json({"status": "success", "password": result, "worker_id": worker_id})
        else:
            feedback_socket.send_json({"status": "failure", "worker_id": worker_id})

if __name__ == "__main__":
    worker()
