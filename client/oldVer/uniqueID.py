# Read UniqueID from QIE Card
from client import webBus
import QIELib
b = webBus("pi5")
q = QIELib

# Label RMs as 0, 1, 2, 3
# Label Slots as 0, 1, 2, 3

# Open Channel for QIE Card Given RM and Slot

def openChannel(rm,slot):
    if rm in [0,1]:
        # Open channel to ngCCM for RM 1,2: J1 - J10
        print '##### RM in 0,1 #####'
        b.write(q.MUXs["fanout"],[0x02])
        b.sendBatch()
    elif rm in [2,3]:
        # Open channel to ngCCM for RM 3, 4: J17 - J26
        print '##### RM in 2,3 #####'
        b.write(q.MUXs["fanout"],[0x01])
        b.sendBatch()
    else:
        print 'Invalid RM = ', rm
        print 'Please choose RM = {0,1,2,3}'
        return 'closed channel'
    # Open channel to i2c group
    print '##### open i2c #####'
    # b.clearBus()
    b.write(q.MUXs["ngccm"]["u10"], [q.RMi2c[rm]])
    return b.sendBatch()

# Read UniqueID 8 bytes from SSN, U48 on QIE Card
def uniqueID(rm,slot):
    openChannel(rm,slot)
    print '##### Read UniqueID #####'
    # Reset entire board by writing 0x6 to 0x0.
    b.write(0x00,[0x06])
    # Note that the i2c_select has register address 0x11
    # Value : 4 = 0x04 selects 0x50
    # Note that the SSN expects 32 bits (4 bytes) for writing (send 0x4, 0, 0, 0)
    b.write(q.QIEi2c[slot],[0x11,0x04,0,0,0])
    # Send 0x0 to 0x50 in order to set pointer for reading ID
    # This removes the permutation problem!
    b.write(0x50,[0x00])
    b.read(0x50,8)
    raw_bus = b.sendBatch()
    print raw_bus
    return raw_bus[-1]

######## Old Function... not in use!!!!! #############################

######## May be useful in the future...? #############################

# Read UniqueID for all QIE Cards in Backplane
# To read IDs for RM 1, pass RMList = [0]
# To read IDs for all RMS, pass RMList = [0, 1, 2, 3]
def getUniqueIDs(RMList,num_slots=4):
    uniqueIDArray = []
    # Iterate through RM 0, 1, 2, 3 (include desired RMs in list)
    for rm in RMList:
        idList = []
        # Iterate through Slot 0, 1, 2, 3 (run for all 4 slots by default)
        for slot in xrange(num_slots):
            idList.append(uniqueID(rm,slot))
        uniqueIDArray.append(idList)
    return uniqueIDArray
