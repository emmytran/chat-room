# CSCI-156 Project
# Group 11: Thuy Tran, Harry Patel, Ananshy Bhatt, Maria Guimaraes

import threading # needs threading so that the sequence of instructions that run independenly of the program and of any other threads
import signal
import socket
import sys

server = socket.gethostbyname(socket.gethostname()) # gethostname() accepts hostname arguments and returns the IP address in a string format
port = 4222 # Port number, can be changed (non-priviledged port are greater than 1023)
address = (server, port)
clients = []
ONLINE = threading.Event()

def main():
    global ONLINE

    # socket.socket() creates a socket object that supprts the context manager type
    # Build TCP socket (SOCK_STREAM) 
    # AF_INET is the Internet address family for IPv4
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SOL_SOCKET is a socket layer, used for options that are protocol independent
    # SOL_REUSEADDR allows a socket to forcibly bind to a port in use by another socket
    server.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )	
    try:
        server.bind(address) # bind the socket with the address
        server.listen() # wait client, listen() enables a server to accecpt connection
        ONLINE.set()    # add main server in socket list

        print(f'\n[CONNECTED] Server Connected!')
        print(f'\nPORT NUMBER: {port}')
        print(f"\nSERVER INFO: {server}")
    except:
        return print(f'\nFAILED TO START ON PORT NUMBER: {port}\n\n')

    while True:
        client, addr = server.accept() # get the client's address and create communication socket
        print(f'Entered chat: {addr}')  
        clients.append(client)  # add this socket into socket list

        thr = threading.Thread(target=recv_msg, args=[client])
        thr.daemon = True
        thr.start()

    # is_set() returns true if the internal flag of an event object is true, else return false
    while ONLINE.is_set():
        pass

def recv_msg(client):
    while True:
        try:
            msg = client.recv(4096) # if the event is from the client, get the message
            broadcast(msg, client) # boardcast the message
        except:
            client.send(''.encode('utf-8'))
            remove_client(client)
            break

# This function is used to send message to all socket connected by client
def broadcast(msg, client):
    for user in clients:
        if not user == client:
            try:
                #send
                user.send(msg)
            except:
                remove_client(user)

# Function to remove the client when the client is disconnected
def remove_client(client):
    if client in clients:
        clients.remove(client)

# Function to close the server
def close_server(signum, frame):
    global ONLINE

    ONLINE.clear()
    print('\rCLOSING SERVER ...')
    exit(0)

signal.signal(signal.SIGINT, close_server)

main()
