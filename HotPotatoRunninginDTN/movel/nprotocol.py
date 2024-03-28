from calendar import c
from email.headerregistry import Address
from encodings import utf_8
from glob import glob
from http import server
from re import S
from shutil import ExecError
from socket import *
import threading 
from packet import Packet
import pickle
from mc import mcsender , mcreceiver
MYGROUP_6 = 'ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
MYTTL = 10 # Increase to reach other networks
global group ,interface 
interface = None 
group = MYGROUP_6
#udpSocket = socket(AF_INET6, SOCK_DGRAM)
#udpSocket.bind(("2001:6::2",9998))
def sender():  
    while(1):
        if(lastId>0):
            b=(lastId,myaddress)
            snd=pickle.dumps(b)
            try:
                mcsender(group,interface,snd)
            except Exception as e:
                #print(e)
                pass
        

def reciever():
        while(1):
            try:
                data=mcreceiver(group,interface)
                (id1,adrfree)=pickle.loads(data)
                #envia inputs em cache do client para vizinho
                if(len(clientcache)>0):
                    for (a,b) in clientcache.items():
                        if(adrfree!=myaddress):
                            try:
                            
                                (ip,port)=adrfree
                                snd=pickle.dumps(b)
                                udpSocket.sendto(snd,(ip,port))
                                clientcache.pop(a)
                            except Exception as e:
                                #print("nao consegui enviar ao vizinhos")
                               #print(e)
                               pass
              
            except :
                #print("nao recebi multicast")
                pass
            if(not(adrfree==myaddress)):
                if(len(buffer)>0):
                    aux=sorted(buffer.items())
                    for (a,b) in aux:
                        
                        if(b.getTtl()<=0): buffer.pop(a)
                        if(id1<a and b.getAddress()==adrfree):
                               # print("queria mandar para "+ str(b.getAddress()))
                                snd=pickle.dumps(b)
                                try:
                                    udpSocket.sendto(snd,b.getAddress())
                                    buffer.pop(a)
                                except :    
                                    pass
                        b.decrTTL()
                    
                        
                
                

   
    


class Nprotocol:
    def __init__(self, address,i):
        # Socket udp da aplicação
        (ip,port)=address
        global udpSocket
        #print(address)
        udpSocket = socket(AF_INET6, SOCK_DGRAM)
        udpSocket.bind((ip,port-1))
        global buffer
        buffer={}
        global lastId
        lastId=0
        global clientcache
        clientcache={}
        global myaddress
        myaddress=('',0)
        # Buffer de mensagens
        # ...
        if(i!=1):
            self.reciever = threading.Thread(target=reciever)
            self.sender = threading.Thread(target=sender)
		
            self.sender.start()
            self.reciever.start()
    def addCache(self,a,b):
           clientcache[a]=b
    def remCache(self,a,b):
            clientcache.pop(a)            
    def getCache(self):
        return clientcache
    def setLastId(self,id,myaddres):
        global lastId , myaddress
        lastId=id
        myaddress=myaddres
    def getLastId(self):
        return lastId
    def getBuffer(self):
            return buffer
    def addBuffer(self,a,b):
            buffer[a]=b
    def removeBuffer(self,a,b):
            buffer.pop(a)            

    def close(self):
            self.sender.join()
            self.reciever.join()


  

  
 

