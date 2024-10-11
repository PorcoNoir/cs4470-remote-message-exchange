# CS 4470 - Chat Application With Socket Programming Assignment

import socket
import threading
import queue


class TcpSocket(socket.socket()):   # Question: should these data fields be private?
    def __init__(self):
        self.MAX_CONNECTIONS = 5
        self.receive_message_queue = queue.Queue()  # Queue incoming messages for WorkerThread to handle.
        self.tcp_event = threading.Event()          # Take and give up event control with a TcpSocket object.

    # Start this machine's server thread.
    # server_socket is a socket object created prior to calling this function, and is passed as a parameter along with the port this machine's server is listening on.
    def start_server_thread(self, server_socket, port):

        tcp_server = threading.Thread(target=self._server_thread, args=(server_socket, port))
        return tcp_server

   # Only accessed by start_server_thread function to start the server thread. 
    def _server_thread(self, server_socket, port):
        server_address = server_socket.getsockname()
        host = server_address[0]
        
        print("Debug: Starting server thread.")

        server_socket.bind((host, port))

        self.tcp_event.set()
        server_socket.listen(self.MAX_CONNECTIONS)
        print("Debug: Listening on port:", port)
        self.tcp_event.clear()

        # Listen on the port. 
        # When connection received from another machine's client: call 'handle_client_sock' function to handle incoming messages. 
        while True:
            client_socket, client_address = server_socket.accept()

            print("Debug: Full socket info:", client_socket)
            print("Debug: Client address (host, port):", client_address)
            
            new_client_convo = threading.Thread(target=self._reception_thread, args=(client_socket))
            new_client_convo.start()

            print("Debug: Bottom of server_thread while loop.")


    # A thread is created on this function when a connection is received. 
    # This is where we receive messages from the client that connected.
    # Assumption:   Terminating a connection via WorkerThread will safely close the participating client socket.
    def _reception_thread(self, client_socket):

        while True:
            message = client_socket.recv(1024)                          # Question: more so a concern - hoping this stores properly. 
            self.receive_message_queue.put([client_socket, message])        # -- Might require string conversion? And length validation here?

    # Call this function to get the next message in the queue.
    # Returns a list with two values of the form [client_socket, "message"]
    def receive(self):
        if self.receive_message_queue.not_empty:
            return self.receive_message_queue.get()
        else:
            return None

    # This machine's client wants to message another machine's server, who should have an open _reception_thread if this client is connected.
    # Assumption:   Client socket is stored and can be located with a connection id entered as an integer by user.
    def send(self, client_socket, message):
        client_socket.send(message)


# Question: Have seen examples use .encode() and .decode() for recv and send. Should our implementation use this?
