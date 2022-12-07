import threading
import socket
import signal
from time import sleep

server = input('What is the server IP:')
port = int(input('What is the server PORT:'))
header = 64
address = (server, port)
CONNECT_SIGNAL = threading.Event()

def main():
    global CONNECT_SIGNAL

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(address)
        CONNECT_SIGNAL.set()
    except:
        return print('\nUnable to connect to the server')

    print(f'\n---------WELCOME TO INIFINITE CHAT--------\n')
    username = input('Enter your name: ')
    print('\n')

    client.send(f'[WELCOME] {username} has entered the chatroom'.encode('utf-8'))

    thread1 = threading.Thread(target=recv_msg, args=[client, username])
    thread1.daemon = True
#    thread1.setDaemon(True)
    thread1.start()

    thread2 = threading.Thread(target=send_msg,args=[client, username])
    thread2.daemon = True
    thread2.start()

    while CONNECT_SIGNAL.is_set():
        pass

    send_msg_client_exit(client, username)
    client.close()

def recv_msg(client, username):
    global CONNECT_SIGNAL

    while CONNECT_SIGNAL.is_set():
        try:
            msg = client.recv(2048).decode('utf-8')
            
            if msg != '!BYE':
                print(f'\r{msg}\nYou: ', end='')

            else:
                CONNECT_SIGNAL.clear()
        except:
            print('\nDISCONNECTED')
            CONNECT_SIGNAL.clear()

def send_msg(client, username):
    global CONNECT_SIGNAL

    while CONNECT_SIGNAL.is_set():
        try:
            msg = input('You: ')
            client.send(f'{username}: {msg}'.encode('utf-8'))
        except:
            CONNECT_SIGNAL.clear()

def send_msg_client_exit(client, username):
    client.send(f'\n[GOODBYE] {username} has left the chat\n'.encode('utf-8'))

def close_connect(sigmun, frame):
    global CONNECT_SIGNAL
    CONNECT_SIGNAL.clear()


signal.signal(signal.SIGINT, close_connect)

main()
