from math import prod
import socket
import random
import time

HEADER = 64
PORT = 5050
SERVER = "192.168.1.188 " #Change if server is running on different computer
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

#Connect client to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


#Client variables
clientId = -1
numberOfClients = 0
productId = 0
lastBidder = -1
clientHighestPrices = []
currentBids = []
bidWinners = []


#update data
def updateWinner(bidClient, bidAmount):
    bidWinners[productId] = bidClient
    currentBids[productId] = bidAmount

#help displays the winners on client side
def displayWinners():
    productId = 0
    print("_______END OF BID_______")
    for bidWinner in bidWinners:
        print(f"CLIENT {bidWinner} bought {list(PRODUCTS.keys())[productId]} for ${currentBids[productId]}")
        productId += 1

#checks if client is up to bid
#helps so that clients are bombarding server with messages
def ableToBid():
    if(lastBidder + 1) % numberOfClients == clientId:
        return True
    return False

def choice():
    toBid = random.choice([True,False])
    return toBid

#Sends message to server
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

#Function to initialize arrays bidWinners and currentBids
#also set the client profile for each client
def varHelper():
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

#function that decides if client bids for item
def makeABid():
    print(f"Bidding for: {list(PRODUCTS.keys())[productId]}")
    print({currentBids[productId]})
    if bidWinners[productId] == clientId:
        why = "CURRENTLY_HIGHEST_BIDDER"
        print(f"<NO BID> YOU ARE CURRENTLY HIGHEST BIDDER")
        send(f"NO_BID {clientId} {why}")
        return

    currentBid =  currentBids[productId]
    bidAmount = currentBid + random.randint(25,75)

    if bidAmount < clientHighestPrices[productId]:
        print(f"<BID> YOU BID FOR PRODUCT {list(PRODUCTS.keys())[productId]} with amount {bidAmount}")
        send(f"BID {clientId} {bidAmount}")
    else:
        why = "PRICE_TOO_HIGH"
        print(f"<NO BID> PRICE TOO HIGH")
        send(f"NO_BID {clientId} {why}")
        return

#handles messages from server
def handle_server():
    global clientId
    global numberOfClients
    global productId
    global lastBidder

    while True:
        msg = client.recv(HEADER).decode(FORMAT)
        if len(msg):
            msgList = msg.split()
            msgType = msgList[0] 
            if msgType == "CONNECTED":  #Once client is connected give it a id and run varHelper() to initialize bidWinner[] and currentBids[]
                clientId = int(msgList[1])
                varHelper()
            elif msgType == "PROD": #Gives client the productId so they know which product is being bid on
                productId = int(msgList[1])
            elif msgType == "START_BID": #Initiates the bidding
                productId = int(msgList[1])
                numberOfClients = int(msgList[2])
                if choice():
                    makeABid()
                else:
                    why = "DO_NOT_WANT_TO"
                    print(f"<NO BID> DO NOT WANT TO")
                    send(f"NO_BID {clientId} {why}")
            elif msgType == "BID":
                clientNum = int(msgList[1])
                bidAmount = float(msgList[2])
                if bidAmount > currentBids[productId]:
                    updateWinner(clientNum, bidAmount)
                print(f"Client {clientNum} bidded {bidAmount} for {list(PRODUCTS.keys())[productId]}")
            elif msgType == "NO_BID":
                clientNum = int(msgList[1])
                msgWhy = msgList[2]
                if(clientNum == clientId):
                    pass
                else:
                    print(f"Client {clientNum} did not bid for reason: {msgWhy}")
            elif msgType == "ANY_BIDS":
                if choice():
                    makeABid()
                else:
                    why = "DO_NOT_WANT_TO"
                    print(f"<NO BID> DO NOT WANT TO")
                    send(f"NO_BID {clientId} {why}")
            elif msgType == "END_BID":
                displayWinners()
                send("DISCONNECT")
                return
handle_server()