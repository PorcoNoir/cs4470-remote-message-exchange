# Google AI example of how to have server listen on one thread while main thread is still running.

import socket
import threading

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print("Received:", data.decode())

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5000))
    server_socket.listen(5)

    while True:
        client_socket, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Main thread can do other things
    while True:
        print("Main thread doing something...")
        input("chat: ")