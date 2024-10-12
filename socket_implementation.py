# CS 4470 - Chat Application With Socket Programming Assignment

import errno
import socket
import sys
import threading
import time

total_connections = 0
list_of_sockets = {"IP": -1} # format {ip_addr: port_no} 
# will come back to this, have to change this or configure it properly

# for now, client socket is actually created in connect function
def create_client_sock(full_socket, client_address):
    global total_connections                                        # come back to this
    total_connections += 1                                          # come back to this
    list_of_sockets[client_address[0]] = client_address[1]          # come back to this
    print('Got connection from', client_address)
    
    full_socket.send(b'Thank you for connecting')
    full_socket.close()

# server_thread function -------------------------------------------------
def server_thread(name, server_sock, port):
    server_address = server_sock.getsockname()
    host = server_address[0]
    
    print("Debug: Starting", name)
    print(host,":",port)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))

    print("Debug: Listening on port:", port)
    server_sock.settimeout(1)
    tcp_event = threading.Event()
    tcp_event.set()
    server_sock.listen(5)
    tcp_event.clear()
        #print("Debug: Finishing", name)
    # listen on the port, call function to create client socket when a machine connects

def is_socket_open(s):
    """Checks if a socket is open."""
    try:
        server_address = s.getsockname()
        s.settimeout(1)  # Set a timeout for the connection attempt
        s.connect((server_address[0], server_address[1]))
        return True
    except OSError as e:
        if e.errno == errno.EISCONN:
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def accept_incoming_connections(server_sock):
    new_incoming_connection = False
    while not new_incoming_connection:
        #TODO: we need the client socket returned
        full_socket, client_address = server_sock.accept()
        print("Debug: Full socket info:", full_socket)
        print("Debug: Client address (host, port):", client_address)
        #create_client_sock(full_socket, client_address)
        new_incoming_connection = True
        
        # for x, y in list_of_sockets.items():
        #     print(x, ":", y)

        print("Debug: Bottom of server_thread while loop.")
        return full_socket

# Functions to handle user input commands.

def command_not_recognized():
    print("Command not recognized. Type 'help' to view available user options.")

def help():
    print("Debug: here are all the things you can do")

def my_ip(ip_address):
    print("This machine IP is:", ip_address)

def my_port(port):
    print("Debug: This machine listening port is:", port)

def display_connections_list():
    print("Debug: here are all current connections")

def exit_app():
    print("Debug: all connections and process will terminate")

def terminate_connection(connection_id):
    # if connection id not found in list, give the user a message
    # else, do the deed
    print("Debug: terminating this connection:", connection_id)

def connect(destination, port_no):
    # if destination and/or port no not found, give the user a message
    # else, do the deed
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Debug: connecting", destination, ":", port_no)

    try:
        print("connecting...")
        client_socket.connect((destination, port_no))
        #print(client_socket.recv(1024))

    except ConnectionRefusedError as cre:
        print("ConnectionRefusedError. Make sure you are entering available destinations and/or port numbers.")
    except TimeoutError as te:
        print("TimeoutError. Make sure you are entering available destinations and/or port numbers.")
        
    return client_socket

def send_message(connection_id, message):
    # if connection id not in list, give the user a message
    # if message is over 100 characters, cut it down to 100 and give both users a message it was cut off
    # else, do the deed
    print("Debug: sending message to", connection_id)

# Infinite loop to take user commands until user exits.
def launch_user_input_loop():
    print("Welcome to CS 4470 chat application demo. Type 'help' to view available user options.")

    exit = False
    while exit == False:

        # Taking input from the user; commands are either 1, 2, or 3 values.
        next = input().split(" ", 2)

        # If the command is a single value (i.e. help, myip, myport, list, exit).
        if len(next) == 1:
            match next[0]:
                case "help":
                    help()
                case "myip":
                    my_ip(ip_address)
                case "myport":
                    my_port(port)
                case "list":
                    display_connections_list()
                case "exit":
                    exit_app()
                    exit = True
                case _:
                    command_not_recognized()

        # If the command is two values (i.e. terminate <connection id>).
        elif len(next) == 2:
            match next[0]:
                case "terminate":
                    try:
                        int(next[1]) # cast str to int for use in function
                        terminate_connection(next[1])
                    except ValueError as ve: # if str cannot be cast, then the command isn't recognized
                        command_not_recognized()
                case _:
                    command_not_recognized()

        # If the command is three values (i.e. connect <destination> <port no>, send <connection id> <message>).
        elif len(next) == 3:
            match next[0]:
                case "connect":
                    try:
                        # int(next[2])   <- There was an error where this wasn't working. FIXED: casting to int in the connect function instead of here.
                        connect(next[1], next[2]) # Note: next[1] (the destination IP) is a str
                    except ValueError as ve:
                        command_not_recognized()
                case "send":
                    try:
                        int(next[1]) # Note: this may cause errors like in connect above, check back here if so, and same for terminate above
                        send_message(next[1], next[2]) 
                    except ValueError as ve:
                        command_not_recognized()
                case _:
                    command_not_recognized()
        # If the command is over three values.
        else:
            command_not_recognized()

        print("Debug: Bottom of input loop.")


# Main thread start ----------------------------------------------------------------
def start_server(server_sock, port):

    # Start the thread that this machine's server listens on.
    port = int(port)
    tcp_server = threading.Thread(target=server_thread, args=("server thread", server_sock, port))
    return tcp_server
    
    # Give control back to CLI

    # Start accepting user input with loop.
    #launch_user_input_loop()
    