import queue
import shlex
import sys
import threading

from multithreaded_sockets import WorkerThread

def shell_loop(port, cli_event):
    
    # Start thread manager
    socket_manager = WorkerThread(port)
    cli_event.set()
    user_queue = queue.Queue() # using notification method to notify other threads
    print("Listening on port", port)       
    
    while True:
        # Read input from the user
        user_input = input(">> ")  # Prompt similar to a shell
        # Check if the user entered a command (non-empty)
        if user_input.strip():
            tokens = shlex.split(user_input)

            command = tokens[0]
            cli_event.set()
            # Call the appropriate function or dummy function based on the command
            # Command routing: decide what function to call based on the command
            if command == "help":
                # need the command in the expected argument
                dummy_help()
            elif command == "myip":
                print(socket_manager.get_myip())
            elif command == "myport":
                print(socket_manager.get_myport())
            elif command == "connect":
      
                destination = tokens[1]
                port = tokens[2]
                    
                cli_event.clear()
                socket_manager.process_event(tokens)
                
                # socket_manager.add_connection(destination, port)
            elif command == "list":
                socket_manager.list_connections()
            elif command == "terminate":
                # suggestion: insert pre processing on the arguments
                # argument 1 should be an int from connections list (is the value in range?)
                # if no argument is given then should show list of connections
                cli_event.clear()
                socket_manager.process_event(tokens)
                # print("Error: 'terminate' command requires <connection id>.")
            elif command == "send":
                # suggestion: insert pre processing on the arguments
                # conditions:
                # should be two arguments
                # argument 1 should be an int from connections list (is the value in range?)
                # argument 2 should be the message (pre processing for the message length)
                cli_event.clear()
                socket_manager.process_event(tokens)
                try:
                    socket_manager.send_message(connection_id, command)  # wrapper to route message to 
                except:
                    pass
            elif command == "exit":
                cli_event.clear()
                socket_manager.process_event(tokens)
                break  # Exit the loop to stop the shell
            else:
                # If the command isn't recognized, inform the user
                cli_event.clear()
                print("Unknown command: ", command)
        else:
            # logic for thread control to server listener
            return


## suggestion to remove the functions below unless you add logic to them. 
def dummy_help():
    print("Available commands: help\nmyip\nmyport\nconnect\nlist\nterminate\nsend\nexit\n")
    #TODO: please add descriptions for these summarizing their functionality and how the user should call them
def dummy_myip():
    print("Your IP address is 192.168.1.2 (dummy)")

def dummy_myport():
    print("Listening on port 4545 (dummy)")

def dummy_connect(destination, port_num):
    print("Connecting to ", destination," on port ", port_num)

def dummy_list():
    print("1: 192.168.1.3 5000 (dummy)\n2: 192.168.1.4 6000 (dummy)")

def dummy_terminate(connection_id):
    print("Terminating connection", connection_id)

def dummy_send(connection_id, message):
    print("Message sent to ", connection_id,": ", message)

def dummy_exit():
    print("Exiting and closing all connections (dummy)")

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        sys.exit(1)
    
    port = sys.argv[1]
    event = threading.Event()
    cli_thread = threading.Thread(target=shell_loop, args=(port, event))
    cli_thread.start()
