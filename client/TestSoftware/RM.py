#RM.py
from qCard import qCard
from client import *

cardAddresses = [0x19, 0x1A, 0x1B, 0x1C]

def getCardAddress(slot):
    if slot in [2,7,18,23] : return cardAddresses[0]
    if slot in [3,8,19,24] : return cardAddresses[1]
    if slot in [4,9,20,25] : return cardAddresses[2]
    if slot in [5,10,21,26]: return cardAddresses[3]

def getReadoutSlot(slot):
    if slot in [2,3,4,5] : return     1
    if slot in [7,8,9,10] : return    2
    if slot in [18,19,20,21] : return 3
    if slot in [23,24,25,26] : return 4

def ngccmGroup(rm):
    i2cGroups = [0x01, 0x10, 0x20, 0x02]
    return i2cGroups[rm-1]

def get_NGCCM_Group(rmLoc):
    #i2cgroup dict
    return {
        1 : 0x04,
        2 : 0x02,
        3 : 0x01,
        4 : 0x20,
        5 : 0x10,
        6 : 0x20,
        7 : 0x10,
        8 : 0x02,
        9 : 0x01
                }.get([9,7,4,2][rmLoc - 1])

class RM:
    def __init__(self, location, activeSlots, inBus):
        '''Initializes an RM object at a specific location on the test stand'''
        self.qCards = []
	self.myBus = inBus
	self.location = location
        for i in activeSlots:
            if self.checkCards(i):
                self.qCards.append(qCard(i))
    def __repr__(self):
        '''Object representation'''
        return "RM()"
    def __str__(self):
        '''Return a string representation of RM contents'''
        s = ""
        for card in self.qCards:
            s += "qCard at %s \n" % card.slot
        return s

    def checkCards(self, slot):
	self.openChannel()
	bus = webBus(self.myBus, 0)
	activeCard = getCardAddress(slot)
	bus.write(0x00,[0x06])
	bus.write(activeCard,[0x00])
	bus.read(activeCard,4)
	data=bus.sendBatch()
	if (data[1] == "1"):
		return False
	else:
		return True

    # Open Channel to RM
    def openChannel(self):
    	bus = webBus(self.myBus,0)
        if self.location in [3,4]:
            # Open channel to ngCCM for RM 3,4: J1 - J10
            bus.write(0x72,[0x02])
        elif self.location in [1,2]:
            # Open channel to ngCCM for RM 1,2: J17 - J26
            bus.write(0x72,[0x01])
        else:
            print 'Invalid RM = ', self.location
            print 'Please choose RM = {1,2,3,4}'
            return 'closed channel'
        # Open channel to i2c group
        bus.write(0x74, [ngccmGroup(self.location)])
	    bus.read(0x74, 2)
        return bus.sendBatch()

    def runAll(self):
    	self.openChannel()
    	for q in range(len(self.qCards)):
    		self.qCards[q].runAll(self.myBus)

    def runSingle(self, key):
    	self.openChannel()
    	for q in self.qCards:
    	    q.runSingle(key,self.myBus)

    def printAll(self):
        for q in self.qCards:
            print q
