#!usr/bin/env python3
_debug = None
namespace = ("F","R","U","B","L","D")
dn = dict(zip(namespace,range(6)))
defaultcolor = (0,1,2,3,4,5)

def adj(*pl):
    if all(isinstance(x,Plane)for x in pl):
        if not pl[0].cube==pl[1].cube==pl[-1].cube:return False
    pl = sorted(dn[i] if i in namespace else dn[i.str] for i in pl)
    if len(pl)==1:return True
    if len(pl)==2:return True if pl[1]-pl[0]-3 else False
    if len(pl)==3:return False if sum(pl)%3 else True

def adjpairs():
    return(a+b for a in namespace for b in namespace if 0<dn[b]-dn[a]!=3)

def adjtris():
    return(sortpl(tris) for tris in (a+b+c for a in"FB"for b in"UD" for c in "RL"))

def sortpl(pls):
    ans=pls if all(pl in namespace for pl in pls)else (pl.str for pl in pls)
    ans=''.join(ans)
    ans=sorted(set(ans),key=lambda x:dn[x])
    return ''.join(ans)

class Pos:
    def __init__(self,x=0,y=0,parent=None,child=None):
        if child:self.parent=child.place
        else:self.parent=parent
        self.child=child
        self.pos=(x,y)
class MetaPos(type):
    def __new__(cls,name,bases,attrs):
        if not Pos in bases:bases=(Pos,)+bases
        def i(self):return iter(self.pos)
        def s(self):return "<Pos%s>"%str(self.pos)
        newattrs={"__iter__":i,"__str__":s,"__repr__":s,"pos":None}
        attrs.update(newattrs)
        return super().__new__(cls,name,bases,attrs)
class SpPos(metaclass=MetaPos):
    def __init__(self,x=0,y=0,spot=None,corner=None):
        if not x-y:return
        if not 0<=min(x,y)<=max(x,y)<=2:return
        super().__init__(x,y,spot,corner)
class LnPos(metaclass=MetaPos):
    def __init__(self,x=0,y=0,line=None,edge=None):
        if line and line.cube:
            if not line.cube.rank-2>x>=0:return
        if not y in (0,1):return
        super().__init__(x,y,line,edge)
class PlPos(metaclass=MetaPos):
    def __init__(self,x=0,y=0,plane=None,inner=None):
        if plane and plane.cube:
            if not plane.cube.rank-2>max(x,y)>=min(x,y)>=0:return
        super().__init__(x,y,plane,inner)

class Map(dict):
    def __init__(self,arg=None,*args,**kwargs):
        self.arg=arg
        if arg and len(arg) is 1:
            for k in tuple(adjpairs())+tuple(adjtris()):
                if arg in k:
                    super().__setitem__(k,Map())
        super().__init__(*args,**kwargs)
    def __getitem__(self,key):
        arg = self.arg
        try:
            return super().__getitem__(key)
        except:
            if arg and len(arg)is 1 and len(key)is 2:
                newself=super().__getitem__(key[0])
                return dict.__getitem__(newself,key[1])
            if isinstance(key,int):
                return super().__getitem__(tuple(filter(lambda x:0 if isinstance(x,str) else 1,self.keys()))[key])
            for k in self.keys():
                if isinstance(k,Pos) and key == k.pos:
                    return super().__getitem__(k)
            raise KeyError
    def __setitem__(self,key,value):
        arg = self.arg
        if not isinstance(key,Pos):raise Exception("key of map must be Pos")
        if arg and len(arg)is 1:
            if not isinstance(key,PlPos):
                newself=super().__getitem__(key.parent.str)
                super(Map,newself).__setitem__(key,value)
        if not key in self.keys():
            if isinstance(key,SpPos)and self.keys():raise Exception("Full")
            if isinstance(key,LnPos)and key.pos[0] in (x.pos[0]for x in filter(lambda x:isinstance(x,Pos),self.keys())):
                print("gagsads!!!!!!!!!",self.arg,type(key),key.pos,self.keys())
                raise Exception("Occupied")
        super().__setitem__(key,value)
        
        
