#RM.py
from qCard import qCard
from client import webBus
b = webBus("pi5")

# For QIE Bridge FPGA Addresses
# RM Locations = {1,2,3,4}
# RM 1: i2cGroup 9, J(23, 24, 25, 26)
# RM 2: i2cGroup 7, J(18, 19, 20 21)
# RM 3: i2cGroup 4, J(7, 8, 9, 10)
# RM 4: i2cGroup 2, J(2, 3, 4, 5)

def ngccmGroup(rm):
    i2cGroups = [0x01,0x10,0x20,0x02]
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
    def __init__(self, location, activeSlots):
        '''Initializes an RM object at a specific location on the test stand'''
        self.qCards = []
        self.location = location
        for i in activeSlots:
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

    # Open Channel to RM
    def openChannel(self):
        if self.location in [3,4]:
            # Open channel to ngCCM for RM 3,4: J1 - J10
            b.write(0x72,[0x02])
        elif self.location in [1,2]:
            # Open channel to ngCCM for RM 1,2: J17 - J26
            b.write(0x72,[0x01])
        else:
            print 'Invalid RM = ', self.location
            print 'Please choose RM = {1,2,3,4}'
            return 'closed channel'
        # Open channel to i2c group
        b.write(0x74, ngccmGroup(self.location))
        return b.sendBatch()

    def runAll(self,barCodeList):
        self.openChannel()
        for q in range(len(self.qCards)):
            self.qCards[q].runAll(barCodeList[q])

    def runSingle(self, key):
        self.openChannel()
        for q in self.qCards:
            q.runSingle(key)

    def printAll(self):
        for q in self.qCards:
            print q
