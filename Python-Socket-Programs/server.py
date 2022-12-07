import threading
import signal
import socket
import sys

server = socket.gethostbyname(socket.gethostname())
port = 4222
address = (server, port)
clients = []
ONLINE = threading.Event()

def main():
    global ONLINE
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Build TCP socket
    server.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )	# Reuse the port after unexpected close
    try:
        server.bind(address) # bind the socket and adress
        server.listen() # wait client
        ONLINE.set()    # add main server in socket list

        print(f'\nServer Connected!\nPORT NUMBER: {port}\n')
        print(f"SERVER INFO: {server}")
    except:
        return print(f'\nFAILED TO START ON PORT NUMBER: {port}\n\n')

    while True:
        client, addr = server.accept() # get the client's address and create communication socket
        print(f'Entered chat: {addr}')  
        clients.append(client)  # add this socket into socket list

        thr = threading.Thread(target=recv_msg, args=[client])
        thr.daemon = True
        thr.start()

    while ONLINE.is_set():
        pass

def recv_msg(client):
    while True:
        try:
            msg = client.recv(2048) # if the event is from the client, get the message
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

def remove_client(client):
    if client in clients:
        clients.remove(client)

def close_server(signum, frame):
    global ONLINE

    ONLINE.clear()
    print('\rCLOSING SERVER ...')
    exit(0)

signal.signal(signal.SIGINT, close_server)

main()