class Place:pass       
class MetaPlace(type):
    def __new__(cls,name,bases,attrs):
        if not Place in bases:bases=(Place,)+bases
        def s(self):return "<%s %s of %s>"%(name,self.str,self.cube)
        def r(self):return "%s at 0x%08X>"%(str(self)[:-1],id(self))
        def p(self):return tuple(self.cube.plane[pl]for pl in self.str)
        newattrs={"__inst__":{},"__str__":s,"__repr__":r,"planes":p}
        if not 'dim' in attrs:newattrs['dim']=3
        attrs.update(newattrs)
        return super().__new__(cls,name,bases,attrs)
    def __call__(cls,arg,cube=None,*args,**kw):
        if isinstance(arg,cls):return arg
        if all(isinstance(x,Plane)for x in arg):cube=arg[0].cube
        elif all(isinstance(x,Line)for x in arg):cube=arg[0].cube
        elif all(isinstance(x,(Plane,Line))for x in arg):cube=arg[0].cube
        arg=sortpl(arg)
        if not adj(*arg):return
        if cls.dim + len(arg) -3:return
        if not cube in cls.__inst__:cls.__inst__[cube]={}
        if not arg in cls.__inst__[cube]:
            cls.__inst__[cube][arg]=super().__call__(*args,**kw)
            cls.__inst__[cube][arg].str=arg
            cls.__inst__[cube][arg].cube=cube
            try:
                cls.__inst__[cube][arg].corner=Map(arg)
                cls.__inst__[cube][arg].edge=Map(arg)
                cls.__inst__[cube][arg].inner=Map(arg)
            except:pass
        return cls.__inst__[cube][arg]

class Spot(metaclass=MetaPlace):
    __slots__=("str","cube","corner")
    dim=0
    def colors(self):
        if len(self.corner):
            m = self.corner[0]
            t = m.pos.pos
            c = m.color
            return c[t[0]],c[t[1]],c[3-t[0]-t[1]]
        else: return (None,)*3
     
class Line(metaclass=MetaPlace):
    __slots__=("str","cube","corner","edge")
    dim=1
    def colors(self):
        r=self.cube.rank-2
        ans = [[None]*r,[None,]*r]
        for k,v in self.edge.items():
            if not k.pos:continue
            if k.pos[1]:
                ans[0][k.pos[0]]=v.color[1]
                ans[1][k.pos[0]]=v.color[0]
            else:
                ans[0][k.pos[0]]=v.color[0]
                ans[1][k.pos[0]]=v.color[1]
        return tuple(tuple(y) for y in ans)
    

class Plane(metaclass=MetaPlace):
    __slots__=("str","cube","corner","edge","inner")
    dim=2
    def colors(self):
        r=self.cube.rank-2
        ans = []
        for i in range(r):ans.append([None]*r)
        for k,v in self.inner.items():
            if not k.pos:continue
            ans[k.pos[0]][k.pos[1]]=v.color
        return tuple(tuple(y)for y in ans)
        
    
class Tor:
    def __init__(self,direction):
        self.dir=direction
    def __call__(self,inst,step=1):
        step=step%4
        if not step:return
        if self.dir in "FLU":step=step-1
        else: step = step+1
        if self.dir in "FB":inst.x()
        if self.dir in "LR":inst.y()
        if self.dir in "UD":inst.z()
        self(inst,step)
    def __str__(self):
        return "<unbound Tor Method %s at 0x%08X>"%(self.dir,id(self))

class Unit:pass

class MetaUnit(type):
    def __new__(cls,name,bases,attrs):
        if not Unit in bases:bases=(Unit,)+bases
        newattrs=dict(zip(namespace,map(lambda x:(lambda *step:x(*step)),map(Tor,namespace))))
        newattrs.update(dict(zip(('x','y','z'),(print,)*3)))
        if not "__str__" in attrs:
            newattrs["__str__"] = lambda self:"<%s object with color %s on %s %s>"%(name,self.color,self.place,self.pos)
            newattrs["__repr__"] = lambda self:"%s at 0x%08X>"%(self.__str__()[:-1],id(self))
        newattrs["__inst__"]=[]
        newattrs["crdn"]=property(lambda x:(x.pl,x.pos,x.color))
        attrs.update(newattrs)
        return super().__new__(cls,name,bases,attrs)
    def __call__(cls,*args,**kwargs):
        cls.__inst__.append(super().__call__(*args,**kwargs))
        return cls.__inst__[-1]

