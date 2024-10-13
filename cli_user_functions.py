import queue
import select
import shlex
import sys
import threading
import msvcrt  # Windows-specific library for keyboard input

from multithreaded_sockets import WorkerThread
# from multithreaded_sockets import WorkerThread

def shell_loop(port, cli_event):
    """
    Command line shell loop for processing user input and executing socket commands.
    """
    #print(f"Listening on port {port}")
    print(">> ", end='', flush=True)
    socket_manager.event_handler.set()
    running = socket_manager.is_alive()
    user_input = ""
    
    while running:
        # Listen for user input with a timeout of 0.5 seconds
        try:
            # rlist, _, _ = select.select([sys.stdin], [], [], 0.5)
            
            # # user_input = input("chat: ")  # Prompt similar to a shell

            # if rlist:
            # # if user_input.strip():
            #     user_input = sys.stdin.readline().strip()
            if msvcrt.kbhit():  # Non-blocking check
                char = msvcrt.getch()  # Get the pressed key
                
                tokens = None
                if char in (b'\r', b'\n'):  # Enter key pressed
                    if user_input.strip():  # Check if there's input
                        tokens = shlex.split(user_input.strip())  # Tokenize input 
                        print()#dont know if this was the thing that was asked when asked to fix the token
                    user_input = ""  # Reset user input after processing
                    print(">> ", end='', flush=True)  # Print prompt again
                elif char == b'\x08':  # Backspace key pressed
                    #
                    #
                    #to erase mistakes
                    #able to see the user input and can delete/rewite mistakes
                    if user_input: # Ensure there's something to delete
                        user_input = user_input[:-1]  # Remove last character
                        print('\b \b', end='', flush=True) #Erase the last character from console
                else:
                    user_input += char.decode()  # Append character to user input
                    #
                    #
                    #to see what are the inputs
                    print(char.decode(), end='', flush=True)  # Display the character

                    #tokens = shlex.split(user_input) if user_input else None
                if tokens:
                    command = tokens[0].lower()

                    # Process commands
                    if command == "help":
                        help()
                    elif command == "myip":
                        print(socket_manager.get_myip())
                    elif command == "myport":
                        print(socket_manager.get_myport())
                    elif command == "connect":
                        if len(tokens) != 3:
                            print("Error: 'connect' command requires <destination> <port>.")
                        else:
                            destination = tokens[1]
                            port = tokens[2]
                            cli_event.clear()
                            print(f"Connecting to {destination}:{port}")
                            socket_manager.process_event(tokens)
                    elif command == "list":
                        socket_manager.list_connections()
                    elif command == "terminate":
                        if len(tokens) != 2:
                            print("Error: 'terminate' command requires <connection id>.")
                        else:
                            try:
                                connection_id = int(tokens[1])
                                print(f"Terminating connection {connection_id}")
                                socket_manager.process_event(tokens)
                            except ValueError:
                                print("Error: Connection id must be an integer.")
                    elif command == "send":
                        if len(tokens) < 3:
                            print("Error: 'send' command requires <connection id> <message>.")
                        else:
                            try:
                                connection_id = int(tokens[1])
                                message = ' '.join(tokens[2:])#allows user ot send full messages
                                socket_manager.process_event(tokens)
                                socket_manager.send_message(connection_id, message)
                            except ValueError:
                                print("Error: Connection id must be an integer.")
                    elif command == "exit":
                        socket_manager.process_event(tokens)
                        socket_manager.join()
                        cli_event.clear()
                        break  # Exit loop
                    else:
                        print(f"Unknown command: {command}")

                    # Prompt for next command
                    print(">> ", end='', flush=True)
                else:
                    pass
            else:
                # Optional: Handle other processing or a sleep to avoid busy waiting
                #pass  # Remove or replace with sleep if needed
                # Check server for incoming messages
                cli_event.clear()
                socket_manager._server_listening()
                cli_event.set()
        except OSError as e:
            pass
    return 0

def help():
    """
    Display help information for available commands.
    """
    text = """
OPTIONS:
help
   Display information about the available user interface options or command manual.

myip
   Display the IP address of this process.

myport
   Display the port on which this process is listening for incoming connections.

connect <destination> <port no>
   Establish a new TCP connection to the specified <destination> at the specified <port no>.

list
   Display a numbered list of all the connections this process is part of.

terminate <connection id>
   Terminate the connection listed under the specified id.

send <connection id> <message>
   Send a message to the specified connection id.

exit
   Close all connections and terminate the process.
    """
    print(text)


if __name__ == "__main__":
    # Check for the port argument
    if len(sys.argv) < 2:
        print("Error: Port number required.")
        sys.exit(1)

    p = int(sys.argv[1])  # Get port from command line arguments
    print("port = ", p)
    # Create WorkerThread and event for managing CLI and server interaction
    global socket_manager
    socket_manager = WorkerThread(p)
    cli_event = threading.Event()

    # Start the CLI shell in a separate thread
    cli_thread = threading.Thread(target=shell_loop, args=(p, cli_event), daemon=False)
    cli_thread.start()
