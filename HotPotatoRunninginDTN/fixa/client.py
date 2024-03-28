from http import server
from socket import *
import threading
import pickle
import re
import time
import signal
from dtn1 import dtn
import os
import sys
serverIPs = ("2001:4::20",9999)
serverIP = (sys.argv[1],int(sys.argv[2]))
cycle = True
myID = 0
dt=dtn(serverIPs)
lock = threading.Lock()
explosion = None
target = None
countdown = None
explosionPlace = None
movement = None

rows = 0
colm = 0
mapa = []

def handler(signum, frame):
    global udpSocket
    global cycle
    global serverIP
    
    msg = 'Q'
    cycle = False
    try:
        dt.sendto(msg.encode(),serverIP,serverIPs)
    except Exception as e:
        print(e)
        print("Faliled to send to server")
        cycle = False
    
def generate_map():
    global mapa
    global rows
    global colm
    mapa = []
    for i in range(rows):
        row = []
        if i == 0 or i == rows-1:
            for j in range(colm):
                row.append("#")
        else:
            for j in range(colm):
                if j == 0 or j == colm-1:
                    row.append("#")
                else:
                    row.append(" ")
        mapa.append(row)

def print_matrix(matrix):
    colm = len(matrix[0])
    rows = len(matrix)
    print("",flush=False)
    for i in range(rows):
        for j in range(colm):
            print(matrix[i][j], end=" ",flush=False)
        print("",flush=False)
    print("",flush=True)

def timeCheck(myTime,newTime):
    result = False
    if myTime > (1000000-100) and newTime < 100:
        if newTime < myTime:
            result = True
    else:
        if newTime > myTime:
            result = True
    return result

def udpReciever():
    global udpSocket
    global cycle

    global movement
    global target
    global countdown
    global explosionPlace
    bombtime = -1
    movetime = -1
    global msg
    while cycle:
        msg="-2"
        try:
                msg, addr = dt.recvfrom()
               # msg=msg.decode()
        except :
            pass
            #print("Cannot recieve from server")
        else:
            try:
                    msg = pickle.loads(msg)
                    #print(msg)
            except:
                msg = msg.decode()
                if msg == "-1":
                    cycle = False
                else:
                    pass
                    #print("Uknown message:", msg ,"\nRecieved from:", addr)
            else:
                    lock.acquire()
                    try:   
                        if msg[0] == '1':
                            if timeCheck(bombtime, int(msg[2])):
                                bombtime = int(msg[2])
                                target = msg[1][0]
                                countdown = int(msg[1][1])
                        elif msg[0] == '2':
                            if timeCheck(movetime, int(msg[2])):
                                movetime = int(msg[2])
                                movement = msg[1]
                    finally:
                        lock.release()

def udpSender():
    global udpSocket
    global cycle
    global serverIP
    
    while cycle:
        msg = input()
        if msg == "Q":
            cycle = False
        try:
            dt.sendto(msg.encode(),serverIP,serverIPs)
        except Exception as e:
            #print(e)
            #print("Faliled to send to server")
            cycle = False
        
def printer():
    global cycle
    
    global target
    global mapa
    global myID
    global movement
    global explosion
    global explosionPlace
    global countdown
    global lock
    waiting = 0

    while cycle:
        
            generate_map()
        
            lock.acquire()
            try:

                if countdown != None:
                    if countdown > 0:
                        print("\nEXPLOSION COUNTDOWN",countdown, "TICKS!",flush=False)
                        #countdown -= 1
                    else:
                        print("\nBOOM!!!!",flush=False)
                        countdown = None
                        if target == myID:
                            print("\nYou died!! Better luck next time.\n",flush=False)
                        target = None
                        explosion = 2
                else:
                    print("\nWaiting for players",flush=False,end="")
                    i = 0
                    while i < waiting:
                        print(".",end="",flush=False)
                        i += 1
                    if waiting == 3:
                        waiting = 0
                    else: 
                        waiting += 1
                    print("\n",flush=False)
                    
                if movement:
                    for p in movement:
                        l = movement.get(p)
                        if p == target:
                            mapa[l[0]][l[1]] = 'P'
                            explosionPlace = l
                        elif p == myID:
                            mapa [l[0]][l[1]] = 'X'
                        else:
                            mapa [l[0]][l[1]] = 'O'

                if explosion and explosionPlace:
                    if explosion > 0:
                        mapa[explosionPlace[0]][explosionPlace[1]] = '@'
                        explosion -= 1
                    elif explosion == 0:
                        mapa[explosionPlace[0]][explosionPlace[1]] = ' '
                        explosionPlace = None
                        explosion = None

            finally:
                lock.release()

            print_matrix(mapa)
            
            time.sleep(1)
            print("\n\n\n\n\n\n\n")
            

if __name__ == "__main__":
    flag=1
    msg = "1"
    
    try:
        
        dt.sendto(msg.encode(),serverIP,serverIPs)
        while(flag==1):
            msg, addr = dt.recvfrom()
            h=msg.decode()
            if(h!="-2"):
                flag=0          
    except Exception as e:
        print(e)
        print("Failed to connect to server")
    else:
        msg = msg.decode()
        #print(msg)
        if msg == "-1":
            print("Connection refused from server at", addr)
            print("Game is full")
        else:
            msg = re.findall("\d+",msg)
            myID = int(msg[0])
            rows = int(msg[1])
            colm = int(msg[2])
            generate_map()

            # UDP connextions
            reciever = threading.Thread(target=udpReciever)
            sender = threading.Thread(target=udpSender,daemon=True)
            gui = threading.Thread(target=printer)
            
            signal.signal(signal.SIGINT, handler)

            gui.start()
            sender.start()
            reciever.start()

            reciever.join()
            gui.join()
    finally:
        dt.close()

    # both threads completely executed
    print("Closing successfully")
