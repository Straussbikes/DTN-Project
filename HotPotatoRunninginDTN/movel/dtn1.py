from http import server
import sys
import time
from re import S
from socket import *
import threading
from packet import Packet
import pickle
from nprotocol import Nprotocol

gateway=("2001:6::1",9999)
global id
id=0
flag=0   
global inputViz
inputViz=[]    
def sender():  
    while(1):

            aux=sorted(bufferE.items())
            for (a,b) in aux:
                try:
                    if(len(aux)>0):
                        sb=pickle.dumps(b)
                        udpSocket.sendto(sb,gateway)
                        bufferE.pop(b.getId())
                except:
                    b.setTipo(3)
                    np.addCache(a,b)
            if(len(inputViz)>0):    
                for a in inputViz:
                    if(a.getTtl()>0):
                        try:
                                sb=pickle.dumps(a)
                                udpSocket.sendto(sb,gateway)
                                inputViz.remove(a)     
                        except Exception as e:
                               pass
                               #print("nao tenho conexao com o gateway")
                               #a.decrTTL()  
                    else:
                        inputViz.remove(a)
            else:
                pass
    

def reciever():
            
            while(1):
                try:  
                  rcv, address = udpSocket.recvfrom(2048)
                  data=pickle.loads(rcv)
                  if(data.getAddress()==myAddress):
                        if(np.getLastId()>data.getId()):
                            pass
                        else:
                            bufferR[data.getId()]=data
                  elif(data.gettipo()==3):
                      inputViz.append(data)
                  else:
                      #data.decrTTL()
                      np.addBuffer(data.getId(),data)
                except Exception as e:
                    #print(e)
                    pass 

   
    


class dtn:
    def __init__(self, address):
        # Socket udp da aplicação
        global myAddress
        myAddress=address
        global udpSocket
        udpSocket = socket(AF_INET6, SOCK_DGRAM)
        udpSocket.bind(address)
        #Buffer de mensagens
        global bufferR
        bufferR={}
        global bufferE
        bufferE={}
        self.id=0
        global np
        #Neighbor Protocol Start
        np=Nprotocol(address,0)
 
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
                    np.setLastId(b.getId(),b.getAddress())
                    break
            #for(c,d) in bufferR.items():
                #d.decrTTL()
                #if(retira>=c and reti==d.getAddress()):
                    #bufferR.pop(c) 
            bufferR.pop(retira)    
            return (re,re2)
                   
                #elif(b.getTtl()<0):
                   # bufferR.pop(a)
        
    # Envia mensagem para um endereço
    def sendto(self,data,address,myaddress):
        global id 
        id=id+1
        pkt = Packet(address,id,100,data,1,myaddress)
        bufferE[id]=pkt

    

    def close(self):
        udpSocket.close()
        self.sender.join()
        self.reciever.join()