class Coordinate(object):
    def __init__(self,*args,**kw):pass
        
class Corner(metaclass=MetaUnit):
    @property
    def color(self):return self.__color
    @property
    def pos(self):return self.__pos
    @property
    def sp(self):return self.__sp
    place=sp
    @property
    def ln(self):return self.__ln
    @property
    def pl(self):return self.__pl
    def refresh(self):
        for x in (self.sp,)+self.ln+self.pl:x.corner[self.pos]=self
    def clear(self):
        for x in (self.sp,)+self.ln+self.pl:del x.corner[self.pos]
    def __init__(self,c,s,*xy):
        if len(xy)==1:xy=xy[0]
        self.__color = c
        self.__sp = Spot(s) 
        self.__pl = self.sp.planes()
        self.__ln = tuple(self.sp.cube.line[self.sp.str.replace(p,"")]for p in reversed(self.sp.str))
        self.__pos = SpPos(*xy,self.sp,self)
        self.refresh()

class Edge(metaclass=MetaUnit):
    @property
    def color(self):return self.__color
    @property
    def pos(self):return self.__pos
    @property
    def ln(self):return self.__ln
    place=ln
    @property
    def pl(self):return self.__pl
    def refresh(self):
        for x in (self.ln,)+self.pl:
            print(x,self.pl,self.ln)
            x.edge[self.pos]=self
    def clear(self):
        for x in (self.ln,)+self.pl:del x.edge[self.pos]
    def __init__(self,c,e,*xy):
        if len(xy)==1:xy=xy[0]
        self.__color = c
        self.__ln = Line(e)
        self.__pl = self.ln.planes()
        self.__pos = LnPos(*xy,self.ln,self)
        self.refresh()

class Inner(metaclass=MetaUnit):
    @property
    def color(self):return self.__color
    @property
    def pos(self):return self.__pos
    @property
    def pl(self):return self.__pl
    place=pl
    def refresh(self):self.pl.inner[self.pos]=self
    def clear(self):del self.pl.inner[self.pos]
    def __init__(self,c,p,*xy):
        if len(xy)==1:xy=xy[0]
        self.__color = c
        self.__pl = Plane(p)
        self.__pos = PlPos(*xy,self.pl,self)
        self.refresh()
    def x(self):
        print("Innerxing")
        if self.pl:pass
        
class Cube(object):
    __inst__={}
    def __new__(cls,rank=3,ni=False,*args,**kw):
        rank=int(rank)
        if not rank in cls.__inst__:
            cls.__inst__[rank]=[super().__new__(cls)]
        if ni:
            cls.__inst__[rank].append(super().__new__(cls))
        return cls.__inst__[rank][-1]
    def __init__(self,rank=3,*args,**kw):
        self.rank=int(rank)
        self.plane=dict((k,Plane(k,self))for k in namespace)
        self.line=dict((k,Line(k,self))for k in adjpairs())
        self.spot=dict((k,Spot(k,self))for k in adjtris())
        for index in range(5):
            for x in range(rank-2):
                for y in range(rank-2):
                    Inner(defaultcolor[index],self.plane[namespace[index]],(x,y))
        for k,v in self.line.items():
            for x in range(rank-2):
                print(k,x)
                Edge((defaultcolor[namespace.index(k[0])],defaultcolor[namespace.index(k[1])]),v,(x,0))
            
    def __str__(self):return "<Cube%s>"%(self.rank,)
    def __repr__(self):return "%s at 0x%08X>"%(str(self)[:-1],id(self))
            

def main():
    Cube()

if __name__ == "__main__":
    main()
    a=Cube(5)
    b=a.plane["U"]
    c=a.plane["F"]
    d=a.plane['L']
    e=Line((b,c))
    f=Line((b,d))
    g=Spot((e,f))
    h=Spot((b,c,d))
    i=Inner("RED",b,(1,2))    
    j=Edge(("BLUE","RED"),e,(0,0))
    k=Spot((e,d))
    l=Spot((d,f))
    m=Corner(("BLUE","RED","GREEN"),k,(1,2))
