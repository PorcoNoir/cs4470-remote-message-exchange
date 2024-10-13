# CS 4470 - Chat Application With Socket Programming Assignment

import errno
import socket
import threading
import queue
from requests import get

# class TcpSocketHandler():
class TcpSocket(socket.socket):   # Question: should these data fields be private?
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None):  
        super().__init__(family, type, proto, fileno)
        self.MAX_CONNECTIONS = 5
        self.receive_message_queue = queue.Queue()  # Queue incoming messages for WorkerThread to handle.
        self.server_ip = self.get_myip()
        
        self.tcp_event = threading.Event()          # Take and give up event control with a TcpSocket object.

    # Start this machine's server thread.
    # server_socket is a socket object created prior to calling this function, and is passed as a parameter along with the port this machine's server is listening on.
    def start_server_thread(self, port):

        server_thread = threading.Thread(target=self._server_thread, args=(port,))
        return server_thread

   # Only accessed by start_server_thread function to start the server thread. 
    def _server_thread(self, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = server_socket.getsockname()
        host = server_address[0]
        
        print("Debug: Starting server thread on ", self.server_ip, "port", port)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((server_address[0], port))

        self.tcp_event.set()
        server_socket.listen(self.MAX_CONNECTIONS)
        print("Debug: Listening on port:", port)
        self.tcp_event.clear()

    def accept_incoming_connections(self):
        new_incoming_connection = False
        while not new_incoming_connection:
            #TODO: we need the client socket returned
            try:
                full_socket, client_address = self.accept()
                print("Debug: Full socket info:", full_socket)
                print("Debug: Client address (host, port):", client_address)
                #create_client_sock(full_socket, client_address)
                new_incoming_connection = True
                new_client_convo = threading.Thread(target=self._reception_thread, args=(full_socket,), daemon=False)
                new_client_convo.start()
            except Exception as e:
                print(f"Error accepting connections: {e}")
                break
            
            self.tcp_event.clear()
            return full_socket

    def get_myip(self):
        host = socket.gethostname()
        ip_address = socket.gethostbyname(host)
        return ip_address
        #print('My public IP address is: {}'.format(ip))


    # A thread is created on this function when a connection is received. 
    # This is where we receive messages from the client that connected.
    # Assumption:   Terminating a connection via WorkerThread will safely close the participating client socket.
    def _reception_thread(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    print("Client disconnected.")
                    break
                print(f"Received message: {message}")
                self.receive_message_queue.put([client_socket, message])
        except Exception as e:
            print(f"Error receiving message: {e}")
        finally:
            client_socket.close()

    # Call this function to get the next message in the queue.
    # Returns a list with two values of the form [client_socket, "message"]
    def receive(self):
        if not self.receive_message_queue.empty():
            return self.receive_message_queue.get()
        return None
        
    # Create a client socket on this machine to connect to another machine's server at its IP address (destination) and on its listening port.
    def client_connect(self, destination, port_no):
        # if destination and/or port no not found, give the user a message
        # else, do the deed
        
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Debug: connecting", destination, ":", port_no)

        try:
            print("connecting...")
            print('ip:port = ',destination,":",port_no)
            client_socket.connect((destination, port_no))
            #print(client_socket.recv(1024))

        except ConnectionRefusedError as cre:
            print("ConnectionRefusedError. Make sure you are entering available destinations and/or port numbers.")
        except TimeoutError as te:
            print("TimeoutError. Make sure you are entering available destinations and/or port numbers.")
            
        return client_socket

    # This machine's client wants to message another machine's server, who should have an open _reception_thread if this client is connected.
    # Assumption:   Client socket is stored and can be located with a connection id entered as an integer by user.
    # Assumption:   Checking if the user is trying to send to a valid connection is done prior to calling this function.

    def send(self, client_socket, message):
        try:
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
            
    def is_socket_open(self):
        """Checks if a socket is open."""
        try:
            server_address = self.getsockname()
            self.settimeout(1)  # Set a timeout for the connection attempt
            self.connect((server_address[0], server_address[1]))
            return True
        except OSError as e:
            if e.errno == errno.EISCONN:
                return True
        except (socket.timeout, ConnectionRefusedError):
            return False


# Question: Have seen examples use .encode() and .decode() for recv and send. Should our implementation use this?
