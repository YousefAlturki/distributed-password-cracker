import zmq

SERVER_IP = "192.168.1.3"
REQUEST_PORT = 5557  # Master listens for requests on this port

def request_crack(hash_to_crack):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # Create a REQ socket
    socket.connect(f"tcp://{SERVER_IP}:{REQUEST_PORT}")

    # Send the hash to crack
    print(f"Requesting crack for hash: {hash_to_crack}")
    socket.send_json({"hash": hash_to_crack})

    # Wait for the result
    response = socket.recv_json()
    if response.get("status") == "success":
        print(f"Password found: {response['password']}")
    else:
        print("No password found or the task failed.")

if __name__ == "__main__":
    hash_to_crack = input("Enter the hash (MD5) of string length 5 to crack: ")
    request_crack(hash_to_crack)
