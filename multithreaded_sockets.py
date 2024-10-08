import threading
import queue

class WorkerThread(threading.Thread):
    """ Worker thread is a wrapper for Threads and handles the 
    thread pool of all connections in this application
    
    tailored to TCP communication
    """
    def __init__(self, port='4545', ip='0.0.0.0'):
        super().__init__()
        self.event_queue = queue.Queue() 
        self.running = True
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start()  

    def add_connection(self, sockfd):
        # handles adding socket fd to a new thread
        #server_socket
        return 0

    def run(self):
        while self.running:
            try:
                event = self.event_queue.get_nowait()  # Wait for an event with a timeout
                self._event_message_rx(event)
            except queue.Empty:
                self.event_queue.clear()
                pass  # No event received within the timeout

    def send_message(self, message):
        self.event_queue.put(message)

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

    def stop(self):
        # should send close request to all connections that are open
        self.running = False

if __name__ == "__main__":
    
    # start thread manager
    socket_manager = WorkerThread()

    socket_manager.send_message("Event 1")
    socket_manager.send_message("Event 2")
    # Simulate sending events

    # Wait for worker to finish processing events
    socket_manager.join()
    socket_manager.stop()