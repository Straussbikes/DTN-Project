class Packet :
    
    def __init__(self, address,id,ttl,data,tipo,source):
        self.id=id
        self.address=address
        self.ttl=ttl
        self.data=data
        self.tipo=tipo
        self.source=source

    def getId(self):
        return self.id
    def getAddress(self):
        return self.address
    def getTtl(self):
        return self.ttl
    def setId(self,id):
        self.id=id
    def setAddress(self,address):
        self.address=address
    def setTtl(self,ttl):
        self.ttl=ttl
    def getData(self):
        return self.data
    def setData(self,data):
        self.data=data
    def gettipo(self):
        return self.tipo
    def setTipo(self,data):
        self.tipo=data
    def decrTTL(self):
        self.ttl=self.ttl-1
    def getSource(self):
        return self.source
    def setSource(self,tipo):
        self.source=tipo




