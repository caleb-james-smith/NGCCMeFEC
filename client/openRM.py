# openRM.py
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
######## open channel to RM! ######################

def openChannel(rm):
    if rm in [3,4]:
        # Open channel to ngCCM for RM 3,4: J1 - J10
        b.write(0x72,[0x02])
    elif rm in [1,2]:
        # Open channel to ngCCM for RM 1,2: J17 - J26
        b.write(0x72,[0x01])
    else:
        print 'Invalid RM = ', rm
        print 'Please choose RM = {1,2,3,4}'
        return 'closed channel'
    # Open channel to i2c group
    b.write(0x74, ngccmGroup(rm))
    return b.sendBatch()

def openRM(rm):
    if rm in [0,1]:
        # Open channel to ngCCM for RM 0,1: J1 - J10
        b.write(0x72,[0x02])
    elif rm in [2,3]:
        # Open channel to ngCCM for RM 2,3: J17 - J26
        b.write(0x72,[0x01])
    else:
        print 'Invalid RM = ', rm
        print 'Please choose RM = {0,1,2,3}'
        return 'closed channel'
    b.write(0x74, ngccmGroup(rm))
    return b.sendBatch()
