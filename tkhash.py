# Python - Find my hash
import sys
import hashlib
import datetime

class Cog:
    Iter = 0
    Max = 256  #sys.maxunicode
    
    def __init__(self):
        self.i = -1
        self.child = None
    
    def get(self):
        u = ""
        try:
            u = chr(self.i)#unichr
        except:
            None
            
        if self.child:
            u = u + self.child.get()
        
        return u
    
    def childOrNext(self):
        Cog.Iter = Cog.Iter + 1
        
        if self.child  and not self.child.isEnd():
            self.child.childOrNext()
        else:
            self.i = self.i + 1
            if self.child:
                self.child.reset()
            
    def isEnd(self):
        return self.i == Cog.Max
    
    def reset(self):
        self.i = 0


tries = 0
guess = ""
accguess = ""
findText = "123"
find = None

if len(sys.argv) > 1:
    findText = sys.argv[1]
    
    if len(findText.strip()) == 32:
        find = findText
        print("LOOK FOR: " + find + " HASH/MD5")
    else:
        find = hashlib.md5(findText.encode('utf-8')).hexdigest()
        print("LOOK FOR: " + findText + " AS " + find)
else:
    find = hashlib.md5(findText.encode('utf-8')).hexdigest()
    print("LOOK FOR: " + findText + " AS " + find)

c = Cog()
c.child = Cog()
c.child.child = Cog()
c.child.child.child = Cog()

start = datetime.datetime.now()

while not c.isEnd():
    s = c.get()
    
    x = hashlib.md5(s.encode('utf-8')).hexdigest()
    
    print(x)
    
    if x == find:
        print("FOUND --> " + s + " --> " + find)
        break
    
    c.childOrNext()
    
elapsed = datetime.datetime.now() - start
elapSec = elapsed.total_seconds()

print("End, iterations: " + str(Cog.Iter) + ", time used: " + str(elapsed) + ", itr/sec: " + str(Cog.Iter/float(elapSec)))