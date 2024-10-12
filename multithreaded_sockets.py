
# from prettytable import PrettyTable
    
import socket
import threading
import time
import queue

import socket_implementation as tcp_sockets


class WorkerThread(threading.Thread):
    """ Worker thread is a wrapper for Threads and handles the 
    thread pool of all connections in this application
    
    tailored to TCP communication
    """
    def __init__(self, port):
        super().__init__()
        self.command_queue = queue.Queue()
        self.running = True
        self.event_handler = threading.Event()
        self.connection_list = {}  # {(connection 1), (2), (etc)}
        self.server_socket = -1
                     
        # ready to start thread
        print("Starting worker thread and going back to CLI")
        
        self.event_handler.set()
        self._start_tcp_server(port)
        self.start()
        self.server_socket_thread.start()

    def _update_connections(self, action, 
                            ip_addr='0.0.0.0', port=5000, socket_object=-1,
                            connection_id=0):
        try:
            num_connections = max(self.connection_list.keys())
        except:
            num_connections = 0
        
        if action == "push":
            self.connection_list[num_connections + 1] = [ip_addr, port, socket_object]
            print(f"Adding connection at {ip_addr}:{port}")
        elif action == "pop":
            try:
                print("trying to terminate: ", connection_id)
                if connection_id in self.connection_list.keys():
                    self._terminate_connection(connection_id)
                    self.connection_list.pop(connection_id, None)
                else:
                    print('Connection id not found')
            except KeyError:
                print('Connection id does not exist, please run the command \'list\'')
            
        print("Updated connections ... num connections is now: ", len(self.connection_list.keys()))
            
    def _terminate_connection(self, connection_id):
        values = self.connection_list[connection_id]
        ip = values[0]
        port = values[1]
        sock_obj = values[2]
        
        print('Values to be deleted are: ', values)
        try:
            num_connections = max(self.connection_list.keys())
        except:
            num_connections = 0
        if sock_obj != -1:
            sock_obj.close()
    
    def _start_tcp_server(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_handler.clear()
        self.server_socket_thread = tcp_sockets.start_server(self.server_socket, port)
        #self.myip = self.server_socket.getsockname()[0]
        self.myip = '127.0.0.1'
        self.myport = port
        
        self._update_connections("push",ip_addr=self.myip, 
                                        socket_object=self.server_socket,
                                        port=self.myport)

        #TODO: might be nice to replace this with our own TcpSocket wrapper that way we can add custom methods/properties
    
    def server_listening(self):
        self.event_handler.set()
        start_time = time.time()
        end_time = start_time + 1

        while time.time() < end_time:
            # Check if socket is open
            if tcp_sockets.is_socket_open(self.server_socket):
                try:
                    # Accept incoming connections
                    client_sock = tcp_sockets.accept_incoming_connections(self.server_socket)
                    dest_address = client_sock.getpeername()

                    # Update the connection details
                    self._update_connections("push", ip_addr=dest_address[0], port=dest_address[1], socket_object=client_sock)
                except TimeoutError:
                    # Handle timeout error for socket accept
                    # print("Connection timed out while listening for incoming connections.")
                    break  # You might want to break or handle the retry logic here


    def get_myip(self):
        return self.myip
    
    def get_myport(self):
        return self.myport
    
    def process_event(self, event):
        self.set_event_handle()
        # Process the event here
        if ("terminate" in event):
            print("terminate():")
            id = event[1]
            self._update_connections("pop", connection_id=int(id))
        elif ("send" in event):
            print("Message received:", event)
        elif ("connect" in event):
            print(f"Attempting connection to {event[1]}:{event[2]}")
            self.add_connection(event[1], event[2])
            # add send and receive threads here
        elif ("exit" in event):
            print("Closing all socket connections")
            self.stop()
        else:
            print("Not a supported command, please type help")

    def set_event_handle(self):
        if self.event_handler.is_set():
            pass
        else:
            self.event_handler.set()
               
    def list_connections(self):
        
        print('id:','IP Address','Port No.', sep="\t")
        for k,v in self.connection_list.items():
            print(k, v[0], v[1], sep="\t")
        #print("TBD: TEMPLATE FOR CONNECTIONS LIST")
        return self.connection_list       

    def add_connection(self, dest_address, port):
        # handles adding socket fd to a new thread
        #server_socket
        print("port = ", port)
        client_socket = tcp_sockets.connect(dest_address, int(port))
        self.event_handler.set()
        self._update_connections("push", ip_addr=dest_address, port=port, socket_object=client_socket)
        
        self.event_handler.clear()
        return 0

    def run(self):
        while self.running:
            try:
                event = self.command_queue.get(block=False, timeout=1)  # Wait for an event with a timeout
                self.process_event(event)
            except queue.Empty:
                # self.command_queue.clear()
                pass  # No event received within the timeout

    def send_message(self, message):
        self.command_queue.put(message)

    def stop(self):
        # should send close request to all connections that are open
        self.running = False

if __name__ == "__main__":
    
    # start thread manager
    socket_manager = WorkerThread()

    socket_manager.send_message([0, "Event 1"])
    socket_manager.send_message("myip")
    socket_manager.send_message("myport")
    socket_manager.send_message("terminate")
    socket_manager.send_message("connect")
    socket_manager.send_message("list")
    socket_manager.send_message("exit")
    # Simulate sending events

    # Wait for worker to finish processing events
    socket_manager.join()