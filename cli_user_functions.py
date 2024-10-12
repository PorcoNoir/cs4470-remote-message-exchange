import queue
import select
import shlex
import sys
import threading

from multithreaded_sockets import WorkerThread

def shell_loop(port, cli_event):
    
    # Start thread manager
    #socket_manager = WorkerThread(port)
    cli_event.set()
    user_queue = queue.Queue() # using notification method to notify other threads
    print("Listening on port", port)       

    print(">> ", end='', flush=True)
    sys.stdout.flush()
    while True:
        # Read input from the user

        rlist, _, _ = select.select([sys.stdin], [], [], 0.5)  # 1-second timeout for input

        if rlist:
            user_input = sys.stdin.readline().strip()  # Read user input if available
        else:
            user_input = None
            
        # Check if the user entered a command (non-empty)
        # if user_input:
        if sys.stdin in rlist:
            tokens = shlex.split(user_input)

            command = tokens[0]
            # Call the appropriate function or dummy function based on the command
            # Command routing: decide what function to call based on the command
            if command == "help":
                # need the command in the expected argument
                help()
            elif command == "myip":
                print(socket_manager.get_myip())  
            elif command == "myport":
                print(socket_manager.get_myport())
            elif command == "connect":
                if len(tokens) < 3:
                    print("Error: 'connect' command requires <destination> <port>.")
                else:
                    destination = tokens[1]
                    port = tokens[2]
                    
                    cli_event.clear()
                    socket_manager.process_event(tokens)
                    socket_manager.add_connection(destination, port)
            elif command == "list":
                socket_manager.list_connections()
            elif command == "terminate":
                if len(tokens) < 2:
                    print("Error: 'terminate' command requires <connection id>. Use 'list' to see available connections.")
                else:
                    try:
                        connection_id = int(tokens[1])
                        if connection_id < 0 or connection_id >= len(socket_manager.list_connections):
                            print("Error: Connection id out of range.")
                            return
                        cli_event.clear()
                        socket_manager.process_event(tokens)
                        socket_manager.terminate_connection(connection_id)
                    except ValueError:
                        print("Error: Connection id must be an integer.")
            elif command == "send":
                if len(tokens) < 3:
                    print("Error: 'send' command requires <connection id> <message>.")
                else:
                    try:
                        connection_id = int(tokens[1])
                        message = " ".join(tokens[2:])

                        # Check if connection_id is in the valid range of connections
                        if connection_id < 1 or connection_id > len(socket_manager.list_connections):
                            print("Error: Connection id is out of range.")
                            return
                        #checks for the legnth of the message 
                        if len(message) < 1:
                            print("Error: Message is too short.")
                            return
                        elif len(message) > 256:
                            print("Error: Message is too long (max 256 characters).")
                            return

                        cli_event.clear()
                        socket_manager.process_event(tokens)
                        socket_manager.send_message(connection_id, message)
                    except ValueError:
                        print("Error: Connection id must be an integer.")
            elif command == "exit":
                cli_event.clear()
                #can also use command in .process_event(tokens) if handles are just the command
                socket_manager.process_event(tokens)
                break  # Exit the loop to stop the shell
            else:
                # If the command isn't recognized, inform the user
                cli_event.clear()
                print("Unknown command: ", command)
                
            sys.stdout.flush()
            print(">> ", end='', flush=True)
        else:
            # TODO: logic for thread control to server listener
            cli_event.clear()
            socket_manager.server_listening()
            cli_event.set()
            # timer for 5 seconds


## suggestion to remove the functions below unless you add logic to them. 
def help():
    text = """
OPTIONS:
help
   Display information about the available user interface options or command manual.

myip
   Display the IP address of this process.
   Note: The IP should not be your “Local” address (127.0.0.1). It should be the actual IP of the computer.

myport
   Display the port on which this process is listening for incoming connections.

connect <destination> <port no>
   This command establishes a new TCP connection to the specified <destination> at the specified <port no>.
   The <destination> is the IP address of the computer. Any attempt to connect to an invalid IP should be 
   rejected and a suitable error message should be displayed. Success or failure in connections between 
   two peers should be indicated by both the peers using suitable messages.
   Self-connections and duplicate connections should be flagged with suitable error messages.

list
   Display a numbered list of all the connections this process is part of. This list includes connections 
   initiated by this process and connections initiated by other processes. The output should display the 
   IP address and the listening port of all the peers the process is connected to.
   Example:
   id: IP address       Port No.
   1:  192.168.21.21    4545
   2:  192.168.21.22    5454
   3:  192.168.21.23    5000
   4:  192.168.21.24    5000

terminate <connection id>
   This command terminates the connection listed under the specified number when LIST is used to display 
   all connections. Example: terminate 2. In this example, the connection with 192.168.21.22 should end. 
   An error message is displayed if a valid connection does not exist as number 2. If a remote machine 
   terminates one of your connections, you should also display a message.

send <connection id> <message>
   (For example, send 3 "Oh! This project is a piece of cake"). This sends the message to the host on the 
   connection designated by the number 3 when the "list" command is used. The message can be up to 100 
   characters long, including spaces. After executing the command, the sender should display “Message 
   sent to <connection id>” on the screen. On receiving a message, the receiver should display the message 
   along with the sender's information.
   Example:
   Message received from 192.168.21.21
   Sender’s Port: <Port number of the sender>
   Message: “<received message>”

exit
   Close all connections and terminate this process. The other peers should also update their connection 
   list by removing the peer that exits.
    """
    print(text)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        sys.exit(1)
    
    port = sys.argv[1]
    global socket_manager
    socket_manager = WorkerThread(port)
    event = threading.Event()
    cli_thread = threading.Thread(target=shell_loop, args=(port, event))
    cli_thread.start()
