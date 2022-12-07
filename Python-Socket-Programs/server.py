import threading
import signal
import socket
import sys

server = socket.gethostbyname(socket.gethostname())
port = 5050
address = (server, port)
clients = []
ONLINE = threading.Event()

def main():
    global ONLINE
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(address)
        server.listen()
        ONLINE.set()

        print(f'\nServer Connected!\nPORT NUMBER: {port}\n')
        print(f"SERVER INFO: {server}")
    except:
        return print(f'\nFAILED TO START ON PORT NUMBER: {port}\n\n')

    while True:
        client, addr = server.accept()
        print(f'Entered chat: {addr}')
        clients.append(client)

        thr = threading.Thread(target=recv_msg, args=[client])
        thr.daemon = True
        thr.start()

    while ONLINE.is_set():
        pass

def recv_msg(client):
    while True:
        try:
            msg = client.recv(2048)
            broadcast(msg, client)
        except:
            client.send('!BYE'.encode('utf-8'))
            remove_client(client)
            break

def broadcast(msg, client):
    for user in clients:
        if not user == client:
            try:
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
