from concurrent.futures import thread
from encodings import utf_8
from glob import glob
from re import S
from socket import *
import threading 
import time
from tkinter import Pack
from packet import Packet
from nprotocol import Nprotocol
import pickle
import sys

serverIP=("2001:6::1",9999)
global id
id=0
servidor=(sys.argv[1],int(sys.argv[2]))
global store 
global pesos
#pesos={("2001:6::3",9999):0,("2001:6::2",9999):1,("2001:6::4",9999):0}
store={}
def sender():  
 
        counter=0
        while(1):
        
            if(not(len(bufferR)==0)):
                for (a,b) in sorted(bufferR.items()):
                    if(b.getTtl()<=0): 
                        bufferR.pop(b.getId())
                    else: b.decrTTL()
                    try:
                        sb=pickle.dumps(b)
                        udpSocket.sendto(sb,b.getAddress())
                        #print("mandei "+ str(b.getId()) + " "+str(b.getAddress()))
                       
                        #maxAddr=max(pesos,key=pesos.get)
                        #print(maxAddr)
                        
                        if(len(np.getBuffer())>0): 
                            despeja=np.getBuffer()
                            for (c,d)in despeja.items():
                                d.decrTTL()
                            
                                if(d.getTtl()>0 and d.getAddress()!=b.getAddress()):
                                    try:
                                        sb1=pickle.dumps(d)
                                        udpSocket.sendto(sb1,b.getAddress())
                                        #print("mandei: "+ str(d.getId())+ " para: "+str(b.getAddress()))
                                        np.removeBuffer(c,d)  
                                    except Exception as e:
                                        print(e)
                                       
                                else: 
                                    #print("eliminei "+ str(c))
                                    np.removeBuffer(c,d)
                               # else: np.removeBuffer(c,d)

                        #pesos[b.getAddress()]=pesos.get(b.getAddress())+1
                        #print(pesos)
                        #print("enviei para "+str(b.getAddress())+ " " +str(b.getId()))
                        #bufferR.pop(b.getId())
                        
                    except :
                        b.decrTTL()
                        
                        np.addBuffer(b.getId(),b)
         
def reciever():
        while(1):
            try:
                msg,addrs=udpSocket.recvfrom(2048)
                pkt=pickle.loads(msg)
                if(pkt.gettipo()==0):
                    #print("recebi "+str(pkt.getId()))
                    bufferR[pkt.getId()]=pkt
                if(pkt.gettipo()==1 or pkt.gettipo()==3):
                    try:
                        print("a enviar ao servidor"+str(pkt.getAddress())+ " "+ str(pkt.getSource())+ str(pkt.gettipo()))
                        udpSocket.sendto(msg,pkt.getAddress())
                    except Exception as e :
                        print(e)
              
            except Exception as e:
                print(e)
       
                
                

   
    


class gateway:
    def __init__(self):
        # Socket udp da aplicação
        global udpSocket
        udpSocket = socket(AF_INET6, SOCK_DGRAM)
        udpSocket.bind(serverIP)
        global bufferR
        bufferR={}
        self.id=0
        ###
        ###@inicia conexao
        snd=Packet(0,0,0,0,0,0)
        snd.setTipo(2)
        snd=pickle.dumps(snd)
        udpSocket.sendto(snd,servidor)
        ###
       
        # Buffer de mensagens
        # Neighbor Protocolo  so usa buffers
        global np
        np=Nprotocol(serverIP,1)
       
        self.reciever = threading.Thread(target=reciever)
        self.sender = threading.Thread(target=sender)
        
        self.sender.start()
        self.reciever.start()
       
   

    def close(self):
        udpSocket.close()
        self.sender.join()
        self.reciever.join()
       

if __name__ == "__main__":
    
   teste= gateway()
 
 

