import shlex

def shell_loop():
    while True:
        # Read input from the user
        user_input = input("chat: ")  # Prompt similar to a shell
        # Check if the user entered a command (non-empty)
        if user_input.strip():
            tokens = shlex.split(user_input)

            command = tokens[0]
            # Call the appropriate function or dummy function based on the command
            # Command routing: decide what function to call based on the command
            if command == "help":
                dummy_help()
            elif command == "myip":
                dummy_myip()  
            elif command == "myport":
                dummy_myport()
            elif command == "connect":
                print("Error: 'connect' command requires <destination> <port no>.")
            elif command == "list":
                dummy_list()
            elif command == "terminate":
                print("Error: 'terminate' command requires <connection id>.")
            elif command == "send":
                print("Error: 'send' command requires <connection id> <message>.")
            elif command == "exit":
                dummy_exit() 
                break  # Exit the loop to stop the shell
            else:
                # If the command isn't recognized, inform the user
                print("Unknown command: ", command)

def dummy_help():
    print("Available commands: help, myip, myport, connect, list, terminate, send, exit")

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
    shell_loop()
