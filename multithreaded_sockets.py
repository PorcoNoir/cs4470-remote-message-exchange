
# from prettytable import PrettyTable
    
import socket
import threading
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

    def _update_connections(self, action, 
                            ip_addr='0.0.0.0', port=5000, socket_object=-1,
                            connection_id=0):
        try:
            num_connections = max(self.connection_list.keys())
        except:
            num_connections = 0
        
        if action == "push":
            self.connection_list[num_connections+1] = [ip_addr, port]
        elif action == "pop":
            try:
                self.connection_list.pop(connection_id)
                self._terminate_connection(self.connection_list[connection_id])
            except KeyError:
                print('Connection does not exist, please run >> list')
            
        print("updated connections ...")
            
    def _terminate_connection(self, connection_id):
        ip = connection_id[0]
        port = connection_id[1]
        try:
            num_connections = max(self.connection_list.keys())
        except:
            num_connections = 0
    
    def _start_tcp_server(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_thread = tcp_sockets.start_server(self.server_socket, port)
        self._update_connections("push",ip_addr=self.server_socket.getsockname()[0], port=port, socket_object=self.server_socket)
        #TODO: might be nice to replace this with our own TcpSocket wrapper that way we can add custom methods/properties
        
    def _process_event(self, event):
        # Process the event here
        if ("myip" in event):
            print("myip()")
        elif ("myport" in event):
            print("myport()")
        elif ("list" in event):
            print("list()")
        elif ("terminate" in event):
            print("terminate():")
            id = event[0]
            self._update_connections("push", connection_id=id)
        elif ("send" in event):
            print("Message received:", event)
        elif ("exit" in event):
            print("Closing all socket connections")
            self.stop()
        else:
            print("Not a supported command, please type help")

    def set_event_handle(self, command):
        if self.event_handler.is_set():
            pass
        else:
            self.event_handler.set()
            
        if "exit" in command:
            self.stop()
        #self._process_event
        
    # TODO: still have to see how to implement this.
    # def from_cli(self, event):
    #     """ function receives event from the cli, will execute the command 
    #     then gives back control to cli to continue to wait for user input
    #     """
    def list_connections(self):
        
        print('id:','IP Address','Port No.', sep="\t")
        for k,v in self.connection_list.items():
            print(k, v[0], v[1], sep="\t")
        #print("TBD: TEMPLATE FOR CONNECTIONS LIST")
        return        

    def add_connection(self, dest_address, port):
        # handles adding socket fd to a new thread
        #server_socket
        self.event_handler.clear()
        client_socket = tcp_sockets.connect(dest_address, port)
        self.event_handler.set()
        self._update_connections("push", ip_addr=dest_address, port=port, socket_object=client_socket)
        
        self.event_handler.clear()
        return 0

    def run(self):
        while self.running:
            try:
                event = self.command_queue.get(block=False, timeout=1)  # Wait for an event with a timeout
                self._process_event(event)
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