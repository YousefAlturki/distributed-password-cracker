import zmq
import math
import itertools
def distribute_tasks(hash_to_crack, keyspace, client_socket):
    context = zmq.Context()

    # Sockets for task distribution
    task_socket = context.socket(zmq.PUSH)
    task_socket.bind("tcp://*:5555")

    feedback_socket = context.socket(zmq.PULL)
    feedback_socket.bind("tcp://*:5556")

    registration_socket = context.socket(zmq.PULL)
    registration_socket.bind("tcp://*:5558")

    print(f"Hash to crack: {hash_to_crack}")
    print(f"Keyspace: {keyspace}")

    connected_workers = 0
    workers = []

    print("Waiting for workers to connect...")
    while True:
        try:
            registration_socket.setsockopt(zmq.RCVTIMEO, 2000)  # Timeout after 2 seconds
            message = registration_socket.recv_json()
            if message.get("status") == "ready":
                connected_workers += 1
                workers.append(message.get("worker_id", f"Worker-{connected_workers}"))
                print(f"{message.get('worker_id', f'Worker-{connected_workers}')} connected! Total workers: {connected_workers}")
        except zmq.Again:
            break

    if connected_workers == 0:
        print("No workers connected. Exiting.")
        client_socket.send_json({"status": "failure"})
        return

    # Generate combinations and distribute
    max_length = 5
    all_combinations = []
    for length in range(1, max_length + 1):
        all_combinations.extend([''.join(p) for p in itertools.product(keyspace, repeat=length)])

    total_combinations = len(all_combinations)
    chunk_size = math.ceil(total_combinations / connected_workers)
    tasks = []
    for i in range(connected_workers):
        start = i * chunk_size
        end = min(start + chunk_size, total_combinations)
        tasks.append({
            'hash': hash_to_crack,
            'keyspace_combinations': all_combinations[start:end]
        })

    for task in tasks:
        task_socket.send_json(task)

    # Wait for feedback
    while True:
        feedback = feedback_socket.recv_json()
        print(f"Worker feedback: {feedback}")
        if feedback.get("status") == "success":
            print(f"Password found: {feedback['password']}")
            client_socket.send_json({"status": "success", "password": feedback['password']})
            for _ in range(connected_workers):
                task_socket.send_json({"terminate": True})
            return



def main():
    context = zmq.Context()

    # Client communication socket (REQ/REP)
    client_socket = context.socket(zmq.REP)
    client_socket.bind("tcp://*:5557")

    print("Waiting for hash from client...")
    while True:
        # Receive request from the client
        request = client_socket.recv_json()
        hash_to_crack = request['hash']
        keyspace = "abcdefghijklmnopqrstuvwxyz"

        # Distribute tasks and wait for the result
        distribute_tasks(hash_to_crack, keyspace, client_socket)



if __name__ == "__main__":
    main()
