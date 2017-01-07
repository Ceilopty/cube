#!usr/bin/env python3
namespace = ("F","L","R","U","D","B")
d = zip(namespace,range(6))


class Tor:
    def __init__(self,direction):
        self.dir=direction
    @property
    def inst(self):
        return self.__inst
    def __call__(self,inst,step=1):
        step=step%4
        print(self,step)
        #self.inst.blabla(step) #todo
        
class MetaUnit(type):
    def __new__(cls,name,bases,attrs):    
        newattrs=dict(zip(namespace,map(lambda x,y:Tor(x,y),namespace)))
        print(name,attrs.keys(),newattrs.keys())
        attrs.update(newattrs)
        return super().__new__(cls,name,bases,attrs)
    def __init__(cls,*args,**kw):
        cls.TEST=lambda x:print(x)
        

class Coordinate(object):
    
    def __init__(self,*args,**kw):pass
        
        
class Corner(object,metaclass=MetaUnit):
    def __init__(self,c1,c2,c3):pass
    pass

class Edge(object,metaclass=MetaUnit):
    pass

class Inner(object,metaclass=MetaUnit):
    @property
    def crdn(self):
        pass
    def __init__(self,c,p,x,y):
        self.__color = c
        self.__pos = (x,y)
        self.__pl = p
    

class Cube(object):
    __ins__={}
    def __new__(cls,rank=3,ni=False,*args,**kw):
        rank=int(rank)
        if not rank in cls.__ins__:
            cls.__ins__[rank]=[super().__new__(cls)]
        if ni:
            cls.__ins__[rank].append(super().__new__(cls))
        return cls.__ins__[rank][-1]
    def __init__(self,rank=3,*args,**kw):
        self.rank=int(rank)
