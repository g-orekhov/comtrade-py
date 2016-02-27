#!/usr/bin/python30
#Version 0.7.0
#Made by Griffon (c) 2009
#gpm@ukr.net
################### IMPORTS ###################

import os

################# DEFINITIONS #################

class Analog_signal:
    
    def __init__(self,num=1,name="Analog Signal"):
        self.num = num
        self.name = name
        #value param name
        self.param = ""
        self.a = 1.0
        self.b = 0.0
        self.time = 0.0
        self.max = 0
        self.min = 0
        self.values = []
    #get real value
    def getRValue(self, id):
        return self.values[id] * self.a + self.b
    
class Binary_signal:
    
    def __init__(self,num=0,name=""):
        self.num = num
        self.name = name
        self.nState = 0
        self.values = []

class Comtrade_config_file:
    
    def __init__(self,file=None):
        self.objectName = "MyStation"
        self.objectNumber = 0
        #A - analog, B - binary
        self.count = 4
        self.countA = 2
        self.countB = 2
        #list of signals
        self.listA = [Analog_signal(1,"Analog 1"),Analog_signal(2,"Analog 2")]
        self.listB = [Binary_signal(1,"Binary 1"),Binary_signal(2,"Binary 2")]
        #frecvency
        self.frecvency = 50
        self.discrCount = 1
        self.discrList = [[1000,100]]
        self.localTimeStart = ["01/01/01","00:00:00.000"]
        self.globalTimeStart = ["01/01/01","00:00:00.000"]
        self.charset = "ASCII"
        
    def readFile(self, filename):
        if (len(filename) < 5) or (filename[-4:] != '.cfg'): return (False,"Wrong config file.")
        if not (os.path.isfile(filename)): return (False,"Config file is not exist.")

        f = open(filename)#, encoding="UTF-8")
        cfg = f.readlines()
        f.close()
        del f
        buf = cfg[0][:-1].split(",")
        self.objectName = buf[0]
        self.objectNumber = int(buf[1])
        
        buf = cfg[1][:-1].split(",")
        self.count = int(buf[0])
        self.countA = int(buf[1][:-1])
        self.countB = int(buf[2][:-1])
        #read analog signals
        self.listA = []
        for i in range(2,self.countA+2):
            sig = Analog_signal()
            buf = cfg[i][:-1].split(",")
            sig.num = int(buf[0])
            sig.name = buf[1]
            sig.param = buf[4]
            sig.a = float(buf[5])
            sig.b = float(buf[6])
            sig.min = int(buf[8])
            sig.max = int(buf[9])
            self.listA += [sig]
        self.listA = tuple(self.listA)
        #read binary signals
        self.listB = []
        for i in range(2+self.countA,self.countA+self.countB+2):
            sig = Binary_signal()
            buf = cfg[i][:-1].split(",")
            sig.num = int(buf[0])
            sig.name = buf[1]
            sig.nState = buf[2]
            self.listB += [sig]
        self.listB = tuple(self.listB)
        #get frecvency
        currPos = self.countA + self.countB + 2
        self.frecvency = int(cfg[currPos][:-1])
        #get discr
        currPos += 1
        self.discrCount = int(cfg[currPos][:-1])
        currPos += 1
        self.discrList = []
        for discr in range(currPos,currPos + self.discrCount):
            buf = cfg[discr][:-1].split(",")
            self.discrList += [[int(buf[0]),int(buf[1])]]

        currPos += self.discrCount
        self.localTimeStart = cfg[currPos][:-1].split(",")
        self.globalTimeStart = cfg[currPos+1][:-1].split(",")
        self.charset = cfg[currPos+2][:-1]
        
        return (True,"")

    def writeFile(self, filename):
        cfg = []
        cfg += [self.objectName+","+format(self.objectNumber)+"\n"]
        cfg += [format(self.count)+","+format(self.countA)+"A,"+format(self.countB)+"D\n"]
        #analog signals
        for sig in self.listA:
            buf = format(sig.num,"02")+","
            buf += sig.name+","
            buf += ","
            buf += ","
            buf += sig.param+","
            buf += format(sig.a)+","
            buf += format(sig.b)+","
            buf += format(sig.time)+","
            buf += format(sig.min)+","
            buf += format(sig.max)
            cfg += [buf+"\n"]
        #binary signals
        for sig in self.listB:
            buf = format(sig.num,"02")+","
            buf += sig.name+","
            buf += format(sig.nState)
            cfg += [buf+"\n"]
        #frecvency
        cfg += [format(self.frecvency)+"\n"]
        #discr
        cfg += [format(self.discrCount)+"\n"]
        for discr in self.discrList:
            cfg += [format(discr[0])+","+format(discr[1])+"\n"]
        #time
        cfg += [self.localTimeStart[0]+","+self.localTimeStart[1]+"\n"]
        cfg += [self.globalTimeStart[0]+","+self.globalTimeStart[1]+"\n"]
        #charset
        cfg += [self.charset+"\n"]
        #writefile
        f = open(filename,"w")
        f.writelines(cfg)
        f.close()

