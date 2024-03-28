from http import server
from socket import *
import threading
import time
import pickle
import random
import signal
from dtn1 import dtn
import sys

potato = []
boom = 0
players = {}
location = {}
cycle = True
serverIP = (sys.argv[1],int(sys.argv[2]))
dtn1=dtn(serverIP)
gameTime = 0
movementFlag = True

rows =10
colm =30
player_limit = 5 # isto pode ser calculado automaticamente consoante o tamanho do mapa

def handler(signum, frame):
    global cycle
    global players
    global udpSocket

    cycle = False
    print("\nAtempting server shutdown...")

    exit = "-1"
    for p in players:
        try:
            dtn1.sendto(exit.encode(),p,serverIP)
        except Exception as e:
            print("Failed in sending closing messagem to",p,"because:\n",e)
    

    socket(AF_INET6,SOCK_DGRAM).sendto(exit.encode(),serverIP,serverIP)
    print("Clossing socket")
    dtn1.close()


def checkPass():
    global players
    global location
    global potato
    result = None
    position = location.get(players.get(potato[0][0])) 
    for p in players:
        if [p,players.get(p)] not in potato:
            pos = location.get(players.get(p)) 
            if pos[1] == position[1]:
                if pos[0] == position[0]-1 or pos[0] == position[0]+1:
                    result = p
                    break
            if pos[0] == position[0]:
                if pos[1] == position[1]-1 or pos[1] == position[1]+1:
                    result = p
                    break
    return result

def move(direction, addr):
    global players
    global location
    global movementFlag

    block = False

    position = location.get(players.get(addr))
    if direction == "w":
        if position[0] != 1:
            block = False
            for p in players:
                p = location.get(players.get(p))
                if not block and p[1] == position[1]:
                    if p[0] == position[0]-1:
                        block = True
            if not block:
                position[0] = position[0]-1
    elif direction == "s":
        if position[0] != rows-2:
            block = False
            for p in players:
                p = location.get(players.get(p))
                if not block and p[1] == position[1]:
                    if p[0] == position[0]+1:
                        block = True
            if not block:
                position[0] = position[0]+1
    elif direction == "a":
        if position[1] != 1:
            block = False
            for p in players:
                p = location.get(players.get(p))
                if not block and p[0] == position[0]:
                    if p[1] == position[1]-1:
                        block = True
            if not block:
                position[1] = position[1]-1
    elif direction == "d":
        if position[1] != colm-2:  
            block = False
            for p in players:
                p = location.get(players.get(p))
                if not block and p[0] == position[0]:
                    if p[1] == position[1]+1:
                        block = True
            if not block:
                position[1] = position[1]+1
    else:
        print("Invalid movement from:", addr)
    if not block:
        movementFlag = True
    location.update({players.get(addr):position})

def getEmptyPos():
    global players
    global location
    global rows
    global colm
    i = 0
    found = False
    while not found and i<rows-1:
        i += 1
        j = 0
        while not found and j<colm-1:
            j += 1
            newlocation = [i,j]
            found = True
            for p in players:
                playerLocation = location.get(players.get(p))
                if not found or playerLocation == [i,j]:
                    found = False 
    if not found:
        newlocation = [-1,-1]

    return newlocation

# Finds a new valid ID for a new player
def getValidID():
    global location
    found = False
    newID = 0

    while not found:
        if location.get(newID) != None:
            newID += 1
        else:
            found = True
    return newID

def udpReciever():
    global udpSocket
    global cycle
    global players
    global location
    global movementFlag

    while cycle:
        try:
            
            rcv,addr = dtn1.recvfrom()    
        except:
            pass
        else:
            rcv = rcv.decode()
            if rcv == "1": # Connect new Player
                if len(players) == player_limit: # Decide to accept player or not
                    rcv = "-1"
                    try:
                        dtn1.sendto(rcv.encode(),addr,serverIP)
                    except Exception as e:
                        print(e)
                        break
                    else:
                        print("Refused player at addr:", addr)
                        print("Game full!!! :)")
                else:
                    newEntry = getValidID()
                    players.update({addr:newEntry})
                    l = getEmptyPos()
                    location.update({newEntry:[l[0],l[1]]})
                    rcv = str(newEntry) + "," +str(rows) + "," + str(colm)
                    try:
                        dtn1.sendto(rcv.encode(),addr,serverIP)
                    except Exception as e:
                        print(e)
                        break
                    else:
                        movementFlag = True
                        print("Player joined at addr:", addr)
                print(players)
                print(location)
            elif rcv == "Q": # Disconect Player
                removePlayer(addr)
            elif rcv=="-2":
                pass
            else:
                if rcv == "-1":
                    break
                move(rcv,addr)

# Removes a player from the data and sends a disconect message
def removePlayer(addr):
    global udpPort
    global players
    global location
    location.pop(players.get(addr))
    players.pop(addr)
    msg = "-1"
    try:
        dtn1.sendto(msg.encode(),addr,serverIP)
    except Exception as e:
        print("Failed to disconect player at",addr,"\n",e)  

def increaseGameTime():
    global gameTime

    if gameTime > 1000000:
        gameTime = 0
    else:
        gameTime +=1

def udpSender():
    global udpSocket
    global players
    global location
    global cycle
    global potato
    global boom
    global gameTime
    global movementFlag

    while cycle:
        if len(players) >=3:
            if len(potato) == 0:
                chosen = random.choice(list(players))
                chosen = [chosen,players.get(chosen)]
                potato.append(chosen)
                boom = 120
                bombstate = [potato[0][1],boom]
            elif boom == 0:
                bombstate = [potato[0][1],boom]
                boom -= 1
            elif boom == -1:
                if potato:
                    removePlayer(potato[0][0])
                    movementFlag =  True
                potato = []
                bombstate = None
            else:
                if p:=checkPass():
                    p = [p,players.get(p)]
                    potato.insert(0,p)
                    if len(potato) > 2:
                        potato.pop()
                    if boom < 5:
                        boom += 5
                else:
                    boom -= 1
                bombstate = [potato[0][1],boom]
        else:
            boom = 0
            bombstate = None

        if bombstate:
            bombstateData = ['1',bombstate,gameTime]
            print(bombstateData)
            bombstateData = pickle.dumps(bombstateData)
            for p in players:
                try:
                    
                    dtn1.sendto(bombstateData,p,serverIP)
                except Exception as e:
                    print(e)
                    break

        if movementFlag:
            movementFlag = False
            locationData = ['2',location,gameTime]
            locationData = pickle.dumps(locationData)

            for p in players:
                try:
                    dtn1.sendto(locationData,p,serverIP)
                except Exception as e:
                    print(e)
                    break

        gameTime += 1
        time.sleep(1)

if __name__ == "__main__":
    
    #  connextions
    reciever = threading.Thread(target=udpReciever)
    sender = threading.Thread(target=udpSender)
    
    sender.start()
    reciever.start()

    signal.signal(signal.SIGINT, handler)

    sender.join()
    reciever.join()

    # both threads completely executed
    print("Closing successfully")

