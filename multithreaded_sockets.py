import socket
import threading
import time
import queue

from socket_implementation import TcpSocket


class WorkerThread(threading.Thread):
    """ Worker thread for managing TCP connections and multithreaded communication. """

    def __init__(self, port):
        super().__init__(daemon=False)
        self.command_queue = queue.Queue()
        self.running = True
        self.event_handler = threading.Event()
        self.connection_list = {}  # {(connection 1), (2), (etc)}
        self.threads_open = {}
        self.server_socket = TcpSocket()  # Initialize the TcpSocket object
        self.current_client = -1

        print("Starting worker thread and going back to CLI")
        self.event_handler.set()
        self._start_tcp_server(port)
        self.start()
        self.server_socket_thread.start()

    def _update_connections(self, action, 
                            ip_addr='0.0.0.0', port=5000, 
                            socket_object=None, connection_id=0, 
                            thread_obj=None):
        try:
            num_connections = max(self.connection_list.keys(), default=0)
        except ValueError:
            num_connections = 0
        
        if action == "push":
            self.connection_list[num_connections + 1] = [ip_addr, port, socket_object]
            self.threads_open[num_connections + 1] = thread_obj
            print(f"Added connection at {ip_addr}:{port}")
        elif action == "pop":
            if connection_id in self.connection_list:
                print(f"Terminating connection >> {connection_id}.")
                self._terminate_connection(connection_id)
                self.connection_list.pop(connection_id, None)
                self.event_handler.set()
                self._close_thread(connection_id)
            else:
                print(f"Connection id {connection_id} not found.")
            
        print(f"Updated connections. Number of connections: {len(self.connection_list)}")

    def _close_thread(self, connection_id):
        thread = self.threads_open[connection_id]
        print("Current thread:\n",thread,"\n")
        if thread:
            print("_close_thread")
            del self.threads_open[connection_id]
            print(f"Closed thread for connection {connection_id}.")
        self.event_handler.clear()

    def _get_client_socket(self, connection_id):
        return self.connection_list.get(connection_id, [None, None, None])[-1]

    def _terminate_connection(self, connection_id):
        values = self.connection_list[connection_id]
        ip = values[0]
        port = values[1]
        sock_obj = values[2]
        
        print('Terminating connection ', ip, ":",port)
        if sock_obj:
            print(f"Terminating connection {ip}:{port}")
            sock_obj.close()

    def _start_tcp_server(self, port):
        self.event_handler.clear()
        self.server_socket_thread = self.server_socket.start_server_thread(port)
        # self.myip = self.server_socket.getsockname()[0]
        self.myip = self.server_socket.get_myip()
        self.myport = port

        self._update_connections(
            "push",
            ip_addr=self.myip, 
            socket_object=self.server_socket,
            port=self.myport, 
            thread_obj=self.server_socket_thread
        )
    def _server_listening(self):
        self.event_handler.set()
        start_time = time.time()
        end_time = start_time + 1

        while time.time() < end_time:
               
            # Check if socket is open
            if self.server_socket.is_socket_open():
                try:
                    # Accept incoming connections
                    client_sock = self.server_socket.accept_incoming_connections()
                    dest_address = client_sock.getpeername()

                    # Update the connection details
                    self._update_connections("push", ip_addr=dest_address[0], port=dest_address[1], socket_object=client_sock)
                    
                except TimeoutError:
                    # Handle timeout error for socket accept
                    # print("Connection timed out while listening for incoming connections.")
                    break  # You might want to break or handle the retry logic here
                
            if len(self.threads_open) > 1:
                recv_start_time = time.time()
                while time.time() - recv_start_time < 1:
                    try:
                        for k, v in self.connection_list.items():
                            sock = v[2]
                            self.event_handler.set()
                            self.command_queue.put(sock.recv(1024))
                            self.event_handler.clear()    
                    except OSError:
                        pass
                        
                
    def server_listening(self):
        self.event_handler.set()
        start_time = time.time()
        end_time = start_time + 1

        while time.time() < end_time:
            message = self.server_socket.receive()
            if message:
                client_socket, received_message = message
                self.command_queue.put(received_message)
        self.event_handler.clear()
        
        if len(self.threads_open) > 1:
            recv_start_time = time.time()
            while time.time() - recv_start_time < 1:
                for thread in self.threads_open.values():
                    self.event_handler.set()
                    self.command_queue.put(thread.recv(1024))
                    self.event_handler.clear()
    def get_myip(self):
        return self.server_socket.get_myip()
    
    def get_myport(self):
        return self.myport
    
    def process_event(self, event):
        command, *args = event
        args = event[1:]
        self.set_event_handle()

        if command == "terminate":
            self._update_connections("pop", connection_id=int(args[0]))
        elif command == "send":
            self.send_message(int(args[0]), args[1])
        elif command == "connect":
            self._connect_to_client(args[0], int(args[1]))
        elif command == "exit":
            print("Closing all socket connections.")
            self.stop()
            self.event_handler.clear()
        else:
            print(f"Unsupported command: {command}")

    def _connect_to_client(self, ip, port):
        self.event_handler.clear()
        self.current_client = self.server_socket.client_connect(ip, port)
        client_thread = threading.Thread(target=self.read_message, args=(self.current_client,), daemon=False)
        client_thread.start()
        self._update_connections("push", ip_addr=ip, port=port, socket_object=self.current_client, thread_obj=client_thread)
        self.event_handler.set()

    def set_event_handle(self):
        if not self.event_handler.is_set():
            self.event_handler.set()

    def list_connections(self):
        print('id:\tIP Address\tPort No.')
        for k, v in self.connection_list.items():
            print(f"{k}\t{v[0]}\t{v[1]}")
        return self.connection_list

    def run(self):
        while self.running:
            try:
                event = self.command_queue.get(block=False, timeout=1)
                self.process_event(event)
            except queue.Empty:
                pass

    def send_message(self, id, message):
        try:
            client_sock = self.get_client(id)
            self.server_socket.send(client_sock, message.encode('utf-8'))  # Use TcpSocket.send method
            self.command_queue.put(message)
        except:
            print("Failed to get client socket")


    def read_message(self, sock):
        try:
            message = sock.recv(1024).decode()
            self.command_queue.put(message)
        except Exception as e:
            print(f"Failed to receive message: {e}")
            self.event_handler.clear()

    def stop(self):
        for conn_id in list(self.connection_list.keys()):
            self._update_connections("pop", connection_id=conn_id)
        self.running = False


if __name__ == "__main__":
    socket_manager = WorkerThread(port=5000)
    socket_manager.send_message(0, "Event 1")
    socket_manager.join()
