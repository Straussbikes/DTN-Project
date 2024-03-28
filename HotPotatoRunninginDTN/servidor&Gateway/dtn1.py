from http import server
import time
from re import S
from socket import *
import threading
from packet import Packet
import pickle

#gateway=("2001:6::1",9999)
global id
id=0
global gateways
gateways=[]
global mobileNodes
mobileNodes=[]
            
def sender():  
    while(1):
           aux=sorted(bufferE.items())
           for (a,b) in aux:
               flag=0
               try:
                    if(len(aux)>0):
                        sb=pickle.dumps(b)
                        for a in mobileNodes:
                            if(a==b.getAddress()):
                                for a in gateways:  
                                    udpSocket.sendto(sb,a)
                                    bufferE.pop(b.getId())
                                    flag=1
                                
                        if(flag==0):
                            udpSocket.sendto(sb,b.getAddress())
                            bufferE.pop(b.getId())
                       
                   
               except:
                   pass
                   #print("ttl decremented")
                   
                   
                
    

def reciever():

            
            while(1):
                try:  
                  rcv, address = udpSocket.recvfrom(2048)
                  data=pickle.loads(rcv)
                  if(data.gettipo()==1):
                    mobileNodes.append(data.getSource())
                  elif(data.gettipo()==2):
                      (a,b,c,d)=address
                      gateways.append((a,b))
                      #recebe pedido de conexcao do gateway
               
                  bufferR[data.getId()]=data                
                except Exception as e:
                    #print(e)
                    pass 

   
    


class dtn:
    def __init__(self, address):
        # Socket udp da aplicação
        global udpSocket
        udpSocket = socket(AF_INET6, SOCK_DGRAM)
        udpSocket.bind(address)
        global bufferR
        bufferR={}
        global bufferE
        bufferE={}
        self.id=0
        # Buffer de mensagens
        # ...
        self.reciever = threading.Thread(target=reciever)
        self.sender = threading.Thread(target=sender)
        
        self.sender.start()
        self.reciever.start()

    # Receber mensagens do buffer
    def recvfrom(self):
       # recebe da aplicacao
            (ip,port,ss,dd) =udpSocket.getsockname()
            erro="-2"
            aux=sorted(bufferR.items())
            if(len(aux)==0): return  (erro.encode(),(ip,port))    
            for (a,b) in aux:
                b.decrTTL()
                if(b.getAddress()==(ip,port) and b.getTtl()>0):
                    re=b.getData()
                    reti=b.getAddress()
                    retira=a
                    re2=b.getSource()
                    break
            
 
            bufferR.pop(retira)    
            return (re,re2)

        
    # Envia mensagem para um endereço
    def sendto(self,data,address,myaddress):
        global id 
        id=id+1
        pkt = Packet(address,id,500,data,0,myaddress)
        bufferE[id]=pkt

    

    def close(self):
        udpSocket.close()
        self.sender.join()
        self.reciever.join()

