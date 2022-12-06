from itertools import product
from math import prod
import socket
import threading
import time

#SERVER VARIABLES
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

#CREATING SERVER 
#USES IPV4 and TCP CONNECTION
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

PRODUCTS = {
    'PAINTING' : 500.0,
    'SHOES': 100.0,
    'WATCH' : 300.0,
    'GEM' : 750.0,
    'GLASSES' : 250.0,
    'RING' : 350.0
}

clients = []
numberOfClients = 0
clientsAdded = 0
bidStart = False
bidWinners = []
productId = 0
currentBids = []


#Send message to all clients
def sendToAll(msg):
    for client in clients:
        time.sleep(1)
        client.send(msg.encode(FORMAT))

#UPDATES CURRENT BIDWINNERS AND CURRENTBIDS
def updateWinner(bidClient, bidAmount):
    if bidAmount > currentBids[productId]:
        bidWinners[productId] = bidClient
        currentBids[productId] = bidAmount
    return

#ENDS BIDDING
def endBid():
    global bidStart
    productId = 0
    bidStart = False
    time.sleep(5)
    print("_______END OF BID_______")
    for bidWinner in bidWinners:
        print(f"CLIENT {bidWinner} bought {list(PRODUCTS.keys())[productId]} for ${currentBids[productId]}")
        productId += 1
    sendToAll("END_BID")

def handle_client(conn, addr):
    #declaring global variables 
    global clientsAdded
    global clients
    global productId
    global bidStart
    

    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append(conn)
    clientId = clientsAdded
    clientsAdded += 1
    print(f"[CONNECTIONS] Client {clientId} connected")
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
                updateWinner(clientNum, bidAmount)
                print(f"Client {clientNum} bid {bidAmount} for {list(PRODUCTS.keys())[productId]}")
                sendToAll(f"BID {clientNum} {bidAmount}")
            if msgType == "NO_BID":
                clientNum = int(msgList[1])
                msgWhy = msgList[2]
                print(f"Client {clientNum} did not bid reason: {msgWhy}")
                sendToAll(f"NO_BID {clientNum} {msgWhy}")
            if msgType == "DISCONNECT":
                connected = False
    conn.close()
                

#STARTS THE SERVER
def start():
    global numberOfClients
    global bidWinners
    global bidStart
    global productId
    Timer = 7
    numberOfClients = 4
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    i = 0
    while i < len(PRODUCTS):
        bidWinners.append(-1)
        currentBids.append(list(PRODUCTS.values())[i])
        i = i + 1
    while numberOfClients > len(clients):
        print(f"Waiting for {numberOfClients - (threading.active_count() - 1)} more clients")
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        if((numberOfClients) == clientsAdded):
            print(f"ALL CLIENTS ARE CONNECTED...BIDS WILL START SOON")
            bidStart = True
            sendToAll(f"START_BID {productId} {numberOfClients}")
    while bidStart:
        if(Timer <= 0):
            if productId >= 5:
                endBid()
                return
            print(f"Client {bidWinners[productId]} won {list(PRODUCTS.keys())[productId]}")
            sendToAll(f"Client {bidWinners[productId]} won {list(PRODUCTS.keys())[productId]}")
            productId += 1
            Timer = 7
            sendToAll(f"START_BID {productId} {numberOfClients}")
        if(Timer <= 5):
            sendToAll(f"ANY_BIDS")
        Timer -= 1
        #print(Timer)
        time.sleep(1)

print("[STARTING] Server is booting up...")
start()