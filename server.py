from itertools import product
from math import prod
import socket
import threading
import time

# Server Variables
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#Crating server (using IPV4 and TCP connection)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

PRODUCTS = {
   'CAR' : 2000.0,
    'PHONE': 600.0,
    'NECKLACE' : 250.0,
    'CLOTHES' : 120.0,
    'HOUSEWARE' : 350.0,
    'EARPHONE' : 50.0
}

clients = [] # Client array initially is empty
numClients = 0 # The number of clients is initially 0
clientJoined = 0 # The number of clients joined is initialy 0
bidBegin = False 
bidWinners = [] # The bid winner is initally empty
productId = 0 # The product ID is initially 0
currentBids = [] # The current bid is initally empty


# Function to send message to all clients
def sendAll(msg):
    for client in clients:
        time.sleep(1)
        client.send(msg.encode(FORMAT))

# Function to update current bid winner and the current bid
def winnerUpdate(bidClient, bidAmount):
    if bidAmount > currentBids[productId]:
        bidWinners[productId] = bidClient
        currentBids[productId] = bidAmount
    return

# Function to end bid
def endBid():
    global bidBegin
    productId = 0
    bidBegin = False
    time.sleep(5)
    print("_______RESULT_______")
    for bidWinners in bidWinners:
        print(f"CLIENT {bidWinners} bought {list(PRODUCTS.keys())[productId]} for ${currentBids[productId]}")
        productId += 1
    sendAll("END_BID")

# Function to handle clients
def clientHandle(conn, addr):
    # global variables declaration
    global clientJoined
    global clients
    global productId
    global bidBegin
    

    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append(conn)
    clientId = clientJoined
    clientJoined += 1
    print(f"[CONNECTIONS] Client {clientId} has been connected")
    conn.send(f"CONNECTED {clientId}".encode(FORMAT))
    time.sleep(1)
    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            msgList = msg.split()
            msgType = msgList[0]
            if msgType == "BID":
                clientNum = int(msgList[1])
                bidAmount = float(msgList[2])
                winnerUpdate(clientNum, bidAmount)
                print(f"Client {clientNum} bid {bidAmount} for {list(PRODUCTS.keys())[productId]}")
                sendAll(f"BID {clientNum} {bidAmount}")
            if msgType == "NO_BID":
                clientNum = int(msgList[1])
                msgWhy = msgList[2]
                print(f"Client {clientNum} reason for not bidding: {msgWhy}")
                sendAll(f"NO_BID {clientNum} {msgWhy}")
            if msgType == "DISCONNECT":
                connected = False
    conn.close()
                

# Function to start the server
def start():
    global numClients
    global bidWinners
    global bidBegin
    global productId
    Timer = 7
    numClients = 4
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    i = 0
    while i < len(PRODUCTS):
        bidWinners.append(-1)
        currentBids.append(list(PRODUCTS.values())[i])
        i = i + 1
    while numClients > len(clients):
        print(f"Waiting for {numClients - (threading.active_count() - 1)} more clients")
        conn, addr = server.accept()
        thread = threading.Thread(target=clientHandle, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        if((numClients) == clientJoined):
            print(f"ALL CLIENTS HAVE BEEN SUCCESSFULLY CONNECTED! BIDDING SESSION WILL START SOON")
            bidBegin = True
            sendAll(f"START_BID {productId} {numClients}")
    while bidBegin:
        if(Timer <= 0):
            if productId >= 5:
                endBid()
                return
            print(f"Client {bidWinners[productId]} won {list(PRODUCTS.keys())[productId]}")
            sendAll(f"Client {bidWinners[productId]} won {list(PRODUCTS.keys())[productId]}")
            productId += 1
            Timer = 7
            sendAll(f"START_BID {productId} {numClients}")
        if(Timer <= 5):
            sendAll(f"ANY_BIDS")
        Timer -= 1
        #print(Timer)
        time.sleep(1)

print("........Server is booting up.........")
start()