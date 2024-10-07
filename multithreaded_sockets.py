# import socket programming library

import argparse
import getopt
import socket
import sys

# import thread module
#from _thread import *
import _thread
import threading

# Communication and threading
lock_print = threading.Lock()
DATA_SIZE = 100
CONNECTION_IDS = {}

# Arguments List
ARGUMENT_LIST = sys.argv[1:]
OPTS = "hmo:"
LONG_OPTIONS = ["Help", "My_File", "Output="]

MSG = "Adding description"

try:
    # Parsing args
    args, vals = getopt.getopt(ARGUMENT_LIST, OPTS, LONG_OPTIONS)

    for currentArg, currentValue in args:

        if currentArg in ("-h", "--Help"):
            print("Help")
        elif currentArg in ("-m", "--My_File"):
            print("Displaying file_name: ", sys.argv[0])
        elif currentArg in ("-o", "--Output"):
            print ("Enabling special output mode ", currentValue)

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))

# thread function
def start_thread(c):
    """ application to fork new sockets and handle connections

    Args:
        c (socket object): socket object to send and receive messages.
    """
    while True:

        # data received from client
        data = c.recv(DATA_SIZE)
        if not data:
            print('Bye')

            # lock released on exit
            lock_print.release()
            break

        # reverse the given string from client
        data = data[::-1]

        # send back reversed string to client
        c.send(data)

    # connection closed
    c.close()


def ConnectServer(dest_ip, port):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((dest_ip, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:

        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        lock_print.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(start_thread, (c,))
    s.close()


if __name__ == '__main__':
    DEST_IP = "0.0.0.0"
    DEST_IP = "192.168.0.10"
    DEST_IP = "127.0.0.1"
    PORT = 4545
    ConnectServer(DEST_IP, PORT)
