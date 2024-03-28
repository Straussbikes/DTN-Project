from glob import glob
from re import S
from socket import *
import threading 
import time
from packet import Packet
import pickle
from mc import mcsender , mcreceiver
MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
MYTTL = 10 # Increase to reach other networks

global group ,interface 
interface = None 
group = MYGROUP_6
global udpSocket
udpSocket = socket(AF_INET6, SOCK_DGRAM)
udpSocket.bind(("2001:6::1",9998))
def sender():  
    while(1):
        if(lastId>0):
            #print("mcast send")
            b=(lastId,myaddress)
            snd=pickle.dumps(b)
            try:
                mcsender(group,interface,snd)
                #print("mcast send")
            except Exception as e:
                print(e)
        

def reciever():
        while(1):
            #da o que tem no buffer
            try:
                data=mcreceiver(group,interface)
                (id1,adrfree)=pickle.loads(data)
            except Exception as e:
                print(e)
           
            if(len(buffer)>0):
                aux=sorted(buffer.items())
                for (a,b) in aux:
                    if(id1<a and b.getAddress()==adrfree):
                        #print("try send")
                        snd=pickle.dumps(b)
                        try:
                            udpSocket.sendto(snd,b.getAddress())
                            #print("sent")
                            buffer.pop(a)
                        except:
                            pass
                    b.decrTTL()
                        #send in multicast? ou manda por unicast outra  vez? xD 
                     
                        
                
                

   
    


class Nprotocol:
    def __init__(self, address,i):
        # Socket udp da aplicação
        (ip,port)=address
        global buffer
        buffer={}
        global lastId
        lastId=0
        global myaddress
        myaddress=('',0)
        # Buffer de mensagens
        # ...
        if(i!=1):
            self.reciever = threading.Thread(target=reciever)
            self.sender = threading.Thread(target=sender)
		
            self.sender.start()
            self.reciever.start()
        
    def setLastId(self,id,myaddres):
        global lastId , myaddress
        lastId=id
        myaddress=myaddres
    def getBuffer(self):
            return buffer
    def addBuffer(self,a,b):
            buffer[a]=b
    def removeBuffer(self,a,b):
            buffer.pop(a)            

    def close(self):
            self.sender.join()
            self.reciever.join()


  

  
 