class Comtrade_dat_file:
    
    def __init__(self,file=None):
        self.localTimeList = []
        self.globalTimeList = []
        self.listA = []
        self.listB = []
        
    def readFile(self, filename, cfg):
        if not (os.path.isfile(filename)): return (False,"Data file is not exist.")

        f = open(filename)#, encoding="UTF-8")
        bCount = cfg.countB
        aCount = cfg.countA

        self.listA = []
        self.listB = []
        buf1 = range(2, aCount + 2)
        buf2 = range(aCount + 2, aCount + bCount + 2)
        for line in f.readlines():
            if line[-1] == "\n": line = line[:-1]
            buf = line.split(",")
            self.localTimeList += [int(buf[0])]
            self.globalTimeList += [int(buf[1])]
            l = []
            for i in buf1:
                l += [int(buf[i])]
            self.listA += [tuple(l)]
            l = []
            for i in buf2:
                l += [int(buf[i])]
            self.listB += [tuple(l)]
            
        self.listA = tuple(self.listA)
        self.listB = tuple(self.listB)
        f.close()
        return (True,"")
            
    def writeFile(self, filename):
        dat = []
        for i in range(0,len(self.listA)):
            buf = format(self.localTimeList[i],"010")
            buf += ","+format(self.globalTimeList[i],"010")
            for j in range(0,len(self.listA[0])):
                buf += ","+format(self.listA[i][j]," 07")
            for j in range(0,len(self.listB[0])):
                buf += ","+format(self.listB[i][j])                
            dat += [buf+"\n"]

        f = open(filename,"w")
        f.writelines(dat)
        f.close()
        
class Comtrade:
    
    def __init__(self):
        #object info
        self.objectName = "MyStation"
        self.objectNumber = 0
        #time
        self.localTimeList = []
        self.globalTimeList = []
        self.localTimeStart = ["01/01/01","00:00:00.000"]
        self.globalTimeStart = ["01/01/01","00:00:00.000"]
        #A - analog, B - binary
        self.count = 4
        self.countA = 2
        self.countB = 2
        self.listA = []
        self.listB = []
        #frecvency
        self.frecvency = 50
        #discretization
        self.discrCount = 1
        self.discrList = [[1000,100]]
        #charset
        self.charset = "ASCII"
        #filename
        self.file = ""
        #length
        self.length = 0
        #error information
        self.errorState = (True,"")
        
    def readFile(self, filename):
        cfg = Comtrade_config_file()
        self.file = filename
        #read config file and set config params
        res = cfg.readFile(filename[:-3]+'cfg')
        if not res[0]:
            self.errorState = res
            return res

        self.objectName = cfg.objectName
        self.objectNumber = cfg.objectNumber
        self.localTimeStart = cfg.localTimeStart
        self.globalTimeStart = cfg.globalTimeStart
        self.count = cfg.count
        self.countA = cfg.countA
        self.countB = cfg.countB
        self.frecvency = cfg.frecvency
        self.discrCount = cfg.discrCount
        self.discrList = cfg.discrList
        self.charset = cfg.charset
        #read data file and set values of signals
        dat = Comtrade_dat_file()
        res = dat.readFile(filename[:-3]+'dat',cfg)
        if not res[0]:
            self.errorState = res
            return res

        self.length = len(dat.listA)
        self.localTimeList = dat.localTimeList
        self.globalTimeList = dat.globalTimeList
        
        self.listA = cfg.listA
        for i in range(self.countA):
            buf = []
            for j in range(self.length):
                buf.append(dat.listA[j][i])
            self.listA[i].values = tuple(buf)
        
        self.listB = cfg.listB    
        for i in range(self.countB):
            buf = []
            for j in range(self.length):
                buf.append(dat.listB[j][i])
            self.listB[i].values = tuple(buf)

        del dat, cfg
        return (True,"")

    def writeFile(self, filename=None):
        if filename == None:
            filename = self.file
        #form config file
        cfg = Comtrade_config_file()

        cfg.objectName = self.objectName
        cfg.objectNumber = self.objectNumber
        cfg.localTimeStart = self.localTimeStart
        cfg.globalTimeStart = self.globalTimeStart
        cfg.count = self.count
        cfg.countA = self.countA
        cfg.countB = self.countB
        cfg.frecvency = self.frecvency
        cfg.discrCount = self.discrCount
        cfg.discrList = self.discrList
        cfg.charset = self.charset
        cfg.listA = self.listA
        cfg.listB = self.listB
        
        #form data file
        dat = Comtrade_dat_file()

        dat.localTimeList = self.localTimeList
        dat.globalTimeList = self.globalTimeList
        for i in range(self.length):
            buf = []
            for sig in self.listA:
                buf += [sig.values[i]]
            dat.listA += [buf]
            buf = []
            for sig in self.listB:
                buf += [sig.values[i]]
            dat.listB += [buf]
            
        #write files
        base = os.path.dirname(filename)
        name = os.path.basename(filename)
        cfg.writeFile(base +"/"+ name.split(".")[0]+'.cfg')
        dat.writeFile(base +"/"+ name.split(".")[0]+'.dat')

    def addSignal(self, signal, sType):
        l = []
        if (sType == "a") or (sType == "A"): l = self.listA
        if (sType == "b") or (sType == "B"): l = self.listB
        if l == []: return (False, "Wrong signal type.") 
        l.insert(0, signal)
        self.renum()
        return (True,"")
        
    def delete(self, num, sType):
        l = []
        if (sType == "a") or (sType == "A"): l = self.listA
        if (sType == "b") or (sType == "B"): l = self.listB
        if l == []: return (False, "Wrong signal type.") 
        l.remove(l[num])
        self.renum()
        return (True,"")

    def renum(self):
        self.countA = len(self.listA)
        self.countB = len(self.listB)
        self.count = self.countA + self.countB
        for i in range(self.countA):
            self.listA[i].num = i
        for i in range(self.countB):
            self.listB[i].num = i
       
def test():
    from time import time
    T1 = time()
    com = Comtrade()
    com.readFile("11.cfg") 
    print(time()-T1)

def makecsv(base, fase, r):
    import csv
    c = Comtrade()
    c.readFile("11.cfg")
    f = open('eggs2.csv', 'wt')
    w = csv.writer(f)
    for i in r:
        a = w.writerow((c.listA[base].getRValue(i), c.listA[fase].getRValue(i),))
    f.close()
        
if __name__ == "__main__":
    test()
