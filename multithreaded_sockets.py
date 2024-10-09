import socket
import threading
import queue


class WorkerThread(threading.Thread):
    """ Worker thread is a wrapper for Threads and handles the 
    thread pool of all connections in this application
    
    tailored to TCP communication
    """
    def __init__(self, port='4545', ip='0.0.0.0'):
        super().__init__()
        self.command_queue = queue.Queue()
        self.running = True
        self.event_hander = threading.Event()
        self.connection_list = {}
        
        #TODO: might be nice to replace this with our own TcpSocket wrapper that way we can add custom methods/properties
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        
        # ready to start thread
        print("Starting worker thread and going back to cli")
        self.start()
        self.event_hander.set()  

    def set_event_handle():
        if self.event_handler.is_set():
            pass
        else:
            self.event_handler.set()
        
    # TODO: still have to see how to implement this.
    # def from_cli(self, event):
    #     """ function receives event from the cli, will execute the command 
    #     then gives back control to cli to continue to wait for user input
    #     """
    def list_connections(self):
        print("TBD: TEMPLATE FOR CONNECTIONS LIST")
        return        

    def _add_connection(self, dest_address, port):
        connect(dest_address, port)  # from socket_implementation code

    def add_connection(self, sockfd):
        # handles adding socket fd to a new thread
        #server_socket
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

    def _process_event(self, event):
        # Process the event here
        if ("myip" in event):
            print("myip()")
        elif ("myport" in event):
            print("myport()")
        elif ("connect" in event):
            # event[0] should be "connect"
            try:
                destination_address = event[1]
                port = event[2]
                self._add_connection(destination_address, port)
            except:
                print("connect()")
        elif ("list" in event):
            print("list()")
            for val in self.connection_list:
                print(val)
        elif ("terminate" in event):
            print("terminate()")
        elif ("send" in event):
            print("Message received:", event)
        elif ("exit" in event):
            print("Closing all socket connections")
            self.stop()
        else:
            print("Not a supported command, please type help")

## TCP Socket methods 
    def _event_message_rx(self, event):
        # Process the event here
        print("Message received:", event)

    def _event_message_tx(self, event):
        # Process the event here
        print("Sending message:", event)

    def _event_socket_open(self, event, sockfd):
        # Process the event here
        print("Opening connection:", event)

    def _event_socket_close(self, event, sockfd):
        # Process the event here
        print("Closing connection:", event)
        
    def _terminate_connection(self, connection_id):
        # function to terminate connection_id socket
        return 0

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