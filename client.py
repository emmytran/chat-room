from math import prod
import socket
import random
import time

HEADER = 64
PORT = 5050
SERVER = "192.168.1.188" # Change if server is running on different computer. The IP address of the server can be found after running 'py server.py' on the terminal
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'


PRODUCTS = {
   'CAR' : 2000.0,
    'PHONE': 600.0,
    'NECKLACE' : 250.0,
    'CLOTHES' : 120.0,
    'HOUSEWARE' : 350.0,
    'EARPHONE' : 50.0
}

# Client to Server connection 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


# Client variables
clientId = -1
numClients = 0
productId = 0
lastBidder = -1
clientHighestPrices = []
currentBids = []
bidWinners = []


# Function to update data
def winnerUpdate(bidClient, bidAmount):
    bidWinners[productId] = bidClient
    currentBids[productId] = bidAmount

# Helper function to display the winners on client side
def winnersDisplay():
    productId = 0
    print("_______RESULT_______")
    for bidWinners in bidWinners:
        print(f"CLIENT {bidWinners} bought {list(PRODUCTS.keys())[productId]} for ${currentBids[productId]}")
        productId += 1

# Function to check if client is up to bid, which helps so that clients are bombarding server with messages
def canBid():
    if(lastBidder + 1) % numClients == clientId:
        return True
    return False

def choice():
    toBid = random.choice([True,False])
    return toBid

# Function to send message to the server
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

# Function to initialize arrays bidWinners and currentBids, and also the client profile for each client
def helperVar():
    global bidWinners
    global clientHighestPrices
    file = f"client{clientId}.txt"
    i = 0
    while i < len(PRODUCTS):
        bidWinners.append(-1)
        currentBids.append(list(PRODUCTS.values())[i])
        i += 1
    with open (file) as f:
        for value in f:
            clientHighestPrices.append(float(value))
    print(f"You are {file}")

# Function to decide whether the client has bid for an item
def makeBid():
    print(f"Bidding for: {list(PRODUCTS.keys())[productId]}")
    print({currentBids[productId]})
    if bidWinners[productId] == clientId:
        why = "CURRENTLY_THE_HIGHEST_BIDDER"
        print(f"<NO BID> YOU ARE CURRENTLY THE HIGHEST BIDDER")
        send(f"NO_BID {clientId} {why}")
        return

    currentBid =  currentBids[productId]
    bidAmount = currentBid + random.randint(25,75)

    if bidAmount < clientHighestPrices[productId]:
        print(f"<BID> YOU BID FOR {list(PRODUCTS.keys())[productId]} for {bidAmount}")
        send(f"BID {clientId} {bidAmount}")
    else:
        why = "PRICE_IS_TOO_HIGH"
        print(f"<NO BID> PRICE IS TOO HIGH")
        send(f"NO_BID {clientId} {why}")
        return

# Function to handle the message to the server
def serverHandle():
    global clientId
    global numClients
    global productId
    global lastBidder

    while True:
        msg = client.recv(HEADER).decode(FORMAT)
        if len(msg):
            msgList = msg.split()
            msgType = msgList[0] 
            if msgType == "CONNECTED":  # When the client is connected give it a id and run helperVar() to initialize bidWinners[] and currentBids[]
                clientId = int(msgList[1])
                helperVar()
            elif msgType == "PROD": # this gives client the productId so they know which product is being bid on
                productId = int(msgList[1])
            elif msgType == "START_BID": # this initiates the bidding
                productId = int(msgList[1])
                numClients = int(msgList[2])
                if choice():
                    makeBid()
                else:
                    why = "NO_INTEREST"
                    print(f"<NO BID> NO INTEREST")
                    send(f"NO_BID {clientId} {why}")
            elif msgType == "BID":
                clientNum = int(msgList[1])
                bidAmount = float(msgList[2])
                if bidAmount > currentBids[productId]:
                    winnerUpdate(clientNum, bidAmount)
                print(f"Client {clientNum} bidded {bidAmount} for {list(PRODUCTS.keys())[productId]}")
            elif msgType == "NO_BID":
                clientNum = int(msgList[1])
                msgWhy = msgList[2]
                if(clientNum == clientId):
                    pass
                else:
                    print(f"Client {clientNum} reason for not bidding: {msgWhy}")
            elif msgType == "ANY_BIDS":
                if choice():
                    makeBid()
                else:
                    why = "NO_INTEREST"
                    print(f"<NO BID> NO INTEREST")
                    send(f"NO_BID {clientId} {why}")
            elif msgType == "END_BID":
                winnersDisplay()
                send("DISCONNECT")
                return
serverHandle()