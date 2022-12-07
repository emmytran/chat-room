import threading # needs threading so that the sequence of instructions that run independenly of the program and of any other threads
import socket
import signal
from time import sleep

server = input('ENTER SERVER IP:') # Client must input the correct server IP of the server
port = int(input('ENTER SERVER PORT:')) # Client must inpput the correct port number of the server
header = 64
address = (server, port)
# threading.Event() is a simple way to communicate between threads
# manages internal flag that callers can either set() or clear()
# example: CONNECT_SINGAL.set() is used for setting the thread 
#          CONNECT_SIGNAL.clear() is used for closing the thread
CONNECT_SIGNAL = threading.Event()

def main():
    global CONNECT_SIGNAL

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Build TCP socket (SOCK_STREAM) // AF_INET is the Internet address family for IPv4

    try:
        client.connect(address)
        CONNECT_SIGNAL.set()
    except:
        return print('\n[ERROR] Unable to connect to the server')

    # open textfile function
    f = open("welcome.txt", "r") 
    print(f.read())

    # Get user's name through their input
    username = input('YOUR NAME: ')
    print('\n')

    client.send(f'[WELCOME] {username} has entered the chatroom'.encode('utf-8')) # Welcome message when a client enters the chat room

    thread1 = threading.Thread(target=recv_msg, args=[client, username])
    thread1.daemon = True
#   thread1.setDaemon(True)
    thread1.start()

    thread2 = threading.Thread(target=send_msg,args=[client, username])
    thread2.daemon = True
    thread2.start()

    while CONNECT_SIGNAL.is_set():
        pass

    send_msg_client_exit(client, username)
    client.close()

# Function for receiver message
def recv_msg(client, username):
    global CONNECT_SIGNAL

    while CONNECT_SIGNAL.is_set():
        try:
            msg = client.recv(4096).decode('utf-8') # 4096 means the number of bytes you want to except, can be changed depending how you want
            
            if msg != '':
                print(f'\r{msg}\nYou: ', end='')

            else:
                print('\nYOU ARE DISCONNECTED')
                CONNECT_SIGNAL.clear()
        except:
            print('\nYOU ARE DISCONNECTED')
            CONNECT_SIGNAL.clear()

# Function to show the messages sent
def send_msg(client, username):
    global CONNECT_SIGNAL

    while CONNECT_SIGNAL.is_set():
        try:
            msg = input('You: ')
            client.send(f'{username}: {msg}'.encode('utf-8'))
        except:
            CONNECT_SIGNAL.clear()

# Function to alert when someone has left the chat
def send_msg_client_exit(client, username):
    client.send(f'\n[GOODBYE] {username} has left the chat\n'.encode('utf-8'))

# Function to close the connection
def close_connect(sigmun, frame):
    global CONNECT_SIGNAL
    CONNECT_SIGNAL.clear()


signal.signal(signal.SIGINT, close_connect)

main()
