# CS 4470 - Chat Application With Socket Programming Assignment

import socket
import threading
import queue

# class TcpSocketHandler():
class TcpSocket(socket.socket):   # Question: should these data fields be private?
    def __init__(self):
        self.MAX_CONNECTIONS = 5
        self.receive_message_queue = queue.Queue()  # Queue incoming messages for WorkerThread to handle.
        self.tcp_event = threading.Event()          # Take and give up event control with a TcpSocket object.

    # Start this machine's server thread.
    # server_socket is a socket object created prior to calling this function, and is passed as a parameter along with the port this machine's server is listening on.
    def start_server_thread(self, server_socket, port):

        server_thread = threading.Thread(target=self._server_thread, args=(server_socket, port))
        return server_thread

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
        # When connection received from another machine's client: call '_reception_thread' function to handle incoming messages. 
        while True:
            client_socket, client_address = server_socket.accept()

            print("Debug: Full socket info:", client_socket)
            print("Debug: Client address (host, port):", client_address)
            
            new_client_conversation = threading.Thread(target=self._reception_thread, args=(client_socket))
            new_client_conversation.start()

            print("Debug: Bottom of server_thread while loop.")


    # A thread is created on this function when a connection is received. 
    # This is where we receive messages from the client that connected.
    # Assumption:   Terminating a connection via WorkerThread will safely close the participating client socket.
    def _reception_thread(self, client_socket):

        while True:
            # Received as byte.
            message = client_socket.recv(1024)              # Question: more so a concern - hoping this stores properly.
            # .decode() to convert to a string. 
            message = message.decode('utf-8')
            # Limit message to 100 characters.
            if len(message) > 100:
                message = message[0:100]
            # Queue the message in a list along with the client_socket that sends messages to this thread.
            self.receive_message_queue.put([client_socket, message])

    # Call this function to get the next message in the queue.
    # Returns a list with two values of the form [client_socket, "message"]
    def receive(self):
        if self.receive_message_queue.not_empty:
            return self.receive_message_queue.get()
        else:
            return None
        
    # Create a client socket on this machine to connect to another machine's server at its IP address (destination) and on its listening port.
    def connect(self, destination, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        port_no = int(port_no)

        print("Debug: connecting", destination, "on port", port_no)

        # Try to connect client socket to the other machine's server. If successful, return the client socket.
        try:
            client_socket.connect((destination, port_no))
            # print(client_socket.recv(1024))
            
            return client_socket

        except ConnectionRefusedError as cre:
            print("Connection was refused. Make sure you are entering available destinations and/or port numbers.")
        except TimeoutError as te:
            print("Connection was refused. Make sure you are entering available destinations and/or port numbers.")
            
        # If connection is unsuccessful, close and return None.
        client_socket.close()
        return None 

    # This machine's client wants to message another machine's server, who should have an open _reception_thread if this client is connected.
    # Assumption:   Client socket is stored and can be located with a connection id entered as an integer by user.
    # Assumption:   Checking if the user is trying to send to a valid connection is done prior to calling this function.
    def send(self, client_socket, message):
        client_socket.send(message)


# Question: Have seen examples use .encode() and .decode() for recv and send. Should our implementation use this?
