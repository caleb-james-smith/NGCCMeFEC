# openRM.py

######## open channel to RM! ######################

def openRM(rm):
    if rm in [0,1]:
        # Open channel to ngCCM for RM 0,1: J1 - J10
        # print '##### RM ', rm,' #####'
        b.write(q.MUXs["fanout"],[0x02])
        b.sendBatch()
    elif rm in [2,3]:
        # Open channel to ngCCM for RM 2,3: J17 - J26
        # print '##### RM ', rm,' #####'
        b.write(q.MUXs["fanout"],[0x01])
        b.sendBatch()
    else:
        print 'Invalid RM = ', rm
        print 'Please choose RM = {0,1,2,3}'
        return 'closed channel'
    # Open channel to i2c group
    # print '##### open i2c ' + hex(q.RMi2c[rm]) + ' #####'
    # b.clearBus()
    b.write(q.MUXs["ngccm"]["u10"], [q.RMi2c[rm]])
    return b.sendBatch()
